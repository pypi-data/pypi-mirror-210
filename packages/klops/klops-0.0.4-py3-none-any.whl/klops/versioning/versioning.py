"""
Main module for versioning Control.
"""
from os.path import splitext
from typing import Any, Dict, Iterable, List, Optional, Union

import joblib
import yaml


import dvc
import dvc.api
import pandas as pd

from klops.config import LOGGER
from klops.versioning.helper import shell_executor


class Versioning:
    """
    Versioning control for klops. Based on DVC.
    """

    def init(self) -> None:
        """Initiate DVC

        Initiate the DVC when it's not found.
        """
        shell_executor("dvc init")

    def add_remote(self, name: str, remote_url: str) -> None:
        """
        Add remote repository. Could be local, or remote storage such as GCP bucket or AWS s3.
        Args:
            remote_url (str): The remove URL for the DVC remote repository.
        """
        shell_executor(f"dvc remote add -d {name} {remote_url}")

    def add(self, file_or_path: str) -> None:
        """
        Track the file / path into DVC.
        Args:
            file_or_path (str):  File or path tobe added.
        """
        shell_executor(f"dvc add {file_or_path}")

    def push(self) -> None:
        """
        Push every tracked changes into dvc.
        """
        shell_executor("dvc push")

    def pull(self) -> None:
        """
        Pull the commited data.
        """
        shell_executor("dvc pull")

    def repro(self) -> None:
        """
        Reproduce the DVC pipeline.
        """
        shell_executor("dvc repro")

    def run(self,
            entry_point: str,
            name: str = None,
            dependencies: List = [],
            outputs: List = []) -> None:
        """
        Run the defined DVC pipeline.
        Args:
            entry_point (str):  The main program to be executed.
            name (str, optional): Defaults to None. The Pipeline name.
            dependencies (List, optional): Defaults to []. List of dependencies. \
                The same as `-d` options in dvc command.
            outputs (List, optional): Defaults to []. List of the outputs, The same as `-o` \
                options in dvc command.
        """
        deps = ""
        outs = ""
        name = "" if name is None else f" -n {name}"
        for dep in dependencies:
            deps = deps + "-d " + dep

        for out in outputs:
            outs = outs + "-o " + out

        shell_executor(f"dvc run{name} {deps} {outs} {entry_point}")

    def read_binary(self, file_name: str) -> Any:
        """
        Read the binary file such as .pkl, .joblib, etc. stored in the DVC storage / repository.
        Args:
            file_name (str):  The file name. Including its path.

        Returns:
            Any:  Object pointer instances.
        """
        try:
            with dvc.api.open(
                    file_name,
                    mode='rb'
                ) as buffer:
                model = joblib.load(buffer)

            return model
        except dvc.exceptions.FileMissingError as file_missing:
            LOGGER.error(str(file_missing))
        except dvc.exceptions.PathMissingError as path_missing:
            LOGGER.error(str(path_missing))

    def read_dataset(self,
                     file_name: str,
                     rev: str = None,
                     remote: str = None,
                     **args: Any) -> Any:
        """
        Read dataset from DVC artifact storage.
        Args:
            file_name (str): The file name. Including it's path.
            rev (str, optional): Revision or tags that already defined in git. Defaults to None.
            remote (str, optional): Remote repository URL. Defaults to None.
        Returns:
            Any:  The dataset file buffer. Need to parse.
        """
        try:
            with dvc.api.open(file_name, rev=rev, remote=remote) as file_buffer:
                name, extension = splitext(file_name)
                LOGGER.info("Reading file %s with extension %s", name, extension)
                if extension in [".csv", ".json", ".yaml", ".yml", ".txt"]:
                    if extension == ".csv":
                        return pd.read_csv(file_buffer)
                    elif extension == ".json":
                        return pd.read_json(file_buffer)
                    elif extension in [".yml", ".yaml"]:
                        return yaml.safe_load(file_buffer)
                    elif extension == ".txt":
                        return [line.rstrip() for line in file_buffer.readlines()]
                else:
                    LOGGER.warning("Unsupported file extension: %s, \
                                   this would be return as a buffer.", extension)
                    return file_buffer
        except dvc.exceptions.FileMissingError as file_missing:
            LOGGER.error(str(file_missing))
        except dvc.exceptions.PathMissingError as path_missing:
            LOGGER.error(str(path_missing))

    def get_url(self,
                path: str,
                repo: str = None,
                rev: str = None,
                remote: str = None) -> Any:
        """Get the URL to the storage location of a data file or \
            directory tracked in a DVC project.

        Args:
            path (str): Path to the data file or directory.
            repo (str, optional): Repository URL. Defaults to None.
            rev (str, optional): Revision or tags that already defined in git. Defaults to None.
            remote (str, optional): Remote URL for the repository. Defaults to None.

        Returns:
            Any: Returns the URL string of the storage location (in a DVC remote) \
                where a target file or directory, specified by its path in a repo \
                    (DVC project), is stored.
        """
        return dvc.api.get_url(path, repo, rev, remote)

    def params_show(self,
            *targets: str,  # Optional
            stages: Optional[Union[str, Iterable[str]]] = None,
            repo: Optional[str] = None,
            rev: Optional[str] = None,
            deps: bool = False,
        ) -> Dict:
        """Get parameters tracked in `repo`.

        Without arguments, this function will retrieve all params from all tracked
        parameter files, for the current working tree.

        See the options below to restrict the parameters retrieved.

        Args:
            *targets (str, optional): Names of the parameter files to retrieve
            params from. For example, "params.py, myparams.toml".
            If no `targets` are provided, all parameter files tracked in `dvc.yaml`
            will be used.
            Note that targets don't necessarily have to be defined in `dvc.yaml`.
            repo (str, optional): location of the DVC repository.
                Defaults to the current project (found by walking up from the
                current working directory tree).
                It can be a URL or a file system path.
                Both HTTP and SSH protocols are supported for online Git repos
                (e.g. [user@]server:project.git).
            stages (Union[str, Iterable[str]], optional): Name or names of the
                stages to retrieve parameters from.
                Defaults to `None`.
                If `None`, all parameters from all stages will be retrieved.
                If this method is called from a different location to the one where
                the `dvc.yaml` is found, the relative path to the `dvc.yaml` must
                be provided as a prefix with the syntax `{relpath}:{stage}`.
                For example: `subdir/dvc.yaml:stage-0` or `../dvc.yaml:stage-1`.
            rev (str, optional): Name of the `Git revision`_ to retrieve parameters
                from.
                Defaults to `None`.
                An example of git revision can be a branch or tag name, a commit
                hash or a dvc experiment name.
                If `repo` is not a Git repo, this option is ignored.
                If `None`, the current working tree will be used.
            deps (bool, optional): Whether to retrieve only parameters that are
                stage dependencies or not.
                Defaults to `False`.

        Returns:
            Dict: See Examples below.

        Raises:
            DvcException: If no params are found in `repo`.

        Examples:

            - No arguments.

            Working on https://github.com/iterative/example-get-started

            >>> import json
            >>> import dvc.api
            >>> params = dvc.api.params_show()
            >>> print(json.dumps(params, indent=4))
            {
                "prepare": {
                    "split": 0.2,
                    "seed": 20170428
                },
                "featurize": {
                    "max_features": 200,
                    "ngrams": 2
                },
                "train": {
                    "seed": 20170428,
                    "n_est": 50,
                    "min_split": 0.01
                }
            }

            ---

            - Filtering with `stages`.

            Working on https://github.com/iterative/example-get-started

            `stages` can a single string:

            >>> import json
            >>> import dvc.api
            >>> params = dvc.api.params_show(stages="prepare")
            >>> print(json.dumps(params, indent=4))
            {
                "prepare": {
                    "split": 0.2,
                    "seed": 20170428
                }
            }

            Or an iterable of strings:

            >>> import json
            >>> import dvc.api
            >>> params = dvc.api.params_show(stages=["prepare", "train"])
            >>> print(json.dumps(params, indent=4))
            {
                "prepare": {
                    "split": 0.2,
                    "seed": 20170428
                },
                "train": {
                    "seed": 20170428,
                    "n_est": 50,
                    "min_split": 0.01
                }
            }

            ---

            - Using `rev`.

            Working on https://github.com/iterative/example-get-started

            >>> import json
            >>> import dvc.api
            >>> params = dvc.api.params_show(rev="tune-hyperparams")
            >>> print(json.dumps(params, indent=4))
            {
                "prepare": {
                    "split": 0.2,
                    "seed": 20170428
                },
                "featurize": {
                    "max_features": 200,
                    "ngrams": 2
                },
                "train": {
                    "seed": 20170428,
                    "n_est": 100,
                    "min_split": 8
                }
            }

            ---

            - Using `targets`.

            Working on `multi-params-files` folder of
            https://github.com/iterative/pipeline-conifguration

            You can pass a single target:

            >>> import json
            >>> import dvc.api
            >>> params = dvc.api.params_show("params.yaml")
            >>> print(json.dumps(params, indent=4))
            {
                "run_mode": "prod",
                "configs": {
                    "dev": "configs/params_dev.yaml",
                    "test": "configs/params_test.yaml",
                    "prod": "configs/params_prod.yaml"
                },
                "evaluate": {
                    "dataset": "micro",
                    "size": 5000,
                    "metrics": ["f1", "roc-auc"],
                    "metrics_file": "reports/metrics.json",
                    "plots_cm": "reports/plot_confusion_matrix.png"
                }
            }


            Or multiple targets:

            >>> import json
            >>> import dvc.api
            >>> params = dvc.api.params_show(
            ...     "configs/params_dev.yaml", "configs/params_prod.yaml")
            >>> print(json.dumps(params, indent=4))
            {
                "configs/params_prod.yaml:run_mode": "prod",
                "configs/params_prod.yaml:config_file": "configs/params_prod.yaml",
                "configs/params_prod.yaml:data_load": {
                    "dataset": "large",
                    "sampling": {
                    "enable": true,
                    "size": 50000
                    }
                },
                "configs/params_prod.yaml:train": {
                    "epochs": 1000
                },
                "configs/params_dev.yaml:run_mode": "dev",
                "configs/params_dev.yaml:config_file": "configs/params_dev.yaml",
                "configs/params_dev.yaml:data_load": {
                    "dataset": "development",
                    "sampling": {
                    "enable": true,
                    "size": 1000
                    }
                },
                "configs/params_dev.yaml:train": {
                    "epochs": 10
                }
            }

            ---

            - Git URL as `repo`.

            >>> import json
            >>> import dvc.api
            >>> params = dvc.api.params_show(
            ...     repo="https://github.com/iterative/demo-fashion-mnist")
            {
                "train": {
                    "batch_size": 128,
                    "hidden_units": 64,
                    "dropout": 0.4,
                    "num_epochs": 10,
                    "lr": 0.001,
                    "conv_activation": "relu"
                }
            }


        .. _Git revision:
            https://git-scm.com/docs/revisions

        """
        return dvc.api.params_show(*targets, stages=stages, repo=repo, rev=rev, deps=deps)
