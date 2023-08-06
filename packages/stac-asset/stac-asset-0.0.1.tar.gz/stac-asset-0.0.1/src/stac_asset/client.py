import json
import os.path
from abc import ABC, abstractmethod
from asyncio import TaskGroup
from pathlib import Path
from typing import AsyncIterator, Optional, TypeVar

import aiofiles
import pystac.utils
from pystac import Asset, Item
from yarl import URL

from .constants import DEFAULT_ASSET_FILE_NAME
from .types import PathLikeObject

T = TypeVar("T", bound="Client")


class Client(ABC):
    """An abstract base class for all clients."""

    @classmethod
    async def default(cls: type[T]) -> T:
        """Creates the default version of this client.

        We can't just use the initializer, because some clients need to do
        asynchronous actions during their setup.
        """
        return cls()

    @abstractmethod
    async def open_url(self, url: URL) -> AsyncIterator[bytes]:
        """Opens a url and yields an iterator over its bytes.

        Args:
            url: The input url

        Yields:
            AsyncIterator[bytes]: An iterator over chunks of the read file
        """
        # https://github.com/python/mypy/issues/5070
        if False:
            yield

    async def open_href(self, href: str) -> AsyncIterator[bytes]:
        """Opens a href and yields an iterator over its bytes.

        Args:
            href: The input href

        Yields:
            AsyncIterator[bytes]: An iterator over chunks of the read file
        """
        async for chunk in self.open_url(URL(href)):
            yield chunk

    async def open_asset(self, asset: Asset) -> AsyncIterator[bytes]:
        """Opens an asset and yields an iterator over its bytes.

        Args:
            asset: The input asset

        Yields:
            AsyncIterator[bytes]: An iterator over chunks of the read file
        """
        async for chunk in self.open_href(asset.href):
            yield chunk

    async def download_href(self, href: str, path: PathLikeObject) -> None:
        """Downloads a file to the local filesystem.

        Args:
            href: The input href
            path: The ouput file path
        """
        async with aiofiles.open(path, mode="wb") as f:
            async for chunk in self.open_href(href):
                await f.write(chunk)

    async def download_asset(
        self,
        asset: Asset,
        directory: PathLikeObject,
        make_directory: bool = False,
        asset_file_name: str = DEFAULT_ASSET_FILE_NAME,
    ) -> None:
        """Downloads a STAC Asset into the given directory.

        The file at the asset's href is downloaded into the directory. The asset is
        also downloaded into the directory, and its href is updated to point to the
        local file.

        Args:
            asset: The Asset to download.
            directory: The location of the downloaded file and Asset.
            make_directory: If true, create the directory (with exists_ok=True)
                before downloading.
            asset_file_name: The name of the Asset json file in the directory.
        """
        directory_as_path = Path(directory)
        if make_directory:
            directory_as_path.mkdir(exist_ok=True)
        path = directory_as_path / os.path.basename(asset.href)
        await self.download_href(asset.href, path)
        asset.href = str(path)
        asset_as_str = json.dumps(asset.to_dict())
        async with aiofiles.open(directory_as_path / asset_file_name, "w") as f:
            await f.write(asset_as_str)

    async def download_item(
        self,
        item: Item,
        directory: PathLikeObject,
        make_directory: bool = False,
        item_file_name: Optional[str] = None,
        include_self_link: bool = True,
    ) -> None:
        """Downloads all Assets in an item into the given directory.

        Args:
            item: The Item to download, along with its assets.
            directory: The location of the downloaded file and Asset.
            make_directory: If true, create the directory (with exists_ok=True)
                before downloading.
            item_file_name: The name of the Item json file in the directory.
            include_self_link: Whether to include a self link on the item.
        """
        directory_as_path = Path(directory)
        if make_directory:
            directory_as_path.mkdir(exist_ok=True)
        if item_file_name is None:
            item_file_name = f"{item.id}.json"
        item_path = directory_as_path / item_file_name
        async with TaskGroup() as task_group:
            for key, asset in item.assets.items():
                # TODO allow different layout schemes
                path = directory_as_path / os.path.basename(asset.href)
                absolute_href = asset.get_absolute_href()
                if absolute_href is None:
                    raise ValueError(f"asset '{key}' does not have an absolute href")
                task_group.create_task(self.download_href(absolute_href, path))
                item.assets[key].href = pystac.utils.make_relative_href(
                    str(path), str(item_path)
                )
        for link in item.links:
            if link.is_hierarchical():
                link.target = pystac.utils.make_absolute_href(link.href, item.self_href)
        item.save_object(include_self_link=include_self_link, dest_href=str(item_path))
