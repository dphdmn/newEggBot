import os

daily_fmc         = int(os.environ["channel_daily_fmc"])
daily_fmc_results = int(os.environ["channel_daily_fmc_results"])
ten_minute_fmc    = int(os.environ["channel_ten_minute_fmc"])
fmc_5x5           = int(os.environ["channel_5x5_fmc"])

movesgame            = int(os.environ["channel_movesgame"])
movesgame_tournament = int(os.environ["channel_movesgame_tournament"])

optimal_game = int(os.environ["channel_optimal_game"])

random_game = [int(x) for x in os.environ["channel_random_game"].split(",")]

_nxn_ids = [int(x) for x in os.environ["channel_nxn"].split(",")]
_nxn_sizes = list(range(3,11))
nxn_channels = {_nxn_ids[i]: _nxn_sizes[i] for i in range(len(_nxn_ids))}
