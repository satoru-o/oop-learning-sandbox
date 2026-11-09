def overlaps(a: dict, b: dict) -> bool:
    """半開区間 [start, end) で重なるか。隣り合う枠は重ならない"""
    return a["start"] < b["end"] and b["start"] < a["end"]
