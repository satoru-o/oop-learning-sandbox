# ADR（設計判断の記録）

10章で決めた設計判断を、1件1ファイルで書き溜めます。

## 書き方

- ファイル名は `NNNN-短い名前.md`（番号は通し。欠番にしない）
- 先頭に YAML のヘッダーを付ける。AI や grep がヘッダーだけで中身の要点を拾えるようにするため
- 本文は「背景 → 決定 → 検討した他の案 → 結果」の順
- 決定を覆すときは、元のファイルを消さずに `status: superseded` にし、`superseded_by` に新しい番号を書く

### ヘッダーの項目

| 項目 | 内容 |
| --- | --- |
| `id` | 通し番号（ファイル名と同じ4桁） |
| `title` | 何を決めたか（1行） |
| `status` | `proposed`（検討中） / `accepted`（採用） / `superseded`（置き換え済み） |
| `date` | 決めた日（YYYY-MM-DD） |
| `layer` | どの層の判断か（`domain` / `usecases` / `adapters` / `main` / `test` / `all`） |
| `decision` | 決定の要約（1行）。本文を読まずに判断できるように書く |
| `related` | 関係するファイルや ADR の番号 |
| `supersedes` / `superseded_by` | 置き換えの関係（なければ空） |

## 一覧

| id | title | status |
| --- | --- | --- |
| [0001](0001-value-object-field-name.md) | 値オブジェクトの中身は `value` で取り出す | accepted |
| [0002](0002-value-object-as-frozen-dataclass.md) | 値オブジェクトは frozen dataclass で作る | accepted |
