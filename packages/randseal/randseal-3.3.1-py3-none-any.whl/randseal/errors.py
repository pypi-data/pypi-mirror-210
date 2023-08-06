class StatusException(Exception):
	"""Exception for if a HTTP status isn't 200."""
	def __init__(self, status: int):
		super().__init__(f"The HTTP status wasn't 200. ", status)

class WhatException(Exception):
	"""What are you even trying to do..."""
	def __init__(self):
		super().__init__("You are attempting something very strange.")

class InvalidType(Exception):
	"""That isn't the right type"""
	def __init__(self, item: type, expected: str) -> None:
		super().__init__(f"Was expecting {expected}, not {item.__name__}.")