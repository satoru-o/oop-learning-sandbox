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
│   ├── src/                 # 実装
│   │   ├── errors.py / models.py / state.py / rules.py
│   │   ├── late_fee.py                    # 延滞料ルール（Strategy）
│   │   ├── serialization.py / repository.py  # 保存・読み込み（外界との境界）
│   │   └── library.py
│   └── tests/               # pytest
├── 05_vending_machine_with_tdd/     # TDD演習（自動販売機・TypeScript）
│   ├── src/                 # 実装（Product / Slot / CoinBox / 支払い方法 / SalesLedger / VendingMachine）
│   └── tests/               # vitest
├── 06_meeting_room_contracts/       # 契約による設計演習（会議室予約・Pythonのみ）
│   ├── src/                 # 実装（TimeSlot / Position / User / Room / ExecutiveRoom / Reservation / RoomCalendar / CalendarRepository）
│   └── tests/               # pytest
├── 07_meeting_room_functional/      # 06を関数型で作り直す演習（不変データ + 純粋関数 + Result・Pythonのみ）
│   ├── src/                 # 実装（Slot / Room / Access / Booking / Schedule / ScheduleRepository / use_cases / Result）
│   └── tests/               # pytest
├── 08_meeting_room_data_oriented/   # 06・07をデータ指向プログラミングで作り直す演習（dict/list + JSON Schema・Pythonのみ）
│   ├── src/                 # 実装（schemas / validate / slots / rooms / schedules / schedule_store）
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

### TypeScript のテスト（`vitest`）

```bash
npm run test:ts
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

### Step 5: TDDで育てる (`05_vending_machine_with_tdd/`)

* **お題: 自動販売機（TypeScript + vitest）**
* テストを先に書き、Red → Green → Refactor の小さな歩幅で設計を固める。
* 釣り銭の払い出し（`CoinBox`）、支払い方法の差し替え（現金 / ICカード）、売上集計（`SalesLedger`）まで実装する。
* 詳細は `05_vending_machine_with_tdd/README.md` を参照。

### Step 6: 契約で守る (`06_meeting_room_contracts/`)

* **お題: 会議室の予約（Python のみ）**
* 事前条件・事後条件・不変条件を「どのクラスが誰に約束するか」として設計し、`assert` から `icontract` へ置き換える。
* 役員用会議室（`ExecutiveRoom`）を継承で作り、契約を破って Red にしてから直すことで、LSP（置換原則）を体感する。
* 詳細は `06_meeting_room_contracts/README.md` と `DESIGN.md` を参照。

### Step 7: 関数型で作り直す (`07_meeting_room_functional/`)

* **お題: 06と同じ会議室の予約（Python のみ）**
* 不変データ + 純粋関数 + `Result` 型で、同じ4要求を作り直す。契約違反は例外ではなくエラー値として返す。
* 役員室は継承をやめ、利用条件（`Access`）をデータにする。LSP の問題が構造ごと消えることを確かめる。
* 詳細は `07_meeting_room_functional/README.md` と `DESIGN.md` を参照。

### Step 8: データ指向で作り直す (`08_meeting_room_data_oriented/`)

* **お題: 06・07と同じ会議室の予約（Python のみ）**
* データ指向プログラミング（DOP）の4原則（コードとデータを分ける／汎用のデータ構造／不変／スキーマを分ける）で作り直す。
* クラスを作らず `dict` / `list` だけで表し、形は JSON Schema（`jsonschema`）で別に定義して境界で検証する。
* 保存が楽になる一方、補完・型検査・不変性の保証が弱くなることを、06・07と並べて確かめる。
* 詳細は `08_meeting_room_data_oriented/README.md` と `DESIGN.md` を参照。

---

## 💡 Python vs TypeScript 比較のポイント

| 観点 | Python | TypeScript |
| --- | --- | --- |
| **カプセル化** | 慣習的（`_` や `__` の接頭辞） | 言語機能としての `private` / `protected` |
| **インターフェース** | 多重継承や `abc.ABC` を利用 | `interface` による構造的型付け (Structural Typing) |
| **ポリモーフィズム** | ダックタイピング（動的） | 明示的な型・インターフェース適合（静的） |
