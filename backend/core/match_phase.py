PHASES = ["PRE", "LIVE", "HALFTIME", "POST"]

def get_match_phase(elapsed_minutes: int) -> str:
    """
    Returns the current match phase based on elapsed event time in minutes.
    - < 15: PRE (Pre-match, arrival)
    - 15 - 59: LIVE (First half)
    - 60 - 74: HALFTIME (Half-time break)
    - >= 75: POST (Second half and end-of-match)
    """
    if elapsed_minutes < 15:
        return "PRE"
    elif elapsed_minutes < 60:
        return "LIVE"
    elif elapsed_minutes < 75:
        return "HALFTIME"
    else:
        return "POST"
