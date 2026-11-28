---
title: 開発を始める前の打ち合わせのやり方
date: 2026-11-28
topic: process
summary: "アジャイル開発には、作り始める前に全体像と作り方をすり合わせる方法がある。話し合う範囲の大きさごとに、Inception Deck・Story Mapping・Planning Game・Example Mapping・Test List がある。作る順番には outside-in と Walking Skeleton がある"
related:
  - TICKETS.md
  - DESIGN.md
---

# 開発を始める前の打ち合わせのやり方

## 0. なぜ調べたか

10章の T1 では、保存先 `InMemoryUrlRepository` を単独で作った。
T2 で `ShortenUrl` に保存先を渡す段階になって、初めて「`ShortenUrl` が `execute` の中で `save` を呼ぶから保存先が要る」とわかった。
T1 を作った時点では、だれが `InMemoryUrlRepository` を使うのかが見えていなかった。

そこで、アジャイル開発や XP に、作り始める前に全体像と作り方をすり合わせる方法があるかを調べた。
方法は、話し合う範囲の大きさごとにいくつもあった。以下、大きい範囲から順に並べる。

## 1. プロジェクトを始める前：Inception Deck

ThoughtWorks で生まれ、Jonathan Rasmusson が『アジャイルサムライ』で紹介した方法である。
プロジェクトを始める前に関係者を集め、10個の質問に答える。

質問の例：

- なぜこれを作るのか
- やらないことは何か
- 一番のリスクは何か
- どれくらいの大きさか

XP や Scrum には、プロジェクトの立ち上げについての決まりがない。Inception Deck はそこを補うために作られた。

## 2. 機能全体を見渡す：User Story Mapping

Jeff Patton の方法である。

1. 利用者がする操作を、左から右へ時間の順に付箋で並べる。短縮URLなら「URLを短くする」「短いコードで元のURLを開く」
2. それぞれの操作の下に、細かい作業を縦に並べる

チケットを1列に並べるだけだと、全体の中でどこを作っているのかが見えなくなりやすい。Story Mapping はそれを防ぐ。

この中に **Walking Skeleton** という考え方が出てくる。もとは Alistair Cockburn の言葉である。
Walking Skeleton は、入口から出口まで一通り動く、いちばん小さいシステムのことをいう。

## 3. 1回の反復を始める前：XP の Planning Game／Scrum の Sprint Planning

### XP の Planning Game

反復（だいたい1週間）を始めるたびに、半日ほど打ち合わせる。

1. 顧客と開発者で、この反復で作るストーリーを選ぶ
2. 開発者が、選んだストーリーをプログラミングの作業（タスク）に分ける

タスクへの分け方を考えること自体が、設計の作業だとされている。
どう作るか、ほかのストーリーと共通にできる作業はないかを、ここで考える。

### Scrum の Sprint Planning

2020年版の Scrum Guide では、次の3つの話題を話し合う。

- **Why**：このスプリントは何のためにやるのか
- **What**：何を作るのか
- **How**：どうやって作るのか

## 4. 1つのストーリーに取りかかる前：Three Amigos と Example Mapping

コードを書く前に、プロダクトオーナー・開発者・テスターの3つの立場の人で話し合う。これを **Three Amigos** と呼ぶ。

この話し合いを30分ほどで進める方法が、Matt Wynne の **Example Mapping** である。4色のカードを使う。

| 色 | 書くもの | 短縮URLでの例 |
| --- | --- | --- |
| 黄 | ストーリー | URL を渡すと短いコードを返す |
| 青 | ルール | http か https しか受け付けない |
| 緑 | 具体例 | `ftp://example.com` を渡すとエラーになる |
| 赤 | まだ答えが出ていない質問 | 存在しないコードのときは例外にするか、`None` を返すか |

全員が「これで作り始められる」と合意したら終わる。

## 5. TDD を始める前：Canon TDD の Test List

Kent Beck が2023年に書いた記事「Canon TDD」による。
TDD はよく Red → Green → Refactor の3つの手順で説明される。Beck 本人は、最初に Test List を作る手順を入れて、5つの手順だとしている。

1. これから作る振る舞いについて、確かめたいことを全部リストに書き出す
2. リストから1つだけ選び、動くテストにする
3. そのテストと、それまでのテストが全部通るようにコードを変える
4. 必要ならリファクタリングする
5. リストが空になるまで 2 に戻る

## 6. 作る順番：outside-in TDD

Steve Freeman と Nat Pryce の『実践テスト駆動開発』（原題 *Growing Object-Oriented Software, Guided by Tests*）で紹介されている進め方である。
最初に Walking Skeleton を作り、そのあとは外側から内側へ向かってテストを書いていく。

10章の T1・T2 を outside-in の順番に並べ直すと、次のようになる。

1. `ShortenUrl` のテストを書く。テストの中で、保存先を `ShortenUrl` の引数として渡す
2. そのテストを通すのに保存先が要るので、ここで初めて `InMemoryUrlRepository` を作る

この順番なら、`InMemoryUrlRepository` を作る時点で、`ShortenUrl` の `execute` が `save` を呼ぶから必要になる、とわかっている。

反対に、内側の部品から作っていく進め方を inside-out という。T1 は inside-out の順番だった。

## 7. このリポジトリでやること

1人での学習なので、全部はやらない。次の章から、章の最初に次の3つをやる。

1. **Story Map の簡易版**：利用者の操作を並べる。それぞれについて、入口（CLI など）からユースケースを通って保存先まで届く流れを、1本の図に描く
2. **Walking Skeleton を最初のチケットにする**：中身はほとんどなくてよい。入口からの入力がユースケースを通って保存先まで届くところを、最初に作る
3. **チケットごとに Test List と Example Mapping の簡易版を書く**：テストを書き始める前に、確かめることと、まだ決めていないことを箇条書きにする

## 出典

- [Extreme programming practices（Wikipedia）](https://en.wikipedia.org/wiki/Extreme_programming_practices)
- [Extreme Programming Pocket Guide, Ch.8 Iteration Planning（O'Reilly）](https://www.oreilly.com/library/view/extreme-programming-pocket/9781449399849/ch08.html)
- [Why, What, How: Sprint Planning（Scrum.org）](https://www.scrum.org/resources/blog/why-what-how-sprint-planning)
- [The 2020 Scrum Guide](https://www.scrumguides.org/scrum-guide.html)
- [Introducing Example Mapping（Cucumber）](https://cucumber.io/blog/example-mapping-introduction)
- [Example Mapping: steering the conversation（Xebia）](https://xebia.com/blog/example-mapping-steering-the-conversation/)
- [User Story Mapping, Ch.1（O'Reilly）](https://www.oreilly.com/library/view/user-story-mapping/9781491904893/ch01.html)
- [Why Map User Stories（Jeff Patton & Associates）](https://jpattonassociates.com/yow-talk-user-story-mapping/)
- [The Inception Deck in a Nutshell（The Agile Samurai, O'Reilly）](https://www.oreilly.com/library/view/the-agile-samurai/9781680500066/f_0028.html)
- [Canon TDD（Kent Beck）](https://newsletter.kentbeck.com/p/canon-tdd)
- [GOOS Chapter 10. The Walking Skeleton（O'Reilly）](https://www.oreilly.com/library/view/growing-object-oriented-software/9780321574442/ch10.html)
- [TDD - From the Inside Out or the Outside In?（8th Light）](https://8thlight.com/insights/tdd-from-the-inside-out-or-the-outside-in)
