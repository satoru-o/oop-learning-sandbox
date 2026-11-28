<!--
章を始めるときの打ち合わせのひな形。
章のディレクトリに BRIEFING.md としてコピーし、上から順に埋める。
1〜3節は章の最初に1回だけ書く。4節はチケットに取りかかるたびに1つずつ足す。
背景は 10_url_shortener_clean_architecture/notes/briefing-before-development.md を参照。
-->

# NN 打ち合わせ（章のテーマ）

## 1. 何を作るか

<!-- 例：長い URL を渡すと短いコードを返し、そのコードを渡すと元の URL を返す CLI -->
- 一言で：
- 入力と出力の具体例：
  - `（コマンドや呼び出し）` → `（返ってくるもの）`
  - `（コマンドや呼び出し）` → `（返ってくるもの）`
- やらないこと：

## 2. Story Map（簡易版）

利用者がする操作を左から順に並べ、それぞれが通るクラスとメソッドを書く。

<!--
例：
| | shorten | resolve |
| --- | --- | --- |
| 入口 | CLI の `shorten <URL>` | CLI の `resolve <コード>` |
| ユースケース | `ShortenUrl.execute(url)` | `ResolveUrl.execute(code)` |
| domain | `Url` で URL を検査 | （なし） |
| 部品 | `CodeGenerator.generate()`、`UrlRepository.save(code, url)` | `UrlRepository.find(code)` |
| 出力 | コードを表示 | URL を表示。なければエラー表示 |
-->

| | （操作1） | （操作2） |
| --- | --- | --- |
| 入口 | | |
| ユースケース | | |
| domain | | |
| 部品 | | |
| 出力 | | |

## 3. Walking Skeleton

最初のチケットで、入口から出力まで一通り動く1本を作る。

- 通す操作：
- 流れ：（入口）→（ユースケース）→（部品）→（出力）
- 中身を省いてよいところ：
  <!-- 例：URL の検査はまだしない。コードはいつも "abc123" を返す -->
- 確かめるテスト：
  <!-- 例：CLI に `shorten https://example.com` を渡すと、"abc123" が表示される -->

## 4. チケットごとのメモ

チケットに取りかかる前に1つ足す。テストを書くのはこのメモのあと。

### T1：（チケット名）

- 使う側：このチケットで作るクラスやメソッドを呼ぶのは、どのクラスのどのメソッドか
  <!-- 例：`ShortenUrl.execute` が `UrlRepository.save` を呼ぶ。呼ぶ側がまだないなら、先に呼ぶ側のチケットをやる -->
- 触るファイル：
- Test List：
  - [ ]
  - [ ]
- まだ決めていないこと：
  -
