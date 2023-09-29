import random
import pandas as pd

acronyms = pd.read_csv("acronyms.csv", index_col=0)
standings = pd.read_csv("data/current_standings.csv")
east = standings["East"].to_list()
west = standings["West"].to_list()
standings_list = [west,east]

shared_preds = [
    ["DEN", "GSW", "PHX", "LAL", "SAC", "LAC", "MEM", "DAL"],
    ["MIL", "BOS", "CLE", "PHI", "NYK", "MIA", "NYK", "BKN"],
]

cam_preds = [
    random.sample(west,8),
    random.sample(east,8)
]

austy_preds = [
    random.sample(west,8),
    random.sample(east,8)
]

def compute_score(pred_rank, actual_rank):
    diff = abs(pred_rank - actual_rank)
    if diff == 0:
        return 3
    elif diff == 1:
        return 2
    elif diff == 2:
        return 1
    return 0


def sum_scores(user_pred, current_standings):
    scores = []
    for conf in [0,1]:
        for rank, team in enumerate(user_pred[conf]):
            res = compute_score(rank, current_standings[conf].index(team))
            scores.append(res)
    return sum(scores)

shared_score = sum_scores(shared_preds, standings_list)
austy_score = sum_scores(austy_preds, standings_list)
cam_score = sum_scores(cam_preds, standings_list)

print('Shared:',shared_score)
print('Austypoo:',austy_score)
print('Cammykinz:',cam_score)


