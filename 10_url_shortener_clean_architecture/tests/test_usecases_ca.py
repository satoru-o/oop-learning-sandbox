from shortener.usecases import ShortenUrl


class FixedCodeGenerator:
    """いつも同じコードを返す、テスト用のコード生成器"""

    def __init__(self, code: str):
        self.code = code

    def generate(self) -> str:
        return self.code


def test_長いURLを渡すと短いコードを返す():
    shorten = ShortenUrl(generator=FixedCodeGenerator("abc123"))
    assert shorten.execute("https://example.com/very/long/path") == "abc123"
