## 01_basics/account.py

class BankAccount:
    def __init__(self, owner: str, initial_balance: float = 0.0):
        self._owner = owner
        self._balance = max(0.0, initial_balance)

    @property
    def owner(self) -> str:
        """名義人を取得 (読み取り専用) """
        return self._owner

    @property
    def balance(self) -> float:
        """残高を取得 (読み取り専用ゲッター) """
        return self._balance

    def deposit(self, amount: float) -> bool:
        """預金する"""
        if amount <= 0:
            print(f"[{self._owner}] 預金失敗: 0円よりも大きな金額を指定してください ({amount}円)")
            return False
        else:
            self._balance += amount
            print(f"[{self._owner} 預金成功: {amount}円 (現在の残高: {self._balance}円)]")
            return True

    def withdraw(self, amount: float) -> bool:
        """引き出す"""
        if amount <= 0:
            print(f"[{self._owner} 引き出し失敗: 0円よりも大きな金額を指定してください ({amount}円)]")
        elif amount > self._balance:
            print(f"[{self._owner} 引き出し失敗: 残高不足です (現在の残高: {amount}円)]")
        else:
            self._balance -= amount
            print(f"[{self._owner}] 引き出し成功: {amount}円 (現在の残高: {self._balance}円)")

if __name__ == "__main__":
    print("--- 1. アカウントの作成 ---")
    account = BankAccount("Alice", 1000)
    print(f"名義人: {account.owner}")
    print(f"初期残高: {account.balance}円")  # @property のおかげで account.balance() ではなく account.balance でアクセス可能

    print("\n--- 2. 正常な取引 ---")
    account.deposit(500)
    account.withdraw(300)

    print("\n--- 3. 不正な操作の検証 ---")
    account.deposit(-100)      # 失敗するはず
    account.withdraw(2000)     # 残高不足で失敗するはず

    print("\n--- 4. カプセル化の確認 ---")
    account.balance = 999999  # AttributeError になり書き換えられない（セッターを定義していないため）