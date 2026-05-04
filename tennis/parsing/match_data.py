from dataclasses import dataclass
from enum import IntEnum, auto


class PointEvent(IntEnum):
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
    winner: str
    server: str
    current_score: str
    event: PointEvent
        

@dataclass 
class Game:
    winner: str
    server: str
    points: list[Point]


@dataclass
class Match:
    id: str
    games: list[Game]
