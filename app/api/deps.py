from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session, select
import jwt
from app.api.exception import RequiresLoginException
from app.api.models import Team
from app.core.config import settings
from app.core.db import get_session

SessionDep = Annotated[Session, Depends(get_session)]


async def authenticate_team(
    session: SessionDep, auth_jwt: Annotated[str | None, Cookie()] = None
) -> Team:
    if auth_jwt is None:
        raise RequiresLoginException
    try:
        team_jwt = jwt.decode(
            auth_jwt, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise RequiresLoginException
    team = session.exec(select(Team).where(Team.id == team_jwt["id"])).first()
    if team is None:
        raise RequiresLoginException
    return team


async def authenticate_optional_team(
    session: SessionDep, auth_jwt: Annotated[str | None, Cookie()] = None
) -> Team | None:
    try:
        return await authenticate_team(session, auth_jwt)
    except RequiresLoginException:
        return None


AuthDep = Annotated[Team, Depends(authenticate_team)]
AuthOptionalDep = Annotated[Team | None, Depends(authenticate_optional_team)]


async def authenticate_admin(team: AuthDep):
    if not team.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to be admin to do this",
        )


AdminDep = Annotated[None, Depends(authenticate_admin)]
