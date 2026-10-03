# 02_inheritance: マルチチャネル通知システム（継承とポリモーフィズム）

## 🎯 この章で学ぶこと
- **抽象クラス / インターフェース**: 共通の「契約（メソッドのシグネチャ）」を強制する
- **継承（Inheritance）**: 共通処理（ヘッダー付与やログ記録）を親クラスに集約する
- **ポリモーフィズム（Polymorphism）**: 呼び出し側が具象クラスを意識せず、同じメソッド名で異なる挙動を実行させる

---

## 🏗️ クラス設計 & 責務一覧

メッセージを様々なチャネル（Email, Slack, SMS）に送信する通知システムを構築します。

```text
【高レイヤー】
NotificationService ──依存──> BaseNotification (抽象)
                                      ▲
                                      │ 継承
                         ┌────────────┼────────────┐
                         │            │            │
                      Email        Slack          SMS (具象)
```

### 1. `BaseNotification` (抽象基底クラス)

すべての通知チャネルの共通親クラス。

* **共通プロパティ**:
    * `sender_id`: 送信者識別子 (readonly)

* **共通メソッド (具象)**:
    * `format_message(body)`: メッセージの前後共通フォーマット（タイムスタンプ付与など）

* **抽象メソッド (Subclassで実装を強制)**:
    * `send(recipient, body)`: 各チャネル固有の送信ロジック（成功/失敗を boolean で返す）

### 2. 派生クラス群

* **`EmailNotification`**
    * プロパティ: `smtp_server`
    * `send()`: 件名（Subject）の生成とメール形式のバリデーションを行って送信


* **`SlackNotification`**
    * プロパティ: `webhook_url`
    * `send()`: Slack記法への変換を行って送信


* **`SmsNotification`**
    * プロパティ: `phone_number_provider`
    * `send()`: 文字数制限（例: 140文字以内）のチェックを行って送信



### 3. `NotificationService` (ポリモーフィズムの受信側)

通知オブジェクトのリストを保持し、一括送信を担当するサービス。

* **メソッド**:
    * `add_channel(notification)`: 通知チャネルを追加
    * `send_all(recipient, message)`: 保持している全チャネルに対して `send()` をループ実行

---

## 🔍 言語ごとの注目ポイント

### 🐍 Python (`notification.py`)

* `abc` モジュールの `ABC` クラスと `@abstractmethod` デコレータを使用して抽象クラスを定義する。
* 抽象クラスをそのままインスタンス化しようとすると `TypeError` になる挙動を確認する。

### 📘 TypeScript (`notification.ts`)

* `abstract class` と `abstract` メソッドキーワードを使用する。
* インターフェース（`interface INotifiable`）との使い分け（共通コードを継承したいなら `abstract class`）を意識する。
