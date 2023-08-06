"""
Experiment Runner Module without tuner.
"""

from typing import Any, Union, List, Dict
import mlflow
import numpy as np
import pandas as pd

from klops.experiment.runner.base import BaseRunner
from klops.experiment.exception import ExperimentFailedException


class BasicRunner(BaseRunner):
    """
    Experiment Runner Implementation Class without tuner.
    """

    def __init__(self,
                 estimator: Any,
                 x_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                 y_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                 x_test: Union[np.ndarray, pd.DataFrame, List[Dict]],
                 y_test: Union[np.ndarray, pd.DataFrame, List],
                 hyparams: Dict = {},
                 tags: Dict = {},
                 autolog_max_tunning_runs: int = None) -> None:
        """

        Args:
            estimator (Any): _description_
            x_train (Union[pd.DataFrame, np.ndarray, List, Dict]): _description_
            y_train (Union[pd.DataFrame, np.ndarray, List, Dict]): _description_
            x_test (Union[np.ndarray, pd.DataFrame, List[Dict]]): _description_
            y_test (Union[np.ndarray, pd.DataFrame, List]): _description_
            hyparams (Dict, optional):  Defaults to {}.
            autolog_max_tunning_runs (int, optional):  Defaults to None.
        """
        self.hyparams = hyparams
        mlflow.sklearn.autolog(max_tuning_runs=autolog_max_tunning_runs)
        super(BasicRunner, self).__init__(
            estimator=estimator, x_train=x_train, y_train=y_train,
            x_test=x_test, y_test=y_test, tags=tags)

    def run(self,
            metrices: Dict = {"mean_squared_error": {},
                              "root_mean_squared_error": {}},
            **kwargs: Any) -> Dict[str, Any]:
        """
        Run the experiment without any tuner.

        Args:
            metrices (Dict, optional):
                Defaults to {"mean_squared_error": {}, "root_mean_squared_error": {}}.
                The sklearn metrices. All metrices method name could be seen here:
                https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics

        Returns:
            Dict: The best fit hyperparams configuration and its model.
        """
        try:
            mlflow.set_tags({**self.tags, "opt":"hyperopt"})
            mlflow.log_params(kwargs)
            model = self.estimator

            model.fit(self.x_train, self.y_train)
            preds = model.predict(self.x_test)
            metric_name, score = self.call_metrices("root_mean_squared_error", self.y_test, preds)
            for metric, arguments in metrices.items():
                self.call_metrices(metric, self.y_test, preds, **arguments)

            mlflow.end_run()

            return {"best_param": {**self.hyparams}, "model": model, "score":  1 - score}
        except Exception as exception:
            raise ExperimentFailedException(
                message=str(exception)) from exception


__all__ = ["BasicRunner"]
