from fastapi import APIRouter, status
from app.api.models import TeamCreated, TeamCreate, Team
from app.api.utils import generate_password, get_password_hash
from app.api.deps import SessionDep
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.post("/team", response_model=TeamCreated, tags=["team"])
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

    return TeamCreated(name=team.name, password=password)
