---
title: "【保存版】ClaudeとNotionエージェントでX運用を全自動化する方法"
source: "https://newspicks.com/news/16267662/body/?ref=user_1159744"
author:
  - "[[名古屋 彩美]]"
published: 2026-03-19
created: 2026-08-06
description: "AIテーマのPodcastエピソードの記事版です！ジェネトピ(Generative AI Topic)は、明日から試したくなるリアルなAI活用秘話を、雑談感覚でゆるく学べるPodcastです！SpotifyYoutubeApple Podcastエピソードの内容を記事にしてお送ります。文字で見る方が好きなかた、時間がない方にもおすすめです！X運用、全部AIに任せたいと思いませんか？SNSの運用を続けるのは、思った以上に大変ですよね。「何を投稿しようか」と毎日考えて、作って、反応を見て改善して…というPDCAを手動で回すのはなかなか骨が折れます。今回は、Xの運用をAIで全自動化した取り組みを紹介します。ネタ出しから投稿文の作成、さらには動画編集までを包括した仕組みです。"
tags:
  - "clippings"
---
INDEX

 [![生成AI最前線「IKIGAI lab.」のサムネイル画像](https://contents.newspicks.com/topics/231/images/icon-square?updatedAt=20231116055445) ![名古屋 彩美](https://contents.newspicks.com/users/158745/cover)](https://newspicks.com/topics/ikigai-meets-ai/?ref=news-body_16267662)

[生成AI最前線「IKIGAI lab.」名古屋 彩美](https://newspicks.com/topics/ikigai-meets-ai/?ref=news-body_16267662)

AIテーマのPodcastエピソードの記事版です！

ジェネトピ(Generative AI Topic)は、明日から試したくなるリアルなAI活用秘話を、雑談感覚でゆるく学べるPodcastです！

[**Spotify**](https://spotifycreators-web.app.link/e/1kJ78q0AB1b)

[**Youtube**](https://spotifycreators-web.app.link/e/1kJ78q0AB1b)

[**Apple Podcast**](https://podcasts.apple.com/jp/podcast/%E7%94%9F%E3%81%8D%E3%81%A6%E3%82%8B%E3%81%A0%E3%81%91%E3%81%A7-sns%E6%8A%95%E7%A8%BF%E3%81%8C%E5%AE%8C%E6%88%90%E3%81%99%E3%82%8B%E4%BB%95%E7%B5%84%E3%81%BF%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%9F/id1795834993?i=1000755954405)

エピソードの内容を記事にしてお送ります。

文字で見る方が好きなかた、時間がない方にもおすすめです！

## X運用、全部AIに任せたいと思いませんか？

SNSの運用を続けるのは、思った以上に大変ですよね。

「何を投稿しようか」と毎日考えて、作って、反応を見て改善して…というPDCAを手動で回すのはなかなか骨が折れます。

今回は、Xの運用をAIで全自動化した取り組みを紹介します。ネタ出しから投稿文の作成、さらには動画編集までを包括した仕組みです。

## 自動化した3つのポイント

今回作った自動化の全体像は大きく3つです。

1. **ネタが自動で作られる** 仕組み
2. **投稿内容が自動で作られ、動画も自動編集** される仕組み
3. 投稿が自動で改善されるPDCAのCheckとActionの仕組み（次回紹介）

X運用の全自動化の詳しい内容は、エピソード本編でチェック！

**動画** で見るなら → [こちら](https://youtu.be/GqItwauy7j8)

**音声** で聴くなら → [こちら](https://spotifycreators-web.app.link/e/1kJ78q0AB1b)

**記事** で読むなら → [こちら](https://note.com/genai_topic/n/n4b1b1d925a5b?sub_rt=share_pb)

## ネタ出しを自動化する2つの方法

### 方法①：日記・議事録からネタを自動生成する

Notionのカスタムエージェントを使い、前日の日記や議事録からAI活用のノウハウを抽出し、X投稿のネタとしてSlackに毎朝送信してくれます。

![](https://contents.newspicks.com/topics/231/posts/280/images/20260317050856153_93Ik1WFS.jpg?width=1200)

Slackに届く通知

![](https://contents.newspicks.com/topics/231/posts/280/images/20260317050903719_Q5kFCEVa.jpg?width=1200)

Notionデータベースに投稿案が入る

そのネタが自分の実体験をベースにしているため、AIが考えたネタとは違い、リアリティのある投稿が生まれます。日々の振り返りにもなるというメリットもあります。

### 方法②：AIで作業しながら、その場でネタを作る

Claudeの「スキル」機能を使い、AIで何か作業をしていて「これいいな」と思ったら、その場でX投稿を作ってもらう方法です。

たとえば、Claudeで自動化フローを作っていて「これは便利だ」と感じたら、チャット上で「作ったものを紹介するX投稿を作って」と指示するだけです。

作られた投稿文はコネクター機能でNotionに自動保存されます。

![](https://contents.newspicks.com/topics/231/posts/280/images/20260317050928080_53lxNA2R.png?width=1200)

## 動画編集も自動化

録画した動画のパスをClaude Codeに渡すだけで、動画の内容を読み取って自動編集してくれます。

画面操作やキャプチャの録画は自分で行いますが、録画した動画のパスをチャットに貼り付けて「この動画のX投稿を作って」「動画編集してください」と指示するだけで、動画の内容を読み取って編集してくれます。

![](https://contents.newspicks.com/topics/231/posts/280/images/20260317051030840_hAdB2pWN.png?width=1200)

こちらも先ほどのスキル機能を使っており、動画編集スキルとして作成しておくことで、毎回同じ品質の編集が自動で行われます。

## X運用以外にも応用できる

この仕組みはSNS運用以外の業務にも応用できます。

コンテンツ企画やアイデア出し、会議のアクション管理など、「AIが見られる状態のデータを貯めておく」ことさえできれば、無限にアウトプットを生み出す可能性があります。

もし今回の内容が少しでも面白いと思っていただけたら、ぜひチャンネル登録や、Spotifyのフォローをお願いします！

**Spotify**[生きてるだけで、SNS投稿が完成する仕組みを作ってみた by ジェネトピ(Generative AI Topic)](https://spotifycreators-web.app.link/e/1kJ78q0AB1b)

[

X運用を例に、ネタ出し〜投稿作成〜動画編集までAIで全自動化した仕組みを公開！日記や議事録から勝手にネタが生まれる仕組み、Claudeのスキルを使ったX投稿作成、Claude Codeによる動画編集自動化まで。SNS運用以外の業務にも応用できる構造の話です。📌 目次0:00 AI使ってPDCAを全自動化したい1:32 SNS運用のPDCAを自動化する方法2:04 AIで自動化する前はどうやってた？3:31 ①自動で投稿ネタが作られる仕組みを作成8:03 ②Claude codeでX投稿が作成されるスキル11:01. ③投稿用の動画素材の編集も自動化13:27 （次回）PDCAのCとAをAIで自動化しよう15:13 SNS投稿以外にも応用できる！❤️エピソードに登場したAIツール❤️・Notion AI カスタムエージェント・Claude（スキル機能・コネクタ機能）・Claude Code🔷X（Twitter）　ジェネトピ公式：https://x.com/genai\_topic　あやみ：https://x.com/ayami\_marketing　かずま：https://x.com/books\_kazuma🔷Note：https://note.com/genai\_topic🔷Youtube：https://www.youtube.com/@genAI-topic🔷Spotify：https://open.spotify.com/show/6b6Zus539MibWj04OYuiTm🔷Apple Podcast：https://podcasts.apple.com/us/podcast/ジェネトピ-generative-ai-topic/id1795834993

creators.spotify.com

![](https://d3t3ozftmdmh3i.cloudfront.net/staging/podcast_uploaded_nologo400/44744904/f90857027520c7c0.jpg)](https://spotifycreators-web.app.link/e/1kJ78q0AB1b)

**Youtube**

![HoverNotes Icon](chrome-extension://fhdmbhgpabjkadpaafomaabbdckofphm/assets/icons/hover-notes-icon-white.svg)

HoverNotes Icon

Video Note ×

![](https://www.youtube.com/watch?v=GqItwauy7j8)

**Apple Podcast**[生きてるだけで、SNS投稿が完成する仕組みを作ってみた](https://podcasts.apple.com/jp/podcast/%E7%94%9F%E3%81%8D%E3%81%A6%E3%82%8B%E3%81%A0%E3%81%91%E3%81%A7-sns%E6%8A%95%E7%A8%BF%E3%81%8C%E5%AE%8C%E6%88%90%E3%81%99%E3%82%8B%E4%BB%95%E7%B5%84%E3%81%BF%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%9F/id1795834993?i=1000755954405)

[

ポッドキャストのエピソード · ジェネトピ(Generative AI Topic) · 3月18日 · 16分

podcasts.apple.com

![](https://is1-ssl.mzstatic.com/image/thumb/Podcasts211/v4/ba/5f/c3/ba5fc3c8-b3b0-218f-500a-eed65e8a2a2b/mza_5394956203227868437.jpg/1200x1200bf-60.jpg)](https://podcasts.apple.com/jp/podcast/%E7%94%9F%E3%81%8D%E3%81%A6%E3%82%8B%E3%81%A0%E3%81%91%E3%81%A7-sns%E6%8A%95%E7%A8%BF%E3%81%8C%E5%AE%8C%E6%88%90%E3%81%99%E3%82%8B%E4%BB%95%E7%B5%84%E3%81%BF%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%9F/id1795834993?i=1000755954405)

通勤時間や休憩時間など、スキマ時間にご覧いただけたら嬉しいです。それでは、次回のポッドキャストでお会いしましょう！

---

いいねして著者を応援してみませんか

※本記事はNewsPicksによって制作されたものではなく、内容の一切の責任はトピックスの発信者であるオーナーが負っています。内容に誤りや不適切な表現がある場合は、 [報告フォーム](https://newspicks.com/report/topics/231/280/) からご報告ください。

---

トピックスをフォローして通知を受け取ろう

![樋口 真章のアイコン](https://contents.newspicks.com/users/7933955/cover)

![今井 昴のアイコン](https://contents.newspicks.com/users/849358/cover)

![神崎 裕介のアイコン](https://contents.newspicks.com/users/6935096/cover)

![岩瀬 俊のアイコン](https://contents.newspicks.com/users/4100261/cover)

樋口 真章さん、他7207人がフォローしています

---

![アプリをダウンロード](https://newspicks.com/resources/images/banner-app-download.png)

NewsPicks トピックス 3つの特徴

気になるトピックスが、きっと見つかる経営・科学・テクノロジーから、アート・サウナ・世界情勢まで、バラエティに富んだラインナップ

他では得られない独自の知見分野や業界の専門家であるトピックスオーナー独自の知見が読めるのは、NewsPicksトピックスだけ

交流から生まれる新たな価値トピックスオーナーとフォロワーによる双方向コミュニケーションから新たなアイデアやインスピレーションが生まれることも

## このトピックスについて

---

 [![生成AI最前線「IKIGAI lab.」のサムネイル画像](https://contents.newspicks.com/topics/231/images/icon-square?updatedAt=20231116055445) ![髙橋 和馬](https://contents.newspicks.com/users/4593210/cover)](https://newspicks.com/topics/ikigai-meets-ai/?ref=news-body_16267662)

[生成AI最前線「IKIGAI lab.」髙橋 和馬 (オーナー)](https://newspicks.com/topics/ikigai-meets-ai/?ref=news-body_16267662)

---

## このトピックスのおすすめ投稿

---

【保存版】AIツール課金を賢く減らす「サブスク節約術」

全体に公開・

72Picks

---

【実践】話すだけで稼げる？AI副業の最前線

全体に公開・

77Picks

---

【実践】Plaud × Zapierで作る商談の自動フィードバック分析

全体に公開・

40Picks

---

[

トピックストップへ

](https://newspicks.com/topics/?ref=news-body_16267662)
## Related

- [[AI活用法-記事索引]]
