import aiohttp
from PIL import Image
import io
api_url = 'http://app:8000/api/'

async def api(endpoint, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url + endpoint, params=params) as response:

            return await response.json()
async def resize_image(image_url, max_size=(300, 300)):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            image_data = await response.read()

    image = Image.open(io.BytesIO(image_data))
    image.thumbnail(max_size)

    output = io.BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)

    return output