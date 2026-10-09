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
| `cdelib` / `flowlib` | 8 / 3 | 5,009 / 3,422 | 旧 TECSCDE と tecsflow 用。**初期スコープ外** |
| トップレベル `*.rb` | 6 | 2,062 | `tecsgen.rb`・`tecsmerge.rb` など |

自動生成されたパーサテーブルを除くと、移植対象は本体が約2.5万行、プラグインが約1.6万行。

## スコープ

- **対象**: `tecsgen` 本体（CLI・構文解析・意味解析・最適化・コード生成）と標準プラグイン
- **後回し**: `tecsmerge`、`tecsflow`（flowlib）
- **対象外**: `cdelib`（旧 TECSCDE。TS 版の [[TECSCDE-JS-TS実装]] が置き換える）
- **後方互換を切る点（決定事項として記録する）**: 利用者が Ruby で書いたプラグインは Python 版では動かない（`-L` で探すのは `<クラス名>.py`。環境変数 `RUBYLIB` は対応しない。2026-10-01 決定、[[tecsgen-python3 -L ユーザプラグイン探索設計]]）。`tecsgen.rbdmp`（Ruby の `Marshal` 形式）は再現しない

## フェーズ

### P0〜P2（完了） — 詳細は [[tecsgen-python3移植計画 Archive — P0–P2]]

- **P0 準備と方針決定**（2026-09-26 完了）: リポジトリ整備、正解データ採取（WSL・`svn export --native-eol LF`、157ケース中155件）、CLI 完全互換・多重継承・設定オブジェクト・1ファイル対1モジュールの決定
- **P1 基盤**（2026-09-27、`2a281c4`）: Node・エラー処理・メッセージ・入出力・`context.py`・`ruby_compat.py`。Ruby を実行するオラクルとの差分テストで検証
- **P2 構文解析のフロントエンド**（2026-09-27、`db3cb47`・`1b88fdb`・`6d69710`）: tree-sitter をやめ racc 表駆動へ（[[tecsgen-python3 構文解析方式決定]]）。字句解析・駆動部・構文エラー出力が全155ケースで一致

### P3〜P4（完了） — 詳細は [[tecsgen-python3移植計画 Archive — P3–P4]]

- **P3 型・値・式・コンポーネントモデルと意味解析**（2026-09-27）: プラグインを使わない119ケースで、意味解析後のモデル JSON とエラー集合が Ruby 版と一致 → [[tecsgen-python3移植計画 Archive — P3–P4#P3 型・値・式・コンポーネントモデルと意味解析|P3]]
- **P4 最適化とコード生成**（2026-09-27、`3964ec3`）: プラグインを使わない119ケースで `gen/` がバイト単位で一致 → [[tecsgen-python3移植計画 Archive — P3–P4#P4 最適化とコード生成|P4]]

### P5 プラグイン機構と標準プラグイン

- **最初に**: プラグインを使う35ケースも含めた一致一覧（`p4_progress.py` の拡張）と、1ケースの差分表示をリポジトリに用意する（常設ルール、[[Key Decisions]] 2026-09-27）
- `Plugin` 基底クラスと4種のサブクラス、`MultiPlugin`（`Node` の直下にある。内部仕様 9.5）、`PluginModule#load_plugin` → `importlib` による名前解決
- プラグイン引数の解析、`eval` の利用箇所（`tecslib` のうち24ファイル）の置き換え方を決める（**2026-10-03 訂正**: 24ファイルは `eval_const` などを含む部分文字列の一致数で、Ruby の `eval` の呼び出しは r3033 には無い。置き換えは不要）
- 移植の順序（`test/` での使用頻度で決める）: CelltypePlugin/SignaturePlugin の基本 → Through 系（Trace・RPC・opaqueRPC）→ TECSInfo 系 → Multi → カーネル依存（HRP/HRP2/FMP/HRMP/ATK1）→ mruby 系
- 既知の問題3件（内部仕様 9.7）は**そのまま移植しない**。1件ずつ直すか削除するかを決める
- 各プラグインの仕様は [[tecsgen-plugins]] を移植元として使う

**進捗**: 段階ごとの詳細は [[tecsgen-python3移植計画 — P5 進捗ログ]] に分離（2026-09-28、25KB閾値）。プラグイン使用ケースの一致は 20/35、不使用は 119/119（as of 2026-09-28、P5j 後）。

- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5a（2026-09-27）|P5a]]（2026-09-27）: プラグイン読み込み基盤・`Plugin` 基底・`MultiPlugin`／Celltype・Signature・Cell 各基底、一致一覧を `p4_progress.py` に実装
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5b（2026-09-27）|P5b]]（2026-09-27）: `ThroughPlugin` 基底（重複防止キャッシュの import 行の差は未解明の既知差異）
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5c（2026-09-27）|P5c]]（2026-09-27）: `TracePlugin`
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5d（2026-09-27）|P5d]]（2026-09-27）: `RPCPlugin`＋`GenParamCopy`・`GenTransparentMarshaler`（一部）、`load_plugin` の2回目エラーコードのバグ修正
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5e（2026-09-28）|P5e]]（2026-09-28）: `OpaqueRPCPlugin`＋`GenOpaqueMarshaler`
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5f（2026-09-28）|P5f]]（2026-09-28）: `TECSInfoPlugin`・`TECSInfoCompoPlugin`・`CompositePlugin`・`tecsinfo.rb`（TECSInfo系4ケース）
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5g（2026-09-28）|P5g]]（2026-09-28）: Multi 系の `CIfGen`・`CppIfGen`（`cifplugin`・`cppifplugin`）
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5h（2026-09-28）|P5h]]（2026-09-28）: ATK1 の5本（`celltypePlugin`）、HRP・FMP・HRMP 系は正解データが無いため見送り
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5i（2026-09-28）|P5i]]（2026-09-28）: MrubyBridge ファミリー7本（`multiplugin/1・2`）、`CdlParser.parse_file` の潜在バグ修正
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k#P5j（2026-09-28）|P5j]]（2026-09-28）: 正解データのある標準プラグインの残り全部（RPC 系3本＋`GenTransparentMarshaler` 全量、`C2TECSBridge`、`RepeatCell`/`RepeatJoin`、`Notifier`、`DataPumpHolder`）、mixin 順序のバグ修正、P5b の import 行の差の原因判明
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k#P5k（2026-09-30）|P5k]]（2026-09-30）: カーネル依存系（HRP・FMP・HRMP・HRP2・ATK1）の正解データを採取（`tests/golden/kernel/`、hrp3+tecs 2・fmp3+tecs 2・hrmp3+tecs 2・ev3rt+tecs 3・atk1+tecs 2の計11ケース、`arm-none-eabi-gcc`（ATK1 はホストの `gcc -E`）、2回の全件採取で同一）。HRP2 は hrp2+tecs 自体が構文エラーになるため ev3rt+tecs で採った。ATK1 の `ATK1EventPlugin` は入力にイベントのセルが無く、出力が空の経路だけ。正解データの無いプラグインは、計測で18件（プラグイン17＋補助モジュール1。as of 2026-10-01、2026-10-01 に採取された別セッションのパッケージ正解データ16ケース（`tests/golden/packages/`）を加えた再集計。09-30 は20件）: HRP2 のカーネルオブジェクト系7・ドメイン間通信系ほか5（補助モジュール `GenHRP2Marshaler` を含む）・`MrubyInfoBridge*` 3・`TransparentMarshalerPlugin`・`ATK1DelayTaskPlugin`。一覧と入力探索の結果は P5 進捗ログの P5k。移植は未着手
- [[tecsgen-python3移植計画 — P5 進捗ログ#P5l〜P5p（2026-10-01）|P5l〜P5p]]（2026-10-01）: カーネル依存系プラグイン（HRP・FMP・HRMP・HRP2、ATK1Event）を移植。カーネルの11ケースすべてで生成物・標準出力・終了コードが Ruby 版とバイト一致（プラグインありの一致 34/46、プラグインなし 119/119）。`__tool_info__`（`TOOL_INFO`）も移植。
- [[tecsgen-python3移植計画 — P5 進捗ログ#P5q（2026-10-01）|P5q]]（2026-10-01）: `-L` による利用者プラグインの探索（設計は [[tecsgen-python3 -L ユーザプラグイン探索設計]]）と、同梱プラグインの Python 版（`tests/user_plugins/`）。`-L` 待ちの8ケースと、持ち越しの4件（`class`・`ErrorCase/cell-err`・`TECSInfoAccessor/*` 2件）がすべて一致し、**プラグインありの全46ケースが一致**（プラグインなし 119/119。as of 2026-10-02）。

**持ち越し（as of 2026-10-02、P5q 後）**: 正解データのあるケースは全件一致。カーネル依存系（HRP・FMP・HRMP・HRP2・ATK1Event）は P5l〜P5p で移植済み（[[tecsgen-python3移植計画 — P5 進捗ログ#P5l〜P5p（2026-10-01）|P5l〜P5p]]）。正解データの無いもの（`ATK1DelayTaskPlugin` ほか）は未移植。**HRP2 の個別カーネルオブジェクト系・SVC・RPC は 2026-10-03 に正解データを採取し、P3 記録も採って移植済み**（合成入力 CDL、5ケース `hrp2/objects`・`hrp2/rpc`・`hrp2/cyclic`・`hrp2/alarm`・`hrp2/rpc_ptr`、`tests/golden/kernel/cases/hrp2/`・`tests/golden/kernel/p3/hrp2/`。再採取でバイト一致。**プラグインありの全 51 ケース一致**）。周期・アラームハンドラとRPCのポインタ引数は Ruby 版が例外で止まる経路で、その例外・終了コードまで一致。`HRP2Cache`・`HRP2PostHook` は動かす経路が無く対象外。**残りの `HRPRPCPlugin`・`ATK1DelayTaskPlugin`・`MrubyInfoBridge*`・`TransparentMarshalerPlugin`・`TECS2CBridgePlugin`・`Mruby2CBridgePlugin` も同日に正解データ（実プロジェクトの `make tecs`・`test/mruby`・合成入力）と P3 記録を採って移植済み。プラグインありの全 63 ケース一致、pytest 995 件通過**。未移植は 85 本中 2 本のみ（ファイル数を実数で突き合わせ。2026-10-02 の「18 本」は数え間違い）。パッケージ由来のケースも P3 記録で再生できるようにした（`packages/` 接頭辞、`collect_packages.py --p3-oracle`）。

### P6 仕上げ（完了） — 詳細は [[tecsgen-python3移植計画 Archive — P6]]

- **P6a〜P6e**（2026-10-02 完了、`main` にマージ済み）: 配布（標準 CDL ライブラリの同梱）・CLI（`--help`・`--version` が Ruby 版とバイト一致）・実プロジェクトの差分テスト（カーネル・配布パッケージの正解データ）・`tecsmerge`（73シナリオ一致）・仕様書の完成（外部仕様10章・内部仕様12章）。TBC は 2026-10-04 までにすべて解消 → [[tecsgen-python3移植計画 Archive — P6|P6]]

### P7 cmake 対応と正解データの基準の切り替え（2026-10-05）

Ruby 版 tecsgen-rb（`asp3_stm32cube_TECS` の `tecsgen-rb`）の cmake 対応を移植し、正解データの基準を r3304 から tecsgen-rb へ切り替えた。計画・調査・決定は [[tecsgen-python3 cmake対応計画]]。実装は Python 版リポジトリのブランチ `ykominami/cmake-support`（2026-10-05 に PR #9 で `main` へマージ済み）。

- **cmake**: `CMakeLists.tecsgen.cmake` の生成と `CMake` API を移植（内部仕様 [[tecsgen-python3内部仕様 - 08 コード生成#8.6 CMakeLists.tecsgen.cmake（2026-10-05、tecsgen-rb の cmake 対応）|8.6]]）
- **`TransparentRPCSignaturePlugin`**: tecsgen-rb で追加されたプラグイン（r3304 には無く、`RPCPlugin`・`DataPumpHolderPlugin` が参照して失敗していた）を移植。これで `rpc`・`class`・`DataPumpHolder` が成功する。`DataPumpHolder` は、r3304 では実行されなかった `DataPumpHolderPlugin#gen_ep_func_body`（Ruby 約230行）も必要になり、移植した
- **基準の切り替え**: `test/` 158ケース（`transparent_marshaler` を除く）、p2・p3、カーネル23、配布パッケージ17 を tecsgen-rb で再採取。旧との差は `CMakeLists.tecsgen.cmake` の追加と、上の3ケースの成功化だけ。`transparent_marshaler` は tecsgen-rb に `TransparentMarshalerPlugin.rb` が無いため、r3304 の正解を残し比較の対象外にした
- **検証**: プラグインなし119/119・プラグインあり77/77 が一致（`tools/port/p4_progress.py`）。Windows 1025 passed / 78 skipped、WSL 1020 passed / 83 skipped、ruff・ty とも通過。配布パッケージは、これまで p3 記録が2件しか無く検証の対象外だった13件に記録を採り、検証の対象に加えた
- **採取ツール**: `wsl_check.sh` に `--build-src-tree`・`--src-tree`・`--exclude`・`--cases-golden` を追加。svn 以外の移植元に対応した（`tools/golden/README.md`）
- **未了**: `CMake.add_*` を呼ぶプラグインでの一致（呼び出すテストケースが無い）、`asp3_stm32cube_TECS` の `Asp3Tecs.cmake` から Python 版を呼ぶ確認（C5）。ブランチの `main` へのマージ（PR #9）と、`-k` の差異の修正（`ykominami/fix-kcode-differences`、PR #8 で先に取り込み済み）との取り込み順は、2026-10-05 に完了

## 主要リスク

| リスク                                    | 影響            | 対策                                                                                   |
| -------------------------------------- | ------------- | ------------------------------------------------------------------------------------ |
| ~~tree-sitter 文法が racc 文法と同じ言語を受理しない~~ | —             | **解消（2026-09-27）**: 実測で食い違いを確認し、racc の表をそのまま使う方式に切り替えた（[[tecsgen-python3 構文解析方式決定]]） |
| パース中の副作用の順序（プラグインのポストコード、名前空間スタック）の再現  | エラー順序・生成物の不一致 | 段階ごとの JSON ダンプで比較する                                                                  |
| 書式の細かな違いで生成物が一致しない                     | 受入基準を満たせない    | ゴールデン出力との差分を CI で常に取る                                                                |
| cpp の環境依存（`import_C`）                  | ゴールデン出力の再現性   | cpp の出力をテスト用の fixture として固定する                                                        |
| プラグインの量（約1.6万行）                        | 期間            | 使用頻度順に移し、カーネル依存のプラグインは後回し                                                            |

## 現状の問題（2026-09-26 確認 → 同日修正済み）

- ~~ノートに書かれたパス `E:/Ccur/python3/tecsgen-python` は存在しない~~ → 実体は `E:/Ccur/python3/tecsgen-python3`（リモートは `ykominami/tecsgen-python`。2026-09-28 に `ykominami/tecsgen-python3` へ改名）。関連ノート5件のパスを修正済み
- `pyproject.toml` を修正済み
  - 配布名を `tecsgen-python3`、import パッケージを `tecsgen`（`src/tecsgen/`）に改名。CLI 完全互換の決定（[[tecsgen-python3 P0基本方針決定]]）に合わせ、コマンド名を `tecsgen` にした
  - description の誤記「Ptyhon」を修正
  - `my`・`tuff` を削除。PyPI 上の無関係なパッケージだった（中身は数行の無害なコードと確認）。`ruff` の誤記と判断し、`pytest`・`ruff`・`ty` を dev 依存（`[dependency-groups]`）へ移した
  - 依存に入っていなかった `yklibpy` の `[tool.uv.sources]` 指定を削除
  - hatchling がパッケージを見つけられるよう `[tool.hatch.build.targets.wheel]` を追加
- `example.py` を修正済み。インデントが崩れ、DLL パスの文字列が途中で改行されていて動かなかった。また `Language(int)` 方式は非推奨で、Windows では `OverflowError` になる（`unsigned long` が32ビットのため）。PyCapsule を渡す方式に変えた。DLL の場所は環境変数 `TECSGEN_CDL_DLL` で上書きできる
- `.venv` を作り直した。ディレクトリ名が `tecsge-python3` だった頃に作られたもので、スクリプトのパスが古いままだった
- 確認: `uv run example` でサンプル CDL をエラーなくパースできた。pytest 1件 pass、`ruff check`・`ruff format --check`・`ty check` はすべて問題なし

## Related

- [[tecsgen-python3]] — 親ノート
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
