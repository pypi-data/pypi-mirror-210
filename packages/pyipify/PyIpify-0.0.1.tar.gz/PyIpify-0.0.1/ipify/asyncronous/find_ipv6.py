import aiohttp

async def find_ipv6():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api6.ipify.org?format=json') as response:
            return (await response.json())['ip']

