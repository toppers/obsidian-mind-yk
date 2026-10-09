---
date: 2026-08-11
description: "PMB MCP ツールの使い方 — READ FIRST 系（project_overview/prepare/recall/find_lessons/session_brief/list_goals）、mark_lesson_followed、record_batch の WRITE トリガー"
tags:
  - reference
  - claude-code
  - mcp
  - pmb
---

❯ MCPのpmb のツールの使い方を教えて

PMB MCPツールの使い方

PMBは「READ → 行動 → WRITE」のループを回すための記憶システム。基本原則: 書く前に必ず読む(エージェントが記録だけして次回読まずに同じ失敗を繰り返すのを防ぐため)。

1. 作業開始時に読む(READ FIRST)

| 状況 | 使うツール |
|---|---|
| 既知のプロジェクトで作業開始 | `project_overview(name="プロジェクト名")` — レッスン・決定事項・未完了ゴール・直近活動を1回で取得 |
| ユーザーの発言全般から文脈を掴みたい | `prepare(message="ユーザーの発言そのまま")` — recallを何度も呼ぶ代わりに1回で済む |
| 特定のトピックについて過去の記録を調べたい | `recall(query="調べたい内容", project="任意")` — score>0.2の結果は信頼できる記録として扱う |
| 「Xに関する手続き的ルールは?」だけ知りたい | `find_lessons(query="X", project="任意")` |
| 長時間セッションでコンテキストが圧縮された後 | `session_brief()` — このセッションで何を決めたか再確認(ユーザーに聞き直さない) |
| 「自分のゴールは?」「進行中の案件は?」 | `list_goals(status="in_progress")` |

重要: これらのツールはレッスン(lessonsフィールド、surface_id付き)を一緒に返してくる。レッスンが出たら必ず従い、行動後にmark_lesson_followedで報告する。

2. レッスンに従った後の報告

mark_lesson_followed(surface_id=64, followed=True, applicable=True, note="○○の方針に従い××した")
- レッスンが今回の作業に無関係だった → applicable=False
- 関係はあったが意図的に従わなかった → followed=False, note="理由"

3. 記録する(WRITE) — トリガーがあるときだけ

以下のトリガーが起きたときに1ターンにつき1回、record_batchでまとめて記録する:
- ユーザーが「覚えておいて」「重要」と言った → importance=0.95, pin=true
- ユーザーが事実を共有した(「〇〇に取り組んでいる」など) → importance=0.7
- 実質的な作業を完了した/意思決定をした → activityタイプ

record_batch(items=[
  {"type": "fact", "content": "...", "importance": 0.7},
  {"type": "activity", "kind": "...", "content": "..."},
])

項目タイプとフィールド（2026-09-21、ツールスキーマで確認）:

| type | フィールド | 用途 |
|---|---|---|
| `fact` | `content`, `importance`(0-1) | 単発の事実 |
| `fact_tree` | `main`, `subfacts[]`, `importance` | 主要事実＋サブ事実の束 |
| `lesson` | `content`, `project?` | 手続き的ルール |
| `goal` | `title`, `status`, `due_at` | 目標 |
| `plan` | `title` | 将来の意図（未実行） |
| `activity` | `content`, `kind` | 実施した作業内容 |
| `milestone` | `chain_name`, `title`, `state` | 一連の作業の節目 |

可変な個人属性(住所・所属など)はrecord_batchではなく専用の**record_keyed_fact(subject, attribute, value)**を使う — 古い値を上書き(upsert)する点が違う。例: record_keyed_fact("user", "city", "Tampa")

4. ゴールの更新

update_goal(goal_ulid="...", status="done", progress=100, note="完了の経緯")
ゴールの履歴としてgoal_updateイベントが残る。

使い分けの勘所

- PMBは一般的な質問(理論・構文・「Xとは何か」)には使わない。学習知識で答えられるものはそのまま答える。
- 使うときは「読んでから書く」を徹底 — 書きっぱなしで次回読まないと記録が無駄になる。
- 日付は常に絶対日付で保存する(今日は2026-08-10。「昨日」「先週」は解決してから記録)。

## Related

- [[pmb-cmd-使い方]] — PMB のコマンド使い方
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/QMD-使い方|QMD の使い方]] — もう一方の MCP 記憶・検索ツール
- [[reference/Note/AI開発/Claude-Code/Hooks/settings|Hooks settings]] — PMB を呼び出す hooks 設定
