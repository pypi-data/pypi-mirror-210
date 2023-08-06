# Copyright (C) 2023 Indoc Research
#
# Contact Indoc Research for any questions regarding the use of this source code.

import logging
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List

from azure.storage.blob import AccountSasPermissions
from azure.storage.blob import BlobProperties
from azure.storage.blob import BlobSasPermissions
from azure.storage.blob import generate_blob_sas
from azure.storage.blob import generate_container_sas
from azure.storage.blob.aio import BlobServiceClient

from object_storage.managers.base_manager import BaseObjectStorageManager

logger = logging.getLogger('pilot.obect_storage')


class AzureBlobStorageManager(BaseObjectStorageManager):
    """A client for interacting with Azure Blob Storage.

    Inherits from:
        - BaseObjectStorageManager: to provide a generic interface for object storage clients

    :param connection_string:
        A connection string or SAS URL to an Azure Blob Storage account.
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    async def create_container(self, container_name: str) -> Dict[str, Any]:
        """Creates a new container with the specified name."""

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            container_client = service.get_container_client(container_name)
            resp = await container_client.create_container()
            return resp

    async def list_objects(self, container_name: str) -> List[BlobProperties]:
        """Lists blobs in the specified container."""

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            container_client = service.get_container_client(container_name)
            blobs = []
            async for blob in container_client.list_blobs(results_per_page=10):
                blobs.append(blob)
            return blobs

    async def get_blob_sas(self, container: str, key: str, read: bool = False, write: bool = False) -> str:
        """Generates a URL for a blob with a SAS token that allows read and write access."""

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            sas_token = generate_blob_sas(
                account_name=service.account_name,
                account_key=service.credential.account_key,
                blob_name=key,
                container_name=container,
                permission=BlobSasPermissions(read=read, write=write),
                start=datetime.utcnow(),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )
        return f'{service.url}{container}/{key}?{sas_token}'

    async def get_container_sas(
        self,
        container: str,
        read: bool = False,
        write: bool = False,
        list: bool = False,  # noqa: A002 keeping compatibility with Azure API
        delete: bool = False,
    ) -> str:
        """Generates a URL for the storage account with a SAS token that allows read, write, list, and delete access to
        containers and blobs."""
        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            sas_token = generate_container_sas(
                account_name=service.account_name,
                account_key=service.credential.account_key,
                container_name=container,
                permission=AccountSasPermissions(read=read, write=write, list=list, delete=delete),
                start=datetime.utcnow(),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )
        return f'{service.url}?{sas_token}'
