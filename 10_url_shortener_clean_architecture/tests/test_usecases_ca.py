from shortener.adapters import InMemoryUrlRepository
from shortener.usecases import ShortenUrl


class FixedCodeGenerator:
    """いつも同じコードを返す、テスト用のコード生成器"""

    def __init__(self, code: str):
        self.code = code

    def generate(self) -> str:
        return self.code


def test_長いURLを渡すと短いコードを返す():
    shorten = ShortenUrl(generator=FixedCodeGenerator("abc123"),
                         repository=InMemoryUrlRepository())
    assert shorten.execute("https://example.com/very/long/path") == "abc123"


def test_作ったコードとURLを保存先に書き留める():
    repository = InMemoryUrlRepository()
    shorten = ShortenUrl(generator=FixedCodeGenerator(
        "abc123"), repository=repository)
    shorten.execute("https://example.com/very/long/path")
    assert repository.find("abc123") == "https://example.com/very/long/path"
