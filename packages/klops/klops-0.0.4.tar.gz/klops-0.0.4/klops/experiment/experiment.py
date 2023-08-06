"""
Main module for Klops MLflow Experiment.
"""

from __future__ import annotations
from datetime import datetime
import os
from typing import Any, Dict, List, Tuple, Union
import warnings

import joblib

from kubernetes.client import ApiException
import mlflow
from mlflow.tracking import MlflowClient
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import klops
from klops.experiment.exception import ExperimentFailedException, \
    UnknownExperimentTunerTypeException
from klops.experiment.runner.base import BaseRunner
from klops.deployment import Deployment
from klops.experiment.runner import BasicRunner, GridsearchRunner, HyperOptRunner
from klops.deployment.auth.schema import AbstractKubernetesAuth
from klops.deployment.exception import DeploymentException

KLOPS_PATH = klops.__path__[0]

warnings.filterwarnings(action="ignore")


class Experiment(MlflowClient):
    """
    Main class for MLflow Experiment. This class would wrap the MLFlow client and \
    it's experiments features.
    """

    best: Dict = {}
    _tracking_uri: str = ""

    def __init__(self, name: str,
                 tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", None)) -> None:
        """
        The Experiment class constructor. Every arguments sets here, \
        would be implemented to all experiments with the same name.
        Args:
            name (str): The experiment name. Example: "my-classification-experiment"
            tracking_uri (str): The MLflow experiment tracking uri. \
                Its our MLflow Tracking server URI. Example: "http://<your-mlflow-host>:<port>"
        """
        self.name = name
        if tracking_uri in ["", None]:
            raise ValueError("Tracking uri must be specified in the configuration.")
        # self.tracking_uri = tracking_uri
        os.environ["MLFLOW_TRACKING_URI"] = tracking_uri


        mlflow.set_experiment(name)

    # @property
    # def tracking_uri(self):
    #     return self._tracking_uri

    def start(self,
              classifier: Any,
              x_train: Union[np.ndarray, pd.DataFrame, List[Dict]],
              y_train: Union[np.ndarray, pd.DataFrame, List],
              save_best_fit: bool = False,
              dataset_auto_split: bool = True,
              x_test: Union[np.ndarray, pd.DataFrame, List[Dict], None] = None,
              y_test: Union[np.ndarray, pd.DataFrame, List, None] = None,
              test_size: float = .2,
              random_state: int = 11,
              tuner: str = None,
              tuner_args: Dict = {},
              metrices: Dict = {
                  "mean_squared_error": {},
                  "root_mean_squared_error": {"squared": False}},
              **kwargs: Any) -> Experiment:
        """
        Start the experiment with given arguments.

        Args:
            classifier (Any): The classifier pointer class. \
                Example: sklearn.naive_bayes.GaussianNB
            x_train (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
                The input features with 2 Dimensional Array like.
            y_train (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
                The output mapping.
            dataset_auto_split (bool): Whether to automatically split the dataset into train-test pairs.
            x_test (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
                The input test value. Only usable when the dataset_auto_split flag is False.
            y_test (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
                The output test value. Only usable when the dataset_auto_split flag is False.
            test_size (float): The split size of the test data.
            random_state (int): The number of random state.
            tuner (str): The tuner could be one of (default | hyperopt | gridsearch). \
                Defaults to None.
            tuner_args (Dict, optional): Defaults to {}. Tunner keyworded arguments. \
                A Dictionary contains key-value pairs set of hyper parameters.
            metrices (_type_, optional): Defaults to \
                { "mean_squared_error": {}, "root_mean_squared_error": {"squared": True}}. \
                The sklearn metrices. All metrices method name could be seen here: \
                https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics

        Raises:
            ValueError: Raised when conditions are not met.

        Returns:
            Experiment: The Experiment instance class.
        """

        runner: BaseRunner = None

        try:

            tags = {}
            if "tags" in kwargs:
                if isinstance(kwargs["tags"], Dict):
                    tags = kwargs["tags"]
                    del kwargs["tags"]
                else:
                    raise ValueError(
                        "Tags should be a dictionary with key-value pair.")
            max_evals = 20
            if "max_evals" in kwargs:
                if isinstance(kwargs["max_evals"], Dict):
                    max_evals = kwargs["max_evals"]
                    del kwargs["max_evals"]
                else:
                    raise ValueError(
                        "Tags should be a dictionary with key-value pair.")

            if dataset_auto_split is True:
                x_train, x_test, y_train, y_test = self.split_train_test(
                    x_train, y_train, test_size=test_size, random_state=random_state)
            else:
                if x_test in [None, []] or y_test in [None, []]:
                    raise ValueError("X_test and y_test must be passed since you have \
                        been defined the `dataset_auto_split` to False.")

            if tuner in ["basic", None, "default"]:
                runner = BasicRunner(
                    estimator=classifier,
                    x_train=x_train,
                    y_train=y_train,
                    x_test=x_test,
                    y_test=y_test,
                    tags=tags,
                    hyparams=tuner_args)
            elif tuner == "hyperopt":
                runner = HyperOptRunner(
                    estimator=classifier,
                    x_train=x_train,
                    y_train=y_train,
                    x_test=x_test,
                    y_test=y_test,
                    experiment_name=self.name,
                    tags=tags,
                    search_spaces=tuner_args,
                    max_evals=max_evals)
            elif tuner == "gridsearch":
                runner = GridsearchRunner(
                    estimator=classifier,
                    x_train=x_train,
                    y_train=y_train,
                    x_test=x_test,
                    y_test=y_test,
                    tags=tags,
                    grid_params=tuner_args)
            else:
                raise ValueError("Unknown Experiment tuner type exception. \
                        It should be on of: 'default'|'gridsearch'|'hyperopt'.")
        except ValueError as value_error:
            raise UnknownExperimentTunerTypeException(
                message=str(value_error)) from value_error

        best_result = runner.run(metrices, **kwargs)
        self.best = best_result

        if save_best_fit:
            self.store_best_fit(classifier.__class__.__name__, best_result.get("model"))

        return self

    def store_best_fit(self, estimator_name: str, model: Any):
        """Save the best fit model from training phase.
        """
        best_running_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.store_artifact(
            model, f"./{self.name}_{estimator_name}_{best_running_time}.pkl", "models/")

    def split_train_test(self,
                         x_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                         y_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                         test_size: float = .2, random_state: int = 11) -> Tuple:
        """Split Data Into Train - Test Pair.

        Args:
            x_train (Union[pd.DataFrame, np.ndarray, List, Dict]): The features of the training sets.
            y_train (Union[pd.DataFrame, np.ndarray, List, Dict]): The target class.
            test_size (float, optional):  Defaults to .2. The test size in float.
            random_state (int, optional):  Defaults to 11. The randomize state.

        Returns:
            Tuple: x_train, x_test, y_train, y_test pair.
        """
        return train_test_split(
            x_train, y_train, test_size=test_size, random_state=random_state)

    def store_artifact(self, model: Any, local_path: str, artifact_path: str) -> None:
        """
        Store the artifact into a joblib file. Then upload to the artifact registry.
        Args:
            model (Any): The model instance.
            local_path (str): The local_path to be dump.
            artifact_path (str): The artifact path in cloud storage.
        """

        joblib.dump(model, local_path)

        mlflow.log_artifact(local_path=local_path, artifact_path=artifact_path)

    def deploy(self,
               artifact_uri: str,
               deployment_name: str,
               model_name: str,
               authentication: AbstractKubernetesAuth,
               namespace: str = 'default',
               deployment_template: str = None) -> Dict:
        """Deploy experiment to Seldon Environment.

        This method would invoke the Deployment class and its dependencies to deploy \
        the experiment using default / user defined template.

        Args:
            artifact_uri (str): The artifact URI. \
                We could see it in the MLflow Tracking Server UI.
            deployment_name (str): The Kubernetes deployment name.
            model_name (str): The model name.
            authentication (AbstractKubernetesAuth): The authentication object. \
                Currently supports for GCP and default / minikube Auth.
            namespace (str, optional):  Defaults to 'default'. \
                The Kubernetes target namespace.
            deployment_template (str, optional):  Defaults to None. \
                Kubernetes JSON template file path. Recommended using default template.
        """
        try:
            deployment = Deployment(
                authentication=authentication, namespace=namespace)
            if deployment_template is None:
                print("Klops path:", KLOPS_PATH)
                deployment_template = os.path.join(
                    KLOPS_PATH, 'templates/deployment_template.json')

            config = deployment.load_deployment_configuration(
                deployment_template)
            config["metadata"]["name"] = deployment_name
            config["spec"]["name"] = model_name
            config["spec"]["predictors"][0]["graph"]["modelUri"] = artifact_uri

            return deployment.deploy(config)
        except ApiException as api_exception:
            raise DeploymentException(
                status=api_exception.status,
                reason=api_exception.reason,
                http_resp="Failed to deploy.") from api_exception
        except Exception as exception:
            raise ExperimentFailedException(
                message=str(exception)) from exception


def start_experiment(
        name: str,
        tracking_uri: str,
        classifier: Any,
        x_train: Union[np.ndarray, pd.DataFrame, List[Dict]],
        y_train: Union[np.ndarray, pd.DataFrame, List[Dict]],
        dataset_auto_split: bool = True,
        x_test: Union[np.ndarray, pd.DataFrame, List[Dict], None] = None,
        y_test: Union[np.ndarray, pd.DataFrame, List, None] = None,
        test_size: float = .2,
        random_state: int = 11,
        tuner: str = None,
        tuner_args: Dict = {},
        metrices: Dict = {
            "mean_squared_error": {},
            "root_mean_squared_error": {"squared": True}}
) -> Experiment:
    """
    The function that wrap all the basic Experiment class do. This make the process more easier.

    Args:
        name (str): The experiment name. Example: "my-classification-experiment"
        tracking_uri (str): The MLflow experiment tracking uri. \
            Its our MLflow Tracking server URI. Example: "http://<your-mlflow-host>:<port>"
        classifier (Any): The classifier pointer class. \
            Example: sklearn.naive_bayes.GaussianNB
        x_train_data (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
            The input features with 2 Dimensional Array like.
        y_train_data (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
            The output mapping.
        dataset_auto_split (bool):  Whether to automatically split the dataset into train-test pairs.
        x_test (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
            The input test value. Only usable when the dataset_auto_split flag is False.
        y_test (Union[np.ndarray, pd.DataFrame, List[Dict]]): \
            The output test value. Only usable when the dataset_auto_split flag is False.
        test_size (float): The split size of the test data.
        random_state (int): The number of random state.
        tuner (str): The tuner could be one of (default | hyperopt | gridsearch). \
            Defaults to None.
        tuner_args (Dict, optional):  Defaults to {}. Tunner keyworded arguments. \
            A Dictionary contains key-value pairs set of hyper parameters.
        metrices (_type_, optional):  Defaults to \
            { "mean_squared_error": {}, "root_mean_squared_error": {"squared": True}}. \
            The sklearn metrices. All metrices method name could be seen here: \
            https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics

    Raises:
        ValueError: Raised when the input arguments has invalid value.

    Returns:
        Experiment: The Experiment class instance.
    """
    experiment = Experiment(name=name, tracking_uri=tracking_uri)
    experiment = experiment.start(
        classifier=classifier, x_train=x_train,
        y_train=y_train, tuner=tuner,
        dataset_auto_split=dataset_auto_split,
        x_test=x_test, y_test=y_test,
        test_size=test_size, random_state=random_state,
        tuner_args=tuner_args, metrices=metrices)

    return experiment
