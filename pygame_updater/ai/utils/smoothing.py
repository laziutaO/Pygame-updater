"""Path smoothing via line-of-sight: drop intermediate waypoints when a direct line clears."""
from .los import line_of_sight


def smooth_path(path, blocked_fn):
    """Greedy waypoint reduction. Keeps only points where LoS to the next-kept point breaks."""
    if not path or len(path) < 3:
        return list(path) if path else []
    result = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not line_of_sight(path[i], path[j], blocked_fn):
            j -= 1
        result.append(path[j])
        i = j
    return result
