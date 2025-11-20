from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# Shared properties
class TeamBase(SQLModel):
    name: str = Field(max_length=15, unique=True)


# Database model
class Team(TeamBase, table=True):
    id: int = Field(default=None, primary_key=True)
    password: str = Field()


# Properties to receive on team create
class TeamCreate(TeamBase):
    pass


# Properties to return for public endpoints
class TeamPublic(TeamBase):
    id: int


# Properties to return after team creation
class TeamCreated(TeamPublic):
    password: str


# Properties to receive when logging in
class LoginRequest(BaseModel):
    team_name: str
    password: str


# Properties to return after logging in
class LoginJWT(BaseModel):
    jwt: str
