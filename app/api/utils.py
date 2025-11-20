import random
import secrets
from PIL import Image


def generate_password() -> str:
    return secrets.token_urlsafe(10)


def generate_logo(quality: float) -> Image.Image:
    img = Image.open("app/static/images/prime.webp")
    width, height = img.size
    random.seed(1)
    pixels = img.load()
    assert pixels is not None
    for x in range(width):
        for y in range(height):
            if random.random() > quality:
                pixels[x, y] = (100, 66, 150)
    return img
