"""
Unit Test for Seldon Deployment
"""
from unittest import TestCase
from unittest.mock import Mock, patch
from kubernetes.client import CustomObjectsApi

from klops.deployment import SeldonDeployment


class TestSeldonDeployment(TestCase):
    """
    Test class for SeldonDeployment
    """

    def __init__(self, *args, **kwargs) -> None:
        super(TestSeldonDeployment, self).__init__(*args, **kwargs)
        mock_auth = Mock()
        mock_auth.get_token.return_value = "token string"
        mock_auth.get_cluster_endpoint.return_value = "127.0.0.1"
        self.seldon_deployment = SeldonDeployment(mock_auth, "test-namespace")
        self.deployment_config = {
            "metadata": {
                "name": "mockedLearn"
            }
        }

    @patch.object(CustomObjectsApi, "create_namespaced_custom_object")
    def test_deploy_for_new_deployment(self, mocked_create_deployment):
        """
        Test deploy for new deployment.
        """
        with patch.object(self.seldon_deployment,
                          "check_deployment_exist", return_value=False) as mocked_check_deployment:
            self.seldon_deployment.deploy(
                deployment_config=self.deployment_config)
            mocked_check_deployment.assert_called_once_with(
                deployment_name=self.deployment_config["metadata"]["name"])
            mocked_create_deployment.assert_called_once()

    @patch.object(CustomObjectsApi, "patch_namespaced_custom_object")
    def test_deploy_for_existing_deployment(self, mocked_patch_deployment):
        """
        Test deploy or existing deployment.
        """
        with patch.object(self.seldon_deployment,
                          "check_deployment_exist",
                          return_value=True) as mocked_check_deployment:
            self.seldon_deployment.deploy(
                deployment_config=self.deployment_config)
            mocked_check_deployment.assert_called_once_with(
                deployment_name=self.deployment_config["metadata"]["name"])
            mocked_patch_deployment.assert_called_once()

    @patch.object(CustomObjectsApi, "delete_namespaced_custom_object")
    def test_delete_deployment(self, mocked_delete_deployment):
        """
        Test the delete deployment
        """
        with patch.object(self.seldon_deployment,
                          "check_deployment_exist", return_value=True) as mocked_check_deployment:
            self.seldon_deployment.delete(self.deployment_config)
            mocked_check_deployment.assert_called_once_with(
                deployment_name=self.deployment_config["metadata"]["name"])
            mocked_delete_deployment.assert_called_once()

    @patch.object(CustomObjectsApi,
                  "list_namespaced_custom_object",
                  return_value={"items": [{"metadata": {"name": "mockedLearn"}}]})
    def testcheck_deployment_exist(self, mocked_list_object):
        """
        Test Check deployment exists
        """
        result = self.seldon_deployment.check_deployment_exist("mockedLearn")
        self.assertTrue(result)
        mocked_list_object.assert_called_once()

    @patch("builtins.open")
    @patch("json.load", return_value=None)
    def test_load_deployment_configuration_with_json_must_be_success(self, mock_open, mock_json):
        self.seldon_deployment.load_deployment_configuration("test.json")
        mock_open.assert_called_once()
        mock_json.assert_called_once()

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_deployment_configuration_with_yaml_must_be_success(self, mock_open, mock_yaml):
        self.seldon_deployment.load_deployment_configuration("test.yml")
        mock_open.assert_called_once()
        mock_yaml.assert_called_once()

    @patch("builtins.open")
    def test_load_deployment_configuration_with_wrong_file_type_must_be_failed(self, mock_open):
        self.assertRaises(ValueError, self.seldon_deployment.load_deployment_configuration, "file.exe")
