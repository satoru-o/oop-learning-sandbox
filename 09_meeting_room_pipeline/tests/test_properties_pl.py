"""性質テスト。個別の例ではなく、ランダムな操作の列に対して「いつでも成り立つこと」を確かめる"""

from datetime import datetime, timedelta

from codec import schedule_from_dict, schedule_to_dict
from domain import Booking, Error, Position, Room, Schedule, Slot, User, is_available
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule
from pipeline import cancel, reserve

BASE = datetime(2026, 11, 3, 9, 0)
STAFF = User("朝野", Position.STAFF)
EXECUTIVE = User("神田", Position.EXECUTIVE)

# 30分刻みの狭い範囲に絞って、重なりが頻繁に起きるようにする
slots = st.builds(
    lambda start, length: Slot(
        BASE + timedelta(minutes=30 * start), BASE + timedelta(minutes=30 * (start + length))
    ),
    st.integers(0, 15),
    st.integers(1, 4),
)
users = st.sampled_from([STAFF, EXECUTIVE])
bookings = st.builds(Booking, users, slots)


def no_overlap_by_brute_force(schedule: Schedule) -> bool:
    """実装の has_overlap を使わず、別の書き方で確かめる"""
    spans = [(b.slot.start, b.slot.end) for b in schedule.bookings]
    return all(
        a_end <= b_start or b_end <= a_start
        for i, (a_start, a_end) in enumerate(spans)
        for b_start, b_end in spans[i + 1 :]
    )


class ScheduleMachine(RuleBasedStateMachine):
    """予約とキャンセルをランダムに繰り返しても、性質が保たれるか"""

    def __init__(self):
        super().__init__()
        self.schedule = Schedule(Room("会議室A"))

    @rule(booking=bookings)
    def 予約する(self, booking):
        before = self.schedule
        result = reserve(before, booking)
        if isinstance(result, Error):
            assert result == Error.OVERLAPPED
            assert not is_available(before, booking.slot)
            assert self.schedule == before
        else:
            assert is_available(before, booking.slot)
            assert result.bookings == (*before.bookings, booking)
            self.schedule = result

    @precondition(lambda self: self.schedule.bookings)
    @rule(data=st.data())
    def キャンセルする(self, data):
        before = self.schedule
        target = data.draw(st.sampled_from(before.bookings))
        result = cancel(before, target)
        assert isinstance(result, Schedule)
        assert len(result.bookings) == len(before.bookings) - 1
        assert target not in result.bookings
        self.schedule = result

    @invariant()
    def 予約同士は重ならない(self):
        assert no_overlap_by_brute_force(self.schedule)

    @invariant()
    def 辞書にして戻しても同じ(self):
        assert schedule_from_dict(schedule_to_dict(self.schedule)) == self.schedule


TestScheduleMachine = ScheduleMachine.TestCase


@given(booking=bookings)
def test_予約してからキャンセルすると元に戻る(booking):
    empty = Schedule(Room("会議室A"))
    reserved = reserve(empty, booking)
    assert isinstance(reserved, Schedule)
    assert cancel(reserved, booking) == empty


@given(booking=bookings)
def test_一般社員は役員室をどんな枠でも予約できない(booking):
    staff_booking = Booking(STAFF, booking.slot)
    result = reserve(Schedule(Room("役員室", Position.EXECUTIVE)), staff_booking)
    assert result == Error.NOT_ALLOWED
