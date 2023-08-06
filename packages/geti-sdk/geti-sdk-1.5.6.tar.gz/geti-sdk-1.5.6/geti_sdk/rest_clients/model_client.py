# Copyright (C) 2022 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

import json
import logging
import os
from typing import List, Optional, TypeVar, Union

from geti_sdk.data_models import (
    Algorithm,
    Job,
    Model,
    ModelGroup,
    OptimizedModel,
    Project,
    Task,
)
from geti_sdk.data_models.enums import JobState, JobType
from geti_sdk.http_session import GetiSession
from geti_sdk.rest_converters import ModelRESTConverter
from geti_sdk.utils import get_supported_algorithms

ModelType = TypeVar("ModelType", Model, OptimizedModel)


class ModelClient:
    """
    Class to manage the models and model groups for a certain project
    """

    def __init__(self, workspace_id: str, project: Project, session: GetiSession):
        self.session = session
        project_id = project.id
        self.project = project
        self.workspace_id = workspace_id
        self.task_ids = [task.id for task in project.get_trainable_tasks()]
        self.base_url = f"workspaces/{workspace_id}/projects/{project_id}/model_groups"
        self.supported_algos = get_supported_algorithms(self.session)

    def get_all_model_groups(self) -> List[ModelGroup]:
        """
        Return a list of all model groups in the project.

        :return: List of model groups in the project
        """
        response = self.session.get_rest_response(url=self.base_url, method="GET")
        if self.session.version.is_sc_1_1 or self.session.version.is_sc_mvp:
            # The API is not fully consistent here, depending on exact release.
            # Response may either be a dict or a list
            try:
                response_array = response["items"]
            except TypeError:
                response_array = response
        else:
            response_array = response["model_groups"]
        model_groups = [
            ModelRESTConverter.model_group_from_dict(group) for group in response_array
        ]
        # Update algorithm details
        for group in model_groups:
            group.algorithm = self.supported_algos.get_by_model_template(
                model_template_id=group.model_template_id
            )
        return model_groups

    def get_model_group_by_algo_name(self, algorithm_name: str) -> Optional[ModelGroup]:
        """
        Return the model group for the algorithm named `algorithm_name`, if any. If
        no model group for this algorithm is found in the project, this method returns
        None

        :param algorithm_name: Name of the algorithm
        :return: ModelGroup instance corresponding to this algorithm
        """
        model_groups = self.get_all_model_groups()
        return next(
            (
                group
                for group in model_groups
                if group.algorithm.algorithm_name == algorithm_name
            ),
            None,
        )

    def get_model_by_algorithm_task_and_version(
        self,
        algorithm: Algorithm,
        version: Optional[int] = None,
        task: Optional[Task] = None,
    ) -> Optional[Model]:
        """
        Retrieve a Model from the Intel® Geti™ server, corresponding to a specific
        algorithm and model version. If no version is passed, this method will
        retrieve the latest model for the algorithm.

        If no model for the algorithm is available in the project, this method returns
        None

        :param algorithm: Algorithm for which to get the model
        :param version: Version of the model to retrieve. If left as None, returns the
            latest version
        :param task: Task for which to get the model. If left as None, this method
            searches for models for `algorithm` in all tasks in the project
        :return: Model object corresponding to `algorithm` and `version`, for a
            specific `task`, if any. If no model is found by those parameters, this
            method returns None
        """
        if task is not None:
            if algorithm.task_type != task.type:
                raise ValueError(
                    f"Unable to retrieve model. The algorithm {algorithm} is not "
                    f"available for the task {task}"
                )
        model_groups = self.get_all_model_groups()
        model_group: Optional[ModelGroup] = None
        for group in model_groups:
            if group.algorithm == algorithm:
                if task is None:
                    model_group = group
                    break
                else:
                    if group.task_id == task.id:
                        model_group = group
                        break
        if model_group is None:
            return None
        if version is not None:
            try:
                model_summary = model_group.get_model_by_version(version=version)
            except ValueError:
                return None
        else:
            model_summary = model_group.get_latest_model()
        return self._get_model_detail(model_group.id, model_id=model_summary.id)

    def _get_model_detail(self, group_id: str, model_id: str) -> Model:
        """
        Return the Model object holding detailed information about the model with
        `model_id` living in the model group with `group_id`.

        :param group_id: Unique database ID of the model group to which the model to
            get belongs
        :param model_id: Unique database ID of the model to get
        :return: Model instance holding detailed information about the model
        """
        model_detail = self.session.get_rest_response(
            url=f"{self.base_url}/{group_id}/models/{model_id}", method="GET"
        )
        model = ModelRESTConverter.model_from_dict(model_detail)
        model.model_group_id = group_id
        model.base_url = self.base_url
        return model

    def get_active_model_for_task(self, task: Task) -> Optional[Model]:
        """
        Return the Model details for the currently active model, for a task if any.
        If the task does not have any trained models, this method returns None

        :param task: Task object containing details of the task to get the model for
        :return: Model object representing the currently active model in the
            Intel® Geti™ project, if any
        """
        model_groups = self.get_all_model_groups()
        model_id: Optional[str] = None
        group_id: Optional[str] = None
        for group in model_groups:
            if not group.has_trained_models:
                continue
            if group.algorithm.task_type != task.type:
                continue
            model_summary = group.get_latest_model()
            if model_summary is not None:
                if model_summary.active_model:
                    model_id = model_summary.id
                    group_id = group.id
                    break
        if model_id is not None:
            return self._get_model_detail(group_id=group_id, model_id=model_id)
        else:
            # Sometimes the `active_model` flag is not set by the server, even though
            # there is a model available for the task. In that case we fall back to
            # returning the latest model in the available model group
            if len(model_groups) == 1:
                model_summary_no_active_check = model_groups[0].get_latest_model()
                if model_summary_no_active_check is not None:
                    model_id = model_summary_no_active_check.id
                    group_id = model_groups[0].id
                    if model_id is not None:
                        return self._get_model_detail(
                            group_id=group_id, model_id=model_id
                        )
        return None

    def _download_model(self, model: ModelType, path_to_folder: str) -> ModelType:
        """
        Download a Model or OptimizedModel.

        :param model: Model or OptimizedModel to download
        :return: Model or OptimizedModel object holding the details of the downloaded
            model
        """
        if isinstance(model, Model):
            url = f"{self.base_url}/{model.model_group_id}/models/{model.id}/export"
            filename = f"{model.name}_base.zip"
        elif isinstance(model, OptimizedModel):
            url = (
                f"{self.base_url}/{model.model_group_id}/models/"
                f"{model.previous_trained_revision_id}/optimized_models/"
                f"{model.id}/export"
            )
            filename = f"{model.name}_{model.optimization_type}_optimized.zip"
        else:
            raise ValueError(
                f"Invalid model type: `{type(model)}. Unable to download model data."
            )
        response = self.session.get_rest_response(
            url=url, method="GET", contenttype="zip"
        )
        model_folder = os.path.join(path_to_folder, "models")
        os.makedirs(model_folder, exist_ok=True, mode=0o770)
        model_filepath = os.path.join(model_folder, filename)
        with open(model_filepath, "wb") as f:
            f.write(response.content)
        return model

    def download_active_model_for_task(
        self, path_to_folder: str, task: Task
    ) -> Optional[Model]:
        """
        Download the currently active model for the task.
        If the task does not have an active model yet, this method returns None

        This method will create a directory 'models' in the path specified in
        `path_to_folder`

        :param path_to_folder: Path to the target folder in which to save the active
            model, and all optimized models derived from it.
        :param task: Task object containing details of the task to download the model
            for
        :return: Model instance holding the details of the active model
        """
        model = self.get_active_model_for_task(task=task)
        if model is None:
            logging.info(
                f"Project '{self.project.name} does not have any trained models yet, "
                f"unable to download active model."
            )
            return None
        model_filepath = os.path.join(path_to_folder, "models")
        logging.info(
            f"Downloading active model for task {task.title} in project "
            f"{self.project.name} to folder {model_filepath}..."
        )
        self._download_model(model, path_to_folder=path_to_folder)
        for optimized_model in model.optimized_models:
            self._download_model(optimized_model, path_to_folder=path_to_folder)
        model_info_filepath = os.path.join(
            model_filepath, f"{task.type}_model_details.json"
        )
        with open(model_info_filepath, "w") as f:
            json.dump(model.to_dict(), f, indent=4)
        return model

    def get_all_active_models(self) -> List[Optional[Model]]:
        """
        Return the Model details for the active model for all tasks in the project,
        if the tasks have any.

        This method returns a list of Models, where the index of the Model in the list
        corresponds to the index of the task in list of trainable tasks for the project.

        If any of the tasks do not have a trained model, the entry corresponding to
        the index of that task will be None

        :return: Model object representing the currently active model for the task in
            the Intel® Geti™ project, if any
        """
        return [
            self.get_active_model_for_task(task=task)
            for task in self.project.get_trainable_tasks()
        ]

    def download_all_active_models(self, path_to_folder: str) -> List[Optional[Model]]:
        """
        Download the active models for all tasks in the project.

        This method will create a directory 'models' in the path specified in
        `path_to_folder`

        :param path_to_folder: Path to the target folder in which to save the active
            models, and all optimized models derived from them.
        :return: List of Model objects representing the currently active models
            (if any) for all tasks in the Intel® Geti™ project. The index of the
            Model in the list corresponds to the index of the task in the list of
            trainable tasks for the project.
        """
        return [
            self.download_active_model_for_task(
                path_to_folder=path_to_folder, task=task
            )
            for task in self.project.get_trainable_tasks()
        ]

    def get_model_for_job(self, job: Job, check_status: bool = True) -> Model:
        """
        Return the model that was created by the `job` from the Intel® Geti™ server.

        :param job: Job to retrieve the model for
        :param check_status: True to first update the status of the job, to make sure
            it is finished. Setting this to False will not update the job status.
        :return: Model produced by the job
        """
        if check_status:
            job.update(self.session)
        if self.session.version.is_sc_mvp or self.session.version.is_sc_1_1:
            job_pid = job.project_id
        else:
            job_pid = job.metadata.project.id
        if job_pid != self.project.id:
            raise ValueError(
                f"Cannot get model for job `{job.description}`. This job does not "
                f"belong to the project managed by this ModelClient instance."
            )
        if job.status.state != JobState.FINISHED:
            raise ValueError(
                f"Job `{job.description}` is not finished yet, unable to retrieve "
                f"model for the job. Please wait until job is finished"
            )
        metadata = job.metadata
        task_data = metadata.task
        version = task_data.model_version
        algorithm = self.supported_algos.get_by_model_template(
            task_data.model_template_id
        )
        if hasattr(task_data, "name") and job.type in (
            JobType.TRAIN,
            JobType.INFERENCE,
            JobType.EVALUATE,
        ):
            task_name = task_data.name
            task = next(
                (
                    task
                    for task in self.project.get_trainable_tasks()
                    if task.title == task_name
                )
            )
            model = self.get_model_by_algorithm_task_and_version(
                algorithm=algorithm, version=version, task=task
            )
            return model
        if job.type == JobType.OPTIMIZATION:
            model_group_id, optimized_model_id = None, None
            if hasattr(metadata, "model_group_id"):
                model_group_id = metadata.model_group_id
            if hasattr(metadata, "optimized_model_id"):
                optimized_model_id = metadata.optimized_model_id
            if model_group_id is not None and optimized_model_id is not None:
                return self._get_model_detail(model_group_id, optimized_model_id)
        raise ValueError(
            f"Unable to retrieve model for job {job.name} of type {job.type}. Getting "
            f"the model for this job type is not supported. "
        )

    def get_task_for_model(self, model: Union[Model, OptimizedModel]) -> Task:
        """
        Return the task to which a certain model belongs, if possible. This method only
        works when the model identifiers are still in place, if they have been stripped
        it will raise a ValueError.

        If the model does not match any task in the project, this method will raise an
        error.

        :param model: Model or OptimizedModel to find the task for
        :return: Task for which the model was trained
        """
        project_model_groups = self.get_all_model_groups()
        tasks = self.project.get_trainable_tasks()
        model_group: Optional[ModelGroup] = None
        error_msg = (
            f"Unable to match model '{model}' to any task in project "
            f"{self.project}. "
        )
        if model.model_group_id is None:
            raise ValueError(
                error_msg + "The model does not contain a model group identifier"
            )
        for group in project_model_groups:
            if group.id == model.model_group_id:
                model_group = group
                break
        if model_group is None:
            raise ValueError(
                error_msg + "The model does not belong to any of the model groups in "
                "the project."
            )
        else:
            task_id = model_group.task_id
            model_task: Optional[Task] = None
            for task in tasks:
                if task.id == task_id:
                    model_task = task
                    break
        if model_task is None:
            raise ValueError(
                error_msg + f"Model was found on the server but could not be linked "
                f"to specific task for 'task_id={model_group.task_id}'."
            )
        else:
            return model_task
