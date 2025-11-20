import random
import re
import secrets
import textwrap

from fastapi import HTTPException, status
from PIL import Image
from sqlmodel import select

from app.api.models import Question, Submission, Team
from app.api.deps import SessionDep


def generate_password() -> str:
    return secrets.token_urlsafe(10)


def get_team_quality(session: SessionDep, team: Team) -> float:
    score = 0
    max_score = 0
    questions = session.exec(select(Question)).all()
    all_submissions = session.exec(
        select(Submission).where(Submission.team_id == team.id)
    )
    for question in questions:
        max_score += question.max_score
        submissions = [s for s in all_submissions if s.question_id == question.id]
        # TODO: Add penalty for wrong answers and only consider last answer
        for submission in submissions:
            if is_answer_correct(submission.answer, question.solution):
                score += question.max_score
                break

    quality = 1
    if max_score != 0:
        quality = score / max_score

    return quality


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


def validate_question_answer(input: str) -> str:
    """Strips all whitespaces, replace , to . and validates if input is a correct number format"""
    transformed = input.strip().replace(",", ".")
    if not bool(re.fullmatch(r"[0-9.]+", transformed)) or transformed.count(".") > 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Given Solution does not have correct format",
        )

    return transformed
