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
    LOVE_ALL = 0
    LOVE_FIFTEEN = 1
    LOVE_THIRTY = 2
    LOVE_FOURTY = 3
    FIFTEEN_LOVE = 4
    FIFTEEN_ALL = 5
    FIFTEEN_THIRTY = 6
    FIFTEEN_FOURTY = 7
    THIRTY_LOVE = 8
    THIRTY_FIFTEEN = 9
    THIRTY_ALL = 10
    THIRTY_FOURTY = 11
    FOURTY_LOVE = 12
    FOURTY_FIFTEEN = 13
    FOURTY_THIRTY = 14
    DEUCE = 15
    FOURTY_AD = 16
    AD_FOURTY = 17

    # these just make some data analysis operations easier
    SERVER_WON = 18
    RETURNER_WON = 19



    @staticmethod
    def decider(state: GameState) -> int:
        """
        Currently does not work with the NextGen ruleset (no-ad)
        For convenience use Point::decider_for

        :return: 1 if the server will win the game if they win the point, -1 if the returner will win, and 0 if neither will win
        :rtype: int
        """
        match state:
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
    
    
    @staticmethod 
    def result(state: GameState, winner: int) -> GameState:
        """
        Returns the next game state that follows if the indicated player won the point.

        :param int winner: 1 if the server won, -1 if the returner won
        """
        if GameState.decider(state) == winner:
            return GameState.SERVER_WON if winner == 1 else GameState.RETURNER_WON
        if state != GameState.DEUCE and state != GameState.FOURTY_AD and state != GameState.AD_FOURTY:
            if winner == 1:
                return GameState(state + 4)
            elif winner == -1:
                return GameState(state + 1)
        if state == GameState.DEUCE:
            if winner == 1:
                return GameState.AD_FOURTY
            elif winner == -1:
                return GameState.FOURTY_AD
        return GameState.DEUCE




class MatrixIndex(IntEnum):
    """
    Use this to index point-related fields in the numpy array more clearly
    """
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
    players: tuple[str, str]


    def decider_for(self, player: int) -> bool:
        """
        Returns true if 'player' will win the game if they win this point
        """
        d = GameState.decider(self.current_score)
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
