# 10 設計メモ（短縮URL・クリーンアーキテクチャ）

## 設計前提
- 層は domain / usecases / adapters / main の4つ。依存は**内側へだけ**向ける
- 差し替えたい部品（保存先・コード生成器）は、**使う側の usecases** が `Protocol` で約束ごとを書く
- adapters の具象クラスは `Protocol` を継承せず、メソッドの形を合わせるだけ
- 具象クラスを作って組み合わせるのは main の1か所だけ

## 1. 登場人物

| 名前 | 層 | ファイル | 役目 | 状態 |
| --- | --- | --- | --- | --- |
| `Url` | domain | `domain.py` | 正しい URL（http/https・ホスト名あり）だけを表す値 | 済 |
| `InvalidUrlError` | domain | `domain.py` | 不正な URL を作ろうとしたときの例外 | 済 |
| `ShortenUrl` | usecases | `usecases.py` | URL を受け取り、コードを作って保存先に書き留め、コードを返す | 一部（コードを返すだけ） |
| `ResolveUrl` | usecases | `usecases.py` | コードを受け取り、保存先を見に行って元の URL を返す | 未 |
| `CodeGenerator` | usecases | `usecases.py` | コード生成器の約束ごと（Protocol） | 済 |
| `UrlRepository` | usecases | `usecases.py` | 保存先の約束ごと（Protocol）。「書き留める」と「見に行く」ができる | 未 |
| `InMemoryUrlRepository` | adapters | `adapters.py` | `dict` で「コード → URL」を覚える保存先。プログラムを終えると消える | 未 |
| `JsonFileUrlRepository` | adapters | `adapters.py` | JSON ファイルで覚える保存先。プログラムを終えても残る | 未 |
| `RandomCodeGenerator` | adapters | `adapters.py` | ランダムなコードを作る | 未 |
| CLI | adapters | 未定 | 引数を読んでユースケースを呼び、結果やエラーを表示する | 未 |
| main | main | `main.py` | 具象クラスを作り、ユースケースに渡して組み立てる | 未 |

テストでは、`CodeGenerator` の代わりに `FixedCodeGenerator`（いつも同じコードを返す）を使う。

## 2. 依存の向き

```
main ──作って渡す──▶ adapters
 │                  （InMemoryUrlRepository / RandomCodeGenerator / CLI）
 │                     │ CLI はユースケースを呼ぶ
 ▼                     ▼
usecases（ShortenUrl / ResolveUrl / UrlRepository / CodeGenerator）
 │
 ▼
domain（Url / InvalidUrlError）
```

- 矢印は「import している」。どれも内側へ向いている
- domain と usecases は adapters を import しない
- 保存先とコード生成器は、usecases の `Protocol` を import しなくても約束を満たせる

## 3. 処理の流れ

### shorten
1. CLI が引数から URL の文字列を受け取り、`ShortenUrl` に渡す
2. `ShortenUrl` が `Url` を作って検査する（不正なら `InvalidUrlError`）
3. コード生成器でコードを作る
4. 保存先に「コード → URL」を書き留める
5. コードを返し、CLI が表示する

### resolve
1. CLI が引数からコードを受け取り、`ResolveUrl` に渡す
2. `ResolveUrl` が保存先を見に行く
3. 見つかれば URL を返し、CLI が表示する。なければエラーにし、CLI がメッセージと終了コードに変える

## 4. まだ決めていないこと

- コードの型: `str` のままか、`ShortCode` という値オブジェクトにするか
- 保存先のメソッド名・引数・戻り値（T1 で決める）
- 存在しないコードの表し方: 例外か、`None` を返すか（T5）
- 要求3のために、保存先に「URL からコードを引く」操作が要るか（T7）
- ユースケースの戻り値: `str` か、専用のデータ型か（README の問4）
