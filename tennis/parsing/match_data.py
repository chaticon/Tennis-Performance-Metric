from dataclasses import dataclass
from enum import IntEnum, auto
from warnings import deprecated


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


class GameState(IntEnum):
    LOVE_ALL = auto()
    LOVE_FIFTEEN = auto()
    LOVE_THIRTY = auto()
    LOVE_FOURTY = auto()
    FIFTEEN_LOVE = auto()
    FIFTEEN_ALL = auto()
    FIFTEEN_THIRTY = auto()
    FIFTEEN_FOURTY = auto()
    THIRTY_LOVE = auto()
    THIRTY_FIFTEEN = auto()
    THIRTY_ALL = auto()
    THIRTY_FOURTY = auto()
    FOURTY_LOVE = auto()
    FOURTY_FIFTEEN = auto()
    FOURTY_THIRTY = auto()
    DEUCE = auto()
    AD_FOURTY = auto()
    FOURTY_AD = auto()

    """
    Returns 1 if the server will win the game if they win the point, -1 if the returner will win, and 0 if neither will win
    Currently does not work with the NextGen ruleset (no-ad)
    For convenience use Point::decider_for
    """
    def decider(self) -> int:
        match self:
            case GameState.LOVE_FOURTY:
                return -1
            case GameState.FIFTEEN_FOURTY:
                return -1
            case GameState.THIRTY_FOURTY:
                return -1
            case GameState.FOURTY_AD:
                return -1
            case GameState.FOURTY_LOVE:
                return 1
            case GameState.FOURTY_FIFTEEN:
                return 1
            case GameState.FOURTY_THIRTY:
                return 1
            case GameState.AD_FOURTY:
                return 1
            case _:
                return 0


"""
Use this to index point-related fields in the numpy array more clearly
"""
class MatrixIndex(IntEnum):
    MATCH_ID_HASH = 0
    POINT_IDX = 1
    SERVER = 2
    GAME_STATE = 3
    POINT_EVENT = 4
    POINT_WINNER = 5
    GAME_WINNER = 6
    # we can include set and match scores later if needed


game_states = {'0-0': GameState.LOVE_ALL, '0-15': GameState.LOVE_FIFTEEN, '0-30': GameState.LOVE_THIRTY, '0-40': GameState.LOVE_FOURTY,
 '15-0': GameState.FIFTEEN_LOVE, '15-15': GameState.FIFTEEN_ALL, '15-30': GameState.FIFTEEN_THIRTY, '15-40': GameState.FIFTEEN_FOURTY,
 '30-0': GameState.THIRTY_LOVE, '30-15': GameState.THIRTY_FIFTEEN, '30-30': GameState.THIRTY_ALL, '30-40': GameState.THIRTY_FOURTY,
 '40-0': GameState.FOURTY_LOVE, '40-15': GameState.FOURTY_FIFTEEN, '40-30': GameState.FOURTY_THIRTY, '40-40': GameState.DEUCE,
 'AD-40': GameState.AD_FOURTY, '40-AD': GameState.FOURTY_AD}


@dataclass
class Point:
    raw: str
    winner: int
    server: int
    current_score: GameState
    event: PointEvent
    games: tuple[int, int]
    sets: tuple[int, int]


    """
    Returns true if 'player' will win the game if they win this point
    """
    def decider_for(self, player: int) -> bool:
        d = self.current_score.decider()
        return (d == 1 and player == self.server) or (d == -1 and player != self.server)
        

# I changed my mind about how I want to parse the data, as I want to minimize explicit loops in our data analysis
# but I will leave these here for now in case we ever need them for something

@deprecated('Converted to numpy matrix')
@dataclass 
class Game:
    winner: int
    server: int
    points: list[Point]


@deprecated('Converted to numpy matrix')
@dataclass
class Match:
    id: str
    games: list[Game]
