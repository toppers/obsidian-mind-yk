---
date: 2026-09-13
description: "仕様書作成と実装のパターン — コードベース直読みでの仕様書作成、ghrepo型Python CLI、実装言語別分類、多分岐仕様書ツリーの派生。Patternsから分割（verbatim）。"
tags:
  - brain
---

Domain note split from [[Patterns]] (2026-09-13, 25KB threshold). 内容は verbatim、物理順を保持。

## コードベース直読み仕様書作成パターン

- **採用文脈**: NotebookLM・RST変換ツール等の中間ツールなし。Claude Code がソースコードを直接読み、仕様書を生成する
- **適用例**: tecsgen 外部仕様（17KB・420行超）・内部仕様（25KB・530行超）を1日でスクラッチ作成（2026-05-19）
- **利点**: ツール設定コストゼロ・コードと仕様の乖離なし・反復修正が高速
- **適用条件**: コードベースが Claude のコンテキストウィンドウに収まる規模、または対象モジュールを絞れる場合
- **出典**: [[work/active/tecs/TECS開発]], [[tecsgen外部仕様]], [[tecsgen内部仕様]], git `8b5ebd7`

## ghrepo 型 Python CLI パターン（仕様書駆動）

**ghrepo のプログラム構造**を、サブコマンドを持つ Python CLI の canonical パターンとして使う。

```
エントリーポイント層  ghrepo.py / main() — Clix で引数パース → ディスパッチ
CLI定義層           Clix (clix.py)      — argparse 定義のみ、ロジックなし
コマンド実行層      CommandXxx          — yklibpy.command.Command 継承
設定・ストレージ層  AppConfigx + yklibpy.AppStore/Storex
```

**スキル連携（仕様書駆動フロー）**:

```
docs/req/idea/*.md  (アイデアレベルの要件)
    ↓ python-cli-req-to-external-spec スキル
docs/req/detail/*.md (詳細要件)
    ↓ python-cli-external-spec スキル  (ghrepo-external-spec)
外部仕様書 (docs/spec/external.md)
    ↓ python-cli-internal-spec スキル
内部仕様書 (docs/spec/internal.md)
```

- **採用文脈**: [[ghrepo]]・[[gistx]]・[[gitreporemote]]・[[calibrex]]・[[filelist]] 等、Python CLI プロジェクト全般
- **適用条件**: サブコマンドを持つ CLI、yklibpy を共通基盤として使うプロジェクト
- **出典**: [[ghrepo]], [[gistx]], [[gitreporemote]], `reference/Inbox/仕様書駆動の取り組み.md`（2026-06-04）

## プロジェクト実装言語別分類（2026-04-11 時点）

### Ruby 実装
- [[bookinfor]], [[bookmarkr]], [[cpiconfiles]]

### Python 実装
| 状態 | プロジェクト |
|------|-------------|
| 済 | [[ghrepo]], [[gistx]], [[calibrex]] |
| 未済 | [[filelist]], [[gitreporemote]], [[notebooklmclix]] |

## 多分岐仕様書ツリーの派生パターン（2026-09-05）

1つの外部仕様から、実装方式ごとに複数の代替内部仕様を分岐させて執筆するワークフロー。

- **系譜**: [[TECSCDE外部仕様]]（ブラウザ版） → [[TECSCDE内部仕様]]（関数/interfaceベース、実装済み）／[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]（クラスベース代替案）。さらに[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（デスクトップ版、Electron/Tauri言語非依存） → [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]（Electron/TS）／[[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]]（Tauri/Rust）と枝分かれ。1セッションで4文書・計49ファイルを執筆。
- **執筆手順（毎回同じ形）**: ①既存の姉妹文書群を全章読み込み、差分が生じる章と生じない章を仕分ける ②新文書の目次冒頭に「文書状態」callout で位置づけ・採用方針・姉妹文書との対応表を明記 ③差分が小さい章は全文複製せず「姉妹文書と同一、変更なし」+ 一次情報源へのリンクのみで済ませる（単一情報源の原則を保つ） ④差分が大きい章のみ実装コード例つきで詳述する。
- **章番号ずれの罠**: 元文書の章を1つ統合・省略すると（例: TECSCDE-TS内部仕様でCDLパーサ章をモジュール構成章に統合）、それ以降の章番号が1つずれる。目次・各章の相互参照・前方参照（「本書第N章で扱う」）を**同じ編集パスで全て直さないと、後から章を書き足すときに矛盾が露呈する**（本セッションで実際に発生し、第4章執筆時に気づいて目次・第1章を修正した）。
- **言語・フレームワークによる設計転換は機械的な置換で済まない**: TypeScriptの`class`ベース設計をRustへ「移植」する際、Rustに継承がないため単純な文法変換ではなく、コンポジション（別structへの分離）や所有権システムによる不変性の言い換えが必要だった。「同じ設計思想を別言語のイディオムで表現し直す」という作業自体を明示的な章（第1章）で扱うと、読み手が「単なる翻訳」と誤解しない。
- **各文書は「対応する実装は存在しない、採否は未決定」と明記**——複数の代替設計を書くことは実装への昇格を意味しない。North Starには追加せず、検討中の設計案として`work/active/`に留め置く。
- **出典**: 2026-09-05セッション、[[Memories]]同日エントリ

## Related

- [[Patterns]] — 索引
