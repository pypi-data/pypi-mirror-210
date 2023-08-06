"""
Base runner module.
"""


from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union

import mlflow
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split

from klops.experiment.exception import InvalidArgumentsException, LogMetricException


class BaseRunner(ABC):
    """
    Abstract class as Base runner implementation.
    """

    metrices: Dict = {"mean_squared_error": {}, "root_mean_squared_error": {}}

    def __init__(self,
                estimator: Any,
                x_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                y_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                x_test: Union[np.ndarray, pd.DataFrame, List[Dict]],
                y_test: Union[np.ndarray, pd.DataFrame, List],
                tags: Dict = {}) -> None:
        """

        Args:
            estimator (Any): _description_
            x_train (Union[pd.DataFrame, np.ndarray, List, Dict]): _description_
            y_train (Union[pd.DataFrame, np.ndarray, List, Dict]): _description_
            x_test (Union[np.ndarray, pd.DataFrame, List[Dict]]): _description_
            y_test (Union[np.ndarray, pd.DataFrame, List]): _description_
            tags (Dict): Defaults to {}. Additional tags for logging in Experiment.
        """
        self.estimator = estimator
        self.x_test = x_test
        self.y_test = y_test
        self.x_train = x_train
        self.y_train = y_train
        self.tags = tags

    @abstractmethod
    def run(self, metrices: Dict, **kwargs: Any) -> Dict[str, Any]:
        """
        The abstract method for base implementation to execute the experiment.

        Args:
            metrices (Dict): The metrices that would be invoked as measurements.

        Returns:
            Dict: The best fit hyperparams configuration and its model.
        """

    def split_train_test(self,
                         x_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                         y_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                         test_size: float = .2, random_state: int = 11) -> None:
        """
        Splits the given datasets of features and its class into train-test group pair.
        Args:
            x_train (Union[pd.DataFrame, np.ndarray, List, Dict]): The features data.
            y_train (Union[pd.DataFrame, np.ndarray, List, Dict]): The class data.
        """
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            x_train, y_train, test_size=test_size, random_state=random_state)

    def call_metrices(self, metric_name: str, *args: Any, **kwargs: Any) -> Tuple:
        """
        Call the measurement metrices (inherited from sklearn metrices), log as mlflow metric.
        Args:
            metric_name (str): The sklearn metrices.
            All metrices method name could be seen here:
            https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics
        """
        try:
            if metric_name != "root_mean_squared_error":

                metric_function = getattr(metrics, metric_name)
                score = metric_function(*args, **kwargs)
            else:
                score = metrics.mean_squared_error(*args, **kwargs)
            mlflow.log_metric(metric_name, score)
            
            return metric_name, score
        except ValueError as value_error:
            raise InvalidArgumentsException(message=str(value_error)) from value_error
        except Exception as exception:
            raise LogMetricException(message=str(exception)) from exception


__all__ = ["BaseRunner"]
