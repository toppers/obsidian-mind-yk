---
date: 2026-10-09
description: "tecsgen-python3 cmake対応計画のうち、C3（CMake.add_* を呼ぶプラグインで Ruby 版と一致）・golden ケースとしての固定・種類ごとの確認（signature・cell・composite・multi・through・domain・class）の結果の記録を、verbatim で分離したもの。25KB閾値による分割"
project: tecsgen-python3
status: tracking
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3 cmake対応計画 — C3 の結果

## C3 の結果（2026-10-09）: `CMake.add_*` を呼ぶプラグインで Ruby 版と一致

標準付属プラグインと `asp3_stm32cube_TECS` には `CMake.add_*` を呼ぶ箇所が無い（`get_*` を呼ぶのは `gen_cmake_tecsgen` だけ）ので、`-L` の利用者プラグインで合成して確かめた。**Python 版のリポジトリは変更していない**（入力はスクラッチパッドにあり、リポジトリには入れていない）。

- **入力**: セルタイププラグイン `MyCMakePlugin`（Ruby 版 `.rb` と Python 版 `.py`）を、1セルタイプ・1セルの CDL に `generate( MyCMakePlugin, tHello, "" )` で付けた。コンストラクタから `add_source`（重複・Symbol）、`add_include`（`$(BASE_DIR)/inc`・`\` を含む絶対パス）、`add_define`（文字列・整数）、`add_link_option`、`add_custom_command`、`add_line`（重複）を呼び、`new_cell` から `add_source` を、`gen_factory` から `add_source` を呼ぶ
- **実行**: Ruby 版は WSL で `tecsgen-rb/tecsgen.rb -L plug --gen=gen hello.cdl`、Python 版は `tecsgen -L plug --gen=gen hello.cdl`。作業ディレクトリの名前とプラグインのディレクトリ名（`plug`）は揃えた（`Makefile.templ` に実行コマンドが記録されるため）
- **結果**: `gen/` の13ファイル（`CMakeLists.tecsgen.cmake` を含む）が**バイト一致**。差は Ruby 版だけが書く `tecsgen.rbdmp` のみ（仕様どおり）。`TECS_PLUGIN_EXTRA_SOURCES`・`TECS_INCLUDE_DIRS`・`TECS_COMPILE_DEFINITIONS`・`TECS_LINK_OPTIONS`・`TECS_CUSTOM_COMMANDS` と末尾の追加行がすべて出ており、`uniq`（最初に出たものを残す）、Symbol と整数の `to_s`、`\` から `/` への変換も一致した
- **わかったこと（Ruby 版と共通）**:
  - `gen_cmake_tecsgen` は `generate` の最初（`gen_makefile_tecsgen` の次）に走るので、**`gen_factory` など生成段階のフックから呼んだ `add_*` は出力に反映されない**（上の `too_late.c` は両方で出なかった）。反映されるのは、コンストラクタ、`new_cell` など、生成より前に呼ばれるところ
  - `add_include` に渡した `$(BASE_DIR)/inc` は変換されず、そのまま出る（`add_include` の値は `\` から `/` の変換だけ）
- **ほかの種類のプラグイン**: 同日、signature・cell・composite・multi・through・domain・class についても確かめた（下の「種類ごとの確認」）。リポジトリのテストとしても固定済み（下の「golden ケースとしての固定」）

### golden ケースとしての固定（2026-10-09）

上の合成ケースを、Python 版リポジトリのブランチ `ykominami/golden-cmake-add`（コミット `6b8b932`）に、ケース `cmake_add` として固定した。PR #11 で `main` にマージ済み（2026-10-09、マージコミット `11f38ef`）。

- **入力**: `tools/golden/inputs/cmake_add/`（CDL、Ruby 版 `MyCMakePlugin.rb`、README）。Python 版プラグインは `tests/user_plugins/cmake_add/MyCMakePlugin.py`
- **正解データ**: tecsgen-rb で採取した `tests/golden/cases/cmake_add/`、P2・P3 の記録（`tests/golden/p2/`・`p3/` の `cmake_add.jsonl.gz`）
- **ツールの変更**: `generate_golden.py` の `place_inputs` が `*.rb` も写し、`cwd` が無ければ作る。`wsl_check.sh` に、`--oracle` で記録を採るケースを絞る先頭オプション `--case` を追加（`run_p2_oracle.sh`・`run_p3_oracle.sh` も対応）
- **検証**: `p4_progress.py` はプラグインあり **78/78**（これまで 77）・なし 119/119。Windows 1031 passed / 80 skipped、WSL 1026 passed / 85 skipped、ruff・ty とも通過。Python 版プラグインの `add_line` の値を一時的に変えると `CMakeLists.tecsgen.cmake` の差として検出されることを確認した（元に戻してある）
- **注意**: 正解データの `TECS_INCLUDE_DIRS` の並びは WSL のディレクトリ列挙順。P3 記録に列挙順が入っているので、Windows での再生は安定している

### 種類ごとの確認（2026-10-09）

セルタイプ以外の7種類（signature・cell・composite・multi・through・domain・class）のプラグインのコンストラクタから `add_source`・`add_define`・`add_include`・`add_line` を呼ぶ最小のプラグインで、Ruby 版（tecsgen-rb）と Python 版の `gen/` を比べた。signature・cell・composite・multi は合成、through・domain・class は既存ケース（`through`・`restrict`・`class`）のプラグインに `add_*` を足した変種。

- **結果**: 7種類とも、`CMakeLists.tecsgen.cmake` に値が反映され、標準出力・終了コードも同じ。**multi だけ差が出て、移植のずれが見つかった**（下）。`new_cell` など他のフックは、セルタイプ以外では試していない
- **multi の差**: Python 版は `tmp_<クラス名>_post_code.cdl` を出さず、`TECS_IMPORT_CDLS`（`Makefile.tecsgen`・cmake）の行も抜けた。`MultiPlugin#get_plugin` が返す `MyMultiCelltypePlugin` を、`MultiPlugin` の子と同じファイルに書いたため。Python 版は post_code の生成でプラグイン名からファイルを読み直す（`_import_plugin_class`）ので、ファイル名と違う名前のクラスを見つけられず、黙って飛ばしていた（クラスを独立したファイルに分けると一致した）。Ruby ではロード済みのクラスが定数になるので動く。標準付属の Multi 系は別ファイルなので影響を受けなかった（`CMake` API とは無関係の移植のずれ）
- **修正と固定**（Python 版 PR #12。`main` にマージ済み、`9c3d635`。SonarCloud の品質ゲートは「新規コードの重複 33.2%（基準 3% 以下）」で失敗したままマージした。through・domain・class の変種ケースが既存のテスト用プラグインを複製しているため）: `get_plugin` が返したクラスを実行ごとの名前表に登録する（`_register_plugin_class`、[[tecsgen-python3内部仕様 - 09 プラグイン機構]]）。golden ケース `cmake_add_signature`・`_cell`・`_composite`・`_multi`・`_through`・`_domain`・`_class` を追加（`generate_golden.py` のケースに、既存ケースのディレクトリを写してから重ねる `base` を追加）。`cmake_add_multi` が修正の回帰テスト（修正を無効にすると不一致になる）。プラグインありの一致は 85/85（これまで 78）、pytest は Windows 1059 passed / 94 skipped、WSL 1054 passed / 99 skipped

## Related

- [[tecsgen-python3 cmake対応計画]] — 本体
- [[tecsgen-python3 cmake対応計画 — C6 ビルド検証]] — configure 以降（コンパイル・リンク）の確認
- [[tecsgen-python3]]
