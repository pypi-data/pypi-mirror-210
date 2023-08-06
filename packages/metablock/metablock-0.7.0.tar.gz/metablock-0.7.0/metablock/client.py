from __future__ import annotations

import logging
import os
import sys
from typing import Any

from aiohttp import ClientResponse, ClientSession
from yarl import URL

from .components import Callback, HttpComponent, MetablockResponseError
from .extensions import Extension, Extensions, Plugin, Plugins
from .orgs import Org, Orgs
from .spaces import Block, Blocks, Domains, Space, Spaces
from .user import User

DEFAULT_USER_AGENT = f"Python/{'.'.join(map(str, sys.version_info[:2]))} metablock"

logger = logging.getLogger("metablock.client")


class Metablock(HttpComponent):
    """Metablock client"""

    url: str = os.environ.get("METABLOCK_URL", "https://api.metablock.io/v1")
    auth_key: str = os.getenv("METABLOCK_API_TOKEN", "")

    def __init__(
        self,
        url: str | None = None,
        auth_key: str = "",
        auth_key_name: str = "x-metablock-api-key",
        session: ClientSession | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.url: str = url if url is not None else self.url
        self.auth_key: str = auth_key or self.auth_key
        self.auth_key_name = auth_key_name
        self.session = session
        self.default_headers: dict[str, str] = {
            "user-agent": user_agent,
            "accept": "application/json",
        }
        self.orgs: Orgs = Orgs(self, Org)
        self.spaces: Spaces = Spaces(self, Space)
        self.blocks: Blocks = Blocks(self, Block, "services")
        self.plugins: Plugins = Plugins(self, Plugin)
        self.extensions: Extensions = Extensions(self, Extension)
        self.domains = Domains(self)
        self.services = self.blocks

    def __repr__(self) -> str:
        return self.url

    __str__ = __repr__

    @property
    def cli(self) -> Metablock:
        return self

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def __aenter__(self) -> Metablock:
        return self

    async def __aexit__(self, exc_type: type, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def spec(self) -> dict:
        return await self.request(f"{self.url}/spec")

    async def get(self, url: str | URL, **kwargs: Any) -> Any:
        kwargs["method"] = "GET"
        return await self.request(url, **kwargs)

    async def patch(self, url: str | URL, **kwargs: Any) -> Any:
        kwargs["method"] = "PATCH"
        return await self.request(url, **kwargs)

    async def post(self, url: str | URL, **kwargs: Any) -> Any:
        kwargs["method"] = "POST"
        return await self.request(url, **kwargs)

    async def put(self, url: str | URL, **kwargs: Any) -> Any:
        kwargs["method"] = "PUT"
        return await self.request(url, **kwargs)

    async def delete(self, url: str | URL, **kwargs: Any) -> Any:
        kwargs["method"] = "DELETE"
        return await self.request(url, **kwargs)

    async def request(
        self,
        url: str | URL,
        method: str = "",
        headers: dict[str, str] | None = None,
        callback: Callback | None = None,
        wrap: Any = None,
        **kw: Any,
    ) -> Any:
        if not self.session:
            self.session = ClientSession()
        method = method or "GET"
        headers_ = self.get_default_headers()
        headers_.update(headers or ())
        response = await self.session.request(method, url, headers=headers_, **kw)
        if callback:
            return await callback(response)
        else:
            return await self.handle_response(response, wrap=wrap)

    async def handle_response(self, response: ClientResponse, wrap: Any = None) -> Any:
        if response.status == 204:
            return True
        if response.status >= 400:
            try:
                data = await response.json()
            except Exception:
                data = await response.text()
            raise MetablockResponseError(response, data)
        response.raise_for_status()
        data = await response.json()
        return wrap(data) if wrap else data

    async def get_user(self, **kw: Any) -> User:
        kw.setdefault("wrap", self._user)
        return await self.get(f"{self.url}/user", **kw)

    async def get_space(self, **kw: Any) -> Space:
        kw.setdefault("wrap", self._space)
        return await self.get(f"{self.url}/space", **kw)

    async def update_user(self, **kw: Any) -> User:
        kw.setdefault("wrap", self._user)
        return await self.patch(f"{self.url}/user", **kw)

    async def delete_user(self, **kw: Any) -> None:
        return await self.delete(f"{self.url}/user", **kw)

    def get_default_headers(self) -> dict[str, str]:
        headers = self.default_headers.copy()
        if self.auth_key:
            headers[self.auth_key_name] = self.auth_key
        return headers

    def _user(self, data: dict) -> User:
        return User(self, data)

    def _space(self, data: dict) -> Space:
        return Space(self.spaces, data)
