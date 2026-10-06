import json
import os

import pytest
from errors import CorruptedDataError, StorageError
from repository import InMemoryRepository, JsonFileRepository, LibraryRepository
from state import LibraryState


def test_LibraryRepositoryは抽象クラス():
    with pytest.raises(TypeError):
        LibraryRepository()


class TestInMemoryRepository:
    def test_最初は空の状態(self):
        assert InMemoryRepository().load() == LibraryState()

    def test_保存した状態を読み込める(self, full_state):
        repo = InMemoryRepository()
        repo.save(full_state)
        assert repo.load() == full_state

    def test_初期状態を渡せる(self, full_state):
        assert InMemoryRepository(full_state).load() == full_state


class TestJsonFileRepository:
    @pytest.fixture
    def path(self, tmp_path):
        return tmp_path / "library.json"

    def test_ファイルがなければ空の状態(self, path):
        assert JsonFileRepository(path).load() == LibraryState()
        assert not path.exists()  # 読み込みだけではファイルを作らない

    def test_保存すると別のインスタンスからも読み込める(self, path, full_state):
        JsonFileRepository(path).save(full_state)
        assert JsonFileRepository(path).load() == full_state

    def test_保存内容は人が読めるJSON(self, path, full_state):
        JsonFileRepository(path).save(full_state)
        text = path.read_text(encoding="utf-8")

        assert "一般太郎" in text  # 日本語がエスケープされない
        assert json.loads(text)["version"] == 1

    def test_存在しないディレクトリも作って保存する(self, tmp_path, full_state):
        nested = tmp_path / "data" / "nested" / "library.json"
        JsonFileRepository(nested).save(full_state)
        assert JsonFileRepository(nested).load() == full_state

    def test_上書き保存できる(self, path, full_state):
        repo = JsonFileRepository(path)
        repo.save(LibraryState())
        repo.save(full_state)
        assert repo.load() == full_state

    @pytest.mark.parametrize(
        "content",
        [
            "",
            "{ broken json",
            "[]",
            '{"version": 999}',
            '{"version": 1}',
        ],
        ids=["空", "JSONとして不正", "オブジェクトでない", "未対応の版", "項目が欠けている"],
    )
    def test_壊れたファイルはCorruptedDataError(self, path, content):
        path.write_text(content, encoding="utf-8")
        with pytest.raises(CorruptedDataError):
            JsonFileRepository(path).load()

    def test_文字コードが不正なファイルもCorruptedDataError(self, path):
        path.write_bytes(b"\xff\xfe\x00invalid")
        with pytest.raises(CorruptedDataError):
            JsonFileRepository(path).load()

    def test_読めない場所はStorageError(self, tmp_path):
        with pytest.raises(StorageError):
            JsonFileRepository(tmp_path).load()  # ディレクトリをファイルとして読む

    def test_書けない場所はStorageError(self, tmp_path, full_state):
        blocker = tmp_path / "file"
        blocker.write_text("x")
        with pytest.raises(StorageError):
            JsonFileRepository(blocker / "library.json").save(full_state)

    def test_書き込みに失敗しても元のファイルは壊れず一時ファイルも残らない(
        self, path, full_state, monkeypatch
    ):
        repo = JsonFileRepository(path)
        repo.save(LibraryState())
        before = path.read_text(encoding="utf-8")

        def fail(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", fail)
        with pytest.raises(StorageError):
            repo.save(full_state)

        assert path.read_text(encoding="utf-8") == before
        assert [p.name for p in path.parent.iterdir()] == ["library.json"]
