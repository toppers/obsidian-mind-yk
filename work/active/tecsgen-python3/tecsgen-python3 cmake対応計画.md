---
date: 2026-10-05
description: "Ruby版tecsgenのcmake対応（CMakeLists.tecsgen.cmake の生成と TECSGEN::CMake API）をPython版へ反映する計画のたたき台。調査結果、r3304との差分、実装・検証の段階、未決事項"
project: tecsgen-python3
status: active
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3 cmake対応計画（たたき台）

[[tecsgen-python3]] の目標「Ruby版tecsgenのcmake対応をPython版に反映する」（2026-10-05 追加）の調査と計画。移植全体の計画は [[tecsgen-python3移植計画]]。**調査はソースの読み取りだけで、Ruby 版・Python 版とも実行していない**（実行して確かめた事項は無い）。

## 調査対象

- 参照先: `E:\Ccur\python3\asp3_stm32cube_TECS\tecsgen-rb`（`ykominami/asp3_stm32cube_TECS`、`hiro22022/asp3_stm32cube_TECS` の fork。HEAD `7ea7851`。Ruby 版 tecsgen は 2026-09-21 のコミット `5d02ef8`「tecsgen を tecsgen-rb に移動」で現在の位置に置かれた）
- 比較した移植元: SVN trunk の tecsgen 本体（r3304。[[tecsgen-python3移植計画]] で正解データの採取に使っているもの）

## 結論

1. **cmake 対応は、Ruby 版の2ファイルへの追加（約235行）だけ**で、CLI オプションの追加は無い。標準プラグインで cmake の API を使うものも無い。
2. **tecsgen-rb と r3304 は、cmake 以外ではほぼ同じ**（下記）。移植元を取り替える必要は無く、cmake の差分だけを取り込めばよい。
3. 現在のリポジトリ（Python 版）には cmake の記述が1つも無い（`src/tecsgen/` を検索）。

## Ruby 版のどこが cmake に対応しているか

| 区分 | 内容 | 場所（tecsgen-rb） |
|---|---|---|
| **生成物** | `<gen>/CMakeLists.tecsgen.cmake`。Makefile.tecsgen の代わりに、CMake が `include()` するソース一覧マニフェスト | `tecslib/core/generate.rb` の `gen_cmake_tecsgen`（939〜1018行付近） |
| **出力の中身** | `set(<変数名> "…" …)` の列。変数は `TECS_IMPORT_CDLS`・`TECS_TECSGEN_SOURCES`・`TECS_PLUGIN_TECSGEN_SOURCES`・`TECS_PLUGIN_CELLTYPE_SOURCES`・`TECS_CELLTYPE_SOURCES`・`TECS_PLUGIN_EXTRA_SOURCES`・`TECS_INCLUDE_DIRS`・`TECS_COMPILE_DEFINITIONS`。`TECS_LINK_OPTIONS`・`TECS_CUSTOM_COMMANDS`・追加行は、あるときだけ出す | 同上 |
| **パス変換** | `cmake_normalize_path`・`cmake_write_list`（853〜874行付近）。`$(GEN_DIR)` → `${TECS_GEN_DIR}`、`$(TECSPATH)` → `${ASP3_TECSGEN_DIR}/tecs`、`$(BASE_DIR)` → `${ASP3_SRCDIR}`、`.` → `${ASP3_SRCDIR}`、絶対パスは `\` を `/` に | 同上 |
| **呼び出し** | root namespace の `generate` で `gen_makefile_template`・`gen_makefile_tecsgen` の次に呼ぶ（135行付近）。`gen_makefile` からも呼ぶ（323行付近）。**`$generate_no_template` では止まらず、空のセル領域でも出る**（`return` より前） | 同上 |
| **API** | `TECSGEN::CMake` モジュール（`add_source`・`add_include`・`add_define`・`add_link_option`・`add_custom_command`・`add_line`、取得用の `get_*`、`set_default_config`）。`Makefile` モジュールと同型で、`tecsgen` の初期化（`set_default_config`）に組み込まれている | `tecslib/core/tecsgen.rb`（108〜176行） |
| **CLI オプション** | **無い**（`tecsgen.rb` に cmake の記述なし）。生成は常に行われる（inferred。実行では未確認） | — |
| **プラグイン** | 標準プラグインで `TECSGEN::CMake` を呼ぶものは**無い**（検索で `generate.rb`・`tecsgen.rb` 以外にヒットしない）。利用者プラグイン向けの拡張点として用意されたもの | — |
| **利用側** | `asp3/cmake/Asp3Tecs.cmake` が configure 時に tecsgen を実行して `CMakeLists.tecsgen.cmake` を `include()` する。`tecsgen.rb` と `tecsgen.py` のどちらか存在する方を使う（同一ディレクトリ想定） | `asp3_stm32cube_TECS/asp3/cmake/`、同リポジトリの `docs/tecs-cmake.md` |

## tecsgen-rb と r3304 の差分（`diff` で確認）

- **cmake 以外の中身の差は無い**: 差があるのは15ファイルで、うち `celltype.rb`・`namespace.rb`・`namespacepath.rb`・`CelltypePlugin.rb`・`GenTransparentMarshaler.rb`・`OpaqueRPCPlugin.rb`・`RPCPlugin.rb`・`SharedRPCPlugin.rb`・`SharedOpaqueRPCPlugin.rb`・`tMessageBufferChannel.cdl` は **SVN の `$Id` 行1行だけ**。`ATK1DelayTaskPlugin.rb`・`ATK1EventPlugin.rb` は**改行コード（CR）だけ**（CR を除くと差分0）
- **cmake の差分**: `generate.rb`（+169行、コメント1行の書き換え）と `tecsgen.rb`（+69行）
- **プラグインの名前の差**: tecsgen-rb には `TransparentRPCSignaturePlugin.rb`（303行、スループラグイン）があり、r3304 の `TransparentMarshalerPlugin.rb`（84行）が無い。cmake とは無関係。Python 版は `TransparentMarshalerPlugin` を移植済みなので、扱いは別途決める（未決）
- 注意: この比較は `$Id` の日付から見て、tecsgen-rb が r3304 より古い版から派生している（inferred）。r3304 より新しい変更を取りこぼしていないかは、この比較からは分からない

## 計画（段階）

| 段階 | 内容 | 合格条件 |
|---|---|---|
| **C0 基準の確認** | tecsgen-rb を WSL の Ruby で実行できるか確認。既存の正解データ（`tests/golden/`）の元と同じ条件（Ruby 3.2.3）で動くか | 既存のケース1件を tecsgen-rb で実行し、`CMakeLists.tecsgen.cmake` が出る |
| **C1 基準を tecsgen-rb に切り替える（正解データの再採取）** | 既存の全ケース（プラグイン不使用119、使用63、カーネル11、パッケージ16）を tecsgen-rb で再採取し、正解データを置き換える。置き換える前に、**既存の正解と比べて増える物が `CMakeLists.tecsgen.cmake` だけ**であることを確認する（想定外の差が出たら、その原因を先に特定する）。`TransparentMarshalerPlugin` のケースは、tecsgen-rb にこのプラグインが無いため再採取できない（下の「残る確認」） | 全ケースで、既存ファイルが一致、新規ファイルは cmake のマニフェストのみ。切り替え後の正解で、既存のテストが通る |
| **C2 実装** | `tecsgen.py` に `CMake` クラス（`Makefile` クラスと同型）と `set_default_config` への組み込み。`generate.py` に `gen_cmake_tecsgen`・`cmake_normalize_path`・`cmake_write_list` と、3か所の呼び出し（`generate`・`gen_makefile`、空のセル領域の早期 return の前） | C1 の全ケースで `gen/CMakeLists.tecsgen.cmake` がバイト一致 |
| **C3 API の公開** | 利用者プラグインから `CMake.add_*` を呼べるようにする（`-L` の利用者プラグインの仕組みに合わせる） | `add_*` を使う最小のプラグインで、出力が Ruby 版と一致（正解は Ruby 版の同等プラグインで採る） |
| **C4 仕様書** | 外部仕様4章（出力）に `CMakeLists.tecsgen.cmake` を追加。内部仕様8章（コード生成）に、生成の手順とパス変換を追加。CLI は変更なしと明記 | 両章の更新 |
| **C5 利用側の確認** | `asp3_stm32cube_TECS` の `Asp3Tecs.cmake` から、Python 版を呼べるか。現状は `tecsgen.rb`／`tecsgen.py` を同一ディレクトリで探す作り。Python 版は `uv tool install` 等の配布で、コマンド名 `tecsgen` を使う | configure までを通す（実機ビルドは CubeMX 生成物が必要で範囲外の可能性） |

## 決定事項（2026-10-05、ユーザー決定）

1. **Ruby 版から直接移植する。** 同リポジトリの `tecsgen-py`（別の Python 実装）は参考にしない。Ruby 版を正解とする既存の方針（[[tecsgen-python3 P0基本方針決定]]）のとおり
2. **正解データを tecsgen-rb に切り替える。** `tecsgen-python3.md` の「Ruby版最新コード」の参照先も、tecsgen-rb に更新済み（旧参照先 `branches/ykominami_r3033` は「旧」として残している）
3. **tecsgen-rb だけにある `TransparentRPCSignaturePlugin` を取り込む。** 303行のスループラグイン。ファイルの冒頭に「mikan through plugin: namespace が考慮されていない」とある（Ruby 版の既知の未完成を、そのまま移植することになる。[[Patterns - 検証と調査|Ruby 版の癖は直さず再現する]]という常設ルールに従う）
4. **パスは、フルパスではなく、テストデータを格納しているディレクトリからの相対パスでそろえる。** 対象は、`CMakeLists.tecsgen.cmake` に出るパス（`cmake_normalize_path` が絶対パスをそのまま出す部分）と、正解データの比較（Windows の Python 版と WSL の Ruby 版でパスの形が違う問題）
5. **相対化は、採取時に行う（2026-10-05、ユーザー決定）。** Ruby 版の出力を正解データとして保存するときに、絶対パスをテストデータのディレクトリからの相対パスに置き換える。`generate_golden.py` が作業ディレクトリとソースの絶対パスを `@WORK@`・`@SOURCE@` に置き換えている方式の延長にあたる（inferred）。比較する Python 版の出力にも、同じ置き換えを通す必要がある（実装は C1・C2 で行う）
6. **`TransparentMarshalerPlugin` は Python 版に残す（2026-10-05、ユーザー決定）。** tecsgen-rb には `TransparentMarshalerPlugin.rb`（84行）が無く、基準を切り替えても再採取できないため、**このプラグインの合成入力1ケースの正解データは、r3304 で採ったものを残す**。C1 の再採取では、このケースを対象から外し、例外として記録する（標準の CDL に使用箇所が無いことは、P5k の探索結果）

## 残る確認

- **`-L` 等の新しい CLI オプション**: Ruby 版に無いので、追加しない前提（未確認。決定ではない）
- **C1 の再採取の対象と例外の一覧**: `TransparentMarshalerPlugin` のケースは例外。ほかにも tecsgen-rb で再採取できない（プラグインのファイルが無いなど）ケースが無いかは、C1 で確かめる

## 進捗（2026-10-05）

| 段階 | 状態 |
|---|---|
| C0 実行確認 | 完了 |
| C1 基準の切り替え | **完了**（下の結果）。`test/` 158（`transparent_marshaler` を除く）・p2・p3・カーネル23・配布パッケージ17 を再採取して置き換えた |
| C2 実装 | **完了**。`CMake` クラス・`gen_cmake_tecsgen` ほか、`TransparentRPCSignaturePlugin`、`DataPumpHolderPlugin.gen_ep_func_body` |
| C3 API の公開 | `CMake` クラスは `from tecsgen.core.tecsgen import CMake` で使える。**`add_*` を呼ぶプラグインでの一致は未確認**（呼び出すテストケースが無い） |
| C4 仕様書 | **完了**（外部仕様4章・6章、内部仕様8章8.6） |
| C5 利用側の確認 | **生成までは確認済み・反映は実装し、マージ済み**（2026-10-06。Python 版 PR #10、`asp3_stm32cube_TECS` PR #1）。下の「C5 の結果」。実機ビルド・リンクは未確認 |

## 次の一手

- （完了 2026-10-05）Python 版リポジトリのブランチ `ykominami/cmake-support` を、PR #9 で `main` へマージした（マージコミット `f3ded69`）。`-k` の差異の修正（`ykominami/fix-kcode-differences`）は PR #8 で先に取り込み済みで、取り込み順の調整は不要だった
- （完了 2026-10-06）C5: 方針（案3）の2つのブランチを、それぞれマージした。Python 版の `ykominami/tecsgen-path`（PR #10、`f6782ab`）、`asp3_stm32cube_TECS` の `ykominami/tecsgen-python3-command`（自分の fork の PR #1、`3b72ead`。上流 `hiro22022/asp3_stm32cube_TECS` への PR は出していない）。残りは、configure 以降（ビルド・リンク・実機）の確認（CubeMX 生成物が必要）
- `CMake.add_*` を呼ぶ最小のプラグインを作り、Ruby 版の同等プラグインと出力を比べる（C3 の確認）

## C5 の結果（2026-10-06）: Asp3Tecs.cmake から Python 版を呼ぶ

`asp3_stm32cube_TECS` の `asp3/cmake/Asp3Tecs.cmake` の `asp3_tecs_run_generator`（configure 時に tecsgen を実行する関数）を、実サンプル `asp3/sample/sample1.cdl`（NUCLEO-H563ZI 向け）で、**変更なしのまま**呼び、Ruby 版（tecsgen-rb）と Python 版で出力を比べた。**`asp3_stm32cube_TECS` のリポジトリは変更していない**（検証用の道具はスクラッチパッド）。

- **方法**: `cmake -P` のスクリプトから `asp3_tecs_run_generator` を呼ぶ。CubeMX の生成物（`Drivers/`、gitignore 対象で、このワークスペースには無い）は使わず、`asp3_tecs_setup_paths` の include からそれを除いた。`asp3_core`（サブモジュール。このワークスペースでは空）は、固定されているコミット `6496ca7` を作業用の場所へクローンして使った。Python 版は、`tecsgen.py`（Python 版の `main` を呼ぶ数行の shim）と `tecs/`（標準 CDL ライブラリのコピー）を置いたディレクトリを `ASP3_TECSGEN_DIR` に指し、`PYTHON_EXECUTABLE` を Python 版の `.venv` に向けた
- **結果**: Ruby 版・Python 版とも、`asp3_tecs_run_generator` が成功し（`CMakeLists.tecsgen.cmake`・`tecsgen.cfg` が出る）、Ruby 版100ファイル・Python 版99ファイルを生成した。**改行（Ruby 版は Windows で CRLF、Python 版は LF）と出力先のパスをそろえると、99ファイルは完全に一致**した（`CMakeLists.tecsgen.cmake`・`tecsgen.cfg`・全ヘッダ・C ソースを含む）。差は、Ruby 版だけが書く `tecsgen.rbdmp` の1ファイルだけ（Python 版は仕様どおり書かない。外部仕様4章4.3）。つまり、**呼び出し側の `Asp3Tecs.cmake` の既存の `tecsgen.py` 経路（`${PYTHON_EXECUTABLE} ${ASP3_TECSGEN_DIR}/tecsgen.py <引数>`）で、Python 版は Ruby 版の代わりに動く**
- **確認していないこと**: `asp3_tecs_configure`・`asp3_tecs_apply_manifest`（ターゲットへのソースの登録）以降、実際の `cmake --preset` による configure、ビルド、リンク、実機。CubeMX の生成物（`Drivers/`）が無く、ここまでは検証できない。N6570-DK でも同様に未確認。マニフェストの中身は Ruby 版と一致しているので、`include()` 以降の挙動は同じになる見込みだが、確かめてはいない
- **見つけたこと（Ruby 版と共通）**: `Asp3Tecs.cmake` は、コンパイラのフルパスを `--cpp "…"` の1つの文字列にして渡す。Windows で `CMAKE_C_COMPILER` が `C:/Program Files (x86)/Arm GNU Toolchain …/arm-none-eabi-gcc.exe` のように空白を含むと、`popen for CPP failed` で失敗する（Ruby 版でも同じ。PATH 上のコマンド名なら通る）
- **反映の方針（2026-10-06、ユーザー決定）**: 案3を採用 = 実行ファイルを直接呼ぶ経路（`-DASP3_TECSGEN_COMMAND`）＋ `tecs/` の場所を返す手段。ほかの案（現状のまま shim を使う、実行ファイルの経路だけ足す）は採らない
- **実装（2026-10-06、いずれもマージ済み）**:
  - Python 版（`ykominami/tecsgen-python3`）のブランチ `ykominami/tecsgen-path`（`dd33023`）: `tecsgen-path` コマンドを追加（`tecs/` を含むディレクトリを `/` 区切りで1行出力）。`tecsgen` コマンドには新しいオプションを足していない（CLI の Ruby 版完全互換の方針）。テスト・README・CHANGELOG を追加
  - `asp3_stm32cube_TECS`（`ykominami/asp3_stm32cube_TECS`）のブランチ `ykominami/tecsgen-python3-command`（`0a9f59e`）: `Asp3Tecs.cmake` に `ASP3_TECSGEN_COMMAND` を追加。指定すると、そのコマンドを直接実行し、`ASP3_TECSGEN_DIR` を、そのコマンドの隣の `tecsgen-path` の出力に置き換える。指定しなければ従来どおり（`tecsgen.rb`／`tecsgen.py`）。`docs/tecs-cmake.md` に利用方法を追記
  - **確認**: 変更後の `Asp3Tecs.cmake` に、`-DASP3_TECSGEN_COMMAND=<.venv の tecsgen.exe>` を渡し、shim も `tecs/` のコピーも無しで、`sample1.cdl` の生成が成功し、Ruby 版と改行・パスを除いて99ファイルが一致した。Ruby 版の既存の経路も変わらず動く。configure 以降（ビルド・リンク・実機）は未確認のまま

## C0〜C2 の結果（2026-10-05） — 詳細は [[tecsgen-python3 cmake対応計画 — C0〜C2 の結果]]

- **C0**: tecsgen-rb は WSL の Ruby 3.2.3 でそのまま動き、`CMakeLists.tecsgen.cmake` が出た。**C1-a**: `test/` 158ケースの比較で、差は cmake の追加と7件（3件は `TransparentRPCSignaturePlugin` による成功化）。**C1・C2**: 基準を tecsgen-rb に切り替え、`CMake` クラス・`TransparentRPCSignaturePlugin`・`gen_ep_func_body` を移植。プラグインなし119/119・あり77/77 が一致 → [[tecsgen-python3 cmake対応計画 — C0〜C2 の結果|C0〜C2 の結果]]

## Related

- [[tecsgen-python3 cmake対応計画 — C0〜C2 の結果]] — C0〜C2 の結果（分割、2026-10-06）

- [[tecsgen-python3]] — 親ノート
- [[tecsgen-python3移植計画]] — 全体の計画
- [[tecsgen-python3内部仕様 - 08 コード生成]] — 生成の仕様（C4 で更新）
- [[tecsgen-python3外部仕様 - 04 出力]] — 出力の仕様（C4 で更新）
- [[tecsgen-python3 P0基本方針決定]] — Ruby 版を正解とする方針
- [[tecsgen-python3 -L ユーザプラグイン探索設計]] — C3 で利用者プラグインから API を呼ぶ際の前提
