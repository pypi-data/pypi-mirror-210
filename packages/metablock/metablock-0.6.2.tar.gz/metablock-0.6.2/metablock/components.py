from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncIterator, Awaitable, Callable, cast

from aiohttp import ClientResponse
from yarl import URL

from .utils import as_dict, as_params

if TYPE_CHECKING:  # pragma: no cover
    from .client import Metablock


Callback = Callable[[ClientResponse], Awaitable[Any]]


class MetablockError(Exception):
    pass


class MetablockResponseError(MetablockError):
    def __init__(self, response: ClientResponse, message: Any = "") -> None:
        self.response = response
        self.message = as_dict(message, "message")
        self.message["request_url"] = str(response.url)
        self.message["request_method"] = response.method
        self.message["response_status"] = response.status

    @property
    def status(self) -> int:
        return self.response.status

    def __str__(self) -> str:
        return json.dumps(self.message, indent=4)


class HttpComponent(ABC):
    @abstractmethod
    def execute(self, url: str, *, method: str = "", **kwargs: Any) -> Any:
        """Execute Http request"""

    async def get(self, url: str, **kwargs: Any) -> Any:
        kwargs["method"] = "GET"
        return await self.execute(url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> Any:
        kwargs["method"] = "PATCH"
        return await self.execute(url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Any:
        kwargs["method"] = "POST"
        return await self.execute(url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> Any:
        kwargs["method"] = "PUT"
        return await self.execute(url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> Any:
        kwargs["method"] = "DELETE"
        return await self.execute(url, **kwargs)

    def wrap(self, data: Any) -> Any:
        return data


class MetablockEntity(HttpComponent):
    """A Metablock entity"""

    __slots__ = ("root", "data")

    def __init__(
        self, root: Metablock | CrudComponent | MetablockEntity, data: dict
    ) -> None:
        self.root = root
        self.data = data

    def __repr__(self) -> str:
        return repr(self.data)

    def __str__(self) -> str:
        return self.__repr__()

    def __getitem__(self, item: str) -> Any:
        return self.data[item]

    def __contains__(self, item: str) -> bool:
        return item in self.data

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.data == other.data

    def _asdict(self) -> dict:
        return self.data

    @property
    def cli(self) -> Metablock:
        return self.root.cli

    @property
    def id(self) -> str:
        return self.data.get("id", "")

    @property
    def name(self) -> str:
        return self.data.get("name", "")

    @property
    def url(self) -> str:
        return "%s/%s" % (self.root.url, self.id)

    async def execute(self, url: str | URL, **kwargs: Any) -> Any:
        return await self.cli.execute(url, **kwargs)

    def nice(self) -> str:
        return json.dumps(self.data, indent=4)


class Component:
    __slots__ = ("root", "name")

    def __init__(
        self, root: Metablock | CrudComponent | MetablockEntity, name: str = ""
    ) -> None:
        self.root = root
        self.name = name or self.__class__.__name__.lower()

    def __repr__(self) -> str:
        return self.url

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def cli(self) -> Metablock:
        return self.root.cli

    @property
    def url(self) -> str:
        return f"{self.cli.url}/{self.name}"


class CrudComponent(HttpComponent):
    Entity = MetablockEntity
    __slots__ = ("root", "name")

    def __init__(
        self, root: Metablock | CrudComponent | MetablockEntity, name: str = ""
    ) -> None:
        self.root = root
        self.name = name or self.__class__.__name__.lower()

    def __repr__(self) -> str:
        return self.url

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def cli(self) -> Metablock:
        return self.root.cli

    @property
    def url(self) -> str:
        return f"{self.cli.url}/{self.name}"

    @property
    def parent_url(self) -> str:
        return f"{self.root.url}/{self.name}"

    @property
    def is_entity(self) -> bool:
        return isinstance(self.root, MetablockEntity)

    async def execute(self, url: str | URL, **kwargs: Any) -> Any:
        return await self.root.execute(url, **kwargs)

    async def paginate(self, **params: Any) -> AsyncIterator[MetablockEntity]:
        url = self.list_create_url()
        next_ = url
        url_params = as_params(**params)
        while next_:
            if not next_.startswith(url):
                next_ = f'{url}?{next_.split("?")[1]}'
            data = await self.execute(next_, params=url_params)
            next_ = data.get("next")
            for d in data["data"]:
                yield self.wrap(d)

    async def get_list(self, **kwargs: Any) -> list[MetablockEntity]:
        url = self.list_create_url()
        kwargs.setdefault("wrap", self.wrap_list)
        return cast(
            list[MetablockEntity],
            await self.execute(url, **kwargs),
        )

    async def get_full_list(self, **kwargs: Any) -> list[MetablockEntity]:
        return [d async for d in self.paginate(**kwargs)]

    async def get(self, id_: str, **kwargs: Any) -> MetablockEntity:  # type: ignore
        url = f"{self.url}/{id_}"
        kwargs.setdefault("wrap", self.wrap)
        return cast(MetablockEntity, await self.execute(url, **kwargs))

    async def has(self, id_: str, **kwargs: Any) -> bool:
        url = f"{self.url}/{id_}"
        kwargs.update(wrap=self.head)
        return cast(bool, await self.get(url, callback=self.head))

    async def create(
        self, callback: Callback | None = None, **params: Any
    ) -> MetablockEntity:
        url = self.list_create_url()
        return cast(
            MetablockEntity,
            await self.post(url, json=params, callback=callback, wrap=self.wrap),
        )

    async def update(
        self, id_name: str, callback: Callback | None = None, **params: Any
    ) -> MetablockEntity:
        return cast(
            MetablockEntity,
            await self.patch(
                self.update_url(id_name), json=params, callback=callback, wrap=self.wrap
            ),
        )

    async def upsert(
        self, callback: Callback | None = None, **params: Any
    ) -> MetablockEntity:
        return cast(
            MetablockEntity,
            await self.put(self.url, json=params, callback=callback, wrap=self.wrap),
        )

    async def delete(  # type: ignore
        self,
        id_name: str,
        **kwargs: Any,
    ) -> Any:
        return await self.cli.delete(self.delete_url(id_name), **kwargs)

    async def delete_all(self) -> int:
        n = 0
        async for entity in self.paginate():
            await self.delete(entity.id)
            n += 1
        return n

    async def head(self, response: ClientResponse) -> bool:
        if response.status == 404:
            return False
        elif response.status == 200:
            return True
        else:  # pragma: no cover
            raise MetablockResponseError(response)

    def wrap(self, data: dict) -> MetablockEntity:
        return self.Entity(self, data)

    def entity(self, **data: Any) -> MetablockEntity:
        return self.Entity(self, data)

    def wrap_list(self, data: list[dict]) -> list[MetablockEntity]:
        return [self.wrap(d) for d in data]

    def list_create_url(self) -> str:
        return self.parent_url if self.is_entity else self.url

    def update_url(self, id_name: str) -> str:
        return f"{self.url}/{id_name}"

    def delete_url(self, id_name: str) -> str:
        return f"{self.url}/{id_name}"
