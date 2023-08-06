
import requests
from requests.exceptions import ConnectionError
def ping(site):
    try:
        requests.get(site)
    except ConnectionError:
        return "site is not reacheable"
    return "pong"



