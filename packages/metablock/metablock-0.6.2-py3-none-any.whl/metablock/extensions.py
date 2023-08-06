from typing import Any

from .components import CrudComponent, MetablockEntity
from .spaces import BlockPlugin


# Extension
class Extension(MetablockEntity):
    """Object representing an Extension"""


class Extensions(CrudComponent):
    """Extensions"""

    Entity = Extension


# Plugin
class Plugin(MetablockEntity):
    """Object representing an Plugin"""

    async def blocks(self, **kwargs: Any) -> list[BlockPlugin]:
        return await self.get(f"{self.url}/services", **kwargs)


class Plugins(CrudComponent):
    """Plugins"""

    Entity = Plugin
