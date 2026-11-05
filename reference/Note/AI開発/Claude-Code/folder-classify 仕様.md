---
date: 2026-07-05
description: "削除された claude.ai スキル folder-classify の仕様退避。原本一式（SKILL.md・analyze_folders.py・zip）は同フォルダ folder-classify-skill/ に保全済み"
tags:
  - reference
---

# folder-classify 仕様（退避・原本保全済み）

claude.ai の Web スキル folder-classify は 2026-07-03 に削除された。将来 `analyze()` を実装する際に必要な仕様をここに退避する。

**原本一式は [[folder-classify 仕様|このノート]] と同じフォルダの `folder-classify-skill/` に保全済み**（SKILL.md 原文・`scripts/analyze_folders.py`・スキルzip。出所: 2026-07-03 11:22 に Downloads へ保存された `folder-classify.skill.zip`。「注意事項」削除前・一本化後の最終健全版）。

## スキル概要（SKILL.md 原文より）

- 目的: ワークスペース直下のフォルダを分類し、Markdown 表で一覧化する
- 分類ロジックの正（source of truth）は `scripts/analyze_folders.py`。SKILL.md 側に恒常的コードを置かない
- `.git` の有無・リモートの有無・Ruby スクリプトの有無も自動検出して表に反映

## 分類観点

1. 空フォルダ
2. フォルダのみ
3. ファイルのみ
4. ディレクトリ+ファイル

## 注意事項（原文ママ — 2026-07-03 に SKILL.md から削除された仕様）

> - `.git` 以外の隠しディレクトリ（`.github`, `.bundle` など）は「フォルダ」としてカウントするが、`.git` の存在判定には使用しない
> - `git remote` コマンドはタイムアウト5秒で実行し、失敗した場合は `remote=なし` として扱う

## 実装状況と将来実装時のメモ

- `analyze()` は**ダミー実装**（FIXTURE 固定データを返す。対象ディレクトリは見ない）
- 出力契約は `render_table()` / `render_summary()` で確定済み — **本実装時も変更しない**。差し替えるのは `analyze()` のみ（docstring に明記あり）
- シンボリックリンク: 旧仕様「ファイル判定に含めない」は実装（`os.path.isfile` はリンクを辿る）と矛盾していたため、2026-07-03 に**仕様側を削除する判断を実施済み**。本実装時に「含める/含めない」を改めて決めること

## 経緯

- 2026-07-03: 棚卸しチャットで symlink 矛盾行の削除・インラインコードの scripts/ への一本化を実施 → zip を Downloads に保存 → 別チャットで「注意事項」全体を削除 → その後スキル自体を削除
- 2026-07-05: 運用レビューで「仕様がどこにも残っていない」ことが判明し、本ノートに退避（`_inbox/claude 棚卸.md` の質問への回答として）

## Related

- [[Gotchas]] — 仕様と実装の乖離はダミー実装の宣言漏れから始まった
