# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for artifacts_utils.py"""
import copy
import os

from unittest.mock import patch, call, MagicMock

from tests.common.run_mock import RunMock

import azureml.automl.core.shared.constants as shared_constants
import azureml.automl.dnn.vision.common.artifacts_utils as artifacts_utils
from azureml.automl.dnn.vision.common.training_state import TrainingState


class TestArtifactsUtils:

    def test_get_latest_checkpoint_filename(self):
        # No checkpoints
        checkpoint_filenames = []
        filename, epoch = artifacts_utils._get_latest_checkpoint_filename(checkpoint_filenames)
        assert filename is None
        assert epoch == -1

        # Invalid checkpoint file names
        checkpoint_filenames = ["model.pt", "str_model.pt", "0_model.txt"]
        filename, epoch = artifacts_utils._get_latest_checkpoint_filename(checkpoint_filenames)
        assert filename is None
        assert epoch == -1

        # Single checkpoint
        checkpoint_filenames = ["0_model.pt"]
        filename, epoch = artifacts_utils._get_latest_checkpoint_filename(checkpoint_filenames)
        assert filename == "0_model.pt"
        assert epoch == 0

        # Multiple checkpoints should return latest checkpoint
        checkpoint_filenames = ["0_model.pt", "1_model.pt", "2_model.pt"]
        filename, epoch = artifacts_utils._get_latest_checkpoint_filename(checkpoint_filenames)
        assert filename == "2_model.pt"
        assert epoch == 2

        # Combination of valid and invalid checkpoints
        checkpoint_filenames = ["model.pt", "str_model.pt", "5_model.txt", "2_model.pt"]
        filename, epoch = artifacts_utils._get_latest_checkpoint_filename(checkpoint_filenames)
        assert filename == "2_model.pt"
        assert epoch == 2

        # checkpoint file names with nested paths
        checkpoint_filenames = ["train_artifacts/model.pt", "train_artifacts/str_model.pt",
                                "train_artifacts/5_model.txt", "train_artifacts/2_model.pt"]
        filename, epoch = artifacts_utils._get_latest_checkpoint_filename(checkpoint_filenames)
        assert filename == "train_artifacts/2_model.pt"
        assert epoch == 2

    @patch('os.listdir')
    @patch('tests.common.run_mock.RunMock.get_file_names')
    @patch('tests.common.run_mock.RunMock.download_file')
    @patch('torch.load')
    def test_get_latest_checkpoint(self, torch_load_mock, run_download_file_mock,
                                   run_get_file_names_mock, listdir_mock):
        # os.remove mock / check that file is not present

        output_dir = 'train_artifacts'
        run = RunMock('exp_mock')

        def _test(output_dir_list, run_files_list, no_checkpoint, from_output_dir,
                  expected_epoch_local, expected_epoch_remote):
            listdir_mock.reset_mock()
            run_get_file_names_mock.reset_mock()
            run_download_file_mock.reset_mock()
            torch_load_mock.reset_mock()

            expected_epoch = expected_epoch_local if from_output_dir else expected_epoch_remote
            torch_load_mock.return_value = {
                'epoch': expected_epoch
            }
            listdir_mock.return_value = output_dir_list
            run_get_file_names_mock.return_value = run_files_list

            checkpoint = artifacts_utils.get_latest_checkpoint(output_dir, run)
            listdir_mock.assert_called_once()
            run_get_file_names_mock.assert_called_once()

            if no_checkpoint:
                # Expected that no checkpoint is found in both output directory and run artifacts
                run_download_file_mock.assert_not_called()
                torch_load_mock.assert_not_called()
                assert checkpoint is None
            elif from_output_dir:
                # Expected that checkpoint is from output_directory
                run_download_file_mock.assert_not_called()
                expected_checkpoint_path = os.path.join(output_dir, "{}_model.pt".format(expected_epoch_local))
                torch_load_mock.assert_called_once_with(expected_checkpoint_path, map_location='cpu')
                assert checkpoint is not None
                assert checkpoint['epoch'] == expected_epoch
            else:
                # Expected that checkpoint is from remote files
                checkpoint_filename = "{}_model.pt".format(expected_epoch)
                remote_checkpoint_filename = os.path.join(output_dir, checkpoint_filename)

                run_download_file_mock.assert_called_once()
                run_download_file_mock_call_args = run_download_file_mock.call_args[0]
                assert len(run_download_file_mock_call_args) == 2
                assert run_download_file_mock_call_args[0] == remote_checkpoint_filename
                local_checkpoint_path = run_download_file_mock_call_args[1]
                assert local_checkpoint_path.endswith(checkpoint_filename)

                torch_load_calls = []
                if expected_epoch_local is not None:
                    # First local checkpoint is loaded
                    torch_load_calls.append(call(os.path.join(output_dir, "{}_model.pt".format(expected_epoch_local)),
                                                 map_location='cpu'))
                torch_load_calls.append(call(local_checkpoint_path, map_location='cpu'))
                torch_load_mock.assert_has_calls(torch_load_calls)

                assert checkpoint is not None
                assert checkpoint['epoch'] == expected_epoch

        # Checkpoints not present in output_directory and run_artifacts
        local_list = []
        remote_list = []
        _test(local_list, remote_list, True, False, None, None)

        # Invalid checkpoints present in both local and remote
        local_list = ['str_model.pt']
        remote_list = ['train_artifacts/0_model.txt']
        _test(local_list, remote_list, True, False, None, None)

        # Checkpoint files present in local directory, but not in run artifacts
        local_list = ['0_model.pt']
        remote_list = []
        _test(local_list, remote_list, False, True, 0, None)

        # Files present only in remote. But not checkpoint files
        local_list = []
        remote_list = ['logs/0_temp.log']
        _test(local_list, remote_list, True, False, None, None)

        # Files present only in remote. But not in correct directory
        local_list = []
        remote_list = ['dummy_output_dir/0_mode.pt']
        _test(local_list, remote_list, True, False, None, None)

        # Checkpoint files present only in remote.
        local_list = []
        remote_list = ['train_artifacts/0_model.pt']
        _test(local_list, remote_list, False, False, None, 0)

        # Checkpoint files present in local directory and remote. Local has the latest checkpoint
        local_list = ['0_model.pt', '3_model.pt']
        remote_list = ['train_artifacts/1_model.pt', 'train_artifacts/2_model.pt']
        _test(local_list, remote_list, False, True, 3, None)

        # Checkpoint files present in local directory and remote. Remote has the latest checkpoint
        local_list = ['0_model.pt', '2_model.pt', '3_model.pt']
        remote_list = ['train_artifacts/1_model.pt', 'train_artifacts/4_model.pt']
        _test(local_list, remote_list, False, False, 3, 4)

    @patch('azureml.automl.dnn.vision.common.artifacts_utils.load_model_from_checkpoint')
    @patch('azureml.automl.dnn.vision.common.artifacts_utils.get_latest_checkpoint')
    @patch('os.path.exists')
    @patch('torch.load')
    def test_load_state_from_latest_checkpoint(self, torch_load_mock, os_path_exists_mock,
                                               get_latest_checkpoint_mock, load_model_mock):
        output_dir = "train_artifacts"
        run = RunMock("exp")
        distributed = False
        optimizer = MagicMock()
        scheduler = MagicMock()
        model_wrapper = MagicMock()

        model_checkpoint = {
            'epoch': 5,
            'model_state': 'dummy_model_state',
            'model_name': 'dummy_model_name',
            'number_of_classes': 5,
            'optimizer_state': 'dummy_optimizer_state',
            'lr_scheduler_state': 'dummy_lr_scheduler_state',
            'specs': 'dummy_specs',
            'score': 0.9,
            'metrics': {
                'dummy_metric': 0.75
            },
            'training_state': {
                'no_progress_counter': 3,
                'stop_early': True
            }
        }

        best_model_checkpoint = {
            'epoch': 3,
            'model_state': 'dummy_best_model_state',
            'model_name': 'dummy_model_name',
            'number_of_classes': 5,
            'optimizer_state': 'dummy_optimizer_state',
            'lr_scheduler_state': 'dummy_lr_scheduler_state',
            'specs': 'dummy_specs',
            'score': 0.9,
            'metrics': {
                'dummy_metric': 0.75
            }
        }

        def _test(has_checkpoint, has_training_state_in_checkpoint, has_best_model_checkpoint):
            torch_load_mock.reset_mock()
            os_path_exists_mock.reset_mock()
            get_latest_checkpoint_mock.reset_mock()
            load_model_mock.reset_mock()
            optimizer.reset_mock()
            scheduler.reset_mock()
            model_wrapper.reset_mock()

            if has_checkpoint:
                model = copy.deepcopy(model_checkpoint)
                if not has_training_state_in_checkpoint:
                    del model['training_state']
                get_latest_checkpoint_mock.return_value = model

                if has_best_model_checkpoint:
                    os_path_exists_mock.return_value = True
                    torch_load_mock.return_value = best_model_checkpoint
                else:
                    os_path_exists_mock.return_value = False
            else:
                get_latest_checkpoint_mock.return_value = None

            training_state = TrainingState()

            artifacts_utils.load_state_from_latest_checkpoint(output_dir, run, model_wrapper, distributed, optimizer,
                                                              scheduler, training_state)

            if has_checkpoint and has_training_state_in_checkpoint:
                load_model_mock.assert_called_once_with(model_checkpoint, model_wrapper, distributed)
                optimizer.load_state_dict.assert_called_once_with(model_checkpoint['optimizer_state'])
                scheduler.lr_scheduler.load_state_dict.assert_called_once_with(model_checkpoint['lr_scheduler_state'])
                assert training_state.epoch == 5
                assert training_state.no_progress_counter == 3
                assert training_state.stop_early

                if has_best_model_checkpoint:
                    torch_load_mock.assert_called_once_with(
                        os.path.join(output_dir, shared_constants.PT_MODEL_FILENAME), map_location='cpu')
                    assert training_state.best_model_wts is not None
                    assert training_state.best_epoch == 3
                    assert training_state.best_score == 0.9
                    assert training_state.best_model_metrics == {
                        'dummy_metric': 0.75
                    }
                else:
                    assert training_state.best_model_wts is None
                    assert training_state.best_epoch == 0
                    assert training_state.best_score == 0.0
                    assert training_state.best_model_metrics is None
            else:
                assert training_state.epoch == -1
                assert training_state.no_progress_counter == 0
                assert training_state.stop_early is False
                assert training_state.best_model_wts is None
                assert training_state.best_epoch == 0
                assert training_state.best_score == 0.0
                assert training_state.best_model_metrics is None

        # No checkpoint
        _test(False, False, False)

        # Has checkpoint, but no training state in checkpoint
        _test(True, False, False)

        # Has checkpoint, but no best model checkpoint
        _test(True, True, False)

        # Has checkpoint, best model checkpoint
        _test(True, True, True)
