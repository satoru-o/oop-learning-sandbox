# 役職の強さもデータ。役職を増やすときはここと schemas.POSITIONS に足す
POSITION_RANK = {"staff": 1, "executive": 2}


def can_use(room: dict, user: dict) -> bool:
    return POSITION_RANK[user["position"]] >= POSITION_RANK[room["min_position"]]
