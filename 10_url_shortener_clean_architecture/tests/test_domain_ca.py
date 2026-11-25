import pytest
from shortener.domain import InvalidUrlError, Url


def test_httpsのURLからUrlを作れる():
    url = Url("https://example.com")
    assert url.value == "https://example.com"


def test_httpでもhttpsでもないURLは受け付けない():
    with pytest.raises(InvalidUrlError, match="ftp://example.com"):
        Url("ftp://example.com")


def test_ホスト名がないURLは受け付けない():
    with pytest.raises(InvalidUrlError, match="https://"):
        Url("https://")


def test_Urlは作ったあと書き換えられない():
    url = Url("https://example.com")
    with pytest.raises(AttributeError):
        url.value = "ftp://example.com"


def test_同じURLのUrlは等しい():
    assert Url("https://example.com") == Url("https://example.com")
