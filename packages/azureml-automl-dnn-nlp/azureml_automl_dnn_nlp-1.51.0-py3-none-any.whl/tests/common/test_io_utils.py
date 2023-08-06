from unittest.mock import ANY, Mock, patch

import os
import unittest

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import UserException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import DetectedVnetIssue
from azureml.automl.dnn.nlp.common.constants import OutputLiterals, SystemSettings
from azureml.automl.dnn.nlp.common.io.utils import save_model_wrapper
from ..mocks import MockRun


class TestIOUtils(unittest.TestCase):
    @patch('azureml.train.automl.runtime._azureautomlruncontext.AzureAutoMLRunContext.batch_save_artifacts')
    @patch('azureml.core.conda_dependencies.CondaDependencies.create')
    def test_save_model_wrapper_mlflow(self,
                                       mock_create_deps,
                                       mock_batch_save_artifacts):
        model = Mock()
        mock_run = MockRun()
        input_sample_str = "pd.DataFrame({\"text\": pd.Series([\"example_value\"], dtype=\"object\")})"
        output_sample_str = "np.array([\"example_value\"])"
        save_model_wrapper(run=mock_run, model=model, save_mlflow=True,
                           input_sample_str=input_sample_str, output_sample_str=output_sample_str)

        mock_batch_save_artifacts.assert_called_once_with(
            os.getcwd(),
            input_strs={constants.RUN_ID_OUTPUT_PATH: mock_run.id,
                        constants.INFERENCE_DEPENDENCIES: mock_create_deps()},
            model_outputs={os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.MODEL_FILE_NAME): model},
            save_as_mlflow=True,
            mlflow_options={constants.MLFlowLiterals.LOADER: SystemSettings.NAMESPACE,
                            constants.MLFlowLiterals.SCHEMA_SIGNATURE: ANY,
                            constants.MLFlowLiterals.INPUT_EXAMPLE: ANY}
        )  # Correctly route request to batch save artifacts with necessary MLflow settings populated.

        self.assertEqual("inputs: \n  ['text': string]\noutputs: \n  [Tensor('str', (-1,))]\n",
                         str(mock_batch_save_artifacts.call_args[1]["mlflow_options"]["signature"]))

    @patch('azureml.train.automl.runtime._azureautomlruncontext.AzureAutoMLRunContext.batch_save_artifacts')
    @patch('azureml.automl.runtime.network_compute_utils.get_vnet_name')
    def test_save_model_wrapper_intercepts_vnet_errors(self,
                                                       mock_get_vnet_name, mock_batch_save_artifacts):
        mock_get_vnet_name.return_value = "some vnet name"
        mock_batch_save_artifacts.side_effect = ConnectionError
        with self.assertRaises(UserException) as e:
            save_model_wrapper(run=MockRun(), model=Mock())
        self.assertEqual(DetectedVnetIssue.__name__, e.exception.error_code)
