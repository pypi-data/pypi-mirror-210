"""
Default Module for Authentication Implementation
"""

from typing import Any
from .schema import AbstractKubernetesAuth


class DefaultAuthentication(AbstractKubernetesAuth):
    """
    Default Class Implementation for Kubernetes authentication.
    """

    def __init__(self,
                 cluster_host: str = "localhost",
                 token: str = "TokenString123",
                 **kwargs: Any) -> None:
        """
        Default Class Implementation for Kubernetes authentication.
        Args:
            cluster_host (str, optional):  Defaults to "localhost".
            token (str, optional):  Defaults to "TokenString123".
        """
        self.cluster_endpoint = f"https://{cluster_host}:443"
        self.token = token
        super(DefaultAuthentication, self).__init__(**kwargs)


__all__ = ["DefaultAuthentication"]
