# チケット

1チケットにつき、Red → Green →（Refactor）→ コミットを1回やります。
後ろのほうのチケットは、進めながら割ったり足したりします。

| # | チケット | 層 | 種類 | 状態 |
| --- | --- | --- | --- | --- |
| T0 | 登場人物と依存の向きの地図を `DESIGN.md` に書く | all | 設計 | 済 |
| T1 | `InMemoryUrlRepository` に書き留めたコードで、URL を取り出せる | adapters | テスト | 済 |
| T2 | `ShortenUrl` が、作ったコードと URL を保存先に書き留める | usecases | テスト | 済 |
| T3 | 保存先の約束ごと `UrlRepository`（Protocol）を usecases に置く | usecases | Refactor | 済 |
| T4 | `ResolveUrl` にコードを渡すと、元の URL を返す（要求2） | usecases | テスト | 未着手 |
| T5 | 存在しないコードを `ResolveUrl` に渡すとエラーになる | usecases | テスト | 未着手 |
| T6 | `ShortenUrl` に不正な URL を渡すとエラーになる（要求4） | usecases | テスト | 未着手 |
| T7 | 同じ URL を2回短縮すると、同じコードを返す（要求3） | usecases | テスト | 未着手 |
| T8 | 本物のコード生成器（ランダム）を作る | adapters | テスト | 未着手 |
| T9 | CLI で `shorten` / `resolve` が動き、組み立てを main の1か所に置く | adapters / main | テスト | 未着手 |
| T10 | 保存先を JSON ファイル版に替えても、usecases は変わらない | adapters | テスト | 未着手 |
| T11 | 【発展】HTTP の入口 | adapters | テスト | 未着手 |

## 済んだもの（チケットを切る前）

- `Url` は http/https とホスト名を検査し、不変で中身で比べられる（要求4の domain 側）
- `ShortenUrl` に URL を渡すと、コード生成器が作ったコードを返す（要求1。まだ保存はしない）
