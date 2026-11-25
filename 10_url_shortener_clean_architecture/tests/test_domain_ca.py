from shortener.domain import Url


def test_httpsのURLからUrlを作れる():
    url = Url("https://example.com")
    assert url.value == "https://example.com"
