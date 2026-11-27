class InMemoryUrlRepository:
    def __init__(self):
        self._table = {}

    def save(self, code: str, url: str) -> None:
        self._table[code] = url

    def find(self, code: str) -> str | None:
        return self._table.get(code)
