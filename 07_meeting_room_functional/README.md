# 07_meeting_room_functional: 会議室予約（関数型で作り直す）

## 🎯 この章のねらい
06 と**同じ4要求**を、**不変データ + 純粋関数 + Result 型**で作り直し、OOP との違いを並べて見ます。

- 言語は **Python**、テストは **pytest**（06 と同条件）
- `icontract` と例外は使わない。失敗は `Err` という値で返す
- 状態は書き換えない。`reserve` / `cancel` は新しい `Schedule` を返す

## 📖 要求（06 と同じ）

| # | 要求 |
| --- | --- |
| 1 | ユーザーは会議室と時間を指定して、枠を予約できる |
| 2 | 先客がいたら、その枠は取れない |
| 3 | ユーザーは予約を解除して、枠を返却できる |
| 4 | 役員用会議室は、役員以上だけが使える |

対比表・設計の考えどころは [DESIGN.md](DESIGN.md) を見てください。

## 🗄️ 予約情報の置き場所
`ScheduleRepository`（`load` / `save`）を端に置き、`use_cases.py` が「読む → 純粋関数で決める → 書く」をつなぎます。`reserve` / `cancel` は純粋関数のままです（[DESIGN.md](DESIGN.md) §5）。

## 🚀 実行方法
```bash
uv run pytest 07_meeting_room_functional
```
