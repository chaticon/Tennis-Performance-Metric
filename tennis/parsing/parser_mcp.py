import csv
from enum import StrEnum
from .match_data import Match, Game, Point, PointEvent
import re


class RallyEnd(StrEnum):
    WINNER = '*'
    UNFORCED_ERROR = '@'
    FORCED_ERROR = '#'


class Fault(StrEnum):
    NET = 'n'
    WIDE = 'w'
    DEEP = 'd'
    WIDE_DEEP = 'x'
    FOOT = 'g'
    SHANK = '!'
    UNKNOWN = 'e'
    TIME = 'V'
    LET = 'c' # technically not a fault, but there's nowhere else to put it


class CourtPosition(StrEnum):
    APPROACH = '+'
    NET = '-'
    BASELINE = '='


class MiscInfo(StrEnum):
    NET_CORD = ';'
    DROP_VOLLEY = '^'


class ServiceDirection(StrEnum):
    WIDE = '4'
    BODY = '5'
    T = '6'
    UNKNOWN = '0'


class StrokeDirection(StrEnum):
    FH_SIDE = '1'
    MIDDLE = '2'
    BH_SIDE = '3'


class ReturnDepth(StrEnum):
    SERVICE_BOX = '7'
    MIDDLE = '8'
    BASELINE = '9'


class Stroke(StrEnum):
    FOREHAND = 'f'
    BACKHAND = 'b'

    SLICE = 's'
    SLICE_FOREHAND = 'r'

    VOLLEY_FOREHAND = 'v'
    VOLLEY_BACKHAND = 'z'

    OVERHEAD = 'o'
    OVERHEAD_BACKHAND = 'p'

    DROP_FOREHAND = 'u'
    DROP_BACKHAND = 'y'

    LOB_FOREHAND = 'l'
    LOB_BACKHAND = 'm'

    HV_FOREHAND = 'h'
    HV_BACKHAND = 'i'

    SV_FOREHAND = 'j'
    SV_BACKHAND = 'k'

    TRICKSHOT = 't'

    UNKNOWN = 'q'


_OPTIONAL_DATA_PATTERN = '[' + ''.join([c.value for c in CourtPosition]) + \
                         ''.join([c.value for c in StrokeDirection]) + \
                         ''.join([c.value for c in ReturnDepth]) + \
                         ''.join([c.value for c in MiscInfo]) + ']' # matches all of the optional data codes. necessary because they are not always in the same order


_SERVICE_WINNER_PATTERN = '[' + ''.join([str(c.value) for c in ServiceDirection]) + '][' \
                         + ''.join([c.value for c in CourtPosition]) + ']?[' \
                         + ''.join([c.value for c in RallyEnd]) + ']' # this matches anything like '4*' or '6+#'


_RETURN_PATTERN = '[' + ''.join([c.value for c in ServiceDirection]) + '][' \
                         + ''.join([c.value for c in CourtPosition]) + ']?[' \
                         + ''.join([c.value for c in Stroke]) + ']' \
                         + _OPTIONAL_DATA_PATTERN + '*[' \
                         + ''.join([c.value for c in Fault]) + ']?[' \
                         + ''.join([c.value for c in RallyEnd]) + ']' # this matches anything like '4f*' or '5+b=37w@'


"""
Determines how the point ended using the raw point string and returns the result as a PointEvent
"""
def event_from_raw(raw: str) -> PointEvent:
    first, second = raw.split(',')
    point = second if second else first # if there was a second serve, then that's where the point actually played out
    
    if point[-1] in Fault: # if the last character is a fault code, then this was a double fault
        return PointEvent.DOUBLE_FAULT
    elif point[-1] in RallyEnd: # the point was won through conventional play in some way
        if re.search(_SERVICE_WINNER_PATTERN, point): # the point ended immediately after the serve
            match point[-1]:
                case RallyEnd.WINNER:
                    return PointEvent.ACE
                case _:
                    return PointEvent.SERVICE_WINNER
        elif re.search(_RETURN_PATTERN, point): # the point ended immediately after the return
            match point[-1]:
                case RallyEnd.WINNER:
                    return PointEvent.RETURN_WINNER 
                case _:
                    return PointEvent.RETURN_ERROR
        else: # the point ended after some rallying
            match point[-1]:
                case RallyEnd.WINNER:
                    return PointEvent.WINNER
                case RallyEnd.UNFORCED_ERROR:
                    return PointEvent.UNFORCED_ERROR
                case RallyEnd.FORCED_ERROR:
                    return PointEvent.FORCED_ERROR
    
    return PointEvent.UNKNOWN


"""
Parse a Match Charting Project data file into a dictionary of Match objects indexed by match_id
"""
def parse_mcp(mcp_file: str) -> dict[Match]:
    matches = {}

    with open(mcp_file) as f:
        reader = csv.DictReader(f)
        # each row represents one point
        for point in reader:
            match_id = point['match_id']
            pts = matches.setdefault(match_id, {}) # get/create the associated point dict
            raw = ','.join([point['1st'].strip(), point['2nd'].strip()]) # put the 1st and 2nd serves together into one raw string
            p = Point(raw, point['Pts'], point['PtWinner'], event_from_raw(raw))
            pts[int(point['Pt'])] = p

    # we should now have the matches in the form of dictionaries of points
    # I do this to account for the possiblity that the points are not ordered
    # now we parse the dictionary into Match and Game objects

    output = {}
    for match_id in matches:
        match = Match(match_id, [])
        points = matches[match_id]
        i = 1
        game_points = []
        while i in points: # now that we know we have all the available points, we can safely view them in order
            point = points[i]
            if point.current_score == '0-0' and game_points:
                if re.search('(?:AD)|(?:40)', game_points[-1].current_score):
                    game = Game(game_points[-1].winner, game_points)
                else:
                    game = Game(-1, game_points) # in the event that we are missing the final point of the game, mark the winner unknown
                match.games.append(game)
                game_points = []
            
            game_points.append(point)
            i += 1
        output[match_id] = match
    
    return output
