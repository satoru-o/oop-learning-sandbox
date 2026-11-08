import icontract


@icontract.invariant(lambda self: self.start < self.end, "start < end")
class TimeSlot:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def _raw_overlaps(self, other) -> bool:
        if self.end <= other.start:
            return False
        elif other.end <= self.start:
            return False
        else:
            return True

    @icontract.ensure(
        lambda self, other, result: result == other._raw_overlaps(self),
        "overlapsは左右を入れ替えても同じ結果になる",
    )
    def overlaps(self, other) -> bool:
        return self._raw_overlaps(other)
