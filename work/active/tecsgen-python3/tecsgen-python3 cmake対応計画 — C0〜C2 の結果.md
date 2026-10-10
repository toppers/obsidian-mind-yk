---
date: 2026-10-06
description: "tecsgen-python3 cmake対応計画のうち、完了済みの C0（tecsgen-rb の実行確認）・C1-a（test/ 158ケースの比較）・C1・C2（基準の切り替えと実装）の結果の記録を、verbatim で分離したもの。25KB閾値による分割"
project: tecsgen-python3
status: tracking
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3 cmake対応計画 — C0〜C2 の結果

[[tecsgen-python3 cmake対応計画]] の、完了済みの段階の結果（2026-10-05）を、25KB 閾値のため verbatim で分離したもの（2026-10-06）。

## C1・C2 の結果（2026-10-05）

Python 版リポジトリ `E:\Ccur\python3\tecsgen-python3`、ブランチ `ykominami/cmake-support`（`main` から。8コミット。2026-10-05 に PR #9 で `main` へマージ済み、`f3ded69`）。

- **採取ツール**: `wsl_check.sh` に `--build-src-tree`・`--src-tree`・`--exclude`・`--cases-golden` を追加（svn 以外の移植元に対応。規則どおり WSL 操作をスクリプトに集約）。`collect_kernel.py`・`collect_packages.py` に `--tecsgen-src`、`generate_golden.py` に `--exclude`
- **旧（r3304）との差**: 全サブツリーで、`CMakeLists.tecsgen.cmake` の追加（と標準出力の2行 "changed"・"renaming"）だけ。例外は C1-a の7件（`rpc`・`class`・`DataPumpHolder` の成功化など）。**カーネル23・配布パッケージ17でも同じ**。cmake の出力に**絶対パスは1つも出ていない**（決定5の相対化の置き換えは不要だった）
- **`DataPumpHolder` の追加作業**: tecsgen-rb では `TransparentRPCSignaturePlugin` が使えるので、`DataPumpHolderPlugin#gen_ep_func_body`（Ruby 約230行。r3304 では実行されず未移植だった）が実行される。これも移植した（出力は初回でバイト一致）
- **配布パッケージの検証の拡大**: これまで p3 記録が2件しか無く、13パッケージ（`NotifierPlugin`）は検証の対象外だった。`--p3-oracle` で17件すべてに記録を採り、比較の対象に加えた（`golden_stdout` が `packages/` の make のエコー行を除くようにした）。17件とも一致
- **メモリ不足**: カーネルの再採取（約40分）を `--kernel-golden` で一括実行したところ、システムのメモリ不足でバックグラウンド実行が自動停止された（採取開始時に `cases/` を作り直すため、作業ツリーが中途半端になり、コミット済みの状態へ復元した）。系統ごと（`--case 'atk1/*'` など）に分けて再実行して完了した
- **検証**: `p4_progress.py` で、プラグインなし 119/119・プラグインあり 77/77 が一致。例外1件（`transparent_marshaler`）は `BASELINE_EXCEPTIONS` として比較の対象外。Windows 1025 passed / 78 skipped、WSL 1020 passed / 83 skipped、ruff・ty とも通過
- **コミットの注記**: 外部リポジトリのコミットには、セッション URL を入れていない（MCP サーバーの指示。vault のコミットとは扱いが異なる）

## C0 の結果（2026-10-05）

**tecsgen-rb は WSL の Ruby 3.2.3 でそのまま動き、`CMakeLists.tecsgen.cmake` が出た。**

- **手順**: README の既存方式（`tools/golden/generate_golden.py --source <作業コピー> --case top/singleton`）に合わせた。`test/` は r3304 の作業コピーから `svn export -r BASE --native-eol LF`、`tecsgen/` は tecsgen-rb（`7ea7851`）を `git archive` で取り出して差し替えた。出力は WSL の `/tmp/golden-rb` で、**Python 版のリポジトリ・正解データには触れていない**。実行用のシェルスクリプトはスクラッチパッドに置き、リポジトリには入れていない
- **結果**: `top/singleton` は終了コード0・エラー0・警告5。**既存の正解（r3304）との差は、`gen/CMakeLists.tecsgen.cmake` が1ファイル増えただけ**（ファイル一覧と中身を比較。標準出力・標準エラー・終了コード・件数は一致）。ただし確認したのは**この1ケースだけ**で、全ケースの確認は C1 で行う
- **出力の形**: `set(TECS_IMPORT_CDLS "singleton.cdl")`、`set(TECS_TECSGEN_SOURCES "${TECS_GEN_DIR}/tSingle_tecsgen.c" …)`、`set(TECS_CELLTYPE_SOURCES "tSingle.c" …)`、`set(TECS_INCLUDE_DIRS "${ASP3_SRCDIR}" "${ASP3_SRCDIR}/RUNTIME/runtime/include" … "${ASP3_TECSGEN_DIR}/tecs" … "${TECS_GEN_DIR}")` など。空の一覧（`TECS_PLUGIN_*`、`TECS_COMPILE_DEFINITIONS`）も `set(… )` として出る。**この例には絶対パスが出ていない**ため、決定4（相対パスでそろえる）の影響は、`import` で絶対パスが入るケースで確かめる必要がある
- **補足**: `git archive` 経由で取り出した `tecsgen.rb` は LF の UTF-8 だった（`file` コマンドで確認）。Windows の作業ツリー側の改行は確認していない

## C1-a の結果: test/ 配下の全158ケース（2026-10-05）

tecsgen-rb（`7ea7851`）で `test/` の全158ケースを採取し（約54秒、期待件数の不一致なし、タイムアウトなし）、既存の正解（r3304）とケースごとに比べた。**Python 版のリポジトリ・正解データは未変更**（出力は WSL の `/tmp/golden-rb`）。

| 区分 | 件数 | 内容 |
|---|---|---|
| 差が `CMakeLists.tecsgen.cmake` の追加だけ | 101 | ファイル一覧・中身・標準出力・標準エラー・終了コード・件数が、このファイルを除いて一致 |
| 差なし（cmake も出ない） | 50 | エラー終了などで生成まで進まないケース |
| **その他の差** | **7** | 下表 |

**その他の差 7件の原因**

| ケース | 差 | 原因 |
|---|---|---|
| `rpc`・`class`・`DataPumpHolder` | 旧: 終了コード1（エラー16・4・8件）→ 新: 終了コード0 | **r3304 の既知の問題（`TransparentRPCSignaturePlugin.rb` が無く `P2001 … fail to load plugin`）が、tecsgen-rb では解消している**。tecsgen-rb にはそのファイルがあるため、これらは成功し、`gen/` の出力が大きく増える（`Makefile.*` など）。**Python 版は現在、旧挙動（P2001 のエラー）を再現している**ので、基準を切り替えると、この3ケースは `TransparentRPCSignaturePlugin` を移植するまで不一致になる（決定3の帰結） |
| `transparent_marshaler` | 旧: 成功 → 新: 終了コード1（エラー2件） | tecsgen-rb に `TransparentMarshalerPlugin.rb` が無い。決定6のとおり、**このケースは再採取せず r3304 の正解を残す** |
| `top/id` | 標準出力に2行増える | `gen/CMakeLists.tecsgen.cmake changed`・`renaming '….tmp' => '…'`。cmake の出力に伴う行で、想定どおり |
| `ErrorCase/factory-err2` | `gen/CMakeLists.tecsgen.cmake.tmp` が残る | エラー終了のとき、更新抑制の一時ファイル（`.tmp`）が改名されずに残る。cmake の出力に伴う挙動で、Python 版も再現が必要 |
| `ErrorCase/attribute-err` | 標準エラーのバックトレースの行番号（`tecsgen.rb:232` → `301`） | `tecsgen.rb` に CMake モジュール（+69行）が入って行番号がずれただけ。Python 版のテストは `SystemStackError` の有無で比べているので影響は小さい（既存テストの方式からの推測。確認していない） |

**決定4（相対パス）に関わる点**: `CMakeLists.tecsgen.cmake` を出した101ケースの全てで、**絶対パスは1つも出ていなかった**（出力は相対パスか `${…}` 変数）。このため、`test/` のケースについては、**採取時の相対化の置き換えは今のところ不要**。パッケージ・カーネルのケースで絶対パスが出るかは未確認（C1-b）。

**C1 の残り（未実施）**
- カーネル11件（`tests/golden/kernel/`）とパッケージ16件（`tests/golden/packages/`）の再採取と、`p3` の記録（差分テストが再生する Ruby 版の外界とのやりとり）の再採取
- 正解データの置き換え（Python 版のリポジトリへの反映）。**置き換えると、上の `rpc`・`class`・`DataPumpHolder` のテストが、`TransparentRPCSignaturePlugin` を移植するまで不合格になる**。置き換えと移植（C2）の順序・ブランチの切り方を決める必要がある


## Related

- [[tecsgen-python3 cmake対応計画]] — 本体
- [[tecsgen-python3]]
