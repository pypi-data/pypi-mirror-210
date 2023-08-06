import requests

def find_ipv6():
    """Return the public IPv6 address of the system."""
    return requests.get('https://api6.ipify.org?format=json').json()['ip']




