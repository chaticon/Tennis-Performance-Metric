A Tennis performance metric which takes the game context into account, measuring the average impact of a player's point outcomes on their probability of winning games. This project is for CS 682 at the Universiy of Massachusetts Boston.

Makes use of data from the Match Charting Project: https://github.com/JeffSackmann/tennis_MatchChartingProject


Required Packages:
numpy


Usage:
First, you need to create a performance metric using a dataset. This metric can then be used to compare players with the given player population. To do so, use the build_metric script:
python -m tennis.stats.build_metric [data format] [metric name] [data files...]

Currently, the only supported data format is the Match Charting Project (MCP) format.

Running this script will produce a file [metric_name].json in the metrics directory. This can now be used to analyze player performance using the analyze_player script:
python -m tennis.stats.analyze_player [data format] [Player_Name or *] [metric name] [data files...]

The player's name should be capitalized properly, with spaces replaced by underscores. Running the script for one player will collect their points from the provided dataset and evaluate their performance using the specified metric. Currently, it will simply output the result to the console.

Running the script with the wildcard (*) instead of specifying the player will evaluate every player in the dataset. The result will be output to [metric_name]_on_[dataset].csv in the performance directory. This file will contain each player's name, their performance, and the point-by-point sample size for that player. Currently, players with fewer than 1000 points in the dataset are omitted.


This much is implemented, I may add a central script that executes these commands with an additional command that combines building the metric and then analyzing all the players into one. I can also produce visuals if needed, as-is the project produces data which can then be used to make visualizations, rather than being a visualization tool itself.
