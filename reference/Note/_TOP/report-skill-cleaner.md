---
date: 2026-07-20
description: "skill-cleaner 実行時の生出力 — cce-code-context-engine 等のキャッシュ名と reverse-gen-internal-spec の起動引数"
tags:
  - reference
  - skill
  - log
---

> ツール本体の説明と実行コマンド: [[skill-cleaner]]

cce-code-context-engine-ebb0d4

cce-ghrepo-c2aad4

doc_dir:from_source project:htmlparser src_dir:lib ext:rb /reverse-gen-internal-spec

# doc_dir:from_source project:htmlparser ext:rb internal-to-external-spec

doc_dir:from_source project:htmlparser internal-to-external-spec

forward-gen-external-spec

========
再度 `skill-cleaner` スキルによる解析が完了しました。一連の Description 短縮による影響の比較も含め、最新のレポートを報告します。

---

# 更新版 Skill Cleaner レポート

## 1. Skill Budget (プロンプト予算の変化)
前回と今回の短縮後の状態を比較します。

| 項目 | 短縮前 | 短縮後 | 変化 |
| :--- | :--- | :--- | :--- |
| **全体の使用トークン** | 2,557 トークン | **2,455 トークン** | `-102 トークン` |
| **2% 予算使用率** | 47.0% | **45.1%** | `-1.9%` |
| **説明の合計文字数** | 5,177 文字 | **5,089 文字** | `-88 文字` |
| **残りのプロンプト枠** | 2,883 トークン | **2,985 トークン** | `+102 トークン` |

> [!TIP]
> 複数の Description を大幅に短縮したことにより、全体の使用トークンが約 **102 トークン** 削減され、プロンプト枠に余裕ができました。

---

## 2. Description Candidates (Descriptionが長いスキル)
前回最長（583文字）だった `reverse-gen-internal-spec` がリストから完全に除外されたほか、短縮したスキルは軒並み下位へ移動、または対象外となっています。

* **[obsidian-cli](file:///C:/Users/ykomi/.agents/skills/obsidian-cli/SKILL.md)** (467文字)
* **[goalbuddy:goal-prep](file:///C:/Users/ykomi/.codex/plugins/cache/goalbuddy/goalbuddy/0.4.0/skills/goal-prep/SKILL.md)** (351文字)
* **[documents:documents](file:///C:/Users/ykomi/.codex/plugins/cache/openai-primary-runtime/documents/26.709.11516/skills/documents/SKILL.md)** (313文字)
* **[browser:control-in-app-browser](file:///C:/Users/ykomi/.codex/plugins/cache/openai-bundled/browser/26.707.31428/skills/control-in-app-browser/SKILL.md)** (299文字)
* **[claude-api](file:///C:/Users/ykomi/.agents/skills/claude-api/SKILL.md)** (291文字)
* **[spec-to-code](file:///C:/Users/ykomi/.agents/skills/spec-to-code/SKILL.md)** (288文字)
* ...
* **[forward-gen-external-spec](file:///C:/Users/ykomi/.agents/skills/forward-gen-external-spec/SKILL.md)** (短縮後: 176文字)
* **[forward-gen-cli-external-spec](file:///C:/Users/ykomi/.agents/skills/forward-gen-cli-external-spec/SKILL.md)** (短縮後: 173文字)
* **[external-spec-contradiction-check](file:///C:/Users/ykomi/.agents/skills/external-spec-contradiction-check/SKILL.md)** (短縮後: 158文字)
* **[external-spec-notation-check](file:///C:/Users/ykomi/.agents/skills/external-spec-notation-check/SKILL.md)** (短縮後: 151文字)
* **[internal-to-external-spec](file:///C:/Users/ykomi/.agents/skills/internal-to-external-spec/SKILL.md)** (短縮後: 132文字)
* **[ghrepo-external-spec](file:///C:/Users/ykomi/.agents/skills/ghrepo-external-spec/SKILL.md)** (短縮後: 118文字)

---

## 3. Duplicate Delete Suggestions (重複削除の推奨案)
前回と同様に、プラグインキャッシュの旧バージョン等が重複検出されています。
* **control-chrome** ([v26.623.141536](file:///C:/Users/ykomi/.codex/plugins/cache/openai-bundled/chrome/26.623.141536/skills/control-chrome/SKILL.md)) などの削除を推奨。
* **gh-address-comments**, **gh-fix-ci**, **github**, **yeet** のリモート（`openai-curated-remote`）版の削除を推奨。

---

## 4. Unused Candidates (未使用スキル候補)
過去3ヶ月間の実行履歴（ログ）上で使用実績が検知されなかったスキル候補に変更はありません。

---

### 次のアクション
プロンプト予算枠は **45.1%** になり、さらに最適化されました。
引き続き、他の長文 `description` の短縮や、重複プラグインのクリーンアップなどを行う場合は、ご指示ください。