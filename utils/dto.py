from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class VoteDTO:
    full_name: str
    vote: str


@dataclass(slots=True)
class PollDTO:
    id: int
    place: str
    meeting_at: datetime
    votes: list[VoteDTO]