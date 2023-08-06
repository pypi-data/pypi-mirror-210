import aiohttp
import asyncio
import json

class async_Client:
	def __init__(self, token):
		self.headers = {
			"accept": "application/json",
			"Rocket-Pay-Key": token,
			"Content-Type": "application/json",
		}

	async def api_version(self):
		async with aiohttp.ClientSession() as session:
			async with session.get("https://pay.ton-rocket.com/version") as responce:
				return await responce.text()