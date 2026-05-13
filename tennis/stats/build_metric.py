from sys import argv
from tennis.parsing.parser_mcp import parse_mcp
from dataclasses import dataclass, asdict
from tennis.parsing.match_data import *
import json
import os
import numpy as np
from numpy.typing import NDArray


_parsers = {'mcp': parse_mcp}

metrics_dir = './metrics'


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
    
    def to_numpy(self) -> NDArray[np.integer]:
        weights = [0.0 for pe in PointEvent]
        for pe in self.weights:
            weights[pe] = self.weights[pe]
            # we don't distinguish between these
            if pe == PointEvent.WINNER:
                weights[PointEvent.RETURN_WINNER] = self.weights[pe]
            elif pe == PointEvent.ACE:
                weights[PointEvent.SERVICE_WINNER] = self.weights[pe]
        weights = np.array(weights)
        
        return weights



def build_metric(name: str, data: NDArray[np.integer]) -> Metric:
    """
    Compute the weights for the metric using the given dataset.
    It's important that we allow for the construction and usage of different metrics,
    since we may be interested in comparison with different populations of players.
    """
    # Step 1: Compute the probability that the server wins the game from a given game state, i.e., the current score
    probs = [0 for _ in GameState]
    for s in GameState:
        pts_in_s = data[data[:, MatrixIndex.GAME_STATE] == s]
        if len(pts_in_s) > 0:
            probs[s] = len(pts_in_s[pts_in_s[:, MatrixIndex.GAME_WINNER] == pts_in_s[:, MatrixIndex.SERVER]]) / len(pts_in_s)
    probs[GameState.SERVER_WON] = 1.0
    probs = np.array(probs)

    # Step 2: Compute the average value of each PointEvent as the average difference in winning probability for the player who scored that point
    weights = {k: 0.0 for k in PointEvent if k != PointEvent.SERVICE_WINNER and k != PointEvent.RETURN_WINNER and k != PointEvent.UNKNOWN}
    result = np.vectorize(GameState.result, otypes=[np.int32])
    filtered = data[data[:, MatrixIndex.POINT_EVENT] != PointEvent.UNKNOWN] # we are not interested in points where we don't know what happened
    for pe in weights:
        # we currently make no distinction between service winners and aces, or between return winners and winners
        if pe == PointEvent.ACE:
            pts_with_pe = filtered[(filtered[:, MatrixIndex.POINT_EVENT] == PointEvent.ACE) | (filtered[:, MatrixIndex.POINT_EVENT] == PointEvent.SERVICE_WINNER)]
        elif pe == PointEvent.WINNER:
            pts_with_pe = filtered[(filtered[:, MatrixIndex.POINT_EVENT] == PointEvent.WINNER) | (filtered[:, MatrixIndex.POINT_EVENT] == PointEvent.RETURN_WINNER)]
        else:
            pts_with_pe = filtered[filtered[:, MatrixIndex.POINT_EVENT] == pe]

        if len(pts_with_pe) > 0:
            returner_won = pts_with_pe[pts_with_pe[:, MatrixIndex.POINT_WINNER] != pts_with_pe[:, MatrixIndex.SERVER], MatrixIndex.GAME_STATE]
            server_won = pts_with_pe[pts_with_pe[:, MatrixIndex.POINT_WINNER] == pts_with_pe[:, MatrixIndex.SERVER], MatrixIndex.GAME_STATE]

            diff = (np.sum(probs[returner_won] - probs[result(returner_won, -1)]) + np.sum(probs[result(server_won, 1)] - probs[server_won])) / len(pts_with_pe)
            weights[pe] = diff

    return Metric(name, weights)


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
            temp, _ = parser(argv[i])
            data.append(temp)
            print(f'Parsed {data[-1].shape[0]} points from file "{argv[i]}"')
        except FileNotFoundError as ex:
            q = input(f'Could not find data file "{ex.filename}". Ignore and continue? (y/n): ')
            if q.lower() == 'n':
                return 0
    
    if data:
        data = np.concatenate(data)
        metric = build_metric(name, data)
        if not os.path.exists(metrics_dir):
            os.mkdir(metrics_dir)
        with open(f'{metrics_dir}/{name}.json', 'w') as f:
            json.dump(asdict(metric), f)
    
    return 0


if __name__ == '__main__':
    main()
