"""予約情報の置き場所。データがそのまま JSON なので、保存・復元は変換コードがほぼ要らない"""

import json

from validate import schedule_errors


class InMemoryScheduleStore:
    def __init__(self):
        self._texts: dict[str, str] = {}  # 部屋名 -> JSON 文字列

    def save(self, schedule: dict) -> None:
        if errors := schedule_errors(schedule):
            raise ValueError(f"不正なスケジュールは保存できない: {errors}")
        self._texts[schedule["room"]["name"]] = json.dumps(schedule, ensure_ascii=False)

    def load(self, room_name: str) -> dict:
        if room_name not in self._texts:
            return {"ok": False, "error": "room_not_found"}
        schedule = json.loads(self._texts[room_name])
        # 外から入ってきたデータは境界で検証する
        if errors := schedule_errors(schedule):
            raise ValueError(f"保存されていたデータが壊れている: {errors}")
        return {"ok": True, "schedule": schedule}
