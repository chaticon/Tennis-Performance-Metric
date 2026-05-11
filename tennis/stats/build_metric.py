from sys import argv
from tennis.parsing.parser_mcp import parse_mcp
from dataclasses import dataclass, asdict
from tennis.parsing.match_data import *
import json
import os
import numpy as np
from numpy.typing import NDArray


_parsers = {'mcp': parse_mcp}


@dataclass
class Metric:
    name: str
    weights: dict[PointEvent, float]

    @staticmethod
    def from_json(js: dict) -> Metric:
        name = js['name']
        weights = {}

        for pe in js['weights']:
            weights[PointEvent(int(pe))] = js['weights'][pe]
        
        return Metric(name, weights)


"""
Compute the weights for the metric using the given dataset.
It's important that we allow for the construction and usage of different metrics,
since we may be interested in comparison with different populations of players.
"""
def build_metric(name: str, data: NDArray[np.integer]) -> Metric:
    # TODO Step 1: Compute the probability that the server wins the game from a given game state, i.e., the current score
    # TODO Step 2: Compute the average value of each PointEvent as the average difference in winning probability for the player who scored that point
    return Metric(name, {PointEvent.WINNER: 1.0})


def main():
    if len(argv) < 4:
        print('Args: [data format e.g. mcp] [metric name] [one or more data files]')
        return 0

    format = argv[1]
    if format not in _parsers:
        print(f'Data format "{format}" is not currently supported.')
        return 0
    parser = _parsers[format]

    name = argv[2]

    data = []
    for i in range(3, len(argv)):
        try:
            data.append(parser(argv[i]))
            print(f'Parsed {data[-1].shape[0]} points from file "{argv[i]}"')
        except FileNotFoundError as ex:
            q = input(f'Could not find data file "{ex.filename}". Ignore and continue? (y/n): ')
            if q.lower() == 'n':
                return 0
    
    if data:
        data = np.concatenate(data)
        metric = build_metric(name, data)
        if not os.path.exists('./metrics'):
            os.mkdir('./metrics')
        with open(f'./metrics/{name}.json', 'w') as f:
            json.dump(asdict(metric), f)
    
    return 0


if __name__ == '__main__':
    main()
