---
date: 2026-08-12
description: "独自スキル群のSKILL.md分割マッピング表 — どのSKILL.mdがどの見出しをどのファイルへ分割したか、~/.agents/skills/実体で検証済み"
tags:
  - reference
  - ai
  - agents
---

# Agent Skill 分割マッピング表

> 関連: [[agent-skill|Agent Skill 調査メモ]] / [[AI-Agents|AI エージェント]]

[[agent-skill|Agent Skill 調査メモ]] のO/Xリストで挙げた独自スキル群のうち、SKILL.md本体から一部の見出しを別ファイルへ分割済みのものの対応表。`~/.agents/skills/<skill>/` の実ファイル構成と突き合わせて検証・訂正済み（2026-08-12）。

| SKILL.md | 分割した見出し | 新規ファイル |
|---|---|---|
| class-external-spec-to-code | 言語別の実装ガイドライン / 品質ガイドライン | `implementation_guidelines.md` / `quality_guidelines.md` |
| class-internal-spec-to-code | 言語別の実装ガイドライン / 品質ガイドライン | `implementation_guidelines.md` / `quality_guidelines.md` |
| internal-spec-to-code | 言語別の実装ガイドライン / 品質ガイドライン | `implementation_guidelines.md` / `quality_guidelines.md` |
| export-skills-csv | 品質ガイドライン | `quality_guidelines.md` |
| gen-class-dependency-diagram | 品質ガイドライン | `quality_guidelines.md` |
| forward-gen-cli-external-spec | 要求定義書 / 要求定義書読み込み手順 / 仕様書テンプレート / 品質ガイドライン | `req_def.md` / `load_req_def.md` / `spec_external_template.md` / `quality_guidelines.md` |
| gen-external-spec-index | インデックスのフォーマット / 品質ガイドライン | `index_format.md` / `quality_guidelines.md` |
| gen-internal-spec-index | インデックスのフォーマット / 品質ガイドライン | `index_format.md` / `quality_guidelines.md` |
| python-cli-req-to-external-spec | ghrepo型外部仕様への写像（テンプレート規則） / 仕様書テンプレート | `class_mapping_rules.md` / `spec_external_template.md` |
| reverse-gen-internal-spec | インデックスのフォーマット / 仕様書テンプレート / 品質ガイドライン | `index_format.md` / `spec_external_template.md` / `quality_guidelines.md` |

## 訂正内容（元の生テーブル貼り付けとの差分）

- `gen-external-spec-index` / `gen-internal-spec-index`: 実ファイル名は `index_template.md` ではなく `index_format.md`
- `python-cli-req-to-external-spec`: 実ファイル名は `spec_format_rules.md` ではなく `spec_external_template.md`
- `forward-gen-cli-external-spec`: `req_def.md`・`load_req_def.md` の2件が元表から欠落していたため追加
- `reverse-gen-internal-spec`: `index_format.md`・`spec_external_template.md` の2件が元表から欠落していたため追加（元表は `quality_guidelines.md` のみ）

## Related

- [[agent-skill|Agent Skill 調査メモ]]
- [[技術文書化]] — 既存記載を実体（ファイルシステム）と突き合わせて検証・訂正した competency 証拠
