from dataclasses import dataclass
from urllib.parse import urlsplit


class InvalidUrlError(Exception):
    """不正なURLエラー"""


@dataclass(frozen=True)
class Url:
    value: str

    def __post_init__(self):
        parts = urlsplit(self.value)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise InvalidUrlError(self.value)
