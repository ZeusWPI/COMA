from fastapi import APIRouter, status, Request
from app.api.models import TeamCreate, Team
from app.api.utils import generate_password, get_password_hash
from app.api.deps import SessionDep
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.post("/team", response_class=RedirectResponse, tags=["team"])
async def create_team(session: SessionDep, team_in: TeamCreate):
    """
    Create a new team and returns generated password
    """
    password = generate_password()
    team = Team.model_validate(
        team_in,
        update={"hashed_password": get_password_hash(password)},
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
