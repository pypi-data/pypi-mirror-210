from importlib.metadata import version
from typing import TypeVar
from os import PathLike
from io import TextIOWrapper
from aiofiles.threadpool.text import AsyncTextIOWrapper

File = TypeVar("File")
"""A `File` from discord or py-cord."""

Embed = TypeVar("Embed")
"""An `Embed` from discord or py-cord."""

FileOrPathLike = TypeVar("FileOrPathLike", PathLike, TextIOWrapper, str)
"""A `TextIOWrapper` or a `Pathlike`."""

AsyncFileOrPathLike = TypeVar("AsyncFileOrPathLike", PathLike, AsyncTextIOWrapper, str)
"""An `AsyncTextIOWrapper` or a `Pathlike`."""

BLANK: int = 0x2B2D31
"""A colour exactly like an embed from discord"""

MAX_NUMBER: int = 82
"""How many seal images there are"""

__version__: str = version("randseal")
"""The version of the package"""