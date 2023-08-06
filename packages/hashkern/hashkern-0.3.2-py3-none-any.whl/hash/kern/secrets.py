import json
import hvac
from google.cloud import secretmanager_v1
from google.api_core.exceptions import NotFound

import pluggy
from hash import secrets_hookimpl as hookimpl

from hash import errors

hookspec = pluggy.HookspecMarker("hash-secrets")


class SecretsSpec:
    @hookspec
    def init(self, config):
        """Initilize the plugin."""

    @hookspec
    def get(self, key):
        """Get a secret using its key"""

    @hookspec
    def set(self, key, value):
        """Set a value for a key"""


class SecretsVault(object):
    @hookimpl
    def init(self, config):
        self.__url = config.get("url")
        if self.__url is None:
            raise errors.SecretsSpecError(
                f"SecretsVault requires a url config in {config}"
            )
        self.__client = hvac.Client(url=self.__url)

    def __format_key(self, key: str) -> str:
        return key.replace(".", "/")

    @hookimpl
    def get(self, key: str) -> str:
        key = self.__format_key(key)
        try:
            read_response = self.__client.secrets.kv.read_secret_version(path=key)
        except hvac.exceptions.InvalidPath as e:
            raise errors.SecretsProviderError(e)
        return read_response["data"]["data"]

    @hookimpl
    def set(self, key: str, value: dict) -> str:
        key = self.__format_key(key)
        self.__client.secrets.kv.v2.create_or_update_secret(
            path=key,
            secret=value,
        )


class SecretsGCPSM(object):
    @hookimpl
    def init(self, config):
        self.__project = config.get("project")
        if self.__project is None:
            raise errors.SecretsSpecError(
                f"Secrets GCP SM requires a `project` key in {config}"
            )
        self.__client = secretmanager_v1.SecretManagerServiceClient()

    def __format_key(self, key: str):
        return key.replace(":", "_").replace(".", "-")

    @hookimpl
    def get(self, key: str):
        key = self.__format_key(key)
        try:
            response = self.__client.access_secret_version(
                request={
                    "name": f"projects/{self.__project}/secrets/{key}/versions/latest"
                }
            )
            return json.loads(response.payload.data.decode("UTF-8"))
        except Exception as e:
            raise errors.SecretsProviderError(e)

    def create_secret(self, key):
        try:
            self.__client.get_secret(
                request={"name": f"projects/{self.__project}/secrets/{key}"}
            )
        except NotFound as e:
            self.__client.create_secret(
                request={
                    "parent": f"projects/{self.__project}",
                    "secret_id": key,
                    "secret": {"replication": {"automatic": {}}},
                }
            )

    @hookimpl
    def set(self, key: str, value):
        key = self.__format_key(key)
        try:
            self.create_secret(key)
            self.__client.add_secret_version(
                request={
                    "parent": f"projects/{self.__project}/secrets/{key}",
                    "payload": {"data": bytes(json.dumps(value), "UTF-8")},
                }
            )
        except Exception as e:
            raise errors.SecretsProviderError(e)


def get_plugin_manager():
    """
    Return the plugin manager for hash-secrets plugins.
    """
    pm = pluggy.PluginManager("hash-secrets")
    pm.add_hookspecs(SecretsSpec)
    pm.load_setuptools_entrypoints("hash-secrets")
    pm.register(SecretsVault(), "SecretsVault")
    pm.register(SecretsGCPSM(), "SecretsGCPSM")
    return pm


def get_secrets(secret, args):
    """
    Docs Return a secret by its name

    Args:
        secret (str): The name of the secret to return.
        args (dict): A dictionary which contains the config for this secret

    Return:
        object: The secret object, which can be used to get and store secrets
    """
    pm = get_plugin_manager()
    plugins = pm.list_name_plugin()
    for plugin in plugins:
        if secret == plugin[0]:
            hash_secret = plugin[1]
            hash_secret.init(args)
            return hash_secret
