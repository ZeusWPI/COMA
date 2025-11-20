from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session, select
import jwt
from app.api.models import Team
from app.core.config import settings
from app.core.db import get_session

SessionDep = Annotated[Session, Depends(get_session)]


async def authenticate_team(session: SessionDep, auth_jwt: Annotated[str | None, Cookie()]) -> Team:
    if auth_jwt is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        team_jwt = jwt.decode(auth_jwt, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cookie expired")
    team = session.exec(select(Team).where(Team.id == team_jwt["id"])).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Team doesn't exist")
    return team


AuthDep = Annotated[Team, Depends(authenticate_team)]
