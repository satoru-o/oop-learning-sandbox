from dataclasses import dataclass
from typing import Generic, TypeVar

# 成功は Ok、失敗は Err という「値」で表す。例外は使わない
T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
