"""
Client for handling interactions with keyvault
"""

from typing import Union

from azure.core.exceptions import ResourceNotFoundError  # pylint:disable=import-error
from azure.identity import (  # pylint:disable=import-error
    AzureCliCredential,
    ChainedTokenCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
)
from azure.keyvault.secrets import SecretClient  # pylint:disable=import-error


class AzureKeyVaultClient:
    """
    Python client to handle communications with Azure keyvault
    """

    def __init__(self, vault_name):
        """
        Init method for KeyVaultClient
        :param vault_name: Name of the vault
        """
        self.credential = self.get_credential()
        self.vault_url = f"https://{vault_name}.vault.azure.net/"
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    @staticmethod
    def get_credential():
        """
        Generates az credentials for authentication

        The following order of credential methods will be
        1. EnvironmentCredential:
            Secrets set in environment variables.
            Refer to azure identity docs for the correct combination of Environment variables.
        2. ManagedIdentityCredential:
            Identity provided to resources hosted on Azure.
        3. AzureCliCredential:
            Credentials set using `az login`.
        4. SharedTokenCacheCredential:
            For windows, using the login provided for the user.
        """
        credential_chain = (
            EnvironmentCredential(),
            ManagedIdentityCredential(),
            AzureCliCredential(),
            SharedTokenCacheCredential(),
        )
        return ChainedTokenCredential(*credential_chain)

    def get_secret(
        self, name: str, return_none_if_not_found: bool = True
    ) -> Union[str, None]:
        """
        Retrieves secret for provided name from key vaults


        :param name: Key of secret to import
        :param return_none_if_not_found:
            if true and key not found, returns None
            if false and key not found, raise exception
        :return: Secret
        """

        try:
            secret_value = self.client.get_secret(name.replace("_", "-")).value
            return secret_value
        except ResourceNotFoundError as err:
            if "SecretNotFound" in err.message:
                if return_none_if_not_found:
                    return None
            raise err
