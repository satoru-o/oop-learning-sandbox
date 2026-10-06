from dataclasses import FrozenInstanceError
from datetime import date

import pytest
from late_fee import CappedLateFee, LateFeeRule, PerDayLateFee, WeekendFreeLateFee

# 2026-10-15 は木曜日。10/16(金) 10/17(土) 10/18(日) 10/19(月) …
THU = date(2026, 10, 15)
FRI = date(2026, 10, 16)
SUN = date(2026, 10, 18)
THU_NEXT = date(2026, 10, 22)  # 木曜から7日後（延滞7日: 金土日月火水木。平日は5日）


def test_LateFeeRuleは抽象クラス():
    with pytest.raises(TypeError):
        LateFeeRule()


class TestPerDayLateFee:
    rule = PerDayLateFee()

    @pytest.mark.parametrize(
        ("returned_on", "expected"),
        [
            (date(2026, 10, 10), 0),  # 期限前
            (THU, 0),  # 期限当日は延滞ではない
            (FRI, 10),
            (THU_NEXT, 70),  # 7日延滞
        ],
    )
    def test_延滞日数かける単価(self, returned_on, expected):
        assert self.rule.calculate(THU, returned_on, daily_fee=10) == expected

    def test_単価が変われば金額も変わる(self):
        assert self.rule.calculate(THU, THU_NEXT, daily_fee=5) == 35


class TestWeekendFreeLateFee:
    rule = WeekendFreeLateFee()

    def test_土日は延滞日数に数えない(self):
        # 金土日月火水木の7日間のうち、平日は金月火水木の5日
        assert self.rule.calculate(THU, THU_NEXT, daily_fee=10) == 50

    def test_平日だけなら通常と同じ(self):
        # 月曜が期限、金曜に返却 → 火水木金の4日
        assert self.rule.calculate(date(2026, 10, 19), date(2026, 10, 23), daily_fee=10) == 40

    def test_延滞が土日だけなら0円(self):
        # 金曜が期限、日曜に返却 → 延滞は土日の2日のみ
        assert self.rule.calculate(FRI, SUN, daily_fee=10) == 0

    def test_土日をまたぐ短い延滞(self):
        # 木曜が期限、日曜に返却 → 金土日のうち平日は金曜のみ
        assert self.rule.calculate(THU, SUN, daily_fee=10) == 10

    @pytest.mark.parametrize("returned_on", [date(2026, 10, 10), THU])
    def test_延滞していなければ0円(self, returned_on):
        assert self.rule.calculate(THU, returned_on, daily_fee=10) == 0


class TestCappedLateFee:
    def test_上限を超えたら上限額(self):
        rule = CappedLateFee(PerDayLateFee(), cap=60)
        assert rule.calculate(THU, THU_NEXT, daily_fee=10) == 60  # 本来は70

    def test_上限以下ならそのまま(self):
        rule = CappedLateFee(PerDayLateFee(), cap=100)
        assert rule.calculate(THU, THU_NEXT, daily_fee=10) == 70

    def test_上限ちょうどはそのまま(self):
        rule = CappedLateFee(PerDayLateFee(), cap=70)
        assert rule.calculate(THU, THU_NEXT, daily_fee=10) == 70

    def test_他のルールと組み合わせられる(self):
        # 土日免除で 50円 → 上限 40円
        rule = CappedLateFee(WeekendFreeLateFee(), cap=40)
        assert rule.calculate(THU, THU_NEXT, daily_fee=10) == 40

    def test_上限を重ねがけできる(self):
        rule = CappedLateFee(CappedLateFee(PerDayLateFee(), cap=60), cap=30)
        assert rule.calculate(THU, THU_NEXT, daily_fee=10) == 30

    def test_上限は0円以上(self):
        assert CappedLateFee(PerDayLateFee(), cap=0).calculate(THU, THU_NEXT, 10) == 0
        with pytest.raises(ValueError):
            CappedLateFee(PerDayLateFee(), cap=-1)


def test_ルールは変更できない値():
    rule = CappedLateFee(PerDayLateFee(), cap=60)
    with pytest.raises(FrozenInstanceError):
        rule.cap = 100


def test_同じ設定のルールは等しい():
    assert CappedLateFee(WeekendFreeLateFee(), cap=60) == CappedLateFee(WeekendFreeLateFee(), 60)
    assert PerDayLateFee() != WeekendFreeLateFee()
