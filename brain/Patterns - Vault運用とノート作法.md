---
date: 2026-09-13
description: "Vault運用とノート作法のパターン — ノート管理フレームワーク、作業停止・再開、スタブノートの限界、vault再分類、タグ運用、サブエージェント活用、一括作成時のfrontmatter欠落。Patternsから分割（verbatim）。"
tags:
  - brain
---

Domain note split from [[Patterns]] (2026-09-13, 25KB threshold). 内容は verbatim、物理順を保持。

## ノート管理フレームワーク（脳のOS）

| ゾーン | 比喩 | 役割 |
|--------|------|------|
| Project | 厨房 | 今、手を動かす場所 |
| Knowledge | 脳 | 自分のOS・判断基準 |
| Reference | 書庫 | 道具箱・資料 |
| Asset | 倉庫 | 素材・材料 |

- **Project**: 今動いているものだけ。終わったら完了フォルダへ → `work/active/`（索引は [[Index|work/Index]]）
- **Knowledge**: 学びのメモ、個人的な哲学、フレームワーク集 → `brain/`（索引は [[Memories]]）
- **Reference**: 道具・資料・コマンドリファレンス → `reference/`

## 作業停止・再開パターン（2026-05-04 週次サマリーより）

- **GW等の長期休暇期間** — コミットゼロは正常。週次サマリーで振り返るだけでよい
- **全タスク停止のデバッグ** — 複数タスクが同時に「詰まっている」と感じたときは、共通ブロッカー1点を先に特定する（例: ドキュメント生成方法が未決定のまま全TECSタスクがブロックされていた → 決定後に全タスクが前進）

## スタブノートの機能限界

- `work/active/` にリンクなし・コンテキストなしのスタブノートが多数あっても、グラフ上では孤立ノードであり実質機能しない
- `quarter` フィールドがないと Work Dashboard Base に表示されない
- 最低限 `[[North Star]]` へのリンクを持つこと

## vault再分類ワークフロー

### 特殊フォルダの役割

- `Clippings/`: Obsidian Web Clipperの未処理inbox。`title`と`source`を保持し、triage後に適切な`reference/`配下へ移します。
- `Clippings-Kindle/`: Kindle highlightの自動export置き場。bulk生成物として扱い、必要なfrontmatterはscriptで補完します。
- `copilot/`: Obsidian Copilotのcustom prompt。user contentとしてGit追跡対象にします。
- `scripts/`: vault maintenance用script。ノート本文の配置先としては使用しません。

大量ファイルの `reference/` → サブフォルダへの再分類を行うとき。

- **Obsidian内で移動**: Obsidian のファイルエクスプローラーでフォルダごと移動すると、wikilink が自動更新される（ファイルシステム直操作は wikilink を壊す）
- **コミット前確認**: `git status` でリネーム追跡（`R`）が検出されていれば git が移動を認識している。`D + ??` ペアになっている場合は `git mv` 相当として扱われず履歴が切れるため、`git add -u` と `git add <new>` の両方を実行してステージングする
- **wikilink のパス除去**: 移動後は `[[reference/Note/X]]` → `[[X]]` に正規化（Obsidian は note 名だけで解決するため）。brag doc や competency の Related などに残った旧パス付きリンクを検索して修正する
- **.gitignore 見直し**: 新しいプラグインフォルダ（`.obsidian/plugins/xxx/`）は plugin バイナリなので除外対象。ユーザコンテンツフォルダ（`copilot/` 等）は追跡対象
- **適用例**: `reference/` 77件 → `Note/` 13サブフォルダへ再分類（2026-06-04）。git rename として正しくトラック済み
- **出典**: git `chore: vault再編成`, [[perf/brag/Q2 2026]]

## Claude サブエージェント活用パターン

- **文章チェック用サブエージェント** — コーディング時の linter 的に使う発想。レビュー・校正を並列エージェントに委譲することで品質ゲートを自動化できる（出典: reference/Inbox/AIAU-雑談(ai)、フォルダ廃止済み）

## Obsidian タグ運用原則

- タグの目的を明確にし一貫したルールを定める: 種類（`work-note`, `decision`）・テーマ・状態（`active`, `completed`）の3軸
- 階層タグ（`project/auth-refactor` など）で粒度と分類の柔軟性を両立
- リンクだけでは捉えきれない「属性によるグルーピング」にタグを使う

## 一括ノート作成はフロントマターを省略しがち

`/om-` 形式の検証パス（作成時にfrontmatter・wikilinkチェックを通す通常のノート作成フロー）を経ずに、ツール調査メモ・クリッピング等をまとめて大量作成すると、frontmatter（`date`・`description`・`tags`）が省略されたまま残りやすい。

- **再現パターン**: 2026-08-27頃、`reference/Note/AI開発/Agent開発/` 配下にツールリファレンスメモ十数〜二十数件を一括作成 → 2026-08-28の `/om-wrap-up` で3件（`AI-Agents-六色思考帽フレームワーク`・`dahatake skills`・`dahatake skills graphrag`）のfrontmatter欠落を検出・修正。同じフォルダへの追加バッチ作成が2026-08-29に発生 → 2026-08-30の `/om-wrap-up` で新たに24件のfrontmatter欠落を検出・一括修正。**同一フォルダ・同一原因で2回連続**して発生した。
- **共通点**: いずれもURLや断片メモを素早く書き留める形式（1〜数行の箇条書き、frontmatterなし）で、通常の「ノート作成」ワークフロー（テンプレート適用 → frontmatter記入 → リンク付け）を通っていない。作成そのものは高速だが、`/om-wrap-up` まで欠落に気づかれない。
- **示唆**: 検出は毎回できているが、発生自体は防げていない。バッチ作成の入口（新規ツール調査メモの量産）に軽量な検証を差し込む、または `/om-tidy` のスコープに「frontmatter欠落の一括検出」を明示的に含めることを検討する余地がある。
- **出典**: [[Memories]]（2026-08-28・2026-08-30エントリ）, `reference/Note/AI開発/Agent開発/` 配下の一括修正差分
- **2026-08-30、示唆を実行**: `/om-tidy` の処理範囲にfrontmatter sweepを明示的なステップ4として追加（`.claude/commands/om-tidy.md`）。同日の初回実行で`work/`・`brain/`・`perf/`・`org/`・`reference/`全体から78件の既存debtを検出——**検出範囲は広がったが、発生自体は依然防げていない**ことが確認された。
- **2026-09-02、4回目の発生・パターンがフォルダ限定ではないと判明**: `reference/Note/PC/{UniGet.md, uv-tool.md}`・`reference/Note/AI開発/Agent開発/Agent-Skill/agent-skill-4.md`・新設`reference/Note/Study/数学-圏論.md`の4件が同一の未置換`{{date}}`テンプレートのまま出現（`/om-wrap-up`で検出・修正）。従来は`reference/Note/AI開発/Agent開発/`という単一フォルダの反復と見えていたが、今回は3つの異なるフォルダ（うち1つは新設）にまたがって発生——**原因はフォルダではなく「Obsidian側でテンプレート挿入コマンドを経由せずファイルを素早く作成する」という作成手段そのもの**だと確定できた。`PC/uv-tool.md`はさらに、既存の`Python開発/uv-tool.md`と同名衝突を起こし`uv-tool-2.md`側のリンクを曖昧化させる副作用も持っていた（`uv-tool-3.md`として正しい系列へ移動して解消）。sweepステップ追加後も発生が止まらないことから、防止策はvault側の検出強化では届かず、Obsidian側のノート作成フロー（テンプレート挿入をデフォルト化する等）に手を入れない限り再発し続けると判断する。

## Related

- [[Patterns]] — 索引
