---
date: 2026-07-05
description: "Claude/Codex/Obsidian に分散した運用ルールの読み取り専用クロス監査結果。記憶システム三重競合(PMB・beads・vault brain/)、RTKルール3重複、ツール設定15ディレクトリの棚卸し指摘"
tags:
  - reference
  - claude-code
  - obsidian
  - audit
---

クロス調査が終わりました。ファイル編集は一切していません。確認できた範囲と、確認できなかった範囲（要確認）を分けて報告します。

1. 全体評価

構造自体（Obsidianのフォルダ設計、CLAUDE.mdのVault Structure定義）は一貫性があり、よく設計されています。問題は「思想」ではなく「同じ役割を持つ仕組みが複数、独立に、後から積み重なっている」ことです。特に 記憶システムとタスク管理システムが3つ並存し、それぞれが互いを「使うな」と明言しているのに、同一セッションに同時注入されている状態は看過できません。加えて、このVaultルート直下には15種類のエージェント/ツール設定ディレクトリ（.claude .codex .cursor .gemini .junie .kilocode .windsurf .serena 等）が存在し、うち少なくとも2つ（Claude Code, Codex）は「同じ内容のはずのルールファイル」を独立に保持しています。これは一つ一つは軽微でも、積分すると「どのルールが本当に有効か本人も追えなくなる」方向に進んでいます。

2. 最も危ない運用上の問題

記憶／タスク管理の三重競合（実ファイルで確認済み）：

- プロジェクトのCLAUDE.md本文（263行目〜）：「全ての永続知識はbrain/配下のVaultノートに書け。~/.claude/にはMEMORY.mdという索引以外のファイルを作るな」
- グローバル~/.claude/CLAUDE.md：「PMB（prepare()/record_batch()）を実質必須の記憶システムとして使え。理論質問以外はほぼ毎回呼べ」
- 同じCLAUDE.mdファイルの末尾に<!-- END BEADS INTEGRATION -->という埋め込みブロックがあり、そこには「タスク管理はbeadsのみ。TodoWrite/TaskCreateは禁止」「永続知識はbd rememberのみ。MEMORY.mdファイルは使うな」と明記——一つの同じCLAUDE.mdファイルの中で「Vaultのbrain/を使え」と「MEMORY.mdは使うな」が矛盾しています。

さらに.claude/settings.jsonを見ると、SessionStartとPreCompactの両方のフックで、Vault専用スクリプト（session-start.ts, pre-compact.ts）とbd primeが両方独立発火するよう設定されており、これが二重コンテキスト注入の実際の原因です。実際、この会話でも「TaskCreateを使うことを検討して」という自動リマインダーが2回出ましたが、これはbeads側ルール（TodoWrite/TaskCreate禁止）と直接矛盾しています。

エージェントがどのタスク・メモリシステムに従うかはその場の運次第になっており、記憶の分裂（同じ決定がPMBとbeadsとVault brain/に別々に、あるいはどこにも記録されない）が実際に起きうる構造です。

3. 矛盾している可能性があるルール

┌─────────────────────────────┬─────────────────────────────────┬─────────────────────────────────────────────────┐
│           ルールA           │             ルールB             │                    矛盾内容                     │
├─────────────────────────────┼─────────────────────────────────┼─────────────────────────────────────────────────┤
│ CLAUDE.md「Memory           │ 同ファイル末尾のBeads統合ブロッ │                                                 │
│ System」節：Vault brain/が  │ ク：bd                          │ 同一ファイル内矛盾（実物確認済み）              │
│ 全ての永続知識の置き場      │ rememberのみ、MEMORY.md禁止     │                                                 │
├─────────────────────────────┼─────────────────────────────────┼─────────────────────────────────────────────────┤
│                             │ Beadsブロック：TodoWrite/TaskCr │                                                 │
│ グローバルCLAUDE.md：PMBのp │ eate/markdown                   │ 「どこに意思決定・進行中タスクを記録すべきか」  │
│ repare()をほぼ毎ターン必須  │ TODO禁止（PMBのgoal/lesson機構  │ が3方向に分岐                                   │
│                             │ とは別レイヤーだが役割が重複）  │                                                 │
├─────────────────────────────┼─────────────────────────────────┼─────────────────────────────────────────────────┤
│                             │ 同ファイル41〜80行目：<!--      │                                                 │
│ ~/.codex/AGENTS.md：@RTK.md │ headroom:rtk-instructions       │ 同一ファイル内でRTKルールが2重定義（矛盾ではな  │
│ をインポート                │ -->で同じ「rtkを必ず前置せよ」  │ く重複だが、片方だけ将来更新されると食い違う）  │
│                             │ ルールを再度べた書き            │                                                 │
├─────────────────────────────┼─────────────────────────────────┼─────────────────────────────────────────────────┤
│ ~/.claude/RTK.md と         │ 同じ「RTK」を説明しているが文面 │ 一次情報源が2箇所に分裂、片方だけ更新されれば即 │
│ ~/.codex/RTK.md             │ ・構成が別物（diffで26行差分）  │ 座に矛盾へ発展                                  │
└─────────────────────────────┴─────────────────────────────────┴─────────────────────────────────────────────────┘

4. 古くなっていそうな情報

- C:\Users\ykomi\AGENTS.md（ホームルート）が中身0バイト。存在理由不明、要確認。
- ~/.codex/rules/default.rules（33件の許可済みコマンドprefixルール）に、明らかに単発作業用だったものが残存：cloudflare-api設定リネーム用の一回限りPowerShellスクリプト、gemini-api-docsへの疎通確認HEADリクエスト、.codex-test-hyphen/.codex-test-underscoreという一時テストディレクトリの削除コマンド、headroomデバッグ実行など。恒久許可リストとして残す必要があるか要見直し。
- ~/.claude/settings.json.bak と settings.json.bak.20260702034943 がホーム直下に放置。意図した保存か事故的な残骸か要確認。
- brain/North Star.mdの「Goals」節（Short/Medium/Long-term, Aspirations, Anti-goals）が初期設定のまま空欄（Shifts Logの最初の行が「Created North Star / Initial setup」のみ）。Current Focusは細かく更新されているのに、上位ゴール欄が一度も埋まっていない状態。

5. 重複・肥大化している領域

- RTKルール：Claude用・Codex用に加え、Codex AGENTS.md内にもう1コピー＝実質3箇所。
- 記憶バックエンド：PMB / beads / Vault brain/ の3系統が同一ユーザーの同一種類の知識（決定・教訓・進行中タスク）を奪い合っている。
- ツール設定サーフェス：Vaultルート直下に.agents(14) .antigravitycli(1) .beads(33) .claude-plugin(2) .claudian(2) .codex(1) .cursor(1) .gemini(1) .junie(2) .kilocode(1) .mux(3) .serena(3) .smart-env(1241) .uv-tools(2) .windsurf(1) — 少なくとも15の異なるエージェント/CLI連携が同時に有効。多くは1〜3ファイルのスタブですが、「本当に全部使っているのか」「使っていないものは残骸ではないか」は本人にしか判断できません。
- ~/.claude/skills/にagentmemory関連が6分割（agents/architecture/config/hooks/mcp-tools/rest-api）で存在し、別途MCPサーバ（agentmemoryらしき記述）も併存している可能性——同じ機能への到達経路が複数（Skill経由／MCP経由）ある場合、片方が古くなっていないか要確認。

6. 改善した方がいいフォルダ構造または命名ルール

- 現状のObsidian側のbrain/ work/ perf/ org/ reference/ thinking/構造自体は健全で、変更不要と判断します。
- 問題はVaultの外側：CLAUDE.md・AGENTS.md・RTK.mdのような「運用ルールファイル」が、ツールごとに別ファイル・別ディレクトリで独立管理されている点。せめてRTK.mdのような「複数ツール共通のはずの内容」は、1つの正本（例：Vault内reference/か共通dotfile）を作り、各ツール側は@importだけにする設計に寄せた方が、今回のような「同じはずが食い違う」問題を根本的に防げます（Codex側はすでに@RTK.mdインポートの仕組みを持っているので、応用は可能なはずです）。
- 日次(om-standup)・週次(om-weekly)はあるが、月次の棚卸しコマンドが存在しない（四半期クローズは手動コミットで実施されている形跡のみ）。週次と四半期の間に情報がこぼれる可能性があります。

7. 今すぐやる3つ

8. CLAUDE.md末尾のBeads統合ブロックと、本文Memory Systemの記述をどちらが優先か本人の頭の中で確定する（ファイルは触らず、まず方針だけ決める）。今のままだと毎回どちらに従うかがブレます。
9. ~/.codex/rules/default.rulesの一回限り許可ルール（cloudflare-apiリネーム、gemini-api-docs疎通確認、testディレクトリ削除など）を棚卸しし、まだ要るものだけ残す。実害は小さいですが肥大化が続く運用です。
10. ~/.claude/settings.json.bak系ファイルと空の~/AGENTS.mdの扱いを確認——事故的な残骸なら次回整理、意図的な保管なら放置でよいと明確化するだけで、今後の「これ何だっけ」を防げます。

11. 本人に確認すべきこと

- PMB・beads・Vault brain/の3つ、どれを「決定・教訓・進行中タスクの正本」にしたいか。全部残すにしても優先順位を明文化しないと矛盾は解消しません。
- C:\Users\ykomi\AGENTS.md（0バイト）は何のために置かれたものか。
- Vaultルートの15個のツール設定ディレクトリのうち、実際に今も使っているものはどれか（特に.antigravitycli .claudian .kilocode .mux .windsurfのような1ファイルのみのものは、動作確認用に一度作って以降触っていない可能性）。
- Claude.ai側（claude.ai上のProjects／Skills／Knowledge、ローカルのCLIとは別物）の内容は本環境からは一切読めていません。ここに古い仕様・価格・機密情報が残っていないかは完全に要確認——見たい場合はスクリーンショットや書き出しを共有してもらえれば確認できます。
- 週次と四半期の間の「月次」に相当する棚卸しは意図的に無いのか、単に未着手なのか。

なお、Git管理下のファイルに対する簡易的な秘密情報パターン検索（APIキー・秘密鍵らしき文字列）では、.beads/config.yaml内の「秘密鍵は環境変数を使え」というコメント行以外に実際の漏洩は見つかりませんでした。ただしこれは追跡対象ファイルへの簡易grepのみで、_inbox配下の未処理スクラッチファイルや添付画像・PDF等までは網羅していません。

✻ Cooked for 6m 37s

※ recap: You asked me to audit how work rules/memory are organized across Claude, Codex, and Obsidian, without editing anything; I finished that read-only review and reported findings. Next: decide which system (PMB, beads, or vault brain/) should be the single source of truth for memory and tasks. (disable recaps in /config)

## Related

- [[ops-prompt]]
- [[ops-structure-review]]