---
date: 2026-07-27
description: "自作 Python CLI 群（ghrepo・gistx・gitreporemote）が共通利用する基盤ライブラリ yklibpy のハブノート。提供コンポーネント・モジュール構成・仕様書の所在"
project: yklibpy
status: active
quarter: Q3-2026
tags:
  - work-note
---

# yklibpy

自作 Python CLI アプリ群が共通利用する基盤ライブラリ。[[ghrepo]]・[[gistx]]・[[gitreporemote]] はいずれもこのライブラリの上に構築されており、[[Patterns - 仕様書と実装#ghrepo 型 Python CLI パターン（仕様書駆動）|ghrepo 型 CLI パターン]]の「共通基盤」層を担う。

このノートは3つの作業ノートから参照される `[[yklibpy]]` リンクの解決先として作成したハブ（2026-07-27）。ライブラリ本体の詳細仕様は下記の仕様書ツリーにあり、ここでは所在と全体像のみを扱う。

## 提供コンポーネント

作業ノート側で依存が明記されているもの:

| コンポーネント | 用途 | 利用元 |
|---|---|---|
| `AppStore` / `Storex` | 設定・データの永続化（YAML 読み書きの委譲先） | ghrepo・gistx |
| `AppConfig` | アプリ設定の基底 | ghrepo |
| `Cli` / `Command` | サブコマンドのディスパッチ基盤（各アプリの `Command*` クラスが継承） | ghrepo |
| `CommandGhUser` | GitHub ユーザー操作 | ghrepo |
| `Loggerx` | ロギング | ghrepo・gistx |
| `Timex` | 時刻処理 | gistx |

## モジュール構成

内部仕様書から確認できるツリー:

```
src/yklibpy/
├── common/      util.py / util_yaml.py / env.py
├── db/          db_yaml.py / storex.py
├── htmlparser/  app.py / configprepare.py / preparex.py
└── tomlop/      tomlop.py
```

## 仕様書の所在

ライブラリ本体のリポジトリ内 `docs/from_source/spec/internal/` にクラス別内部仕様書がある（`reverse-gen-internal-spec` スキルで生成）。vault 側にあるのは検査結果のみ:

- [[reference/Note/yklibpy/内部仕様書-矛盾点|内部仕様書-矛盾点]] — `internal-spec-contradiction-check` の出力。`util_yaml.md` の `_register_constructors` 処理フロー記述とソースの不一致を1件検出
- [[reference/Note/yklibpy/内部仕様書-誤字・脱字・表記の揺れ|内部仕様書-誤字・脱字・表記の揺れ]] — `internal-spec-notation-check` の出力。`htmlparser/app.md` の `sequence` 取得元の脱字、未使用インスタンス変数の注記漏れを検出

> [!warning] 未記録
> yklibpy 本体のソース／リポジトリのローカルパスが vault 内のどこにも記載されていない。次に触れるセッションで確認し次第ここに追記すること（[[gitreporemote]] の v2 と同じ抜け）。

## Related

- [[ghrepo]] — 同ライブラリ上の GitHub リポジトリ管理 CLI
- [[gistx]] — 同ライブラリ上の gist 管理 CLI
- [[gitreporemote]] — 同ライブラリ上の git remote 情報収集 CLI
- [[Patterns]] — ghrepo 型 CLI パターンの定式化
- [[Skills]] — 仕様書生成・検査スキル（`reverse-gen-internal-spec` 等）
