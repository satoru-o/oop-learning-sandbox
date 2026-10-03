# OOP Learning Sandbox (Python & TypeScript)

WSL環境を汚さずに Dev Container 上で Python と TypeScript を使って、オブジェクト指向プログラミング（OOP）を基礎から学び、比較・実験するための環境です。

---

## 🛠️ 環境構築

### 1. 前提条件
- WSL2 (Ubuntu 等)
- Docker Desktop (WSL連携を有効化)
- VS Code (拡張機能 `Dev Containers` がインストール済みであること)

### 2. コンテナの起動
1. VS Code でこのリポジトリを開きます。
2. コマンドパレット (`Ctrl + Shift + P`) を開き、**`Dev Containers: Reopen in Container`** を選択します。
3. ビルドが完了すれば、Python と TypeScript (`ts-node`) がセットアップされた環境が立ち上がります。

### 3. 初回セットアップ (TS設定ファイルの生成)
コンテナ内のターミナルで以下を実行して `tsconfig.json` を生成してください（初回のみ）。

```bash
npx tsc --init
```

---

## 📁 ディレクトリ構成

直下にテーマごとのサブディレクトリを作成し、書き散らしながら学習を進めます。

```text
.
├── .devcontainer/
│   └── devcontainer.json    # Dev Container 設定
├── package.json             # TS 用設定（自動生成）
├── tsconfig.json            # TS コンパイル設定
├── README.md
│
├── 01_basics/               # クラス・インスタンス・カプセル化
│   ├── account.py
│   └── account.ts
├── 02_inheritance/          # 継承・ポリモーフィズム
│   ├── rpg_battle.py
│   └── rpg_battle.ts
├── 03_design_patterns/      # デザインパターン（Strategy, Factory等）
│   ├── payment.py
│   └── payment.ts
└── sandbox/                 # 思いつきで自由に試す場所
```

---

## 🚀 コードの実行方法

コンテナ内のターミナルで各ファイルを直接実行します。

### Python

```bash
python 01_basics/account.py
```

### TypeScript (`ts-node` で直接実行)

```bash
npx ts-node 01_basics/account.ts
```

---

## 🎯 学習ロードマップ & お題案

### Step 1: クラスの基本とカプセル化 (`01_basics/`)

* **お題: 銀行口座 (`account.py` / `account.ts`)**
* 残高（`balance`）を外部から直接変更できないよう隠蔽する。
* `deposit(amount)` (預金) と `withdraw(amount)` (引き出し) メソッド経由でのみ更新を許可する。

### Step 2: 継承とポリモーフィズム (`02_inheritance/`)

* **お題: 簡易RPGの戦闘システム (`rpg_battle.py` / `rpg_battle.ts`)**
* 親クラス/抽象クラス `Character` を作成。
* 継承して `Hero`, `Wizard`, `Monster` を定義。
* 各クラスで `attack(target)` メソッドをオーバーライドし、固有の攻撃処理を書く。

### Step 3: 設計パターンにチャレンジ (`03_design_patterns/`)

* **お題: 柔軟な決済処理 (Strategyパターン)**
* `PaymentStrategy` インターフェースを定義。
* `CreditCardPayment`, `PayPayPayment` などの実装を動的に切り替えられる構造を作る。

---

## 💡 Python vs TypeScript 比較のポイント

| 観点 | Python | TypeScript |
| --- | --- | --- |
| **カプセル化** | 慣習的（`_` や `__` の接頭辞） | 言語機能としての `private` / `protected` |
| **インターフェース** | 多重継承や `abc.ABC` を利用 | `interface` による構造的型付け (Structural Typing) |
| **ポリモーフィズム** | ダックタイピング（動的） | 明示的な型・インターフェース適合（静的） |
