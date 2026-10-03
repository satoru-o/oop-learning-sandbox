// 01_basics/account.ts

export class BankAccount {
    // コンストラクタの引数に private / readonly をつけると、
    // フィールドの宣言と初期化を同時に行うことができる
    constructor(
        public readonly owner: string,
        private _balance: number = 0
    ) {
        if (_balance < 0) {
            this._balance = 0;
        }
    }

    // ゲッター (Python の @property に相当)
    get balance(): number {
        return this._balance
    }

    /**
     * 預金する
     */
    public deposit(amount: number): boolean {
        if (amount <= 0) {
            console.log(`[${this.owner}] 預金失敗: 0円よりも大きな金額を指定してください (${amount}円)`);
            return false;
        }

        this._balance += amount;
        console.log(`[${this.owner}] 預金成功: ${amount}円 (現在の残高: ${this._balance}円)`);
        return true;
    }

    /**
     * 引き出す
     */
    public withdraw(amount: number): boolean {
        if (amount <= 0) {
            console.log(`[${this.owner}] 引き出し失敗: 0円以上の金額を指定してください (${amount}円)`);
            return false;
        }

        if (amount > this._balance) {
            console.log(`[${this.owner}] 引き出し失敗: 残高不足です (現在の残高: ${this._balance}円)`);
            return false;
        }

        this._balance -= amount;
        console.log(`[${this.owner}] 引き出し成功: ${amount}円 (現在の残高: ${this._balance}円)`);
        return true;
    }
}

// 動作確認用メイン処理
function main() {
  console.log("--- 1. アカウントの作成 ---");
  const account = new BankAccount("Alice", 1000);
  console.log(`名義人: ${account.owner}`);
  console.log(`初期残高: ${account.balance}円`);

  console.log("\n--- 2. 正常な取引 ---");
  account.deposit(500);
  account.withdraw(300);

  console.log("\n--- 3. 不正な操作の検証 ---");
  account.deposit(-100);  // 失敗するはず
  account.withdraw(2000); // 残高不足で失敗するはず

  console.log("\n--- 4. カプセル化の確認 ---");
  // TSの静的チェックにより、以下のコードはコンパイルエラー（赤波線）になります：
  // account.balance = 999999; // Error: Cannot assign to 'balance' because it is a read-only property.
  // account.owner = "Bob";     // Error: Cannot assign to 'owner' because it is a read-only property.
  // account._balance = 999999; // Error: Property '_balance' is private and only accessible within class 'BankAccount'.
}

main();