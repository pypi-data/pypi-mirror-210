# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
"""
mlflow utilities
"""
from pathlib import Path
import json
from typing import List, Union, Optional
import shutil

from pathlib import Path

from ..constants.constants import MLFlowHFFlavourConstants

from transformers import TrainerCallback, TrainingArguments, TrainerState, TrainerControl
from transformers import PreTrainedModel
from transformers.utils import (
    WEIGHTS_INDEX_NAME,
    SAFE_WEIGHTS_INDEX_NAME,
    WEIGHTS_NAME,
    SAFE_WEIGHTS_NAME
)

from torch_ort import ORTModule

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.accelerator.utils.error_handling.exceptions import LLMException
from azureml.acft.accelerator.utils.error_handling.error_definitions import LLMInternalError
from azureml.acft.accelerator.utils.license_utils import download_license_file

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
import azureml.evaluate.mlflow as mlflow

from .mlflow_preprocess import prepare_mlflow_preprocess, restructure_mlflow_acft_code


logger = get_logger_app()


def replace_deepspeed_zero3_mlflow_pytorch_weights(pytorch_model_save_path: str, mlflow_model_save_path: str):
    """
    Case1
        finetune [nlp contrib] -> AzuremlTrainer.train() [callbacks] -> merge lora weights -> final PyTorch model
        During the mlflow callback, the merged model is not accessible to the model.
        LoRA weights needs to be updated after merging
    Case2
        When deep speed stage3 optimizer is enabled, the model is a dummy object. Hence, the mlflow weights are replaced
        with the PyTorch weights which has decoded weights
    """
    # copy the checkpoint files when deepspeed zero3 is enabled as the model object is a dummy model
    dst_folder = Path(mlflow_model_save_path, "data", "model")

    index_file = Path(pytorch_model_save_path, WEIGHTS_INDEX_NAME)
    safe_index_file = Path(pytorch_model_save_path, SAFE_WEIGHTS_INDEX_NAME)
    weights_file = Path(pytorch_model_save_path, WEIGHTS_NAME)
    safe_weights_file = Path(pytorch_model_save_path, SAFE_WEIGHTS_NAME)

    # remove the existing dummy file if any
    if index_file.exists() or safe_index_file.exists():
        if weights_file.exists():
            weights_file.unlink()
        elif safe_weights_file.exists():
            safe_weights_file.unlink()

        # copy the sharded files to mlflow model artifacts
        load_index_file = index_file if index_file.exists() else safe_index_file
        with open(load_index_file, "r", encoding="utf-8") as f:
            index = json.load(f)
        shard_files = [str(Path(pytorch_model_save_path, x)) for x in list(set(index["weight_map"].values()))]
        shard_files.append(str(load_index_file))    # already has pytorch_model_save_path as prefix
        for shard_file in shard_files:
            shutil.copy(shard_file, str(dst_folder))
    else:
        if weights_file.exists() or safe_weights_file.exists():
            # copy the file to mlflow model artifacts
            existing_weights_file = weights_file if weights_file.exists() else safe_weights_file
            shutil.copy(str(existing_weights_file), str(dst_folder))
        else:
            raise LLMException._with_error(
                AzureMLError.create(
                    LLMInternalError,
                    error=("PyTorch -> MLFlow model conversion failed with DS Stage3 optimizer")
                )
            )


class SaveMLflowModelCallback(TrainerCallback):
    """
    A [`TrainerCallback`] that sends the logs to [AzureML](https://pypi.org/project/azureml-sdk/).
    """

    def __init__(
        self,
        mlflow_model_save_path: Union[str, Path],
        mlflow_infer_params_file_path: Union[str, Path],
        mlflow_task_type: str,
        model_name: str,
        model_name_or_path: Optional[str] = None,
        class_names: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        init azureml_run which is azureml Run object
        """
        self.mlflow_model_save_path = mlflow_model_save_path
        self.mlflow_infer_params_file_path = mlflow_infer_params_file_path
        self.mlflow_task_type = mlflow_task_type
        self.class_names = class_names
        self.model_name = model_name
        self.model_name_or_path = model_name_or_path

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """
        Event called at the end of training.
        Save MLflow model at the end of training

        Model and Tokenizer information is part of kwargs
        """

        model, tokenizer = kwargs["model"], kwargs["tokenizer"]

        # saving the mlflow on world process 0
        if state.is_world_process_zero:
            # tokenization parameters for inference
            # task related parameters
            with open(self.mlflow_infer_params_file_path, 'r') as fp:
                mlflow_inference_params = json.load(fp)

            misc_conf = {
                MLFlowHFFlavourConstants.TASK_TYPE: self.mlflow_task_type,
                MLFlowHFFlavourConstants.TRAIN_LABEL_LIST: self.class_names,
                MLFlowHFFlavourConstants.HUGGINGFACE_ID: self.model_name,
                **mlflow_inference_params,
            }
            # files_list = prepare_mlflow_preprocess()
            # model_artifact_path = "llm_multiclass_model"
            # conda_env = {
            #     'channels': ['conda-forge'],
            #     'dependencies': [
            #         'python=3.8.8',
            #         'pip',
            #         {'pip': [
            #         'mlflow',
            #         'torch==1.12.0',
            #         'transformers==4.6.0',
            #     ]}
            #     ],
            #     'name': 'mlflow-env'
            # }
            if isinstance(model, PreTrainedModel):
                acft_model = model
            elif isinstance(model, ORTModule) and hasattr(model, "module"):
                acft_model = model.module
            else:
                raise LLMException._with_error(
                    AzureMLError.create(LLMInternalError, error=(
                        f"Got unexpected model - {model}"
                    ))
                )
            mlflow.hftransformers.save_model(
                acft_model, self.mlflow_model_save_path, tokenizer, model.config, misc_conf,)
            # code_paths=files_list, artifact_path=model_artifact_path, conda_env=conda_env,)
            # restructure_mlflow_acft_code(self.mlflow_model_save_path)

            # save LICENSE file to MlFlow model
            if self.model_name_or_path:
                license_file_path = Path(self.model_name_or_path, MLFlowHFFlavourConstants.LICENSE_FILE)
                if license_file_path.is_file():
                    shutil.copy(str(license_file_path), self.mlflow_model_save_path)
                    logger.info("LICENSE file is copied to mlflow model folder")
                else:
                    download_license_file(self.model_name, str(self.mlflow_model_save_path))

            logger.info("Saved as mlflow model at {}".format(self.mlflow_model_save_path))
