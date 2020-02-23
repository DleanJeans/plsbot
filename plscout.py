import random
from const import *

def choose_best_area(areas):
    points = [score_area(a) for a in areas]
    best_point = max(points)
    worst_point = min(points)

    if best_point or worst_point:
        index = points.index(best_point)
        return areas[index]
    else:
        return random.choice(areas)

def score_area(area):
    if area in SCOUT_AREA_PROSPECTS:
        return SCOUT_AREA_PROSPECTS.index(area)
    elif area in SCOUT_AREA_RISKS:
        return -SCOUT_AREA_RISKS.index(area)
    else:
        return 0