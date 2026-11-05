---
date: 2026-08-22
description: "tecsgen内部仕様書 第6章（意味解析）— set_definition_join・set_require_join（require結合の自動生成）・check_join（未結合/配列/size_isチェック）・ポストコード処理。set_require_joinの役割誤認を訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 6 of 12. 2026-08-22、`tecsgen.rb`（`syntax_analisys`/`semantics_analisys_1`/`semantics_analisys_2`）・`componentobj/cell.rb`・`componentobj/celltype.rb`・`componentobj/namespace.rb`・`pluginModule.rb` を直接読んで全面検証・訂正。

## 6. 意味解析

> [!warning] set_require_join は「未結合エラーの検出」ではない
> 旧版は「`optional` 指定のない呼び口で Join が存在しないものをエラーとして報告する」としていたが誤り。その検出は 6.3 の `check_join`（`S1042`/`S1043`）が行う。`set_require_join` はセルタイプの **`require` 節（例: `require Foo foo;`）で宣言された呼び口へ、対象セルタイプの singleton セルまたは指定セルへの `Join` を自動生成する**処理であり、エラー検出ではなく暗黙結合の生成が主目的（`Cell#set_require_join`、`componentobj/cell.rb:1638`）。

処理全体は `TECSGEN` クラス（`tecsgen.rb`）の3段階に分かれており、意味解析はその中間の2段階にまたがる。

- `syntax_analisys`：全 CDL を `Import.new` でパースし、`Generator.end_all_parse` を呼んで構文解析完了を報告（ポストコードのパースはこの後も続く）
- `semantics_analisys_1`：`Cell.create_reverse_join` → `set_definition_join`（1回目）→ プラグインのポストコード生成・再パース → `Cell.create_reverse_join`（再実行）→ `set_definition_join`（2回目）→ `set_max_entry_port_inner_cell` → `set_require_join`
- `semantics_analisys_2`：`Cell.make_cell_list2` → `Cell.create_reverse_require_join` → `set_port_reference_count` → `check_join` → `check_ref_but_undef`

### 6.1 set_definition_join（結合定義解決）

CDL パース時は呼び口名・属性名が文字列のまま Join に格納されている。

`set_definition_join` は `Namespace#set_definition_join` が Namespace ツリーを再帰走査して各 Cell の `set_definition_join`（`componentobj/cell.rb:1684`）を呼び出す形で、各 Cell の Join の左辺を解決する:
- `@name` がセルタイプのポート名 → `@definition = Port`
- `@name` がセルタイプの属性/変数名 → `@definition = Decl`
- 解決できない場合 → エラー
- 併せて `create_relay_allocator_join`（through 適用後のリレー join 生成）と、composite セルタイプの展開（`expand`）もこの中で行う

2回呼ばれる理由: プラグインのポストコード（`tmp_plugin_post_code.cdl`）が1回目のパース後に生成されるため、そのセルの結合解決に2回目が必要（`tecsgen.rb` 256行目・279行目のコメントに明記）。

### 6.2 set_require_join（require 結合の自動生成）

`Namespace#set_require_join`（`componentobj/namespace.rb:566`）は `@celltype_list` の各 Celltype に対して `Celltype#set_require_join`（`componentobj/celltype.rb:843`）を呼び、セルタイプの `@require` リスト（`require` 節で宣言された `[呼び口名, セルタイプ|セル, Port]` の組）を走査する。各要素について、対象セルタイプに属するすべての Cell の `Cell#set_require_join(cp_name, cell_or_ct, port)` を呼び出し:

- 右辺が Celltype の場合、`get_singleton_cell` でその singleton セルを取得（見つからなければ `S1025` エラー）
- 右辺が Cell の場合、そのセルへの到達可能性を `@region.distance` で確認（`S1026`）
- 既に同名呼び口が結合済みなら上書きを警告（`W1003`）
- そうでなければ `cell.port` 形式の右辺式を組み立てて `Join.new` → `new_join` で結合を新規生成し、`set_definition` まで行う

呼び出しは `semantics_analisys_1` の末尾（ポストコード生成・2回目の `set_definition_join` の後）で1回のみ。ソース中には「post の前にも」という mikan コメントがあり、ポストコードで生成されたセルの `require` 結合と2回目呼び出しの間の考慮が未完了である旨が示されている。

### 6.3 check_join（結合整合性チェック）

`Namespace#check_join`（`componentobj/namespace.rb:602`）が各 Cell の `check_join`（`componentobj/cell.rb:1337`）と `check_reverse_require` を呼ぶ。呼び口の**未結合検出はここで行われる**:

- `require` でも `optional` でもない呼び口に Join がない → `S1042`（allocator 呼び口なら `S1043`）
- 添数あり呼び口配列：結合定義との要素数不一致（`S1044`）、`optional` でない要素の未初期化（`S1045`）
- 添数なし呼び口配列：`optional` でない要素の未初期化（`S1046`）
- ポインタ属性/変数の `size_is` 指定：非ポインタ型への指定は `S1048`、定数評価できない引数は `S1049`
- 生成されないリージョンへの結合は `check_region2` で検出

旧版が挙げていた「シグニチャ不一致」「`restrict` によるリージョン間アクセス制御」「`Descriptor` 型パラメータ整合性」は、それぞれ結合時（`join.set_definition`／`Port#find` 経由の型チェック）や `check_restrict_list`（`set_definition_join` 内、6.1 参照）など他箇所で行われており、`check_join` 自体の主眼は**未結合・配列要素数・`size_is`・到達可能リージョン**の4点である（要再検証: シグニチャ不一致検出の正確な発生箇所）。

### 6.4 ポストコード処理（PluginModule）

プラグインが意味解析段階で必要な追加 CDL コードを生成する仕組み。`semantics_analisys_1` の中、1回目の `set_definition_join` の直後に実行される。

1. `PluginModule.gen_plugin_post_code`（`pluginModule.rb:156`）が各プラグインの `gen_cdl_file` を呼ぶ
2. 生成された CDL を `gen/tmp_plugin_post_code.cdl` に書き出し
3. その CDL を `Import.new` で再パース（`pluginModule.rb:229`）
4. 再パース後に `Cell.create_reverse_join` → `set_definition_join`（2回目）を実行（`check_join` は `semantics_analisys_2` まで行われない）

---

