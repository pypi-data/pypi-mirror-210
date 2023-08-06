# Copyright (C) 2023 Indoc Research
#
# Contact Indoc Research for any questions regarding the use of this source code.


from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Optional
from uuid import uuid4

import aiofiles
import aiofiles.os
from azure.storage.blob import BlobBlock
from azure.storage.blob.aio import BlobClient


class AzureClient:
    """Base base class for object storage clients."""

    async def _upload(
        self,
        client: BlobClient,
        file_path: str,
        key: str,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> Dict[str, Any]:
        async def progress_hook(current: int, total: int) -> None:
            if progress_callback:
                await progress_callback(key, current, total)

        stat_res = await aiofiles.os.stat(file_path)
        async with aiofiles.open(file_path, mode='rb') as f:
            resp = await client.upload_blob(
                f,
                length=stat_res.st_size,
                max_concurrency=4,
                progress_hook=progress_hook,
            )
        return resp

    async def _download_bytes(
        self,
        client: BlobClient,
        key: str,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> bytes:
        """Download a file from the specified container."""

        stream = await client.download_blob(max_concurrency=4)
        chunk_list = []
        current = 0
        async for chunk in stream.chunks():
            current += len(chunk)
            if progress_callback:
                await progress_callback(key, current, stream.size)
            chunk_list.append(chunk)
        return b''.join(chunk_list)

    async def _download(
        self,
        client: BlobClient,
        key: str,
        file_path: str,
        chunk_size: Optional[int] = 4 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> None:
        """Download a file from the specified container."""

        async def progress_hook(current: int, total: int) -> None:
            if progress_callback:
                await progress_callback(key, current, total)

        async with aiofiles.open(file_path, 'wb') as file:
            stream = await client.download_blob(max_concurrency=4, progress_hook=progress_hook)
            await file.write(await stream.read(chunk_size))

    async def _copy_from_url(
        self,
        client: BlobClient,
        source_url: str,
    ) -> str:
        """Copies a file from a URL to a blob in the specified container."""

        resp = await client.start_copy_from_url(source_url=source_url)
        return resp['copy_status']

    async def _resume_upload(
        self,
        client: BlobClient,
        key: str,
        file_path: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Optional[Callable[[str, int, int], Awaitable[Any]]] = None,
    ) -> None:
        """Uploads a file to an Azure Blob Storage container, resuming an interrupted upload if there is an uncommitted
        block list."""

        uploaded_blocks = []
        offset = 0
        current = 0

        async with client as blob_client:
            _, block_list = await blob_client.get_block_list('uncommitted')
            for block in block_list:
                offset += block.size
                uploaded_blocks.append(block.id)

            current = offset
            file_length = (await aiofiles.os.stat(file_path)).st_size
            file_renaming_length = file_length - offset

            if file_renaming_length:
                async with aiofiles.open(file_path, mode='rb') as f:
                    await f.seek(offset)
                    while True:
                        chunk = await f.read(chunk_size)
                        if not chunk:
                            break
                        block_id = str(uuid4())
                        await blob_client.stage_block(block_id=block_id, data=chunk)
                        current += chunk_size
                        if progress_callback:
                            await progress_callback(key, current, file_length)
                        uploaded_blocks.append(BlobBlock(block_id=block_id))

            await blob_client.commit_block_list(uploaded_blocks)
