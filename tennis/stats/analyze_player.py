from sys import argv
from tennis.parsing.parser_mcp import parse_mcp
from tennis.parsing.match_data import *
from .build_metric import Metric, metrics_dir
import json
import os
import numpy as np
from numpy.typing import NDArray
import csv
from typing import Any


_parsers = {'mcp': parse_mcp}

WILDCARD = '*'

analysis_dir = './performance'


def analyze_player(player: str, metric: Metric, data: NDArray[np.int32], players: NDArray) -> tuple[float, int]:
    """
    Evaluate a player's performance using the given metric.

    :param str player: The player's full name with spaces replaced by underscores.
    :param Metric metric: A metric that has been calculated from a population of players we want to compare the analyzed player with.
    :param ndarray data: An array of points.
    :param ndarray players: A parallel array to data indicating which players played in each point.
    :return: The performance of the player across their played points, computed using the given metric.
    :rtype: float 
    """

    my_points, me = np.nonzero(players == player)
    my_points = data[my_points, :]
    me += 1

    if len(my_points) == 0:
        return 0.0

    # filter points with unknown point events
    known_events = my_points[:, MatrixIndex.POINT_EVENT] != PointEvent.UNKNOWN
    my_points = my_points[known_events, :]
    me = me[known_events]

    weights = metric.to_numpy()

    # the performance is simply the average weight of their points - lost points are negated
    performance = (np.sum(weights[my_points[my_points[:, MatrixIndex.GAME_WINNER] == me, MatrixIndex.POINT_EVENT]]) - \
                   np.sum(weights[my_points[my_points[:, MatrixIndex.GAME_WINNER] != me, MatrixIndex.POINT_EVENT]])) / len(my_points)

    return performance, len(my_points)


def analyze_all(metric: Metric, data: NDArray[np.int32], players: NDArray, N_cutoff: int = 1000) -> list[dict[str: Any]]:
    """
    Evaluate the performance of every player in the dataset using the given metric.

    :return: The performance of every player in a format suitable for csv output, sorted by performance
    """
    names = np.unique(players)

    result = []
    for player_name in names:
        performance, N = analyze_player(player_name, metric, data, players)
        if N >= N_cutoff:
            result.append({'player_name': player_name, 'performance': performance, 'n_points': N})
    result.sort(key=lambda x: x['performance'], reverse=True)
    
    return result


def main():
    if len(argv) < 4:
        print(f'Args: [data format e.g. mcp] [Player_Name (replace spaces with underscores) or {WILDCARD} to analyze all players in the dataset] [metric name (constructed using build_metric)] [one or more data files]')
        return 0

    format = argv[1]
    if format not in _parsers:
        print(f'Data format "{format}" is not currently supported.')
        return 0
    parser = _parsers[format]

    player_name = argv[2]

    metric = argv[3]
    try:
        with open(f'{metrics_dir}/{metric}.json') as f:
            metric = Metric.from_json(json.load(f))
    except FileNotFoundError:
        print(f'Could not find saved metric "{metric}". Did you construct the metric from a dataset first? Use build_metric to do so.')
        return 0


    data = []
    players = []
    for i in range(4, len(argv)):
        try:
            if player_name != WILDCARD:
                temp, p_temp = parser(argv[i], player_name)
            else:
                temp, p_temp = parser(argv[i])
            data.append(temp)
            players.append(p_temp)
            print(f'Parsed {data[-1].shape[0]} points from file "{argv[i]}"')
        except FileNotFoundError as ex:
            q = input(f'Could not find data file "{ex.filename}". Ignore and continue? (y/n): ')
            if q.lower() == 'n':
                return 0
    
    if data:
        data = np.concatenate(data)
        players = np.concatenate(players)

        if player_name != WILDCARD:
            performance, N = analyze_player(player_name, metric, data, players)
            print(f'In the given dataset, the player had a performance of {performance} across {N} data points using the metric {metric.name}.')
        else:
            result = analyze_all(metric, data, players)
            if not os.path.exists(analysis_dir):
                os.mkdir(analysis_dir)
            dest_file_name = f'{metric.name}_on_{'+'.join([os.path.basename(n) for n in argv[4:]])}.csv'
            with open(f'{analysis_dir}/{dest_file_name}', 'w') as f:
                writer = csv.DictWriter(f, fieldnames=result[0].keys())
                writer.writeheader()
                writer.writerows(result)
                print(f'Full analysis successfully written to {dest_file_name} in the {os.path.abspath(analysis_dir)} directory.')
            
    return 0


if __name__ == '__main__':
    main()
