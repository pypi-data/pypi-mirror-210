"""Client file"""

from .vars import AsyncFileOrPathLike, FileOrPathLike, File, Embed
from aiohttp import ClientSession
from aiofiles import open as iopen
from io import BytesIO, TextIOWrapper
from asyncio import get_event_loop, AbstractEventLoop, iscoroutine
from random import randrange
from traceback import format_exception
from json import loads, dumps, load, dump
from typing import AsyncIterator, Iterator, Coroutine, Any
from .errors import StatusException, BaseException, InvalidType
from os import path
from sys import stderr
from aiofiles.threadpool.text import AsyncTextIOWrapper
from .vars import MAX_NUMBER, BLANK

class Client:
	"""The main `Client` class for this package

	Parameters
	----------
	session : ClientSession | None, optional
		The session used to get images, by default None
	session2 : ClientSession | None, optional
		The session used to get text (unused), by default None
	loop : AbstractEventLoop | None, optional
		The loop used for the sessions, by default None
	"""
	def __init__(self, *, session: ClientSession | None = None, session2: ClientSession | None = None, loop: AbstractEventLoop | None = None):
		self.loop = (get_event_loop() if loop is None else loop)
		self.session = (ClientSession(
			auto_decompress=False, loop=self.loop) if session is None else session)
		self.session2 = (ClientSession(
			auto_decompress=False, loop=self.loop) if session2 is None else session2)

	async def File(self, cls: type[File]) -> File:
		"""
		Returns an `File` of a seal which can be used in a message (reworked in version 3.0.0)

		Parameters
		-----------

		cls: `FileLIke`
			A py-cord `File` or a discord.py `File`
		"""
		if cls.__name__ != "File":
			return await self.on_error(InvalidType(cls, "File"))
		try:
			async with self.session.get(self.url) as r:
				if r.status == 200:
					hi = BytesIO(await r.read())
					return cls(fp=hi, filename=self.number + ".jpg")
				else:
					return await self.on_error(StatusException())
		except Exception as exc:
			await self.on_error(exc)

	def Embed(self, cls: type[Embed]) -> Embed:
		"""
		Returns an `Embed` of a seal which can be edited or used in a message (reworked in version 3.0.0)

		Parameters
		-----------

		cls: `type[Embed]`
			A py-cord `Embed` or a discord.py `Embed`
		"""
		if cls.__name__ != "Embed":
			return self.loop.run_until_complete(self.on_error(InvalidType(cls, "Embed")))
		return cls(colour=BLANK).set_image(url=self.url)


	@classmethod
	async def jsonload(cls, fp: AsyncFileOrPathLike, **loading_kwargs,) -> dict:
		"""
		Asynchronous `json.load()` using the `aiofiles` package (New in 1.3.0)
		"""
		if isinstance(fp, AsyncTextIOWrapper):
			s = await fp.read()
		else:
			if not path.exists(fp):
				async with iopen(fp, "w") as f:
					s = "{}"
					await f.write(s)
			else:
				async with iopen(fp) as f:
					s = await f.read()
		return loads(s, **loading_kwargs)

	@classmethod
	async def jsondump(
			cls,
			obj: dict,
			fp: AsyncFileOrPathLike,
			**dumping_kwargs
	) -> None:
		"""
		Asynchronous `json.dump()` using the `aiofiles` package (New in 1.3.0)
		"""
		if isinstance(fp, AsyncTextIOWrapper):
			e = dumps(obj, **dumping_kwargs)
			await fp.write(e)
		else:
			async with iopen(fp, "w") as f:
				e = dumps(obj, **dumping_kwargs)
				await f.write(e)

	@classmethod
	async def jsonupdate(cls, fp: AsyncFileOrPathLike, data: dict, **dumping_kwargs) -> dict:
		"""
		A combination of `.jsondump` and `.jsonload` to update json files asynchronously. Returns the updated `dict`.
		"""
		e = await cls.jsonload(fp)
		e.update(data)
		await cls.jsondump(e, fp, **dumping_kwargs)
		return e

	@classmethod
	def sync_jsonupdate(cls, fp: FileOrPathLike, data: dict, **dumping_kwargs) -> dict:
		"""
		A non-asynchronous version of `Client.jsonupdate`.
		"""
		if isinstance(fp, TextIOWrapper):
			pf = fp
		else:
			if not path.exists(fp):
				with open(fp, "w") as f:
					f.write("{}")
					return {}
			else:
				with open(fp) as f:
					pf = f
		e: dict = load(pf)
		e.update(data)
		dump(e, pf, **dumping_kwargs)
		return e

	@property
	def url(self) -> str:
		"""
		A seal image url
		"""
		return f"https://raw.githubusercontent.com/mariohero24/randsealimgs/main/{self.number}.jpg"


	@property
	def number(self) -> str:
		"""
		A seal number
		"""
		return f"{randrange(0, MAX_NUMBER)}"

	def __str__(self) -> str:
		return self.url

	def __int__(self) -> int:
		return int(self.number)
	
	async def flatten(self) -> list[str | int | None]:
		"""Flatten the iter into a list.

		Returns
		-------
		list[Any]
			The flattened list.
		"""
		return [e async for e in self]

	def flatten_all(self) -> list[str]:
		return [e for e in self]

	def __aiter__(self) -> AsyncIterator[str | int | None]:
		self.anumber = 0
		return self

	async def __anext__(self) -> str | int | None:
		if self.anumber >= MAX_NUMBER:
			raise StopAsyncIteration
		self.anumber += 1
		async with self.session.get(f"https://raw.githubusercontent.com/mariohero24/randsealimgs/main/{self.anumber}.jpg") as r:
			if r.status == 200:
				if self.url:
					return f"https://raw.githubusercontent.com/mariohero24/randsealimgs/main/{self.anumber}.jpg"
				else:
					byte = await r.read()
					return byte

	def __iter__(self) -> Iterator[str]:
		self.number = 0
		return self
	
	def __next__(self) -> str:
		if self.number >= MAX_NUMBER:
			raise StopIteration
		self.number += 1
		return f"https://raw.githubusercontent.com/mariohero24/randsealimgs/main/{self.number}.jpg"

	async def tobytes(self, bytesio: bool=False) -> bytes | BytesIO | None:
		async with self.session.get(self.url) as r:
			if r.status == 200:
				if bytesio:
					n = await r.read()
					hi = BytesIO(n)
				else:
					hi = await r.read()
				return hi
			else:
				await self.on_error(StatusException(r.status))

	async def on_error(self, exception: Exception) -> None:
		"""|coro|

		Error handler that can be overridden via subclassing `Client`

		Parameters
		-----------

		exception: `Exception`
			The exception that was encountered. Can be determined using `isinstance()`.
		"""
		print(self.format_exception(exception), file=stderr)
		

	@classmethod
	def format_exception(cls, exception: Exception) -> str:
		return "".join(format_exception(exception))

# python3 -m twine upload --repository pypi dist/*