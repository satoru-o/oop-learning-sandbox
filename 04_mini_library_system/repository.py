# 04_mini_library_system/repository.py
# 外界（ファイル）との境界。ファイル I/O はこのモジュールだけで行う。
import json
import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from errors import CorruptedDataError, StorageError
from serialization import state_from_dict, state_to_dict
from state import LibraryState


class LibraryRepository(ABC):
    """LibraryState の保存・読み込みのインターフェース"""

    @abstractmethod
    def load(self) -> LibraryState:
        """保存された状態を読み込む。まだ何も保存されていなければ空の状態"""

    @abstractmethod
    def save(self, state: LibraryState) -> None:
        """状態を保存する。失敗したら StorageError"""


class InMemoryRepository(LibraryRepository):
    """メモリ上に持つだけの実装（テスト・デフォルト用）"""

    def __init__(self, state: LibraryState | None = None):
        self._state = state if state is not None else LibraryState()

    def load(self) -> LibraryState:
        return self._state

    def save(self, state: LibraryState) -> None:
        self._state = state


class JsonFileRepository(LibraryRepository):
    """全体スナップショットを JSON ファイル 1 つに保存する（DB のふり）"""

    def __init__(self, path: str | Path):
        self._path = Path(path)

    def load(self) -> LibraryState:
        try:
            text = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return LibraryState()
        except UnicodeDecodeError as e:
            raise CorruptedDataError(f"文字コードが不正です: {self._path}") from e
        except OSError as e:
            raise StorageError(f"読み込みに失敗しました: {self._path} ({e})") from e

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise CorruptedDataError(f"JSON として不正です: {self._path} ({e})") from e
        return state_from_dict(data)

    def save(self, state: LibraryState) -> None:
        text = json.dumps(state_to_dict(state), ensure_ascii=False, indent=2)
        try:
            self._atomic_write(text)
        except OSError as e:
            raise StorageError(f"保存に失敗しました: {self._path} ({e})") from e

    def _atomic_write(self, text: str) -> None:
        """一時ファイルに書いてから差し替える。途中で失敗しても元のファイルは壊れない"""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            dir=self._path.parent, prefix=f"{self._path.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, self._path)
        except BaseException:
            Path(tmp_name).unlink(missing_ok=True)
            raise
