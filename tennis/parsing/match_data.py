from dataclasses import dataclass
from enum import Enum, auto


class PointEvent(Enum):
    ACE = auto()
    SERVICE_WINNER = auto()
    DOUBLE_FAULT = auto()
    RETURN_ERROR = auto()
    RETURN_WINNER = auto()
    WINNER = auto() 
    FORCED_ERROR = auto()
    UNFORCED_ERROR = auto()

    UNKNOWN = auto()


@dataclass
class Point:
    raw: str
    current_score: str
    winner: int
    event: PointEvent
        

@dataclass 
class Game:
    winner: int
    points: list[Point]


@dataclass
class Match:
    id: str
    games: list[Game]
