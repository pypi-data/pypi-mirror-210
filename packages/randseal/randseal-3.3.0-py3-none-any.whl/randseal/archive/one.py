"""Removed features from the package"""

import discord, io, random, aiohttp, typing, advlink
from client import Client as BaseClient

class ArchiveClient(BaseClient):
	"""A subclass of `Client`. Only features that have been reworked or removed are different."""
	def __init__(self, session: aiohttp.ClientSession | None = None, session2: aiohttp.ClientSession | None = None):
		super().__init__(session=session, session2=session2)

	@property
	def blank(self) -> discord.Colour:
		"""A colour like an embed from discord"""
		col = discord.Colour(0x2f3136)
		return col

	@property
	def number(self) -> str:
		return f"{random.randrange(0, 82)}"

	def File(self) -> discord.File:
		"""Old file."""
		sealrand = self.number
		import requests
		r = requests.get(self.url, stream=True)
		return discord.File(fp=io.BytesIO(r.content), filename=sealrand + ".jpg")

	def Embed(self, title: str=discord.embeds._EmptyEmbed) -> discord.Embed:
		"""Old embed."""
		return discord.Embed(title=title, colour=self.blank).set_image(url=self.url)
	
	@property
	def advlink(self) -> advlink.Link:
		return advlink.Link(self.url, session=self.session, session2=self.session2)

	@property
	def url(self) -> str:
		return f"https://raw.githubusercontent.com/mariohero24/randseal/fbba6657532d0b6db21c91986843a08a7ab19f26/randseal/00{self.number}.jpg"

	def __str__(self):
		return self.url
	
	def __int__(self):
		return int(self.number)
	
	def urls(self) -> typing.Iterable[str]:
		return [f"https://raw.githubusercontent.com/mariohero24/randseal/fbba6657532d0b6db21c91986843a08a7ab19f26/randseal/00{e}.jpg" for e in range(1, 83)]
	
	def __iter__(self):
		return self.urls().__iter__()