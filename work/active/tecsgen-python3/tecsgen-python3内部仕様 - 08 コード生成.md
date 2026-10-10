---
date: 2026-09-27
description: "tecsgen-python3内部仕様8章（P4）。generate.rbをNamespace/Signature/型/Celltypeのmixinへ移植した構成、AppFileとHost経由の出力、sprintf幅などバイト一致のためのRuby互換、プラグイン不使用119ケースのgen/完全一致を確かめる差分テスト"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 8章 コード生成

[[tecsgen-python3内部仕様]] の8章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 08 コード生成|Ruby版 8章]]。P4（2026-09-27）で実装した。生成物は Ruby 版とバイト単位で一致させる（受入基準）。

## 8.1 構成

`generate.rb`（5,399行）は各モデルクラスを再オープンして `generate`・`gen_*` を足している。Python 版はクラスごとの mixin にし、Celltype の部分は生成物ごとに3つのモジュールへ分けた。

| モジュール | mixin | 生成物 |
|---|---|---|
| `core/generate.py` | 共通関数（`print_note`・`ifndef_macro_only` など）、`AppFile`・`MemFile`、`NamespaceGenerate`・`SignatureGenerate`・`TypedefGenerate`・`StructTypeGenerate`・`RegionGenerate`・`DomainTypeGenerate`・`ClassTypeGenerate` | `global_tecsgen.h`・`Makefile.templ`・`Makefile.tecsgen`・`<signature>_tecsgen.h` |
| `core/generate_celltype_ph.py` | `CelltypeGeneratePH`（`gen_ph_*`） | `<celltype>_tecsgen.h`・`<celltype>_factory.h` |
| `core/generate_celltype_cell.py` | `CelltypeGenerateCell`（`generate_cell_code`・`gen_cell_*`・`get_name_array`・`gen_cell_cb_init`） | `<celltype>_tecsgen.c` |
| `core/generate_celltype_templ.py` | `CelltypeGenerateTempl` | `_templ.c`・`_inline_templ.h`・factory の `write`（`tecsgen.cfg` など）・`Makefile.depend`、dealloc マクロ、`subst_name` |
| `core/generate_celltype.py` | `CelltypeGenerate`（上の3つをまとめ、`generate`・`generate_post` を持つ） | — |

mixin のメソッドは `self: Any` と注釈し、モデルの属性を Ruby と同じ名前（`@x` → `self._x`）で参照する。ヒアドキュメントは f 文字列で写した（C の `{`・`}` は `{{`・`}}`）。

## 8.2 出力（AppFile と Host）

- `AppFile.open` は同じ名前の2回目以降を追記で開き、`--force-overwrite` でなければ `<name>.tmp` に書く。`finalize` の `AppFile.update` が既存ファイルと比べ、変わったときだけ `.tmp` を置き換える（Ruby 版と同じ）
- ファイルを開く・読む・`File.readable?`・`rename`・`delete` は、すべて `Host`（`host.py`）を通す。`RubyIO` は `Host.open_write` で開く。これで差分テストの `RecordedHost` が書いた中身を受け取れる（[[tecsgen-python3内部仕様 - 10 ファイル入出力|10章]] の更新）
- エラーで生成を中断すると、Ruby 版と同じく `.tmp` が残る（`ErrorCase/factory-err2` の正解データにも残っている）

## 8.3 バイト一致のための Ruby 互換

- **`sprintf` の `%s` の幅**: CDL から読んだ文字列は Ruby では既定でバイナリ（ASCII-8BIT）なので、幅は**バイト数**で数えられる（`attribute` の `"hello world! ハロー"`）。`TECSGEN_FILE_LANG` で Shift_JIS にしたときは Shift_JIS の String になり**文字数**で数える（`sjis`）。`ruby_compat._pad_str` で切り替える
- **`sprintf` の数値変換**: Ruby は `%d` に `Integer()`、`%f` に `Float()` を使うので、`"10"` のような文字列も受け付ける（factory の書式に属性の値を渡す `top/factory`）
- **`Array#[]` の範囲外は nil**: `domain_regions[0]` が空配列で nil になり、ドメインありと判定される（`sample/normal-*`）。`_get_at` を使う
- **Ruby の正規表現の `^`・`$` は行頭・行末**: `subst_name` などは `re.MULTILINE` でコンパイルする
- **絶対パスの判定**: `TECSGEN.is_absolute_path` は `/` で始まるかを `Host.isabs` に聞く（記録では絶対パスの先頭が `@WORK@` に置き換わっているため）
- **メソッドの戻り値**: `gen_cell_cb_init` は Ruby の最後の式の値を返す（構造体の `C_EXP` は文字列を返すだけで出力しない、など）
- Ruby 版のプラグイン引数の書き方の都合（`get_pre_tecsgen_target` にブロックを渡しているが yield しないので常に空）もそのまま再現した

## 8.4 未移植（P5）

- プラグインが生成するセルタイプの `gen_ep_func?`・`gen_preamble`・`gen_postamble`・`gen_factory`、`TOOL_INFO`（`tool_info.rb`）、`unjoin_plugin`

## 8.5 差分テスト

- **比較の仕組み**: 新しい記録は採らず、P3 のオラクル記録（`tests/golden/p3/`）を再生する（2026-09-27 ユーザー採用。記録は run 全体を通して採っているので、生成中の `File.readable?` なども入っている）。`tests/p4_gen_check.py` が `cli.run` を通しで実行し、`RecordedHost` に書かれたファイルを正解データ `tests/golden/cases/<id>/files/` と比べる。`*.rbdmp`・`tmp_*.h` は比べない
- **テスト**: `tests/test_p4_gen.py`（標準出力・終了コード・生成ファイルの集合・各ファイルの中身）。一覧は `uv run python tools/port/p4_progress.py [-v]`
- **結果（as of 2026-09-27）**: プラグインを使わない **119ケースすべてで一致**（正常終了75件は `gen/` がバイト単位で一致、エラー終了44件は標準出力・終了コード・途中まで書いたファイルが一致）。`ErrorCase/attribute-err`（SystemStackError）は `test_p3_cli` で確認。プラグインを使う35ケースは P5

## 8.6 CMakeLists.tecsgen.cmake（2026-10-05、tecsgen-rb の cmake 対応）

Ruby 版 tecsgen-rb の `generate.rb`（`gen_cmake_tecsgen`・`cmake_normalize_path`・`cmake_write_list`・`collect_celltype_names*`）と `tecsgen.rb`（`module CMake`）に対応する。`Makefile.tecsgen` と同じく root namespace の生成で出力し、CMake が `include()` するソース一覧のマニフェストにする。CLI オプションは無い。

| Python 版 | Ruby 版 | 内容 |
|---|---|---|
| `core/tecsgen.py` の `CMake` クラス | `TECSGEN::CMake` | プラグインが `add_source`・`add_include`・`add_define`・`add_link_option`・`add_custom_command`・`add_line` で足した内容を保持。`Makefile` クラスと同型。`TECSGEN.reset()`・`TECSGEN.set_default_config` から初期化する |
| `core/generate.py` の `gen_cmake_tecsgen` | `gen_cmake_tecsgen` | `AppFile` で `<gen>/CMakeLists.tecsgen.cmake` を書く（`.tmp` → 比較 → 改名。`-v` では "changed"・"renaming" の行も出る。エラー終了のときは `.tmp` が残る） |
| `cmake_normalize_path`・`cmake_write_list` | 同名 | `$(GEN_DIR)` → `${TECS_GEN_DIR}`、`$(TECSPATH)` → `${ASP3_TECSGEN_DIR}/tecs`、`$(BASE_DIR)`・`.` → `${ASP3_SRCDIR}`。絶対パスは `subst_tecspath` の後 `\` を `/` にする。`set(<変数名> "…" …)` の形で、一覧は重複を除く |
| `collect_celltype_names`・`_domain`・`_domain2` | 同名 | `gen_celltype_names*`（`f.print` で書く）のリスト版。ドメイン領域ごとに `_tecsgen.c`・セルタイプのソースを集める |

- **呼び出し位置**: `generate()` の `gen_makefile_tecsgen()` の次（セルが0個のときの早期 return の前）と、`gen_makefile()` の末尾。したがって、セルが無い領域でも出力される
- **出力する変数**: 外部仕様4章（4.2）を参照。空の一覧も `set(… )` として出す。`TECS_LINK_OPTIONS`・`TECS_CUSTOM_COMMANDS`・追加行は、あるときだけ
- **絶対パス**: 正解データ（`test/`・カーネル・配布パッケージの全ケース）の `CMakeLists.tecsgen.cmake` に、絶対パスは1つも出ていない（出力は相対パスか `${…}`）。このため、正解データを採るときの相対化の置き換えは不要だった（決定: 相対化は採取時に行う。必要になったときのための方針）
- **確認**: プラグインなし119ケース・プラグインあり77ケースで、`CMakeLists.tecsgen.cmake` を含めてバイト一致。`CMake.add_*` を呼ぶプラグインの出力は、標準のテストケースが無いので、合成した利用者プラグインで確認した（2026-10-09、`gen/` 13ファイルがバイト一致。[[tecsgen-python3 cmake対応計画 — C3 の結果#C3 の結果（2026-10-09）: `CMake.add_*` を呼ぶプラグインで Ruby 版と一致|C3 の結果]]）。`gen_cmake_tecsgen` は生成の最初に走るので、`gen_factory` など生成段階のフックから呼んだ `add_*` は出力に反映されない（Ruby 版と同じ）。この合成ケースは golden ケース `cmake_add` として固定した（2026-10-09、Python 版 PR #11 で `main` にマージ済み、`11f38ef`。[[tecsgen-python3 cmake対応計画 — C3 の結果#golden ケースとしての固定（2026-10-09）|固定の内容]]。プラグインありの一致は、`cmake_add_<種類>` 7件を加えた PR #12 のマージ後は 85/85）
