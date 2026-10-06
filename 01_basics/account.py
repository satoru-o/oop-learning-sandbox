# 01_basics/account.py
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum


# ドメイン例外の定義
class DomainError(Exception):
    "ドメイン領域の基本例外クラス"


class InsufficientBalanceError(DomainError):
    """残高不足例外"""

    def __init__(self, requested: float, current: float):
        super().__init__(f"残高不足です (申請: {requested}円 / 現在の残高: {current}円)")
        self.requested = requested
        self.current = current


class InvalidAmountError(DomainError):
    """金額不正例外"""

    def __init__(self, amount: float):
        super().__init__(f"0円より大きな金額を指定してください ({amount}円)")
        self.amount = amount


# Transaction (値オブジェクト / イミュータブル)
class TransactionType(Enum):
    DEPOSIT = "預金"
    WITHDRAW = "引き出し"


@dataclass(frozen=True)
class Transaction:
    """1件の取引データ。frozen=True により生成後の改竄を防止"""

    id: int
    type: TransactionType
    amount: float
    timestamp: datetime


# TransactionHistory (ファーストクラス・コレクション)
class TransactionHistory:
    """取引履歴のリストとその操作をカプセル化"""

    def __init__(self):
        self._transactions: list[Transaction] = []
        self._next_id: int = 1

    def add(self, transaction_type: TransactionType, amount: float) -> Transaction:
        tx = Transaction(
            id=self._next_id, type=transaction_type, amount=amount, timestamp=datetime.now(UTC)
        )
        self._transactions.append(tx)
        self._next_id += 1
        return tx

    @property
    def all(self) -> tuple[Transaction, ...]:
        """外部から append() 等で書き換えられないようにタプル (不変) として返す"""
        return tuple(self._transactions)


# BankAccount (ドメインエンティティ)
class BankAccount:
    """口座の状態と検証を担当。I/Oは行わない"""

    def __init__(self, owner: str, initial_balance: float = 0.0):
        if initial_balance < 0:
            raise InvalidAmountError(initial_balance)

        self._owner = owner
        self._balance = initial_balance
        self._history = TransactionHistory()

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def history(self) -> TransactionHistory:
        return self._history

    def deposit(self, amount: float) -> float:
        """預金処理 (失敗時は例外を発生)"""
        if amount <= 0:
            raise InvalidAmountError(amount)

        self._balance += amount
        self._history.add(TransactionType.DEPOSIT, amount)
        return self._balance

    def withdraw(self, amount: float) -> float:
        """引き出し処理 (失敗時は例外を発生)"""
        if amount <= 0:
            raise InvalidAmountError(amount)
        if amount > self._balance:
            raise InsufficientBalanceError(amount, self._balance)

        self._balance -= amount
        self._history.add(TransactionType.WITHDRAW, amount)
        return self._balance


# =====================================================================
# 利用側 (メイン処理): ログ出力やエラーハンドリング (UIの役割) をここで行う
# =====================================================================
if __name__ == "__main__":
    account = BankAccount("Alice", 1000)

    print("--- 1. 正常な取引 ---")
    try:
        new_balance = account.deposit(500)
        print(f"[{account.owner}] 預金成功! 現在の残高: {new_balance}円")

        new_balance = account.withdraw(300)
        print(f"[{account.owner}] 引き出し成功! 現在の残高: {new_balance}円")
    except DomainError as e:
        print(f"エラー発生: {e}")

    print("\n--- 2. 不正な取引と例外の捕捉 ---")
    # 不正な預金
    try:
        account.deposit(-100)
    except InvalidAmountError as e:
        print(f"[失敗ログ] {e}")

    # 残高不足の引き出し
    try:
        account.withdraw(5000)
    except InsufficientBalanceError as e:
        print(f"[失敗ログ] {e}")

    print("\n--- 3. 取引履歴の確認 ---")
    for tx in account.history.all:
        time_str = tx.timestamp.strftime("%H:%M:%S")
        print(f" ID:{tx.id} | 時間:{time_str} | 種別:{tx.type.value} | 金額:{tx.amount}円")

    print("\n--- 4. 防御的コピーの確認 ---")
    # 外から history.all に要素を追加しようとしても、tuple なのでエラーになる
    print(f"現在の履歴件数: {len(account.history.all)}件 (安全に保護されています)")
