def score_to_level(score: int, low_max: int = 39, mid_max: int = 69) -> str:
    if score <= low_max:
        return "low"
    if score <= mid_max:
        return "mid"
    return "high"
