"""データの形（スキーマ）。これ自体もただのデータで、データ表現とは別に持つ"""

POSITIONS = ["staff", "executive"]

# 日時は ISO 8601 の文字列（分まで）。形を固定すれば文字列のまま大小比較できる
TIME = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$"}

USER = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "position": {"enum": POSITIONS},
    },
    "required": ["name", "position"],
    "additionalProperties": False,
}

SLOT = {
    "type": "object",
    "properties": {"start": TIME, "end": TIME},
    "required": ["start", "end"],
    "additionalProperties": False,
}

# min_position が "staff" なら誰でも使える。役員室は "executive"
ROOM = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "min_position": {"enum": POSITIONS},
    },
    "required": ["name", "min_position"],
    "additionalProperties": False,
}

BOOKING = {
    "type": "object",
    "properties": {"user": USER, "slot": SLOT},
    "required": ["user", "slot"],
    "additionalProperties": False,
}

SCHEDULE = {
    "type": "object",
    "properties": {"room": ROOM, "bookings": {"type": "array", "items": BOOKING}},
    "required": ["room", "bookings"],
    "additionalProperties": False,
}
