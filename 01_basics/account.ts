// 01_basics/account.ts

// ドメイン例外の定義 ---
export class DomainError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DomainError";
  }
}

export class InsufficientBalanceError extends DomainError {
  constructor(
    public readonly requested: number,
    public readonly current: number
  ) {
    super(`残高不足です (申請: ${requested}円 / 現在の残高: ${current}円)`);
    this.name = "InsufficientBalanceError";
  }
}

export class InvalidAmountError extends DomainError {
  constructor(public readonly amount: number) {
    super(`0円より大きな金額を指定してください (${amount}円)`);
    this.name = "InvalidAmountError";
  }
}

// Transaction (値オブジェクト / イミュータブル) ---
export enum TransactionType {
  DEPOSIT = "預金",
  WITHDRAW = "引き出し",
}

export interface Transaction {
  readonly id: number;
  readonly type: TransactionType;
  readonly amount: number;
  readonly timestamp: Date;
}

// TransactionHistory (ファーストクラス・コレクション) ---
export class TransactionHistory {
  private _transactions: Transaction[] = [];
  private _nextId: number = 1;

  public add(type: TransactionType, amount: number): Transaction {
    const tx: Transaction = {
      id: this._nextId++,
      type,
      amount,
      timestamp: new Date(),
    };
    this._transactions.push(tx);
    return tx;
  }

  /**
   * 外部から push 等で直接変更されないよう ReadonlyArray を返し、
   * 配列自体も浅いコピー（[...array]）して渡す（防御的コピー）
   */
  get all(): ReadonlyArray<Transaction> {
    return [...this._transactions];
  }
}

// BankAccount (ドメインエンティティ) ---
export class BankAccount {
  private _balance: number;
  private readonly _history: TransactionHistory;

  constructor(
    public readonly owner: string,
    initialBalance: number = 0
  ) {
    if (initialBalance < 0) {
      throw new InvalidAmountError(initialBalance);
    }

    this._balance = initialBalance;
    this._history = new TransactionHistory();
  }

  get balance(): number {
    return this._balance;
  }

  get history(): TransactionHistory {
    return this._history;
  }

  public deposit(amount: number): number {
    if (amount <= 0) {
      throw new InvalidAmountError(amount);
    }

    this._balance += amount;
    this._history.add(TransactionType.DEPOSIT, amount);
    return this._balance;
  }

  public withdraw(amount: number): number {
    if (amount <= 0) {
      throw new InvalidAmountError(amount);
    }
    if (amount > this._balance) {
      throw new InsufficientBalanceError(amount, this._balance);
    }

    this._balance -= amount;
    this._history.add(TransactionType.WITHDRAW, amount);
    return this._balance;
  }
}

// =====================================================================
// 利用側 (メイン処理): ログ出力やエラーハンドリング (UIの役割) をここで行う
// =====================================================================
function main() {
  const account = new BankAccount("Alice", 1000);

  console.log("--- 1. 正常な取引 ---");
  try {
    let newBalance = account.deposit(500);
    console.log(`[${account.owner}] 預金成功! 現在の残高: ${newBalance}円`);

    newBalance = account.withdraw(300);
    console.log(`[${account.owner}] 引き出し成功! 現在の残高: ${newBalance}円`);
  } catch (error) {
    if (error instanceof DomainError) {
      console.error(`エラー発生: ${error.message}`);
    }
  }

  console.log("\n--- 2. 不正な取引と例外の捕捉 ---");
  // 不正な預金
  try {
    account.deposit(-100);
  } catch (error) {
    if (error instanceof InvalidAmountError) {
      console.error(`[失敗ログ] ${error.message}`);
    }
  }

  // 残高不足の引き出し
  try {
    account.withdraw(5000);
  } catch (error) {
    if (error instanceof InsufficientBalanceError) {
      console.error(`[失敗ログ] ${error.message}`);
    }
  }

  console.log("\n--- 3. 取引履歴の確認 ---");
  for (const tx of account.history.all) {
    const timeStr = tx.timestamp.toLocaleTimeString("ja-JP");
    console.log(` ID:${tx.id} | 時間:${timeStr} | 種別:${tx.type} | 金額:${tx.amount}円`);
  }

  console.log("\n--- 4. 防御的コピーと readonly の確認 ---");
  const historyList = account.history.all;
  // historyList.push(...) // TS Error: Property 'push' does not exist on type 'readonly Transaction[]'.
  // historyList[0].amount = 999999; // TS Error: Cannot assign to 'amount' because it is a read-only property.
  console.log(`現在の履歴件数: ${historyList.length}件 (型定義とコンパイルチェックで完全保護)`);
}

main();