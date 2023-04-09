import aiohttp

api_url = 'http://127.0.0.1:8000/api/'

async def api(endpoint, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url + endpoint, params=params) as response:
            return await response.json()

