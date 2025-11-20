from datetime import datetime, timezone
from fastapi import APIRouter, status, Request, Form, HTTPException
from sqlmodel import select
from app.api.models import TeamCreate, Team
from app.api.utils import generate_password
from app.api.deps import AdminDep, SessionDep
from sqlalchemy.exc import IntegrityError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import jwt
from app.core.config import settings
from typing import Annotated

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.post("/team", response_class=RedirectResponse, tags=["team"])
async def create_team(session: SessionDep, team_in: TeamCreate, auth: AdminDep):
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

    return RedirectResponse(f"/admin/team/{team.id}")


@router.get("/admin/team/{id}", response_class=HTMLResponse, tags=["admin"])
async def show_team(request: Request, session: SessionDep, id: int):
    """
    Return detail page of team, only admins have access
    """
    team = session.get(Team, id)
    return templates.TemplateResponse(
        request=request, name="team_show.html", context={"team": team}
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
    response = RedirectResponse("/")
    response.set_cookie(key="auth_jwt", value=team_jwt)
    return response
