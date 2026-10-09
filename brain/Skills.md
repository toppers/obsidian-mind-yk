---
date: 2026-04-07
description: "Vault-specific workflows and slash commands — reusable patterns for review prep, project tracking, and vault maintenance"
tags:
  - brain
  - index
---

# Skills

Custom slash commands, subagents, and reusable workflows. Defined in `.claude/commands/` and `.claude/agents/`. **This note is the canonical command catalog** for agents that don't get the in-session skills injection (Codex, Gemini, Cursor) — keep it current when commands change; CLAUDE.md deliberately carries no command table.

## Slash Commands

### Daily Workflow

| Command | Purpose |
|---------|---------|
| `/om-standup` | Morning kickoff — load context, review yesterday, surface tasks, identify priorities |
| `/om-dump` | Freeform capture — dump anything, gets routed to the right notes automatically |
| `/om-wrap-up` | Full session review — verify notes, indexes, links, suggest improvements. Auto-triggered on "wrap up". |

### Editing & Synthesis

| Command | Purpose |
|---------|---------|
| `/om-humanize` | Voice-calibrated editing — makes Claude-drafted text sound like you wrote it |
| `/om-weekly` | Weekly synthesis — cross-session patterns, North Star alignment, uncaptured wins |

### Meeting Prep & Capture

| Command | Purpose |
|---------|---------|
| `/om-prep-1on1` | Prep for an upcoming 1:1 — load person context, open items, wins to share, suggested agenda |
| `/om-capture-1on1` | Capture 1:1 meeting transcript into structured vault note with quotes, action items, DM context |
| `/om-incident-capture` | Capture incident from Slack channels/DMs into structured vault notes — timeline, people, analysis, brag entry |
| `/om-slack-scan` | Deep scan Slack channels/DMs for evidence — extracts timestamped touchpoints, organizes by context |
| `/om-meeting` | Prep for any meeting by topic — subject-forward briefing with open items, blockers, and brainstormed considerations |
| `/om-intake` | Process meeting notes inbox — classify raw exports in `work/meetings/` and route to the right vault notes |

### Performance & Review

| Command | Purpose |
|---------|---------|
| `/om-peer-scan` | Deep scan a peer's GitHub PRs for review prep — produces structured analysis saved to `perf/evidence/` |
| `/om-review-brief` | Generate review brief (manager or peer version) from vault data |
| `/om-self-review` | Write self-assessment for review tool — projects, competencies, principles |
| `/om-review-peer` | Write peer review — projects, principles, performance summary |

### Vault Maintenance

| Command | Purpose |
|---------|---------|
| `/om-correct` | Sweep a corrected fact through the vault — semantic + literal search, applies at the single source, replaces restatements with links, preserves notes recording what was believed at the time. The acting half of Write-Correctness Law 2 |
| `/om-vault-audit` | Deep structural audit — indexes, frontmatter, links, Bases, folder placement, stale context |
| `/om-vault-upgrade` | Upgrade this vault through ShardMind, keeping local improvements and listing them as upstream candidates; or import content from an existing vault — detects version, classifies notes, transforms frontmatter, rebuilds indexes |
| `/om-project-archive` | Move completed project from `work/active/` to `work/archive/YYYY/`, update all indexes — moves whole `active/<Topic>/` clusters intact |
| `/om-tidy` | Self-maintenance pass — acts on every hygiene flag: archives completed work, groups clusters, splits oversized notes, sweeps missing/placeholder frontmatter, reports open loops. Never deletes, never commits |

## Usage Notes

**Daily:**
- `/om-standup` replaces the manual session start — reads North Star, active work, tasks, git log
- `/om-dump` processes freeform text and routes each piece to the correct note type and folder
- `/om-wrap-up` is auto-triggered when you say "wrap up" — runs full session review

**Editing & Synthesis:**
- `/om-humanize` calibrates against your actual writing samples, not a word blacklist. Detects context from frontmatter (review → corporate-confident, incident → precise, 1:1 → conversational). Run after drafting any note to make it sound human.
- `/om-weekly` bridges standup and review brief — run at end of week for cross-session patterns, North Star drift, and uncaptured wins. Output is transient by default; offer to promote findings to brag doc or North Star.

**Capture:**
- `/om-capture-1on1` handles transcripts, raw notes, or summaries
- `/om-incident-capture` takes Slack URLs and produces structured incident documentation
- `/om-slack-scan` should be run AFTER `/om-peer-scan` to add context beyond code (leadership, communication, collaboration evidence)

**Performance:**
- `/om-peer-scan` works best when launched as parallel agents (one per person)
- `/om-review-brief` needs the private brief to exist first — it generates filtered versions from it

**Maintenance:**
- `/om-vault-audit` should be run at the end of substantial sessions — catches stale indexes and mixed context
- `/om-vault-upgrade` with no source upgrades this vault through ShardMind 0.2.1+: `upgrade-plan.ts` sorts every differing file into behind (take), ahead (keep; upstream candidate), merged or conflict before anything is applied. With a source, it imports content from an existing vault (older obsidian-mind or any Obsidian vault). Detects version, classifies notes, transforms frontmatter, fixes wikilinks, rebuilds indexes. Use `--dry-run` to preview.
- `/om-project-archive` handles the active/ → archive/ move with index updates
- `/om-ops-audit` is diagnostic only (no edits) — run it occasionally, not every session, when instructions from different tools (Claude / Claude Code / Codex / Obsidian) seem to be drifting or contradicting each other. Always reports in the fixed 8-section Japanese format (全体評価 → 本人に確認すべきこと).

## Subagents

| Agent | Purpose | Invoked by |
|-------|---------|------------|
| `brag-spotter` | Proactively finds uncaptured wins and competency gaps | `/om-wrap-up`, `/om-weekly` |
| `context-loader` | Loads all vault context about a person, project, incident, or concept | Direct — "load context on X" |
| `cross-linker` | Finds missing wikilinks, orphans, broken backlinks across the vault | `/om-vault-audit` |
| `people-profiler` | Bulk create/update person notes from Slack profiles | `/om-incident-capture` |
| `review-prep` | Aggregates all performance evidence for a given review period | `/om-review-brief` |
| `slack-archaeologist` | Full Slack reconstruction — reads every message, thread, profile, produces unified timeline | `/om-incident-capture` |
| `vault-librarian` | Deep vault maintenance — orphan detection, broken links, frontmatter validation, stale notes | `/om-vault-audit` |
| `review-fact-checker` | Verify every claim in a review draft against vault sources | `/om-self-review`, `/om-review-peer` |
| `vault-migrator` | Classify, transform, and migrate content from a source vault | `/om-vault-upgrade` |

Subagents run in isolated context windows via `.claude/agents/`. They don't pollute the main conversation.

## Hooks

| Hook | When | What |
|------|------|------|
| SessionStart | On startup/resume | QMD re-index, inject North Star, active work, recent changes, tasks, file listing |
| UserPromptSubmit | Every message | Classify content (decision, incident, 1:1, win, architecture, person, project update) and inject routing hints |
| PostToolUse | After writing `.md` | Validates frontmatter, checks for wikilinks |
| PreCompact | Before context compaction | Back up session transcript to `thinking/session-logs/` |
| Stop | After every response | Checklist + hygiene findings, once per session and again when they change, to the user and to the agent (which decides whether to act); ask the agent to run `om-tidy` to act |

## Other Skills

| Skill | Purpose |
|-------|---------|
| `/section-sort-dedup <file>` | Sort each `## ` section's code-block lines ascending and remove exact-duplicate lines. Node script at `.claude/skills/section-sort-dedup/index.js`; supports `--dry-run` and backups. Used for cleaning up accumulating reference lists like `reference/Note/Gmail/Gmail-filters.md`. |

## Skill Authorship & Provenance

2026-07-27 調査。SKILL.md の「誰が作ったか」を後から判別する方法と、現状の配置。

### スキルの配置と git カバレッジ

| 場所 | git | SKILL.md 数 | 備考 |
|------|-----|------------|------|
| `~/.claude/skills` | ✅ | 18 | リポジトリ toplevel = `C:/Users/ykomi/.claude` |
| vault `.claude/skills` + `.agents/skills` | ✅ | 15 | このリポジトリで追跡 |
| `~/.agents/skills` | ✅ **独立リポジトリ** | 99 tracked | initial commit `514d54b` 2026-07-16 by ykominami。**コミット2件のみ・remote 無し・未コミット変更54件** |
| `~/.agents`（親） | ✅ 2026-07-27 に `git init` | — | `_skills*` 4系統・`plugins/`・`AGENTS.md`・`RTK.md`・`.skill-lock.json` を追跡。`skills/` は自己管理のため `.gitignore` で除外 |

> [!warning] 2026-07-27 の訂正
> 当初「`~/.agents/skills` の86件が git 管理外・履歴ゼロ」と記録したが**誤り**。実際には 2026-07-16 から独立リポジトリとして管理されていた（親ディレクトリを `git init` した際に embedded repository として検出されて判明）。ただし以下は実在するリスク:
> - **remote が無い** — ディスク障害で全消失する単一障害点
> - **未コミット変更54件** — 直近の編集が履歴に入っていない
> - **作成日は復元不可** — 全スキルが initial commit `514d54b`(2026-07-16) 由来のため、それ以前の個別作成日は失われている（author が `ykominami` である事実のみ判明）

### 記録方法: `metadata:` フィールド

`name`/`description` と違い任意のキーを置ける枠で、ローダーは中身を解釈せず素通しする。環境内の先行実例: `~/.agents/skills/find-skills-j/SKILL.md`（株式会社ALSEL — `author`/`homepage`/`source`）と `one-password/SKILL.md`（インライン JSON）。

```yaml
metadata:
  author: ykominami
  created: 2026-07-18
  origin: self          # self | claude | third-party | anthropic
  source: ""            # 第三者製のときだけ URL
```

`origin` が最も実用的 — 「自分で書いたか／拾ってきたか／Claude に生成させたか」の判別が知りたい実際の動機だから。

### Anthropic 公式スキルの機械判別

`license:` の文字列で識別できる（約32件）:
- `Complete terms in LICENSE.txt`
- `Proprietary. LICENSE.txt has complete terms`

### 棚卸し

`export-skills-csv`（CSV 出力）と `audit-skill-yaml`（frontmatter 検証）が既にある。CSV に `author`/`origin` 列を足せば全スキルの由来が一覧化でき、一括変更後の検証は `audit-skill-yaml` がそのまま使える。

関連: [[Gotchas - Tooling & Config#SKILL.md のファイルタイムスタンプは作成日として使えない]]

## LLM Wiki (`/wiki:*`)

Obsidian vault 内に永続的な知識ベースを構築・管理するコマンド群。**プレフィックスは `wiki:`**（`llm-wiki:` ではない — 有効なプラグインは `wiki@llm-wiki`。バージョンは自動更新されるため固定値を覚えず、都度`installed_plugins.json`で確認する。2026-09-13時点でv0.24.4）。

| コマンド | 説明 |
|----------|------|
| `/wiki:wiki` | 自然言語ルータ。`init <name>` / `status` / `config` もここ |
| `/wiki:ingest <path\|url>` | ソース（ファイルまたは URL）を取り込む |
| `/wiki:compile` | raw ソースから wiki ページを生成 |
| `/wiki:query <question>` | wiki に対して質問し回答を得る |
| `/wiki:research` | 並列マルチエージェント調査（`--mode thesis` で賛否フレーミング） |
| `/wiki:lint` / `/wiki:librarian` | 整合性チェック / 品質・鮮度レビュー |
| `/wiki:assess` `/wiki:plan` `/wiki:project` `/wiki:output` `/wiki:refresh` `/wiki:retract` `/wiki:ll` `/wiki:thesis` | その他（`thesis` は `research --mode thesis` に統合済みで非推奨） |

定義の所在（cache のパス・`enabledPlugins` との連鎖）は [[llm-wiki-CLI設定#プラグイン定義の所在（as of 2026-09-13）]]。唯一の真の Skill は `wiki:wiki-manager`、残りはスラッシュコマンド。

現在 `reference/03-Resources/my-topic/` に TECS wiki を運用中。詳細は [[reference/03-Resources/my-topic/CLAUDE]] 参照。

### `/wiki:refresh` — 外部ソース更新の反映（as of 2026-09-13）

自動再コンパイルではなく**人間ゲート型の差分確認**。対象記事の `sources:` frontmatter から元ソースの `source:` URL を再取得し、保存済み内容の主要事実5〜10個と突き合わせて `unchanged` / `updated` / `contradicted` / `unreachable` に分類。変化ありの場合はレポートを提示し、ソースごとに次から選択：

- `skip` — 変化なしと確認、`verified` 日付のみ更新
- `update` — 生ソースを新内容で上書き→記事を再コンパイル
- `flag` — `confidence` を1段階降格（high→medium等）＋記事本文に警告コールアウト追加
- `retract` — `/wiki:retract` へ回してソース自体を除去

期限切れ記事の一括確認は `--due`（`freshness_threshold` 既定70日、鮮度スコア低い順に一覧提示）。定期実行はセッション内なら `/loop 1d /wiki:refresh --due --wiki <name>`（`/resume` を跨いで継続・7日で失効）。wikiがgitクローン可能なリポジトリにあれば `/schedule` でクラウド常駐も可、ローカル/iCloud限定なら `/loop` 推奨。

## Semantic Search (QMD)

If QMD is installed (`npm install -g @tobilu/qmd`), the vault has semantic search. Every command takes `--index <name>`, where `<name>` is `vault-manifest.json`'s `qmd_index` field when set and otherwise the vault folder name slugified:

- `qmd --index <name> query "..."` — hybrid BM25 + vector + LLM reranking (best quality)
- `qmd --index <name> search "..."` — fast BM25 keyword search
- `qmd --index <name> vsearch "..."` — semantic vector search (exploratory)
- `qmd --index <name> update && qmd --index <name> embed` — refresh index after bulk changes

SessionStart hook runs `qmd --index <name> update` automatically, reading the index name from the manifest. First-time setup on a fresh clone: `node --experimental-strip-types .scripts/qmd-bootstrap.ts`. See `.claude/skills/qmd/SKILL.md` for full reference, and [[Memories]] for the topics QMD is most often asked to find across the vault.

## The `om` MCP Server (reaching this vault from another repo)

`.claude/scripts/om-mcp.mjs` exposes this vault over MCP so a session in **another repository** can use it. Registered in the *consuming* project's `.mcp.json`, never in this vault's own — the server refuses a memory write from a session running inside the vault, because such a memory would be scoped to the vault-as-a-project and reach only sessions that already read every note directly.

| tool | purpose |
|------|---------|
| `search` | semantic + keyword over the notes this vault serves |
| `expand` | a note's links out and backlinks |
| `recall` | durable lessons scoped to the calling repo, most specific first; `explain: true` reports what was withheld and why. A capture whose `promoted:` marker carries an anchor serves the promoted `brain/` block instead of the capture body, so you read the corrected version |
| `remember` | record a lesson that generalises beyond this repo |
| `record_work` | record what happened here, filed where it belongs |
| `reason` | judgement across several notes, by reading the vault with a second Claude session |
| `health` | where memories live, which roots are exposed, is the index reachable |

### User-invoked prompts: `prior_art` and `recall_topic`

Two prompts you invoke yourself from the `/` menu. They live in the server's `prompts/list` — separate from the tools (`search`/`recall`/…) — and are **selected** from the menu; typing the displayed label (`om:prior_art` / `mcp__om__prior_art`) by hand errors.

| prompt | arg (required) | what it injects |
|--------|----------------|-----------------|
| `prior_art` | `question` — the decision you are about to make, written as a sentence (not a topic name). e.g. *"search サブコマンドの visibility フィルタを CommandSearch 側に置くか Ghrepo 側に置くか"* | Instruction to search the vault (search → recall) for past decisions on that question and report them **with note paths**; if none found, say so explicitly rather than guessing. Purpose: avoid re-deciding something already settled. |
| `recall_topic` | `topic` | Instruction to summarise what the vault already knows about that topic. Broader than `prior_art`, which is decision-dedup only. |

**Failure mode:** invoking `/om:prior_art` with no argument fails at `prompts/get` because `question` is `required: true`. The error surfaces as `detail withheld on this connection` — a generic message (the server hides stderr detail), **not** a connection problem. Fix: select from the menu, then type the decision text. `om health` reporting green (vault reachable, no warnings, ~25s search latency) confirms the server connection itself is fine.

**`reason` is the slow one.** The rest answer without inference; this one spawns a session, so it takes seconds to minutes. Reach for it when `search` or `recall` returned the notes but not the answer — it seeds itself from search, so there is no need to search first. It runs on your own CLI default model unless `reason.model` pins one, nothing about it is capped, and every call is logged with its cost, turns, model and wall time. Answers land in `.claude/om-reasoning/` marked `confidence: inferred` and are never auto-recorded as memories.

**Debugging it:** call `health` first. Every failure in this layer presents identically as "no results" — a renamed memory folder, a moved launcher, an index registered to a different vault, a session with no identity — and `health` is what tells them apart. A caller reported as `ANONYMOUS` means the client never completed the roots handshake, so only `general`-scope memories are visible.

**Two guards worth knowing:** memories are never served as ordinary notes (they carry their own declared scope), and a memory that would reach nobody is refused rather than silently widened to `general`.

### Repo-side `CLAUDE.md` snippet (step 2 of the install)

The consuming repo also needs a short section in its **own** `CLAUDE.md` — not garnish. Measured: server wired but no repo-side instruction → the session made **zero** vault calls and implemented a design the vault had recorded as rejected. The asymmetry: an MCP `instructions` **prohibition** propagates reliably; a positive "go consult the vault" is advisory and loses to any nearer source. So write it as the repo's own law — imperative/prohibitive, with concrete triggers. The repo ships no copy-paste snippet (`ARCHITECTURE.md` §*Reaching the Vault From Another Repo* only says "add a short section"); this is that snippet.

**Minimal form** (usually enough):

```markdown
## 個人ナレッジボールト（om MCP）

`om` MCP 経由で個人 Obsidian ボールトが接続されている。過去の意思決定・不採用設計・調査済み前例の記録。

- 過去の判断／「なぜこうなっているか」／検討済みかに関わる問いに答える前に、必ず `om` の `search` / `recall` を呼ぶ。会話の記憶ではなくボールトが記録。
- 設計・アーキテクチャを確定する前に `recall`（このリポジトリにスコープされた教訓）を確認する。ボールトが却下と記録した設計は実装せず、該当ノートを引用して指摘する。
- 引用したらノートのパスを明記。`as of YYYY-MM-DD` / `(inferred)` / `(TBC)` の限定子は保持し、推測を断定に格上げしない。
```

**Stronger form** — fold prohibitive lines into the project's existing "Laws"/"Rules" section (nearest source wins, so it must be part of that law set):

```markdown
- **ボールト優先**: 設計判断・命名・スキーマ・公開契約を決める前に `om` の `recall` と `search` を呼ぶこと。`deprecated` / `rejected` と記録された選択肢を、確認せず採用してはならない。違反は過去に「却下済み設計をそのまま実装」という手戻りを生んでいる。
- **判断が要るときは `om reason`**: 複数ノートにまたがる整合性の問い（「この方針は既存の決定と矛盾しないか」）は `reason` に投げる。
- **セッション成果物をコミットに入れない**: claude.ai セッション URL・`Claude-Session:` トレーラー・ローカル絶対パスをコミットメッセージ・PR/issue 本文・レビューコメント・ファイルに書かない（`Co-Authored-By:` は可）。
```

**Writing tips:**

| do | why |
|----|-----|
| Imperative/prohibitive, not advisory ("参照せよ／〜してはならない", never "参照するとよい") | positive advice is skipped when a nearer source exists; prohibitions survived even an authority-override in testing |
| Put it in the project's existing rule section | "nearest source wins" — make it part of that law set |
| Concrete triggers ("設計を確定する前", "命名を決める前") | "関連するとき" never fires |
| One line each for `search` / `recall` / `reason` | prevents the "unsure which to call → don't call" failure |
| Optionally state: do **not** register the raw `qmd` server | it ignores memory scope and matches lessons meant for other projects |

Full setup, which notes the server serves, and the required repo-side snippet: `CLAUDE.md` § *Reaching the Vault From Another Repo*. How the whole layer works — the four MCP surfaces, the identity handshake, a `search` call end to end, memory-visibility evaluation, the write path: `ARCHITECTURE.md` § *Reaching the Vault From Another Repo*.

## Workflow: Weekly Review

1. **`/om-weekly`** — synthesize the week's activity, check alignment, find patterns
2. Promote any uncaptured wins to brag doc
3. Update North Star if focus shifted
4. **`/om-wrap-up`** — close the session cleanly

## Workflow: Full Review Cycle Prep

1. **`/om-review-brief manager`** — generate the manager context transfer doc
2. **`/om-review-brief peers`** — generate the peer context transfer doc
3. **`/om-peer-scan`** (parallel, one per peer) — deep scan each peer's PRs
4. **`/om-slack-scan`** — scan relevant channels for your own evidence + peer context
5. **`/om-capture-1on1`** — capture the review 1:1 with your manager
6. **`/om-vault-audit`** — tidy up after all the new data

## Workflow: Project Ramp-Up

1. **`/om-slack-scan`** — scan project channels for history and decisions
2. **`/om-peer-scan`** (if needed) — understand what teammates have already built
3. Create work note from gathered context
4. **`/om-vault-audit`** — ensure everything links properly
