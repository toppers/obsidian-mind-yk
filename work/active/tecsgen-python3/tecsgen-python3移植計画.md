---
date: 2026-09-26
description: "Ruby版tecsgen（v1.9.1）をPython3へ移植する計画。Rubyを正解とする差分テストを軸に、パーサ→モデル→意味解析→生成→プラグインの順で段階的に移す。規模実測と主要リスク付き"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3 移植計画

[[tecsgen-python3]] の実行計画。移植元の仕様は [[tecsgen内部仕様]]（全12章、検証済み）、[[tecsgen外部仕様]]、[[tecsgen-plugins]]。参照ノート: `reference/Note/TECS-WG/tecsgen/tecsgen-tecsgen.md`（graphify 解析。God Nodes は Celltype・Cell・Inline・CELLIDX）、`reference/Note/0-TECS/TECS-MEMO/tecsgen-VCS*.md`（版の履歴）、[[reference/tecsgen_ruby_global_variables.csv]]・[[reference/tecsgen_ruby_toplevel_methods.csv]]（全数走査の生データ）。

## 基本方針

1. **正解は Ruby 版の実行結果**。移植の受入基準は、同じ入力に対して `gen/` 以下の生成物がバイト単位で一致し、エラー／警告コード・件数・終了コードも一致すること（[[tecsgen-python3外部仕様]] 4章・7章の一致要件）。
2. **差分テストを先に作る**。Ruby 4.0.6 はローカルで動く（2026-09-26 確認）。`test/` の104ケースを Ruby 版で実行し、ゴールデン出力として固定してから移植を始める。
3. **フェーズごとに内部状態を比べる**。生成物の一致だけを見ると、どのフェーズでずれたかが分からない。Ruby 側に小さな JSON ダンプ用フックを足し、パース後・意味解析後・最適化後のモデルを Python 側と比べる。
4. **仕様書は実装の少し前に書く**。[[tecsgen-python3内部仕様]] は章ごとに、該当フェーズに着手する直前に書く。12章を全部書いてから実装に入る進め方はとらない。
5. **WSL での検証は必ず `tools/port/wsl_check.ps1` で行う**（2026-09-28 ユーザー採用）。`wsl.exe -e bash -lc "..."` をその場で手書きしない。このスクリプトは、WSL 用の仮想環境の分離（`~/.venvs/tecsgen-python3`）、`VIRTUAL_ENV` の解除、パス変換、`uv sync`・ruff・ty・pytest の一括実行と結果のまとめ表示を済ませている。各フェーズの計画には「完了時に `pwsh tools/port/wsl_check.ps1` を通す」を検証手順として入れる。スクリプトに無い操作（例: WSL で `tools/port/p4_progress.py` を回す、特定ケースだけ実行する）が必要になったら、手書きで済ませずにスクリプトへオプションとして足してから使い、README の表も更新する。
   - 経緯: P5e〜P5i のセッションで、このスクリプトの存在を見落として WSL コマンドを毎回手書きし、Windows 側と共有の `.venv` を作り直させて1回失敗、さらに場当たりの別の仮想環境（`~/.cache/tecsgen-python3-venv`）まで作った。

## 規模（実測 2026-09-26、`branches/ykominami_r3033/tecsgen`）

| 領域 | ファイル数 | 行数 | 備考 |
|---|---|---|---|
| `tecslib/core` | 22 | 21,726 | 自動生成の `bnf.tab.rb`（5,170行）と `C_parser.tab.rb` を含む。`generate.rb` 5,399行、`bnf.y.rb` 2,211行 |
| `tecslib/core/componentobj` | 19 | 8,100 | Cell・Join・Celltype など |
| `tecslib/core/syntaxobj` | 9 | 1,414 | |
| `tecslib/plugin` | 78 | 15,973 | 標準付属プラグイン |
| `cdelib` / `flowlib` | 8 / 3 | 5,009 / 3,422 | 旧 TECSCDE 用(`cdelib`)は対象外。`flowlib` は tcflow・tecsflow として移植済み(下の「移植済み」) |
| トップレベル `*.rb` | 6 | 2,062 | `tecsgen.rb`・`tecsmerge.rb` など |

自動生成されたパーサテーブルを除くと、移植対象は本体が約2.5万行、プラグインが約1.6万行。

## スコープ

- **対象**: `tecsgen` 本体（CLI・構文解析・意味解析・最適化・コード生成）と標準プラグイン
- **移植済み（P6d、2026-10-02。2026-10-14 に周辺ケース19件を追加検証）**: `tecsmerge`（`tecsgen/tecsmerge.py`）。複数ソース・長いオプション形・省略形・引数の欠けたオプション等を Ruby 版から採取して突き合わせ、`--version`（Ruby 版は「version unknown」で終了）と、オプション解析エラー後に処理が続く挙動（残りの引数で `dst` を判定し、無ければ `error: : not found`）の2件の食い違いを修正。正解データは計91件、全テスト 1117 件通過
- **移植済み（2026-10-15）**: `tecsgen_rcov`（`tecsgen/tecsgen_rcov.py`）。Ruby 版は SimpleCov を起動して `tecsgen` を読むだけの開発用ラッパー。Python 版は coverage.py を起動して `cli.run` を呼ぶ（依存は `dev` グループ。無ければ終了コード 1）。`simplecov begin`/`end` の出力と終了コードは Ruby 版どおり、記録は `.coverage` に追記・HTML は `coverage/`。レポート自体は coverage.py なので Ruby 版と比べない。テスト `tests/test_p8_tecsgen_rcov.py`、全テスト 1119 passed・102 skipped（Windows、tecsflow 取り込み後）。Python リポジトリの PR #5（`ykominami/tecsgen-python3-yk`、マージコミット `fbdba8d`）で `main` にマージ済み（2026-10-15）
- **移植済み（2026-10-14）**: `tecsflow`（`tecsgen/tecsflow.py`、`core/unjoin_plugin.py`）。当初は後回しだったが、ユーザー決定（2026-10-14）で移植した。モデルの受け渡しは Marshal の `tecsgen.rbdmp` ではなく、tecsgen が書く pickle（`gen/tecsgen.pickle`）。TECS の test/ の 8 ケースで標準出力・標準エラー出力・終了コードが Ruby 版と一致（`tests/test_p8_tecsflow.py`）、WSL の `wsl_check.sh` 全通過（1101 passed・99 skipped）。Python リポジトリの PR #3（`ykominami/tecsgen-python3-yk`、マージコミット `85731c2`）で `main` にマージ済み（2026-10-14）。詳細: [[tecsgen-python3 tecsflow・Marshal調査]]
- **移植済み（2026-10-13）**: `tcflow`（`tecsgen/tcflow.py` と `tecsgen/flowlib/`）。Ruby 版と標準出力・標準エラー出力・終了コード・関数リストが一致（合成した正解データ36ケース。実在の C ソースでは、cpp なしの 220 ファイル(WSL・Ruby 3.2.3)と 60 ファイル(Windows・Ruby 4.0.6)、cpp 経由(`gcc -E`、WSL)の 400 ファイル(関数 2397 個、関数5個以上のファイル 257 件)で不一致なし。WSL の `wsl_check.sh` も全通過(1090 passed・99 skipped。as of 2026-10-14)。ただし 400 ファイルのうち構文エラーなしは 15 件で、大半は glibc ヘッダ等に由来する 2〜4 件の構文エラーを含む。エラー出力と回復の一致は確認できたが、エラーなしの入力は少ない）。関数リストの保存は Marshal ではなく JSON（`gen/tcflow.json`、決定は [[tecsgen-python3 tecsflow・Marshal調査#tcflow の保存形式(2026-10-13、決定)|調査ノート]]）
- **対象外**: `cdelib`（旧 TECSCDE。TS 版の [[TECSCDE-JS-TS実装]] が置き換える）
- **移植しないコア機能（2026-10-10 確認、tecsgen-rb 基準）**: `unjoin_plugin.rb` は Ruby 版でも呼び出し元が `dump_tecsgen_rbdmp` だけ（`Marshal.dump` のためにプラグイン参照を外す）で、`tecsgen.rbdmp` を再現しない Python 版では観測できる効果がなかった（**2026-10-14 訂正**: tecsflow 移植に伴い、同じ役割を `core/unjoin_plugin.py` の `UnjoinPickler` として移植した）。`gen_xml.rb` は `require` されるだけで、呼び出し箇所（`Region.gen_xml`・`Namespace.gen_XML`）がコメントアウトされた未使用コード。いずれも移植しない（Python 版 PR #15 で `dump_tecsgen_rbdmp` の docstring を修正済み）。標準プラグイン 85 本のうち Python 版に無いのは `HRP2Cache`・`HRP2PostHook`（動かす経路が無く対象外）の 2 本だけ
- **後方互換を切る点（決定事項として記録する）**: 利用者が Ruby で書いたプラグインは Python 版では動かない（`-L` で探すのは `<クラス名>.py`。環境変数 `RUBYLIB` は対応しない。2026-10-01 決定、[[tecsgen-python3 -L ユーザプラグイン探索設計]]）。`tecsgen.rbdmp`（Ruby の `Marshal` 形式）は再現しない（代わりに `tecsgen.pickle` を書く。2026-10-14 変更、上の tecsflow の項）
- **tecsflow を移植して pickle で dump する場合の `unjoin_plugin` 相当**（2026-10-14 実装済み）: 生きたオブジェクトを書き換える代わりに、`pickle.Pickler` のサブクラスの `reducer_override` で dump 用の状態だけ差し替える（`__getstate__` ではない）。`Proc` 相当と残存 Plugin は `None` に置換 → [[tecsgen-python3 tecsflow・Marshal調査#pickle 形式で dump する場合の `unjoin_plugin` 相当の設計(2026-10-14、実装済み)|設計メモ]]

## フェーズ

### P0〜P2（完了） — 詳細は [[tecsgen-python3移植計画 Archive — P0–P2]]

- **P0 準備と方針決定**（2026-09-26 完了）: リポジトリ整備、正解データ採取（WSL・`svn export --native-eol LF`、157ケース中155件）、CLI 完全互換・多重継承・設定オブジェクト・1ファイル対1モジュールの決定
- **P1 基盤**（2026-09-27、`2a281c4`）: Node・エラー処理・メッセージ・入出力・`context.py`・`ruby_compat.py`。Ruby を実行するオラクルとの差分テストで検証
- **P2 構文解析のフロントエンド**（2026-09-27、`db3cb47`・`1b88fdb`・`6d69710`）: tree-sitter をやめ racc 表駆動へ（[[tecsgen-python3 構文解析方式決定]]）。字句解析・駆動部・構文エラー出力が全155ケースで一致

### P3〜P4（完了） — 詳細は [[tecsgen-python3移植計画 Archive — P3–P4]]

- **P3 型・値・式・コンポーネントモデルと意味解析**（2026-09-27）: プラグインを使わない119ケースで、意味解析後のモデル JSON とエラー集合が Ruby 版と一致 → [[tecsgen-python3移植計画 Archive — P3–P4#P3 型・値・式・コンポーネントモデルと意味解析|P3]]
- **P4 最適化とコード生成**（2026-09-27、`3964ec3`）: プラグインを使わない119ケースで `gen/` がバイト単位で一致 → [[tecsgen-python3移植計画 Archive — P3–P4#P4 最適化とコード生成|P4]]

### P5 プラグイン機構と標準プラグイン（完了） — 詳細は [[tecsgen-python3移植計画 Archive — P5]]

- プラグイン基盤・標準プラグイン・カーネル依存系・`-L` による利用者プラグイン探索を移植。プラグインありの全63ケース、プラグインなし119/119が Ruby 版と一致（as of 2026-10-03）。未移植は標準プラグイン85本のうち `HRP2Cache`・`HRP2PostHook`（動かす経路が無く対象外）の2本。段階ごとの記録は [[tecsgen-python3移植計画 — P5 進捗ログ]]

### P6 仕上げ（完了） — 詳細は [[tecsgen-python3移植計画 Archive — P6]]

- **P6a〜P6e**（2026-10-02 完了、`main` にマージ済み）: 配布（標準 CDL ライブラリの同梱）・CLI（`--help`・`--version` が Ruby 版とバイト一致）・実プロジェクトの差分テスト（カーネル・配布パッケージの正解データ）・`tecsmerge`（73シナリオ一致）・仕様書の完成（外部仕様10章・内部仕様12章）。TBC は 2026-10-04 までにすべて解消 → [[tecsgen-python3移植計画 Archive — P6|P6]]

### P7 cmake 対応と正解データの基準の切り替え（2026-10-05） — 詳細は [[tecsgen-python3移植計画 — P7 cmake対応]]

cmake 対応（`CMakeLists.tecsgen.cmake`・`CMake` API・`TransparentRPCSignaturePlugin`）と、正解データの基準の r3304 から tecsgen-rb への切り替え。プラグインなし119/119・あり77/77 一致。未了（as of 2026-10-10）: 実機（書込み・起動）の確認、実際の CubeMX 生成物でのビルド、H533・C562 への TECS 展開後の確認（現状は TECS 不使用で対象外のため保留。展開されたら実施。2026-10-19 に表現を整理）。（`transparent_marshaler` ケースの扱いは 2026-10-05 に決定済み。[[tecsgen-python3 cmake対応計画#決定事項（2026-10-05、ユーザー決定）|決定6]]、2026-10-19 に表現を整理）

### P8 周辺ツールの移植（2026-10-13〜15、完了）

`tcflow`・`tecsflow`・`tecsgen_rcov` を移植し、`tecsmerge` の周辺ケースを追加で検証した。Python 版リポジトリのコミットメッセージは `tcflow` を「P7」、`tecsflow` を「P8」と呼んでおり、本計画の P7（cmake 対応）と番号が重なっていた。**2026-10-26 に本計画へ P8 を足して整理した**（コード側の番号は変えない。`tests/test_p8_tecsgen_rcov.py` などの名前も、そのまま）。

- **`tcflow`**（2026-10-13、Python 版 PR #1、`c6eeba9`）: Ruby 版と標準出力・標準エラー出力・終了コード・関数リストが一致。合成した正解データ36ケースと、実在の C ソースでの突き合わせ。
- **`tecsflow`**（2026-10-14、PR #3、`85731c2`）: 当初は後回しだったが、ユーザー決定（2026-10-14）で移植。モデルの受け渡しは Marshal の `tecsgen.rbdmp` ではなく pickle（`gen/tecsgen.pickle`）。調査は [[tecsgen-python3 tecsflow・Marshal調査]]。
- **`tecsmerge` の周辺ケース19件**（2026-10-14、PR #4、`9254878`）: `--version` の挙動と、オプション解析エラー後の処理の続き方の食い違い2件を修正。正解データは計91件。
- **`tecsgen_rcov`**（2026-10-15、PR #5、`fbdba8d`）: Ruby 版は SimpleCov を起動して `tecsgen` を読むだけの開発用ラッパー。Python 版は coverage.py を起動して `cli.run` を呼ぶ。
- **結果**: 移植対象（スコープ節）はすべて移植済み。残る未了は P7 の「実機の確認」「実際の CubeMX 生成物でのビルド」「H533・C562 への TECS 展開後の確認」のみ（as of 2026-10-26）。各ツールの詳細は上の「スコープ」節。

### 次の節目: 0.1.0 のリリース（2026-10-27 決定）

移植対象は P8 までに移し終え、実装リポジトリ（`ykominami/tecsgen-python3-yk`）は 2026-10-15 から動いていない。タグが無く、`pyproject.toml` は `0.1.0` のまま、CHANGELOG の `Unreleased` に P7・P8 を含む全内容がたまっている。区切りを付けるため、次の節目を **`v0.1.0` のタグ** とする。

1. `pwsh tools/port/wsl_check.ps1` を通す（Windows 側の最新は 1119 passed・102 skipped、as of 2026-10-15。今回の再実行は未了）
2. CHANGELOG の `Unreleased` を `0.1.0` として確定する
3. `v0.1.0` のタグを打つ
4. P7 の未了3件（実機の確認、実際の CubeMX 生成物でのビルド、H533・C562 への TECS 展開後の確認）は止める理由にせず、「リリース後の保留項目」として残す（TECS 展開待ちの外部要因）

**未決**: 配布先（PyPI か、`uv tool install` のみか）。今回の節目は GitHub のタグまでとし、配布先は次の節目で決める。

## 主要リスク

| リスク                                    | 影響            | 対策                                                                                   |
| -------------------------------------- | ------------- | ------------------------------------------------------------------------------------ |
| ~~tree-sitter 文法が racc 文法と同じ言語を受理しない~~ | —             | **解消（2026-09-27）**: 実測で食い違いを確認し、racc の表をそのまま使う方式に切り替えた（[[tecsgen-python3 構文解析方式決定]]） |
| パース中の副作用の順序（プラグインのポストコード、名前空間スタック）の再現  | エラー順序・生成物の不一致 | 段階ごとの JSON ダンプで比較する                                                                  |
| 書式の細かな違いで生成物が一致しない                     | 受入基準を満たせない    | ゴールデン出力との差分を CI で常に取る                                                                |
| cpp の環境依存（`import_C`）                  | ゴールデン出力の再現性   | cpp の出力をテスト用の fixture として固定する                                                        |
| プラグインの量（約1.6万行）                        | 期間            | 使用頻度順に移し、カーネル依存のプラグインは後回し                                                            |

## 現状の問題（2026-09-26 確認 → 同日修正済み）

解消済み。詳細は [[tecsgen-python3移植計画 Archive — 現状の問題]]。

## Related

- [[tecsgen-python3]] — 親ノート
- [[tecsgen-python3移植計画 Archive — 現状の問題]] — 解消済みの「現状の問題」の節（2026-10-14 分離）
- [[tecsgen-python3移植計画 Archive — P0–P2]] — 完了済みフェーズ P0〜P2 の詳細（2026-09-27 分離）
- [[tecsgen-python3移植計画 — P5 進捗ログ]] — P5 の段階ごとの進捗（2026-09-28 分離）
- [[tecsgen-python3 P0基本方針決定]] — CLI 互換・多重継承・設定オブジェクト
- [[tecsgen-python3 パッケージ構成決定]] — Ruby と1対1の構成、全ファイルの対応表
- [[tecsgen-python3 構文解析方式決定]] — tree-sitter をやめ racc 表駆動へ（P2）
- [[tecsgen-python3 tree-sitter読み込み方式決定]] — superseded
- [[tecsgen-python3内部仕様]] / [[tecsgen-python3外部仕様]]
- [[tecsgen内部仕様]] / [[tecsgen外部仕様]] / [[tecsgen-plugins]] — 移植元
- [[CDLParser(tree-sitter利用-JS版)]] — 同じ tree-sitter 文法の採用例
- [[TECS開発]]
- [[North Star]] — 2番目の優先項目
