import importlib
import unittest
import pytest
import torch
from unittest.mock import MagicMock, patch
from transformers import TrainingArguments
from azureml.automl.dnn.nlp.common.distributed_trainer import (
    DistributedTrainer,
    DistributedTrainingArguments
)
from torch.utils.data.distributed import DistributedSampler


horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


class TestDistributedTrainingArgsTests:

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("horovod.torch.init")
    @patch("horovod.torch.local_rank")
    @patch("torch.device")
    def test_device(self, device_mock, local_rank_mock, init_mock):

        init_mock.return_value = None
        local_rank_mock.return_value = 0
        device_mock.return_value = torch.device("cpu")

        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=1,
            logging_strategy="no",
            report_to="none"
        )
        DistributedTrainingArguments(args)

        device_mock.assert_called_with("cuda", 0)


class TestDistributedTrainerTests:

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("horovod.torch.broadcast_optimizer_state")
    @patch("horovod.torch.broadcast_parameters")
    @patch("horovod.torch.init")
    @patch("horovod.torch.local_size")
    @patch("horovod.torch.local_rank")
    def test_trainer(self, local_rank_mock, local_size_mock, init_mock, param_mock, optim_mock):

        init_mock.return_value = None
        local_size_mock.return_value = 2
        local_rank_mock.return_value = 0

        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=1,
            logging_strategy="no",
            report_to="none"
        )
        training_args = DistributedTrainingArguments(args)
        DistributedTrainer(model=MagicMock(),
                           args=training_args,
                           train_dataset=MagicMock(),
                           tokenizer=MagicMock(),
                           data_collator=MagicMock())
        init_mock.assert_called_once()
        param_mock.asert_called_once()

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("horovod.torch.DistributedOptimizer")
    @patch("horovod.torch.broadcast_optimizer_state")
    @patch("horovod.torch.broadcast_parameters")
    @patch("horovod.torch.init")
    @patch("horovod.torch.size")
    @patch("horovod.torch.rank")
    @patch("horovod.torch.local_size")
    @patch("horovod.torch.local_rank")
    @pytest.mark.parametrize('gradient_accumulation_steps', [1, 2])
    def test_optimizer(self, local_rank_mock, local_size_mock, rank_mock, size_mock, init_mock,
                       param_mock, optim_mock, dist_optim_mock, gradient_accumulation_steps):
        init_mock.return_value = None
        local_size_mock.return_value = 2
        local_rank_mock.return_value = 0
        rank_mock.return_value = 0
        size_mock.return_value = 4

        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=gradient_accumulation_steps,
            logging_strategy="no",
            report_to="none"
        )
        training_args = DistributedTrainingArguments(args)
        trainer = DistributedTrainer(model=MagicMock(),
                                     args=training_args,
                                     train_dataset=MagicMock(),
                                     tokenizer=MagicMock(),
                                     data_collator=MagicMock())
        trainer.create_optimizer()
        optim_mock.assert_called_once()

        sampler = trainer._get_train_sampler()
        assert type(sampler) is DistributedSampler

        dist_optim_mock.assert_called_once()
        if (gradient_accumulation_steps == 1):
            assert dist_optim_mock.call_args[1]['backward_passes_per_step'] == 1
        else:
            assert dist_optim_mock.call_args[1]['backward_passes_per_step'] == 3

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("horovod.torch.broadcast_optimizer_state")
    @patch("horovod.torch.broadcast_parameters")
    @patch("horovod.torch.init")
    @patch("horovod.torch.local_size")
    @patch("horovod.torch.local_rank")
    @patch("azureml.automl.dnn.nlp.common.distributed_trainer.is_main_process")
    @pytest.mark.parametrize('process_0', [True, False])
    def test_distributed_predict(self, process_mock, local_rank_mock, local_size_mock,
                                 init_mock, param_mock, optim_mock, process_0):
        init_mock.return_value = None
        local_size_mock.return_value = 2
        local_rank_mock.return_value = 0
        process_mock.return_value = process_0

        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=1,
            logging_strategy="no",
            report_to="none"
        )
        training_args = DistributedTrainingArguments(args)
        trainer = DistributedTrainer(model=MagicMock(),
                                     args=training_args,
                                     train_dataset=MagicMock(),
                                     tokenizer=MagicMock(),
                                     data_collator=MagicMock())

        with patch("transformers.Trainer.predict", return_value="some_value") as predict_mock:
            trainer.predict(MagicMock())

        if process_0 is True:
            predict_mock.assert_called_once()
        else:
            predict_mock.assert_not_called()

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("horovod.torch.broadcast_optimizer_state")
    @patch("horovod.torch.broadcast_parameters")
    @patch("horovod.torch.init")
    @patch("horovod.torch.local_size")
    @patch("horovod.torch.local_rank")
    @patch("azureml.automl.dnn.nlp.common.distributed_trainer.is_main_process")
    @pytest.mark.parametrize('process_0', [True, False])
    def test_distributed_eval(self, process_mock, local_rank_mock, local_size_mock,
                              init_mock, param_mock, optim_mock, process_0):
        init_mock.return_value = None
        local_size_mock.return_value = 2
        local_rank_mock.return_value = 0
        process_mock.return_value = process_0

        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=1,
            logging_strategy="no",
            report_to="none"
        )
        training_args = DistributedTrainingArguments(args)
        trainer = DistributedTrainer(model=MagicMock(),
                                     args=training_args,
                                     train_dataset=MagicMock(),
                                     tokenizer=MagicMock(),
                                     data_collator=MagicMock())

        with patch("transformers.Trainer.evaluate", return_value="some_value") as eval_mock:
            trainer.evaluate(MagicMock())

        with patch("transformers.Trainer.evaluate", return_value="some_value") as eval_mock_updated:
            trainer.evaluate(eval_dataset=None, ignore_keys=["loss"], metric_key_prefix="eval")

        if process_0 is True:
            eval_mock.assert_called_once()
            eval_mock_updated.assert_called_with(eval_dataset=None, ignore_keys=["loss"], metric_key_prefix="eval")
        else:
            eval_mock.assert_not_called()
            eval_mock_updated.assert_not_called()
