"""
"""
from typing import Any, Type, Union, List, Dict
import mlflow
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV

from klops.experiment.runner import BaseRunner
from klops.experiment.exception import ExperimentFailedException


class GridsearchRunner(BaseRunner):
    """GridSearchCV Runner Implementation.
    """

    def __init__(self,
                 estimator: Type[Any],
                 x_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                 y_train: Union[pd.DataFrame, np.ndarray, List, Dict],
                 x_test: Union[np.ndarray, pd.DataFrame, List[Dict]],
                 y_test: Union[np.ndarray, pd.DataFrame, List],
                 grid_params: Dict = {},
                 tags: Dict = {},
                 autolog_max_tunning_runs: int = None) -> None:
        """

        Args:
            estimator (Type[Any]): _description_
            x_train (Union[pd.DataFrame, np.ndarray, List, Dict]): _description_
            y_train (Union[pd.DataFrame, np.ndarray, List, Dict]): _description_
            x_test (Union[np.ndarray, pd.DataFrame, List[Dict]]): _description_
            y_test (Union[np.ndarray, pd.DataFrame, List]): _description_
            grid_params (Dict, optional):  Defaults to {}.
            autolog_max_tunning_runs (int, optional):  Defaults to None.
        """
        self.grid_params = grid_params
        mlflow.sklearn.autolog(max_tuning_runs=autolog_max_tunning_runs)
        
        super(GridsearchRunner, self).__init__(
            estimator=estimator, x_train=x_train, 
            y_train=y_train, x_test=x_test, y_test=y_test,
            tags=tags)

    def run(self,
            metrices: Dict = {"mean_squared_error": {},
                              "root_mean_squared_error": {}},
            **kwargs: Any) -> Dict[str, Any]:
        """
        Run the experiment using sklearn.model_selection.GridsearchCV tuner.

        Args:
            metrices (Dict, optional):
                Defaults to {"mean_squared_error": {}, "root_mean_squared_error": {}}.
                The sklearn metrices. All metrices method name could be seen here:
                https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics

        Returns:
            Dict: The best fit hyperparams configuration and its model.
        """
        try:
            mlflow.set_tags({**self.tags, "opt": "gridsearch"})

            grid_search = GridSearchCV(
                estimator=self.estimator,
                param_grid=self.grid_params,
                **kwargs
            )

            best_fit = grid_search.fit(self.x_train, self.y_train)
            preds = best_fit.predict(self.x_test)
            for metric, arguments in metrices.items():
                self.call_metrices(metric, self.y_test, preds, **arguments)
            mlflow.end_run()
            return {
                "best_param": best_fit.best_params_,
                "model": best_fit,
                "score": best_fit.best_score_}
        except Exception as exception:
            raise ExperimentFailedException(
                message=str(exception)) from exception


__all__ = ["GridsearchRunner"]
