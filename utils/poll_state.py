from dataclasses import dataclass

@dataclass(slots=True)
class PollState:
    hours_left: float
    allow_later: bool