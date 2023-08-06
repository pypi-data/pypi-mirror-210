"""
The Deployment init module.
"""

import click


from .deployment import Deployment
from .auth import GKEAuthentication, DefaultAuthentication
from .exception import DeploymentException


@click.command()
@click.option('--deployment_file', '-d',
              prompt='Enter the the deployment file',
              help='The deployment file contains your kubernetes \
                  configuration for seldon deployment.')
@click.option('--cluster', '-c', default="seldon",
              prompt='Enter the cluster name', help='cluster name to be deployed.')
@click.option('--klopsrc_file', '-r', default="seldon",
              prompt='Enter the .klopsrc file',
              help='The .klopsrc file contains your deployment configuration.')
def gke(deployment_file: str, cluster: str, klopsrc_file: str):
    """Deploy our machine learning project to the GKE - seldon cluster.

    Args:
        deployment_file (str): The deployment configuration file. Can be yaml/yml or json file.
        auth_method (str): The auth method name. Must be registered first in the .klopsrc file.
        cluster (str): The cluster name to deploy. Default to 'seldon'.
    """
    try:
        auth_instance = GKEAuthentication()
        auth_instance.read_config("gke", klopsrc_file)

        deployment = Deployment(auth_instance, cluster)
        config = deployment.load_deployment_configuration(deployment_file)
        deployment.deploy(config)
    except Exception as exception:
        raise DeploymentException(status=503, reason=str(
            exception), http_resp=503) from exception


@click.command()
@click.option('--deployment_file', '-d',
              prompt='Enter the the deployment file',
              help='The deployment file contains your kubernetes \
                  configuration for seldon deployment.')
@click.option('--cluster', '-c', default="seldon",
              prompt='Enter the cluster name', help='cluster name to be deployed.')
@click.option('--klopsrc_file', '-r', default="seldon",
              prompt='Enter the .klopsrc file',
              help='The .klopsrc file contains your deployment configuration.')
def default(deployment_file: str, cluster: str, klopsrc_file: str):
    """Deploy our machine learning project to the Self hosted Kubernetes - seldon cluster.

    Args:
        deployment_file (str): The deployment configuration file. Can be yaml/yml or json file.
        auth_method (str): The auth method name. Must be registered first in the .klopsrc file.
        cluster (str): The cluster name to deploy. Default to 'seldon'.
    """
    try:

        auth_instance = DefaultAuthentication()
        auth_instance.read_config("default", klopsrc_file)

        deployment = Deployment(auth_instance, cluster)
        config = deployment.load_deployment_configuration(deployment_file)
        deployment.deploy(config)
    except Exception as exception:
        raise DeploymentException(status=503, reason=str(
            exception), http_resp=503) from exception
