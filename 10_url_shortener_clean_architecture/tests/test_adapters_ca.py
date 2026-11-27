from shortener.adapters import InMemoryUrlRepository


def test_書き留めたコードでURLを取り出せる():
    repository = InMemoryUrlRepository()
    repository.save("abc123", "https://example.com/very/long/path")
    assert repository.find("abc123") == "https://example.com/very/long/path"
