import random
import secrets
import textwrap
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


def is_answer_correct(a: str, b: str) -> bool:
    if "." not in a and a == b:
        return True
    if a.count(".") == 1 and b.count(".") == 1:
        split_a = a.split(".")
        split_b = b.split(".")
        after_decimal_a = textwrap.wrap(split_a[1], 10)[0]
        after_decimal_b = textwrap.wrap(split_b[1], 10)[0]
        if split_a[0] == split_b[0] and after_decimal_a == after_decimal_b:
            return True
    return False
