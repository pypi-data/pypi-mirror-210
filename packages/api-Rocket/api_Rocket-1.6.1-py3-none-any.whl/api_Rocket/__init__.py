from .lib.clients.client import Client, Trade_Client
from .lib.clients.async_client import async_Client
import requests
import json


#information
__title__ = "api-Rocket"

__author__ = "Redpiar"

__license__ = "MIT"

__copyright__ = "Copyright 2023 Redpiar"

__version__ = '1.6.0'

__status__ = "(Beta)"

__newest__ = json.loads(requests.get("https://pypi.org/pypi/api-Rocket/json").text)["info"]["version"]

if __version__ != __newest__:
	print(f"""
{__title__} made by {__author__}\nPlease update the library. Your version: {__version__} a new version: {__newest__}
""")
else:
	print(f"""
{__title__} {__version__}{__status__} made by {__author__}\n
""")