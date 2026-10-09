# 04_mini_library_system/late_fee.py
# 延滞料の計算方法（Strategy）。状態を持たない不変の値で、Library に注入して差し替える。
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, timedelta


class LateFeeRule(ABC):
    """延滞料ルールのインターフェース"""

    @abstractmethod
    def calculate(self, due_on: date, returned_on: date, daily_fee: int) -> int:
        """返却期限と返却日、1日あたりの単価から延滞料を計算する（延滞していなければ0円）"""


@dataclass(frozen=True)
class PerDayLateFee(LateFeeRule):
    """延滞日数 × 単価（標準のルール）"""

    def calculate(self, due_on: date, returned_on: date, daily_fee: int) -> int:
        return max(0, (returned_on - due_on).days) * daily_fee


@dataclass(frozen=True)
class WeekendFreeLateFee(LateFeeRule):
    """土日は延滞日数に数えない（図書館が閉まっている日は免除）"""

    def calculate(self, due_on: date, returned_on: date, daily_fee: int) -> int:
        late_days = max(0, (returned_on - due_on).days)
        days = (due_on + timedelta(days=n) for n in range(1, late_days + 1))
        weekdays = sum(1 for d in days if d.weekday() < 5)  # 月曜=0 … 金曜=4
        return weekdays * daily_fee


@dataclass(frozen=True)
class CappedLateFee(LateFeeRule):
    """他のルールで計算した延滞料に、上限額をかける（Decorator）"""

    inner: LateFeeRule
    cap: int

    def __post_init__(self):
        if self.cap < 0:
            raise ValueError(f"上限額は0円以上にしてください ({self.cap}円)")

    def calculate(self, due_on: date, returned_on: date, daily_fee: int) -> int:
        return min(self.inner.calculate(due_on, returned_on, daily_fee), self.cap)


DEFAULT_LATE_FEE_RULE: LateFeeRule = PerDayLateFee()
