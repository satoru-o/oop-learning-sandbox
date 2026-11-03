class TimeSlot:
    def __init__(self, start, end):
        if start >= end:
            raise AssertionError("不変条件違反(start < end)")
        self.start = start
        self.end = end

    def _raw_overlaps(self, other) -> bool:
        if self.end <= other.start:
            return False
        elif other.end <= self.start:
            return False
        else:
            return True

    def overlaps(self, other) -> bool:
        result = self._raw_overlaps(other)
        if result != other._raw_overlaps(self):
            raise AssertionError("事後条件違反(overlapsが対称ではない)")
        return result
