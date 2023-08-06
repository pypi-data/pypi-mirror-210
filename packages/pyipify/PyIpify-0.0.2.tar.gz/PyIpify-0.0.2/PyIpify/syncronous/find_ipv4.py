import requests

def find_ipv4():
    """Return the public IPv4 address of the system."""
    return requests.get('https://api.ipify.org?format=json').json()['ip']
