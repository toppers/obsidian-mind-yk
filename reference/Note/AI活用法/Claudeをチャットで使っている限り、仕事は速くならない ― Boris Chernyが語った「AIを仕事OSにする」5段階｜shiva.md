---
title: "Claudeをチャットで使っている限り、仕事は速くならない ― Boris Chernyが語った「AIを仕事OSにする」5段階｜shiva"
source: "https://note.com/shiva_id/n/nbd8ce622392e"
author:
  - "[[shiva]]"
published: 2026-05-22
created: 2026-05-25
description: "【記事概要】  Claude Codeを作ったBoris Cherny氏が、Lenny's PodcastでClaude Codeの成長、自分の働き方、AIエージェント時代の仕事の変化を語った。Xではその内容に関連して「Claudeには多くの人が触っていない機能が40個ある」という整理も拡散されている。この記事では、単なる機能紹介ではなく、Boris氏の話を日本の業務AI活用に転用するための地図として読み解く。結論はシンプルだ。Claude活用の差は、プロンプト力ではなく、作業環境の設計力で決まる。    まず、何が起きているのか  Boris Cherny氏は、AnthropicでC"
tags:
  - "clippings"
---
**【記事概要】**

Claude Codeを作ったBoris Cherny氏が、Lenny's PodcastでClaude Codeの成長、自分の働き方、AIエージェント時代の仕事の変化を語った。Xではその内容に関連して「Claudeには多くの人が触っていない機能が40個ある」という整理も拡散されている。この記事では、単なる機能紹介ではなく、Boris氏の話を **日本の業務AI活用に転用するための地図** として読み解く。結論はシンプルだ。Claude活用の差は、プロンプト力ではなく、 **作業環境の設計力** で決まる。

---

## まず、何が起きているのか

Boris Cherny氏は、AnthropicでClaude Codeを率いる人物だ。Lenny's Podcastの公式ページでは、Claude Codeが「1年前のターミナルベースのプロトタイプ」から、ソフトウェアエンジニアリングの仕事を変える存在になったと紹介されている。

番組内で語られている数字も強い。Claude Codeは公開GitHubコミットの大きな割合をすでに占め、Boris氏自身も、日々のコード作業のほとんどをClaude Codeに任せる働き方へ移っている。さらに彼は、AIが次に向かう先を「コードを書く」だけでなく、フィードバック、バグ報告、テレメトリから修正案や実装案を考える **同僚のような存在** だと見ている。

ただ、この話を「Claude Codeすごい」で終わらせると、少し浅い。

本当に重要なのは、Boris氏がClaudeを **チャット相手として見ていない** ことだと思う。彼の話に出てくるClaudeは、質問に答える相手ではなく、道具を持ち、文脈を読み、並列で走り、ログを残し、実際の仕事を進める存在である。

つまり、こういう変化だ。

> **チャットAIを使う時代から、AIが働ける作業環境を設計する時代へ。**

---

## 図解: Claude活用は5段階で進化する

Claudeの使い方は、ざっくり5段階で見たほうがわかりやすい。

```
Level 1  Chat
  その場で質問する
  例: Custom Instructions / Memory / Conversation Style

Level 2  Workspace
  仕事ごとに文脈を持たせる
  例: Projects / Knowledge Files / CLAUDE.md / rules.md

Level 3  Agent
  道具を渡して実作業させる
  例: Claude Code / Cowork / MCP / Connectors / Chrome

Level 4  Team
  複数のClaudeを並列に走らせる
  例: Subagents / multiple sessions / Plan Mode

Level 5  Operating System
  業務プロセスに組み込む
  例: Hooks / Git / scheduled tasks / logs / evals
```

![画像](https://assets.st-note.com/img/1779437288-MVaox5TOB04mUizYFvngSPwG.jpg?width=1200)

多くの人はLevel 1で止まっている。

毎回チャット欄に事情を説明し、資料を貼り、出力形式を指定し、うまくいかなければ「もっと丁寧に」「もう少し短く」と言い直す。

これは、優秀な人に毎朝「あなたは誰で、私は何者で、今日の仕事は何か」を最初から説明しているようなものだ。

人間なら3日で嫌になる。AIも当然、非効率になる。

上級者は逆に、Claudeが働ける環境を先に作る。

---

## Level 1: Chat ― まず「毎回の自己紹介」をやめる

最初の差は、実はとても地味だ。

- 自分は何者か
- どんな仕事をしているか
- どんな出力形式が好きか
- どんなトーンで書いてほしいか
- どんな前提を毎回守ってほしいか

これを毎回チャットで説明しているなら、まずそこがロスになっている。

ClaudeにはCustom InstructionsやMemoryのような、会話をまたいで前提を持たせる仕組みがある。X側の整理では、ここを空白のまま使うことを「人を雇ったのに、役割も会社も作法も伝えていない状態」と表現していた。これはかなり本質を突いている。

AIを使う第一歩は、良い質問を考えることではない。

**AIに、自分の仕事の前提を覚えさせること** である。

---

## Level 2: Workspace ― 文脈は「貼る」ものではなく「置く」もの

次に大事なのが、仕事ごとの作業場を分けることだ。

ClaudeのProjects、Knowledge Files、Claude CodeのCLAUDE.md、補助的なrules.mdやstack.mdは、全部まとめると「AIが読む業務マニュアル」である。

たとえば、Note記事を書くなら、

- 誰に向けた記事か
- どんな文体か
- 使ってよい言葉、避ける言葉
- 過去記事とのつながり
- 太字の使い方
- 末尾に必ず入れる参考リンク

こうしたルールは、毎回チャットに貼るより、ファイルとして置いておくほうがよい。

Claude Code公式docsも、CLAUDE.mdにはプロジェクト文脈や指示を入れられる一方で、長くしすぎないことを勧めている。目安は200行未満。詳細資料はSkillsのようなオンデマンドで読める場所へ逃がす。

ここが重要だ。 **文脈は多ければ多いほど良いのではなく、必要なときに読める構造になっているほうが良い** 。

人間の仕事でも同じだ。

優秀な部下に、初日に300ページの規程集を全部暗記させる必要はない。必要な規程にすぐ辿れる棚を作ればよい。

---

## Level 3: Agent ― Claudeに「道具」を渡す

Boris氏の話で一番大きい転換点は、Claudeが単なる会話相手ではなく、 **道具を使って世界に作用する存在** になっていることだ。

Claude Codeなら、コードベースを読み、ファイルを編集し、テストを走らせる。

Coworkなら、フォルダやアプリに接続して、メール、表計算、ファイル整理、ブラウザ作業まで扱える。

MCPやConnectorsは、Claudeに外部サービスや業務データへの入口を渡す。

ここでやってはいけないのは、人間がClaudeの代わりに全部コピペしてしまうことだ。

メールを開いて本文を貼る。

カレンダーを見て予定を貼る。

PDFを1つずつ開いて抜粋を貼る。

Web検索してURLを貼る。

これでは、AIはいつまでも「机の前に座っている相談相手」のままだ。

道具を渡せば、AIは作業者になる。

> **答えをもらうAIから、仕事を任せるAIへ。**

この差は大きい。業務AI活用の本質は、プロンプト文の工夫よりも、AIが読める場所・触ってよい場所・使える道具をどう設計するかに移っている。

---

## Level 4: Team ― 1人のClaudeではなく、小さなチームにする

Boris氏は、複数のエージェントを同時に走らせる働き方にも触れている。朝起きてから複数の作業を起動し、端末だけでなくデスクトップアプリやiOSアプリでもClaudeを使う。もはや「1つのチャットで1つずつ頼む」世界ではない。

ここで効いてくるのがSubagentsだ。

Claude Code公式docsでは、Subagentsはメイン会話とは別のコンテキストで動く専門エージェントだと説明されている。探索、ログ読み、テスト、レビューのように、メイン会話に大量の情報を流し込むと邪魔になる作業を外に逃がせる。

これを仕事に置き換えると、こうなる。

- 調査係: 参考資料を読む
- 設計係: 論点を整理する
- 実装係: 具体物を作る
- レビュー係: 事故や抜け漏れを見る
- 編集係: 読みやすさを整える

人間のチームなら当たり前の分業が、AIでも当たり前になる。

「1人の万能AIに全部やらせる」より、 **小さく分けたAIチームを作る** ほうが、文脈も濁らないし、成果物も安定する。

もうひとつ大事なのが、Plan Mode的な発想だ。

いきなり作らせない。先に設計させる。問いを整理させる。リスクを出させる。そのうえで実行に入る。

人間でも、仕様が曖昧なまま手を動かすと手戻りする。AIも同じだ。

---

## Level 5: Operating System ― AIの作業を「業務プロセス」に組み込む

最後の段階は、Claudeを個人の便利ツールではなく、業務プロセスの一部にすることだ。

ここで出てくるのがHooks、Git、スケジュール、ログ、評価だ。

Hooksは、Claude Codeのライフサイクル上の特定タイミングで自動実行される仕組みだ。たとえば、ファイル編集後にフォーマッタを走らせる。危険なコマンドを止める。プロンプト送信時に追加文脈を差し込む。公式docsでは、ツール実行前後、セッション開始・終了、コンパクション前後など、かなり多くのイベントが用意されている。

ここまで来ると、Claudeは「賢いチャット」ではない。

**業務の中に差し込まれた自動化レイヤー** になる。

ただし、ここで忘れてはいけないのは検証だ。

AIに作業を任せるほど、成果物だけでなく、過程を残す必要がある。

- Gitで差分を残す
- セッション履歴を残す
- テストを走らせる
- 出力品質を評価する
- 定期タスクはログを確認する
- 危険操作はHookで止める

AI活用の成熟度は、「AIが何を作れるか」ではなく、 **AIの作業をどれだけ再現・検証できるか** で測るべきだと思う。

---

## 「40機能」の本質は、機能数ではない

Xでは、ClaudeのWebアプリ、Desktop/Cowork、Claude Code、APIまで含めて、見落とされがちな40機能が整理されていた。

Custom Instructions、Memory、Projects、Artifacts、Knowledge Files、Web Search、Cowork、Folder Access、Scheduled Tasks、Subagents、Plugins、Connectors、Claude Code、Plan Mode、CLAUDE.md、/compact、MCP、API、Structured Outputs、Evaluation Frameworks。

たしかに機能名だけ並べても圧がある。

でも本質は「40個あるから全部覚えよう」ではない。

本質は、Claudeが次の4つを持ち始めていることだ。

```
1. 記憶
   自分・仕事・プロジェクトの前提を保持する

2. 道具
   ファイル、ブラウザ、アプリ、コード、APIに触る

3. 分業
   複数エージェントで並列に進める

4. 検証
   ログ、Git、Hooks、評価で事故を見つける
```

この4つが揃った瞬間、AIは「回答生成ツール」から「仕事の実行環境」に変わる。

---

## 日本企業にとっての読み替え

ここからが、この記事で一番言いたいことだ。

日本企業のAI導入でよくある議論は、「どのモデルを契約するか」「どのツールを入れるか」に寄りがちだ。

もちろんモデル選びは大事だ。

だが、Boris氏の話を読む限り、差がつく場所はそこだけではない。

本当に差がつくのは、 **会社の業務文脈がAIに読める形で整備されているか** である。

AIに読ませるべきものは、実はすでに社内にある。

- 業務手順書
- 提案書の型
- 過去の議事録
- 顧客別の注意点
- 品質チェックリスト
- 禁止事項
- よくある失敗
- 過去のレビューコメント
- 部署ごとの判断基準

これらが人間の頭の中、共有フォルダの奥、古いPowerPoint、Slackの流れた会話に散らばっている限り、AIは強くならない。

逆に、これらをCLAUDE.md、Project、Knowledge File、Skills、MCP、Hooksのような形で渡せるようにすると、AIの出力は急に業務に近づく。

だから、企業のAI活用は「AI研修」だけでは足りない。

必要なのは、 **AIが働ける業務棚卸し** である。

---

## まず何から始めるべきか

いきなり40機能を全部設定する必要はない。

最初の1週間でやるなら、私はこの順番がよいと思う。

### 1\. 自分用の基本指示を固定する

自分の役割、業界、よく作る成果物、好きな文体、避けたい表現をCustom InstructionsやMemoryに入れる。

目標は、毎回の自己紹介を消すこと。

### 2\. 仕事ごとにProjectを分ける

Note執筆、リサーチ、コード、メール返信、提案書作成を同じチャットで混ぜない。

目標は、1つの会話に複数業務の文脈を混ぜないこと。

### 3\. CLAUDE.mdを作る

プロジェクトの目的、フォルダ構造、作業ルール、出力形式、禁止事項を書く。

目標は、同じ指摘を2回したらファイルに移すこと。

### 4\. 道具を接続する

ファイル、ブラウザ、Google Drive、Slack、Gmail、MCPなど、必要な入口を渡す。

目標は、人間のコピペ係をやめること。

### 5\. Plan Modeで先に考えさせる

複雑な作業は、作る前に計画、リスク、確認点を出させる。

目標は、AIに「手を動かす前に頭を使わせる」こと。

### 6\. ログと差分を残す

コードならGit、文章ならバージョン、定期処理なら実行ログを残す。

目標は、AIの仕事をあとから追えるようにすること。

---

## 結論: AIの差は、使う人の頭の中ではなく、周辺環境に宿る

Claudeをチャットとして使うだけなら、誰でも今日からできる。

しかし、それだけでは仕事の速度は大きく変わらない。

仕事を変えるのは、Claudeに次のものを渡したときだ。

- 自分の前提
- 仕事の文脈
- 使ってよい道具
- 分業の仕組み
- 検証のループ

Boris Cherny氏の話から見えるのは、AI活用の主戦場が「良いプロンプトを書くこと」から、 **AIが働ける環境を作ること** へ移っているということだ。

これは、業務設計そのものに近い。

人間の組織でも、優秀な人を採用するだけでは成果は出ない。

役割、権限、情報、道具、レビュー、評価があって初めて仕事になる。

AIも同じだ。

Claudeを賢くするのではない。

**Claudeが働ける会社にする。**

これが、次のAI活用の分岐点になる。

---

## 参考元

- Lenny's Podcast: [Head of Claude Code: What happens after coding is solved | Boris Cherny](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens)
- PodcastTranscript AI: [Transcript: Head of Claude Code: What happens after coding is solved | Boris Cherny](https://podcasttranscript.ai/library/head-of-claude-code-what-happens-after-coding-is)
- X: [Khairallah AL-Awady氏の投稿](https://x.com/eng_khairallah1/status/2057433528363811098)
- X: [How to Actually Set Up Claude. 40 Features Most Users Have Never Touched](https://x.com/eng_khairallah1/status/2057393717657374813)
- Claude Code docs: [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
- Claude Code docs: [Settings](https://code.claude.com/docs/en/settings)
- Claude Code docs: [Hooks reference](https://code.claude.com/docs/en/hooks)
- Claude Code docs: [Subagents](https://code.claude.com/docs/en/sub-agents)

## Related

- [[AI活用法-記事索引]]
