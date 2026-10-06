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
├── pyproject.toml           # Python 用設定（uv / pytest）
├── package.json             # TS 用設定（自動生成）
├── tsconfig.json            # TS コンパイル設定
├── README.md
│
├── 01_basics/               # カプセル化・SRP・コンポジション（銀行口座）
│   ├── account.py
│   └── account.ts
├── 02_inheritance/          # 継承・ポリモーフィズム（通知システム）
│   ├── notification.py
│   └── notification.ts
├── 03_design_patterns/      # デザインパターン（Strategy）
│   ├── pricing.py
│   └── pricing.ts
├── 04_mini_library_system/          # 総合演習（図書館の貸出管理・Pythonのみ）
│   ├── errors.py / models.py / state.py / rules.py
│   ├── late_fee.py                        # 延滞料ルール（Strategy）
│   ├── serialization.py / repository.py   # 保存・読み込み（外界との境界）
│   ├── library.py
│   └── tests/               # pytest
└── sandbox/                 # 思いつきで自由に試す場所
```

---

## 🚀 コードの実行方法

コンテナ内のターミナルで各ファイルを直接実行します。

### Python

```bash
python 01_basics/account.py
```

### Python のテスト（`uv` + `pytest`）

```bash
uv run pytest
```

### Python のリント・整形（`ruff`）

```bash
uv run ruff check .     # リント
uv run ruff format .    # 整形
```

### TypeScript (`ts-node` で直接実行)

```bash
npx ts-node 01_basics/account.ts
```

---

## 🎯 学習ロードマップ & お題案

### Step 1: カプセル化・単一責任・コンポジション (`01_basics/`)

* **お題: 銀行口座と取引履歴 (`account.py` / `account.ts`)**
* `Transaction`（値オブジェクト）、`TransactionHistory`（ファーストクラス・コレクション）、`BankAccount`（ドメインエンティティ）に責務を分割する。
* 残高（`balance`）は外部から直接変更できないよう隠蔽し、`deposit(amount)` / `withdraw(amount)` 経由でのみ更新する。
* クラス内では `print` / `console.log` を使わず、不正な金額や残高不足はカスタム例外（`InsufficientBalanceError` など）で表現する。

### Step 2: 継承とポリモーフィズム (`02_inheritance/`)

* **お題: マルチチャネル通知システム (`notification.py` / `notification.ts`)**
* 抽象基底クラス `BaseNotification` を作成し、共通処理（`format_message`）を集約、`send(recipient, body)` を抽象メソッドにする。
* 継承して `EmailNotification`, `SlackNotification`, `SmsNotification` を定義し、チャネル固有の送信ロジックを実装する。
* `NotificationService` が具象クラスを意識せず、全チャネルへ一括送信する。

### Step 3: 設計パターンにチャレンジ (`03_design_patterns/`)

* **お題: 価格計算エンジン（Strategy パターン）**
* `DiscountStrategy` インターフェースを定義。
* `RegularPricing`, `FixedDiscount`, `PercentageDiscount`, `BulkDiscount` を実装し、`ShoppingCart` が戦略を動的に切り替えられる構造を作る。

### Step 4: 総合演習・ミニシステムを設計する (`04_mini_library_system/`)

* **お題: 図書館の貸出管理システム（Python のみ）**
* 本・会員・貸出を設計し、会員種別ごとの貸出上限・期間・延滞料といった業務ルールを実装する。
* 責務分割・継承/Strategy の使い分け・カスタム例外など、Step 1〜3 の要素を自力で組み合わせる。
* 詳細は `04_mini_library_system/README.md` を参照。

---

## 💡 Python vs TypeScript 比較のポイント

| 観点 | Python | TypeScript |
| --- | --- | --- |
| **カプセル化** | 慣習的（`_` や `__` の接頭辞） | 言語機能としての `private` / `protected` |
| **インターフェース** | 多重継承や `abc.ABC` を利用 | `interface` による構造的型付け (Structural Typing) |
| **ポリモーフィズム** | ダックタイピング（動的） | 明示的な型・インターフェース適合（静的） |
