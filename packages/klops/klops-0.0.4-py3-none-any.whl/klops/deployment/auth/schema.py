"""
Kubernetes authentication Basic Schema module.
"""
from abc import ABC, abstractmethod

import configparser
import os
from typing import Dict, Optional

from klops.deployment.exception import WriteAuthConfigException


class AbstractKubernetesAuth(ABC):
    """
    Abstract Class for Kubernetes get authentication
    """

    cluster_endpoint: str = None
    token: str = None

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    @property
    def get_token(self) -> str:
        """
        Get token string from platforms.
        Returns:
            str: A string of Authorization token.
        """
        return self.token

    @property
    def get_cluster_endpoint(self) -> str:
        """
        Get cluster host URI endpoint from platfroms.
        Returns:
            str: A string of host URI endpoint.
        """
        return self.cluster_endpoint

    def read_config(
            self, config_title: str, file_name: Optional[str] = None) -> None:
        """Read from existing configuration file.

        Args:
            config_title (str): The config title section.
            file_name (Optional[str], optional): The file name, including its path. \
                Defaults to None. If None given, it would set to "<current_work_dir>/.klopsrc".
        """

        if file_name is None:
            file_name = os.path.join(os.getcwd(), '.klopsrc')

        config = configparser.ConfigParser()
        config.read(file_name)

        self.cluster_endpoint = config[config_title]["cluster_endpoint"]
        self.token = config[config_title]["token"]

    def store_config(self, config_title: str, file_name: Optional[str] = None) -> bool:
        """Store config session file for The Kubernetes Authentication.

        Args:
            config_title (str): The config title section.
            file_name (Optional[str], optional): The file name, including its path. \
                Defaults to None. If None given, it would set to "<current_work_dir>/.klopsrc".

        Returns:
            bool: Boolean, True if the file stored successfully, False otherwise.
        """
        try:
            if file_name is None:
                file_name = os.path.join(os.getcwd(), '.klopsrc')

            session_config = {}
            session_config['cluster_endpoint'] = self.cluster_endpoint
            session_config['token'] = self.token

            parser = configparser.ConfigParser()
            parser[config_title] = session_config

            with open(file_name, 'w', encoding="utf-8") as config_file:
                parser.write(config_file)
                return True
        except configparser.NoSectionError as no_section_found:
            print("Section not found:", str(no_section_found))
            return False
        except configparser.DuplicateSectionError as duplicate_section_found:
            print("Duplicate section:", str(duplicate_section_found))
            return False
        except configparser.DuplicateOptionError as duplicate_option_found:
            print("Duplicate section:", str(duplicate_option_found))
            return False
        except configparser.InterpolationError as interpolation_error:
            print("Interpolation error:", str(interpolation_error))
            return False
        except Exception as exception:
            raise WriteAuthConfigException(
                reason=str(exception)) from exception
