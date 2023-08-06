import aiohttp

async def find_ipv4():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.ipify.org?format=json') as response:
            return (await response.json())['ip']
        