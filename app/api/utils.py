import base64
import io
import random
import re
import secrets
import textwrap
from typing import List

from PIL import Image
from sqlmodel import select

from app.api.deps import SessionDep
from app.api.models import Question, Submission, Team


def generate_password() -> str:
    return secrets.token_urlsafe(10)


def get_question_score(
    team: Team, question: Question, question_submissions: List[Submission]
) -> float:
    for submission in question_submissions:
        assert submission.question_id == question.id
        if is_answer_correct(submission.answer, question.solution, question.accuracy):
            return 0.9 ** (len(question_submissions) - 1) * question.max_score

    return 0.0


def get_team_score(session: SessionDep, team: Team, questions: List[Question]) -> float:
    score = 0
    all_submissions = session.exec(
        select(Submission).where(Submission.team_id == team.id)
    ).all()

    for question in questions:
        submissions = [s for s in all_submissions if s.question_id == question.id]
        score += get_question_score(team, question, submissions)

    return score


def get_team_quality(session: SessionDep, team: Team) -> float:
    questions = session.exec(select(Question)).all()
    score = get_team_score(session, team, questions)

    max_score = sum(x.max_score for x in questions)

    if max_score != 0:
        return score / max_score
    else:
        return 1


def question_score_left(
    question: Question, question_submissions: List[Submission]
) -> float:
    return 0.9 ** len(question_submissions) * question.max_score


def generate_logo(quality: float, background=(100, 66, 150)) -> Image.Image:
    img = Image.open("app/static/images/prime.webp")
    width, height = img.size
    random.seed(1)
    pixels = img.load()
    assert pixels is not None
    for x in range(width):
        for y in range(height):
            if random.random() > quality:
                pixels[x, y] = background
    return img


def encoded_logo(logo: Image.Image) -> str:
    bytes = io.BytesIO()
    logo.save(bytes, format="PNG")
    return base64.b64encode(bytes.getvalue()).decode()


def is_answer_correct(a: str, b: str, accuracy: int = 10) -> bool:
    if "." not in a and a == b:
        return True
    if a.count(".") == 1 and b.count(".") == 1:
        split_a = a.split(".")
        split_b = b.split(".")
        after_decimal_a = textwrap.wrap(split_a[1], accuracy)[0]
        after_decimal_b = textwrap.wrap(split_b[1], accuracy)[0]
        if split_a[0] == split_b[0] and after_decimal_a == after_decimal_b:
            return True
    return False


def validate_question_answer(input: str) -> str | None:
    """Strips all whitespaces, replace , to . and validates if input is a correct number format"""
    transformed = input.strip().replace(",", ".")
    if not bool(re.fullmatch(r"[0-9.]+", transformed)) or transformed.count(".") > 1:
        return None

    return transformed
