---
title: "Obsidian Copilotのすゝめ：ノート活動を変えるかもしれない壁打ち相手"
source: "https://qiita.com/hann-solo/items/1566fa38e5b737a2e61a?utm_source=openai"
author:
  - "[[hann-solo]]"
published: 2025-03-16
created: 2026-07-21
description: "はじめに Obsidianは、その柔軟性と拡張性から、多くの人に愛用されている知識管理ツールです。私も、日々のメモやアイデアの整理、そしてビジネス資料の作成まで、Obsidianを活用しています。 近年、目覚ましい進化を遂げているのが、大規模言語モデル（LLM）です。文..."
tags:
  - "clippings"
---
この記事は最終更新日から1年以上が経過しています。

[AIエージェントの知見を共有しよう！](https://qiita.com/official-events/3173172074bd59848652)

- [Markdown](https://qiita.com/tags/markdown)
- [copilot](https://qiita.com/tags/copilot)
- [Obsidian](https://qiita.com/tags/obsidian)
- [LLM](https://qiita.com/tags/llm)
- [ollama](https://qiita.com/tags/ollama)

65

最終更新日 投稿日 2025年03月16日

[![250316_copilot_opt.jpg](https://cdn-ak.f.st-hatena.com/images/fotolife/m/masatora_bd5/20250316/20250316133938.jpg)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fcdn-ak.f.st-hatena.com%2Fimages%2Ffotolife%2Fm%2Fmasatora_bd5%2F20250316%2F20250316133938.jpg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=311000bb02428041b3dcb40c3d858bc3)

## はじめに

Obsidianは、その柔軟性と拡張性から、多くの人に愛用されている知識管理ツールです。私も、日々のメモやアイデアの整理、そしてビジネス資料の作成まで、Obsidianを活用しています。

近年、目覚ましい進化を遂げているのが、大規模言語モデル（LLM）です。文章の生成や要約、翻訳など、LLMは様々なタスクで人間を凌駕する能力を発揮し始めています。このLLMの力をObsidianと組み合わせることで、知的生産性をさらに向上させることができるのではないか。そう考え、私はObsidian Copilotを導入しました。

Obsidian Copilotは、Obsidian内でLLMを活用するためのプラグインです。まるで優秀な「副操縦士（Copilot）」のように、ノート作成、アイデア出し、文章校正など、様々な作業をAIがサポートしてくれます。

### なぜObsidian Copilotを選んだのか（Smart Composerとの比較）

ObsidianでLLMを利用できるプラグインは、Obsidian Copilotだけではありません。例えば、「Smart Composer」というプラグインも存在します。

現時点では、両者に決定的な差を感じているわけではありません。しかし、私がObsidian Copilotを試用している理由は、主に以下の3点です。

1. **出力の質の高さ:** いくつかのプロンプトで比較したところ、Obsidian Copilotは、Smart Composerよりも文脈に沿った、具体的な提案をしてくれる傾向がありました。Smart Composerは、ノートの内容を十分に理解していないかのような、的外れな応答を返すことがあり、この点が気になりました。
2. **設定の柔軟性:** Smart Composerの出力が期待に満たないのは、単に私の設定が不十分である可能性も否定できません。Obsidian Copilotについても、まだ最適な設定を見つけられていないため、現時点では「Obsidian Copilotに確定」とは言えません。
3. **将来性への期待:** Obsidian Copilotは、Smart Composerに比べて開発が活発であり、新機能の追加や改善が頻繁に行われています。今後の発展次第では、Obsidian CopilotがSmart Composerを大きく上回る可能性を秘めていると感じています。

これらの理由から、私は現時点でObsidian Copilotを試用し、その可能性を探っています。

Smart Composerの設定を見直す余地も残されており、最終的な判断は今後の検証次第です。両プラグインの特性を理解し、よい選択をしたいと考えています。

## Obsidian Copilotの概要

[![img](https://raw.githubusercontent.com/logancyang/obsidian-copilot/refs/heads/master/images/ui.jpg)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fraw.githubusercontent.com%2Flogancyang%2Fobsidian-copilot%2Frefs%2Fheads%2Fmaster%2Fimages%2Fui.jpg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d73571891f2c7fe4bd4173009328a926)

Obsidian Copilotは、Obsidian内でAIの力を活用するための **オープンソース** プラグインです。主な特徴は以下の通りです。

- **多様なLLMに対応:** OpenAI、Anthropic、Google Geminiなど、様々なモデルを利用可能。APIキーを登録するだけで、ChatGPT Plusなどの有料プランは不要です。ローカルLLM (LM Studio, Ollama) にも対応。
- **チャットUI:** Obsidian内でLLMと対話できるチャットウィンドウを提供。
- **コマンド:** テキストの簡略化、翻訳、文法修正など、様々な処理をコマンドで実行。
- **カスタムプロンプト:** 独自のプロンプトを作成・管理、呼び出し可能。
- **Vault QA:** Obsidian内の全ノートを対象に質問応答が可能。ローカルインデックスを使用し、プライバシーに配慮。
- **Copilot Plus (ベータ版):** Obsidianに強力なAIエージェント機能を追加 (詳細は [obsidiancopilot.com](https://obsidiancopilot.com/))。

Copilotのチャット機能とVault QAは無料で利用可能です。

## 導入手順

### Obsidian Copilotのインストール

1. Obsidianの「コミュニティプラグイン」から「Obsidian Copilot」を検索し、インストールします。
2. プラグインを有効化します。

### Ollamaとの連携設定

1. **Ollamaのインストール:** [Ollama公式サイト](https://ollama.ai/) から、お使いのOS (Mac, Linux, Windows) に合わせてOllamaをダウンロードし、インストールします。
2. **モデルのダウンロード:** ターミナル（またはPowerShell, CMD）で `ollama pull <モデル名>` を実行し、使用したいLLMモデルをダウンロードします。（例： `ollama pull mistral` ）
3. **コンテキストウィンドウの設定(重要):** `ollama run <モデル名>` を実行後、 `/set parameter num_ctx <コンテキスト長>` (例: `/set parameter num_ctx 32768`)でコンテキスト長を設定し、 `/save <モデル名>` で保存します。 **各モデルで個別に設定が必要です。** サーバーログで `llama_new_context_with_model: n_ctx` の値を確認してください。
4. **サーバーの起動（重要）:** Obsidianからアクセスできるようにするため、以下のいずれかの方法で `OLLAMA_ORIGINS` 環境変数を設定してOllamaサーバーを起動します。
	- **CLI (Mac, Linux):** ターミナルで `OLLAMA_ORIGINS=app://obsidian.md* ollama serve` を実行。(fishシェルの場合は `OLLAMA_ORIGINS="app://obsidian.md*" ollama serve`)
		- **macOS App:** ターミナルで `launchctl setenv OLLAMA_ORIGINS "app://obsidian.md*"` を実行後、Ollamaをメニューバーから終了し、再起動。
5. **Obsidian Copilotの設定:** Obsidian Copilotの設定画面で、「Add Custom Model」を選択し、以下を入力して「add」をクリック。
	- **Model Name:** Ollamaでプルしたモデル名 (例: `mistral`)
		- **Provider:** `ollama`
		- `Verify` ボタンを押してsuccessfulとなることを確認し、 `Add Model` ボタンでモデル追加
6. **ローカル埋め込み(オプション):** RAGでローカル埋め込みモデルを使用する場合、 `ollama pull nomic-embed-text` (または `mxbai-embed-large` など)を実行。CopilotのQA設定で、モデル名(例: `nomic-embed-text`)、プロバイダ `ollama` を指定。

これで、Obsidian CopilotからOllamaで動作するローカルLLMを利用できるようになります。

サーバの起動が重要です。 `setenv` してmacOS.appで起動、で普段づかいはOKと思います。ログを見るにはターミナルで `OLLAMA_ORIGINS=app://obsidian.md* ollama serve` で起動するのがよいです。

### LLMの選択と設定

Obsidian Copilotでは、複数のLLMモデルを使い分けることができます。いまのところ、私は下記のモデルを使っています。

#### テキスト生成モデル

- **gemini-2.0-flash (クラウド):**
	- **メリット:** 高速かつ高品質な文章生成が可能。回数制限などはあるが無料。
		- **デメリット:** インターネット接続が必要。APIキーを取得する必要あり。プライバシーに関する懸念あり。
		- **使い所:** 高品質な文章を素早く生成したい場合。
- **deepseek-r1:14b-qwen-distill-q4\_K\_M (ローカル):**
	- **メリット:** 比較的軽量で、ローカルで動作。
		- **デメリット:** gemini-2.0-flashに比べると、生成速度や品質が劣る。
		- **使い所:** プライバシーを重視しつつ、ある程度の品質の文章を生成したい場合。
- **lucas2024/llama-3-elyza-jp-8b:q5\_k\_m (ローカル):**
	- **メリット:** 上記deepseek-r1:14bより軽量。ローカルで動作。
		- **デメリット:** gemini-2.0-flash、deepseek-r1:14bと比べると、生成速度や品質が劣る。
		- **使い所:** プライバシーとスピードを重視し、文章の品質をあるていど犠牲にしても大丈夫な場合。

#### エンベッディングモデル

- **yxchia/multilingual-e5-large-instruct:latest:**
	- **メリット:** 多言語に対応しており、日本語の文章にも対応可能。
		- **使い所:** とりあえずこれでしばらく運用。
- **mxbai-embed-large:latest:**
	- **メリット:** 高い精度で文章の類似度を計算できる。
		- **使い所:** しばらくこれで運用して不満はなかったが、multilingual-e5-largeのほうが賢いという話なので実験中。

#### モデル選択の理由と使い分け

- **普段使い:** gemini-2.0-flashで高速・高品質な文章生成。
- **オフライン作業:** deepseek-r1:14b-qwen-distill-q4\_K\_Mでプライバシーを確保。
- **速度優先:** lucas2024/llama-3-elyza-jp-8b:q5\_k\_mで質を犠牲にしてスピード優先。
- **RAG利用時**: `yxchia/multilingual-e5-large-instruct:latest` で実験中。いまのところスピードも問題ないと感じている。

### おすすめ設定

Obsidian Copilotの高度な設定の一つに、「User System Prompt」があります。ここに、AIアシスタントの役割や口調などを指示する文章を入力できます。

設定場所は、 `Settings` > `Copilot` > `Advanced` > `User System Prompt` です。

例えば、以下のように設定すると、常に日本語で丁寧な応答をしてくれるようになります。

```text
あなたは誠実で優秀な日本人のアシスタントです。特に指示が無い場合は、常に日本語で回答してください。
```

[![SS 2025-03-16 13.51.48_opt.jpg](https://cdn-ak.f.st-hatena.com/images/fotolife/m/masatora_bd5/20250316/20250316135238.jpg)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fcdn-ak.f.st-hatena.com%2Fimages%2Ffotolife%2Fm%2Fmasatora_bd5%2F20250316%2F20250316135238.jpg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ec6231de8c7330e6e660ab1dadb9dc23)

この設定は、特に日本語でObsidian Copilotを利用する方におすすめです。ぜひ一度お試しください。

## Obsidian Copilotの活用例

Obsidian Copilotは、以下のような場面で、私のObsidianライフをサポートしてくれています。

- **ノート作成の効率化:** タイトルや見出しの提案、本文の自動生成、さらには既存ノートからの関連情報の抽出まで、Obsidian Copilotにお任せすることで、ノートからアウトプットを作成するのが効率的になりました。
- **文章の校正・改善:** 誤字脱字や文法ミスのチェックはもちろん、より自然で洗練された表現を提案してくれるので、文章の質が向上したと実感しています。要約機能も超・便利です（後述）。
- **関連ノートの提示:** Obsidian Copilotは、作業中のノートに関連するノートを自動的に探してきてくれます。これがさりげなく非常に便利で、過去の自分の思考を掘り起こしたり、思わぬ繋がりを発見したりするきっかけになっています。
- **カスタムプロンプトの威力:** 特に「要約」や「簡単に言い換える」といったカスタムプロンプトは、日々の作業を大幅に効率化してくれる、手放せない機能となりました。自分でプロンプトをカスタマイズできるので、Obsidian Copilotを自分専用のAIアシスタントとして活用できるのがありがたいです。

[![250315_shorter.gif](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F184128%2F59843977-b7b0-4bb0-8071-6bcf1d6ea0e7.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9e5a64b7695ffa84337ec6b3fcdb234a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F184128%2F59843977-b7b0-4bb0-8071-6bcf1d6ea0e7.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9e5a64b7695ffa84337ec6b3fcdb234a)

> カスタムプロンプトで、文を要約させている例

## 今後の展望

Obsidian Copilotは発展途上のプラグインであり、今後の進化に期待しています。特に、 **機能拡張（画像生成、音声入力など）** 、 **RAGの高度化** 、 **UI/UXの改善** に注目しています。

私自身の活用計画としては、Obsidian Copilotを日々の作業に取り入れ、新しいワークフローを構築したいと思っています。具体的には、

- **設定の最適化:** 自分の作業スタイルに最適な設定を見つける。
- **LLMモデルの選定:** 速度、精度、プライバシーのバランスが良いモデルを探す。
- **プロンプトエンジニアリング:** 効果的なプロンプト作成技術を磨く。

Obsidian Copilotは、私のノート活動を変える可能性を秘めたツールです。その進化にうまく便乗し、学び続け、共に成長していきたいです。

## リンク集

- **Obsidian公式ページ**: [https://obsidian.md/](https://obsidian.md/)
- **Obsidian Copilotプラグイン（GitHub）**: [https://github.com/logancyang/obsidian-copilot](https://github.com/logancyang/obsidian-copilot)
- **Smart Composerプラグイン（GitHub）**: [https://github.com/glowingjade/obsidian-smart-composer](https://github.com/glowingjade/obsidian-smart-composer)
- **Ollama公式ウェブサイト**: [https://ollama.ai/](https://ollama.ai/)
- **解説記事: Obsidian Copilotの導入と活用方法**: [https://note.com/mekann/n/n4d337ccd8d95](https://note.com/mekann/n/n4d337ccd8d95)
- **解説記事: Smart Composerの導入と活用方法**: [https://zenn.dev/y16ra/articles/e17dd3349836c3](https://zenn.dev/y16ra/articles/e17dd3349836c3)
- **解説記事: Ollamaを用いたローカルLLMの実行方法**: [https://zenn.dev/kesin11/scraps/244a9939f87a39](https://zenn.dev/kesin11/scraps/244a9939f87a39)
- [Obsidian｜使いかたとコツ（目次）](https://qiita.com/hann-solo/items/ac8fa75394813e8adcf4)

この記事は [Obsidian Copilotのすゝめ：ノート活動を変える可能性のある壁打ち相手 - mxt forest](https://silme.zelo-loop.com/mxt/Notes/Obsidian+Copilot%E3%81%AE%E3%81%99%E3%82%9D%E3%82%81%EF%BC%9A%E3%83%8E%E3%83%BC%E3%83%88%E6%B4%BB%E5%8B%95%E3%82%92%E5%A4%89%E3%81%88%E3%82%8B%E5%8F%AF%E8%83%BD%E6%80%A7%E3%81%AE%E3%81%82%E3%82%8B%E5%A3%81%E6%89%93%E3%81%A1%E7%9B%B8%E6%89%8B) に基づいています。最新の情報や更新は、元の記事でご確認ください。

## 環境

以下のバージョンで実施しました。

- Obsidian v1.8.9
- macOS Sequoia 15.3.2
- MacBook Pro (14-inch, 2021)

## おわりに

Obsidian Copilotを導入して1週間が経過しました。私のObsidianを用いたノート活動は、大きく変化しました。一人で作業しているのではなく、誰かと壁打ちしながら物事を進めているような感覚です。

特に、 **カスタムプロンプト** の機能は、作業効率を大幅に向上させました。人に読んでもらうためには、文章の情報量と密度のコントロールが鍵となります。しかし、LLMが作る文章も、人間がつくる文章も、基本的には冗長になりがちです。情報量を落とし密度を上げる作業が必須となります。手作業で行うのも楽しいですが、パートナーがいることで、さらに楽しい体験へと変わりました。

Obsidian Copilotの機能を完全に活用できているわけではありません。RAG機能の高度化や、新しいLLMモデルの登場など、Obsidian Copilotには、まだ多くの潜在能力があると感じています。

「 **Obsidian Copilotは、私のノート活動を変える可能性を秘めたツールである** 」

これが、現時点での率直な評価です。Obsidian Copilotの今後の発展に期待するとともに、私自身もObsidian Copilotを積極的に活用し、その進化に貢献できるよう、継続的な利用を続けていく所存です。この有用なツールは、Obsidianユーザーの方々、特に文章作成に携わる方には、非常に役立つ可能性があると愚考いたします。

[0](#comments)

コメント一覧へ移動

X（Twitter）でシェアする

Facebookでシェアする

はてなブックマークに追加する

新規登録して、もっと便利にQiitaを使ってみよう

1. あなたにマッチした記事をお届けします
2. 便利な情報をあとで効率的に読み返せます
3. ダークテーマを利用できます
[ログインすると使える機能について](https://help.qiita.com/ja/articles/qiita-login-user)

## Related

- [[Obsidian-記事索引]]
