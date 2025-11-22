from datetime import datetime

from sqlmodel import Field, SQLModel


# Shared properties
class TeamBase(SQLModel):
    name: str = Field(max_length=15, unique=True)


# Database model
class Team(TeamBase, table=True):
    id: int = Field(default=None, primary_key=True)
    password: str = Field()
    admin: bool = Field(default=False)


# Properties to receive on team create
class TeamCreate(TeamBase):
    pass


# Properties to return for public endpoints
class TeamPublic(TeamBase):
    id: int
    admin: bool


# Properties to return after team creation
class TeamCreated(TeamPublic):
    password: str


# Shared properties
class QuestionBase(SQLModel):
    title: str = Field(max_length=40)
    body: str
    max_score: float  # the score to calculate with
    # the score to render on the pag, for example sqrt root of 2
    # should match max_score as much as possiblee
    max_score_display: str
    number: int = Field(unique=True)
    visible: bool = Field(default=False)


# Shared properties
class SubmissionBase(SQLModel):
    answer: str


# Properties to receive on create
class SubmissionCreate(SubmissionBase):
    pass


# Database model
class Submission(SubmissionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id", ondelete="CASCADE")
    question_id: int = Field(foreign_key="question.id", ondelete="CASCADE")
    timestamp: datetime = Field(default_factory=datetime.now)


# Database model
class Question(QuestionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    solution: str


class QuestionCreate(QuestionBase):
    solution: str
    pass


class QuestionPublic(QuestionBase):
    pass
