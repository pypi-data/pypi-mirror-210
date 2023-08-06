"""
Google Kubernetes Engine (GKE) Module for Authentication Implementation
"""

from google.auth import compute_engine, transport
from google.cloud.container_v1 import ClusterManagerClient

from klops.deployment.auth.schema import AbstractKubernetesAuth


class GKEAuthentication(AbstractKubernetesAuth):
    """
    Google Kubernetes Engine (GKE) Class Implementation for Kubernetes authentication.
    """

    def __init__(self, **kwargs):

        super(GKEAuthentication, self).__init__(**kwargs)
        self.authenticate()

    def authenticate(self):
        """Authenticate to GKE cluster.
        """
        cluster_manager_client = ClusterManagerClient()
        cluster = cluster_manager_client.get_cluster(
            name=f'projects/{self.kwargs["project_id"]}/locations/{self.kwargs["zone"]}/clusters/{self.kwargs["cluster_id"]}')

        self.cluster_endpoint = f"https://{cluster.endpoint}:443"

        credentials = compute_engine.Credentials()
        credentials.refresh(transport.requests.Request())
        self.token = credentials.token


__all__ = ["GKEAuthentication"]
