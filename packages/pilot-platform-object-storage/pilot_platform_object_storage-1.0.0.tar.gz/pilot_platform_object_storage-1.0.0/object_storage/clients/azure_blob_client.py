# Copyright (C) 2023 Indoc Research
#
# Contact Indoc Research for any questions regarding the use of this source code.

import logging
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Optional

from azure.storage.blob import BlobProperties
from azure.storage.blob.aio import BlobClient

from object_storage.clients.base_file_client import BaseFileClient
from object_storage.providers.azure import AzureClient

logger = logging.getLogger('pilot.obect_storage')


class AzureBlobClient(BaseFileClient, AzureClient):
    """A client for interacting with Azure Blob Storage.

    Inherits from:
        - BaseObjectStorageblob_client: to provide a generic interface for object storage clients

    :param blob_sas_url:
        SAS URL to an Azure Blob Storage blob.
    """

    def __init__(
        self,
        blob_sas_url: str,
    ):
        self.blob_sas_url = blob_sas_url

    def _get_blob_name_from_sas(self) -> str:
        url, _ = self.blob_sas_url.split('?')
        return url[url.rfind('/') + 1 :]

    async def upload_file(
        self,
        file_path: str,
        chunk_size: Optional[int] = 4 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> Dict[str, Any]:
        """Uploads a file to a blob in the specified container."""
        key = self._get_blob_name_from_sas()
        async with BlobClient.from_blob_url(blob_url=self.blob_sas_url, max_block_size=chunk_size) as blob_client:
            return await self._upload(blob_client, file_path, key, progress_callback)

    async def resume_upload(
        self,
        file_path: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> None:
        """Uploads a file to an Azure Blob Storage container, resuming an interrupted upload if there is an uncommitted
        block list."""

        key = self._get_blob_name_from_sas()
        async with BlobClient.from_blob_url(blob_url=self.blob_sas_url, max_block_size=chunk_size) as blob_client:
            await self._resume_upload(blob_client, key, file_path, chunk_size, progress_callback)

    async def download_file_to_bytes(
        self,
        chunk_size: Optional[int] = 4 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> bytes:
        """Download a file from the specified container."""
        key = self._get_blob_name_from_sas()
        async with BlobClient.from_blob_url(blob_url=self.blob_sas_url, max_chunk_get_size=chunk_size) as blob_client:
            return await self._download_bytes(blob_client, key, progress_callback=progress_callback)

    async def download_file(
        self,
        file_path: str,
        chunk_size: Optional[int] = 4 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> None:
        """Download a file from the specified container."""
        key = self._get_blob_name_from_sas()

        async with BlobClient.from_blob_url(blob_url=self.blob_sas_url, max_chunk_get_size=chunk_size) as blob_client:
            await self._download(blob_client, key, file_path, chunk_size, progress_callback)

    async def copy_file_from_url(
        self,
        source_url: str,
    ) -> str:
        """Copies a file from a URL to a blob in the specified container."""

        async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
            return await self._copy_from_url(blob_client, source_url)

    async def get_file_url(
        self,
    ) -> str:
        """Returns the URL that can be used to access the specified file."""

        async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
            return blob_client.url

    async def get_file_properties(
        self,
    ) -> BlobProperties:
        """Retrieves the properties of a blob in the specified container."""

        async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
            return await blob_client.get_blob_properties()
