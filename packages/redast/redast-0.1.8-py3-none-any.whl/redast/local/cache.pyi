from ..core import Bridge, Keeper
from pathlib import Path
from typing import Union

class CacheDrive(Bridge):
    def __init__(self, src: Keeper, root: Union[Path, str], create: bool = ...) -> None: ...

class CacheMemory(Bridge):
    def __init__(self, src: Keeper) -> None: ...
