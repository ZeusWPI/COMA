import base64
import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.api.deps import AdminDep, AuthDep, AuthOptionalDep, SessionDep
from app.api.models import Question, QuestionCreate, Submission, Team, TeamCreate
from app.api.utils import (
    generate_logo,
    generate_password,
    get_team_quality,
    get_team_score,
    is_answer_correct,
    validate_question_answer,
)
from app.core.config import settings
from app.core.render_md import render_md

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["now"] = datetime.now()


@router.get("/", response_class=HTMLResponse, tags=["home"])
async def home_page(request: Request, session: SessionDep, auth: AuthDep):
    # Get logo
    quality = get_team_quality(session, auth)
    logo = generate_logo(quality)
    bytes = io.BytesIO()
    logo.save(bytes, format="PNG")

    # Get questions
    questions = session.exec(select(Question).order_by(text("Question.number"))).all()
    submissions = session.exec(
        select(Submission).where(Submission.team_id == auth.id)
    ).all()

    @dataclass
    class TeamQuestion:
        question: Question
        submissions: int
        correct: bool

    team_questions: list[TeamQuestion] = []

    for question in questions:
        question_submissions = [s for s in submissions if s.question_id == question.id]
        correct_submission = next(
            (
                s
                for s in question_submissions
                if is_answer_correct(s.answer, question.solution)
            ),
            None,
        )

        team_questions.append(
            TeamQuestion(
                question,
                len(question_submissions),
                bool(correct_submission),
            )
        )

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "team": auth,
            "questions": team_questions,
            "img": base64.b64encode(bytes.getvalue()).decode(),
        },
    )


@router.get("/admin/team", response_class=HTMLResponse, tags=["admin", "team"])
async def new_team(request: Request, auth: AdminDep):
    """
    Return page for new team creation
    """
    return templates.TemplateResponse(
        request=request, name="team_new.html", context={"team": auth}
    )


@router.post("/admin/team", response_class=RedirectResponse, tags=["admin", "team"])
async def create_team(
    session: SessionDep, team_in: Annotated[TeamCreate, Form()], auth: AdminDep
):
    """
    Create a new team and returns generated password
    """
    password = generate_password()
    team = Team.model_validate(
        team_in,
        update={"password": password},
    )

    try:
        session.add(team)
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name already taken",
        )

    return RedirectResponse(f"/admin/team/{team.id}", status_code=302)


@router.get("/admin/team/{id}", response_class=HTMLResponse, tags=["admin"])
async def show_team(request: Request, session: SessionDep, id: int, auth: AdminDep):
    """
    Return detail page of team, only admins have access
    """
    team = session.get(Team, id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="question not found"
        )

    return templates.TemplateResponse(
        request=request, name="team_show.html", context={"created": team, "team": auth}
    )


@router.get("/admin/question", response_class=HTMLResponse, tags=["admin", "questions"])
async def new_question(request: Request, auth: AdminDep):
    """
    Render the question creation page
    """
    return templates.TemplateResponse(
        request=request, name="question_form.html", context={"team": auth}
    )


@router.get(
    "/admin/question/{id}", response_class=HTMLResponse, tags=["admin", "questions"]
)
async def update_question_page(
    session: SessionDep, request: Request, auth: AdminDep, id: int
):
    """
    Render the question form page for updating
    """
    question = session.get(Question, id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="question not found"
        )

    question_public = question.model_validate(question)

    return templates.TemplateResponse(
        request=request,
        name="question_form.html",
        context={"question": question_public, "team": auth},
    )


@router.post(
    "/admin/question", response_class=RedirectResponse, tags=["admin", "questions"]
)
async def create_question(
    session: SessionDep, auth: AdminDep, question_in: Annotated[QuestionCreate, Form()]
):
    """
    create the new question and redirect to admin home page
    """
    question = Question.model_validate(
        question_in, update={"solution": validate_question_answer(question_in.solution)}
    )

    try:
        session.add(question)
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="question number already exists",
        )

    return RedirectResponse(f"/admin/question/{question.id}")


@router.post(
    "/admin/question/{id}", response_class=RedirectResponse, tags=["admin", "questions"]
)
async def update_question(
    session: SessionDep,
    auth: AdminDep,
    id: int,
    question_in: Annotated[QuestionCreate, Form()],
):
    """
    create the new question and redirect to admin home page
    """
    question = session.get(Question, id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="question not found"
        )

    update_data = question_in.model_dump(exclude_unset=True)

    if "solution" in update_data:
        update_data["solution"] = validate_question_answer(update_data["solution"])

    for key, value in update_data.items():
        setattr(question, key, value)

    session.add(question)
    session.commit()

    return RedirectResponse(f"/admin/question/{question.id}", status_code=302)


@router.get("/question/{id}", response_class=HTMLResponse, tags=["questions"])
async def show_question(id: int, session: SessionDep, auth: AuthDep, request: Request):
    """
    Return the detail page of a question with submission form
    """
    question = session.get(Question, id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="question not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="question_show.html",
        context={"team": auth, "question": question, "render_md": render_md},
    )


@router.get("/login", tags=["auth"], response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Render the login page
    """
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login", tags=["auth"])
async def login(
    session: SessionDep, name: Annotated[str, Form()], password: Annotated[str, Form()]
):
    """
    Log in and create a JWT
    """
    team = session.exec(
        select(Team).where(Team.name == name, Team.password == password)
    ).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    team_jwt = jwt.encode(
        payload={
            "id": team.id,
            "exp": datetime.now(tz=timezone.utc).timestamp()
            + settings.JWT_EXPIRE_MINUTES * 60,
        },
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(key="auth_jwt", value=team_jwt)
    return response


@router.get("/leaderboard", tags=["leaderboard"], response_class=HTMLResponse)
async def leaderboard_page(
    session: SessionDep, request: Request, auth: AuthOptionalDep
):
    """
    Render the leaderboard page
    """
    template_teams = []
    teams = session.exec(select(Team)).all()
    for team in teams:
        quality = get_team_quality(session, team)
        logo = generate_logo(quality)
        bytes = io.BytesIO()
        logo.save(bytes, format="PNG")
        template_teams.append(
            {"name": team.name, "img": base64.b64encode(bytes.getvalue()).decode()}
        )
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={"teams": template_teams, "team": auth},
    )


# TODO: Optimize function
@router.get("/admin", tags=["admin"], response_class=HTMLResponse)
async def admin_page(request: Request, session: SessionDep, auth: AdminDep):
    questions = session.exec(select(Question).order_by(text("Question.number"))).all()
    submissions = session.exec(
        select(Submission).order_by(desc(text("Submission.timestamp")))
    ).all()
    teams = session.exec(select(Team).order_by(text("Team.name"))).all()

    # Team submissions table

    @dataclass
    class QuestionAnswer:
        question: Question
        submissions: int
        correct: bool | None

    @dataclass
    class TeamAnswer:
        team: Team
        questions: list[QuestionAnswer]

    team_answers: list[TeamAnswer] = []

    for team in teams:
        team_answer = TeamAnswer(team, [])

        for question in questions:
            question_submissions = [
                s
                for s in submissions
                if s.team_id == team.id and s.question_id == question.id
            ]
            correct_submission = next(
                (
                    s
                    for s in question_submissions
                    if is_answer_correct(s.answer, question.solution)
                ),
                None,
            )
            team_answer.questions.append(
                QuestionAnswer(
                    question,
                    len(question_submissions),
                    True
                    if correct_submission
                    else None
                    if len(question_submissions) == 0
                    else False,
                )
            )

        team_answers.append(team_answer)

    # Scoreboard

    @dataclass
    class TeamScore:
        team: Team
        score: float

    team_scores: list[TeamScore] = []

    for team in teams:
        team_scores.append(TeamScore(team, get_team_score(session, team)))

    team_scores = sorted(team_scores, key=lambda x: x.score)

    # All submissions table

    @dataclass
    class SubmissionPopulated:
        submission: Submission
        team: Team
        question: Question
        timestamp: str

    submissions_populated: list[SubmissionPopulated] = []

    for s in submissions:
        team = next((t for t in teams if t.id == s.team_id), None)
        if not team:
            continue  # Shouldn't happen

        question = next((q for q in questions if q.id == s.question_id), None)
        if not question:
            continue  # Shouldn't happen

        submissions_populated.append(
            SubmissionPopulated(
                s, team, question, s.timestamp.strftime("%d-%m-%Y %H:%M:%S")
            )
        )

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "team": auth,
            "answers": team_answers,
            "questions": questions,
            "scores": team_scores,
            "submissions": submissions_populated,
        },
    )


@router.get("/admin/teams.csv", tags=["admin"])
async def teams_csv(request: Request, session: SessionDep, auth: AdminDep):
    """
    Return a CSV with the number of attempts of teams
    """
    teams = session.exec(select(Team)).all()
    questions = session.exec(select(Question)).all()
    output = io.StringIO()
    writer = csv.writer(output)
    header = ["Team Name"]
    for i in questions:
        header.append(f"Question #{i.number}")
    writer.writerow(header)
    for i in teams:
        row = [i.name]
        for j in questions:
            submissions = session.exec(
                select(Submission).where(
                    Submission.team_id == i.id, Submission.question_id == j.id
                )
            ).all()
            row.append(str(len(submissions)))
        writer.writerow(row)

    return PlainTextResponse(output.getvalue())


@router.get("/admin/answers.csv", tags=["admin"])
async def answers_csv(request: Request, session: SessionDep, auth: AdminDep):
    """
    Return a CSV with all answers
    """
    submissions = session.exec(select(Submission)).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Team Name", "Question Number", "Answer", "Correct"])
    for i in submissions:
        team = session.get(Team, i.team_id)
        assert team is not None
        team_name = team.name
        question = session.get(Question, i.question_id)
        assert question is not None
        question_no = question.number
        writer.writerow(
            [
                i.timestamp.strftime("%x %X"),
                team_name,
                question_no,
                i.answer,
                is_answer_correct(question.solution, i.answer),
            ]
        )

    return PlainTextResponse(output.getvalue())
