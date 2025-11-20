import random
import secrets
from PIL import Image


def generate_password() -> str:
    return secrets.token_urlsafe(10)


def generate_logo(original: Image.Image, quality: float) -> Image.Image:
    modified = original.copy()
    width, height = modified.size
    random.seed(1)
    pixels = modified.load()
    assert pixels is not None
    for x in range(width):
        for y in range(height):
            if random.random() > quality:
                pixels[x, y] = (255, 255, 255)

    return modified
