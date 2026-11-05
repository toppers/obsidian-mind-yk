---
date: 2026-08-22
description: "tecsgen内部仕様 第8章（コード生成、generate.rb）— 生成の起点、ファイル出力制御、プレースホルダ、CDL宣言的生成とプラグイン命令的生成の2経路。2026-09-15に検証済み。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 8 of 12. 2026-08-22、`generate.rb`・`plugin.rb`・`tecsgen.rb`（オプション解析部）を直接読んで 8.2/8.4/8.6 を検証・訂正。**2026-09-15、残っていた8.1/8.3/8.5を`tecslib/core/generate.rb`（`Namespace#generate`・`Celltype#generate_private_header`・`generate_celltype_factory_code`/`generate_cell_factory_code`）と`tecslib/plugin/HRPPlugin.rb`等の直接読解で検証・訂正**（[[work/active/tecsgen/tecsgen内部仕様 - 要再検証項目一覧#3. 第8章 コード生成 — 8.1/8.3/8.5節が旧内容のまま|要再検証項目一覧]]項目3）。8.1は実態と一致し訂正なし。8.3は省略されていた中間ステップ多数と二段階構成（本体／post）を追記。8.5は「FACTORY{}/factory{}によるCDL宣言的生成」と「プラグイン独自Rubyコードによる命令的生成」という**別系統の2経路**が同じ`tecsgen.cfg`という慣習的ファイル名に収束していただけ、という構造を訂正・明記。これで8章全節の検証パスが一巡した。

## 8. コード生成（generate.rb）

### 8.1 生成の起点

`root_namespace.generate`（`Namespace#generate`）が起点。1回の呼び出しの中で「`global_tecsgen.h`（typedef/struct/const の生成）→ 各 Signature の `generate` → 各 Celltype の `generate` → サブ Namespace への再帰」の順に処理し、最後に（`Region` の場合のみ）domain/class プラグインの `gen_factory` を呼ぶ。domain/class の `gen_factory` を末尾に回しているのは、他の生成コードが出力し終わった後でなければ正しく生成できないという V1.8 での設計判断（ソースコメント「ドメインプラグインの gen_factory は、諸々のコードの出た後で呼び出す」）。

> [!info] 2026-09-15 再検証: 訂正なし
> `tecslib/core/generate.rb`の`Namespace#generate`（127-181行）を直接読み、上記の記述が実態と一致することを確認した。

### 8.2 ファイル出力制御（AppFile / CFile）

> [!warning] CFile はテンポラリ書き出し用ではない
> 旧版は「`CFile`: テンポラリファイルに生成内容を書き出す」としていたが誤り。`CFile`（`plugin.rb:297`）は `File` の薄いラッパーで、`kconv` による文字コード変換（`$KCONV_CDL` へ変換して出力）を担うだけの汎用出力クラス。`.tmp` へ書いてから比較・リネームする仕組みを持つのは `AppFile` の側であり、`CFile` とは無関係の独立した2つのクラス。

- `AppFile.open`：`$force_overwrite`（`-f`）が偽の場合、常に `<name>.tmp` へ書き込む（同名を2回目以降 open した場合は追記モード）
- `AppFile.update`：生成完了後、`.tmp` と既存ファイルを行単位で比較し、完全一致すれば `.tmp` を削除、差分があれば `.tmp` を実ファイルへ `rename`（不要なタイムスタンプ更新を避けビルド差分を最小化）。`$force_overwrite` が真なら比較を行わず常に上書き
- テンプレートファイル（`_templ.c` 等）の生成可否は `-f`（`$force_overwrite`）とは無関係で、`--generate-all-template`（`$generate_all_template`）/ `--generate-no-template`（`$generate_no_template`）という別系統のオプションと `@b_reuse`（reuse セルタイプか）で決まる（`generate_template_code` 冒頭のガード節）

### 8.3 `_tecsgen.h` の生成

> [!warning] 2026-09-15訂正: 旧版は単一フェーズの9ステップとしていたが、実態は「本体（`generate_private_header`）」と「後処理（`generate_private_header_post`）」の**二段階**に分かれており、中間ステップも複数省略されていた。`Celltype#generate_private_header`／`generate_private_header_post`（`generate.rb` 1218-1325行）を直接読んで全面訂正。

セルタイプに対して以下の順序でコードを出力する（`Celltype#generate`から`generate_private_header`→（他の生成処理）→`generate_private_header_post`の順で呼ばれる。後者は`Namespace#generate_post`経由）:

**本体（`generate_private_header`）**

1. インクルードガード（`gen_ph_guard`）・セルタイプ情報コメント（`gen_ph_info`）・グローバル/シグニチャヘッダのinclude（`gen_ph_include`）
2. `extern "C"`ブロック#1: CELLCB型定義（`gen_ph_cell_cb_type`）→ CBを持たずINIBのみの場合のCB→INIB置換マクロ（`gen_ph_INIB_as_CB`）→ セルの宣言（`gen_ph_extern_cell`、externの実体・テーブル宣言のみで**初期化子はここには無い**——実際の初期化データは`generate_cell_code`が別途`_tecsgen.c`側に生成する）→ IDX型定義（`gen_ph_typedef_idx`）→ 受け口関数プロトタイプ（`gen_ph_ep_fun_prototype`）
3. `CB_TYPE_ONLY`ガード内: セルタイプ基本情報（`gen_ph_base`）→ VALID_IDXマクロ（`gen_ph_valid_idx`）→ 呼び口数マクロ（`gen_ph_n_cp`、呼び口配列がある場合のみ）→ 受け口数マクロ（`gen_ph_n_ep`、受け口配列がある場合のみ）→ オプション呼び口の未結合テストマクロ（`gen_ph_test_optional_call_port`）→ GET_CELLCBマクロ（`gen_ph_get_cellcb`）→ 属性・変数アクセスマクロの**通常形**（`gen_ph_attr_access`）→ 呼び口関数マクロ（`gen_ph_cp_fun_macro`、`#ifndef TECSFLOW`/`#else`で通常版・TECSFLOW版を両方生成。最適化結果によりVMT経由or直接呼び出しを切替）
4. `extern "C"`ブロック#2: 受け口**スケルトン**プロトタイプ（`gen_ph_ep_skel_prototype`、ブロック#1の`ep_fun_prototype`とは別物）→ `CB_TYPE_ONLY`ガード内でディスクリプタ参照／設定関数（`gen_ph_ref_desc_func`／`gen_ph_set_desc_func`）
5. `CB_TYPE_ONLY`ガード内、末尾の一括マクロ群: VALID_IDX・GET_CELLCBの**短縮形**（`gen_ph_valid_idx_abbrev`／`gen_ph_get_cellcb_abbrev`）→ 属性・変数アクセスマクロの**短縮形**（`gen_ph_attr_access_abbrev`、ステップ3の通常形とはここで初めて隣接する——両者は連続していない）→ 呼び口関数マクロの短縮形（`gen_ph_cp_fun_macro_abbrev`）→ ディスクリプタ参照／設定マクロの短縮形→ オプション呼び口未結合テストの短縮形→ 受け口関数マクロ（`gen_ph_ep_fun_macro`）→ FOREACH_CELL／END_FOREACH_CELLマクロ（`gen_ph_foreach_cell`）→ CB初期化マクロ（`gen_ph_cb_initialize_macro`、`$ram_initializer`の値に関わらず常に出力）→ dealloc用コード（`gen_ph_dealloc_code`、通常版・`_RESET`版の2回）

**後処理（`generate_private_header_post`、`Namespace#generate_post`経由で全ファイル生成後にまとめて呼ばれる）**

6. `#include "<CELLTYPE>_inline.h"`のインクルード行（`gen_ph_inline`）
7. inline受け口を持つ場合のみ、`CB_TYPE_ONLY`定義の`#undef`（`gen_ph_undef`）
8. インクルードガードの閉じ（`gen_ph_endif`）

旧版の「9ステップ」のうち1〜8は上記の本体フェーズに、9（`#include`行）は後処理フェーズに属し、両者は`Celltype#generate`と`Celltype#generate_post`という別々のメソッド呼び出し（さらに言えば別々のパス全体を1周した後）で実行される——同じ`generate_private_header`呼び出し内で連続して起きるわけではない。

### 8.4 `_factory.h` の生成

> [!warning] 2026-09-15訂正: `$id$`の展開内容が誤り、かつ利用可能なプレースホルダを大幅に過小記載していた。`generate.rb`の`subst_name`（5234-5276行）・`get_name_array`（3866-3922行）・`generate_celltype_factory_code`（4905-4947行、`FACTORY{}`用）・`generate_cell_factory_code`（4949-5036行、`factory{}`用）を直接読んで訂正。

- `factory{}`（セル単位）／`FACTORY{}`（セルタイプ単位）記述から静的変数・初期化コードを生成
- **`FACTORY{}`と`factory{}`で使えるプレースホルダの種類が異なる**——`FACTORY{}`（`generate_celltype_factory_code`）は`$ct$`/`$ct_global$`/`$$`の3種のみを素の`gsub`で置換するのに対し、`factory{}`（`generate_cell_factory_code`）は`subst_name`メソッドを通して**11種類**のプレースホルダをすべて使える（`FACTORY{}`にはセル単位の文脈が無いため、セル固有のプレースホルダはそもそも意味を持たない）

`factory{}`で使える全プレースホルダ（`subst_name`のdocコメントと`get_name_array`の実装を突き合わせた対応表）:

| プレースホルダ | 展開内容 | 備考 |
|---|---|---|
| `$ct$` | セルタイプ名（ローカル名） | |
| `$ct_global$` | セルタイプのグローバル名 | |
| `$cell$` | セル名（ローカル名） | 旧版に記載なし |
| `$cell_global$` | セルのグローバル名 | |
| `$cb$` | セルのCB参照式 | **設定により形が変わる**——singletonなら`<ct_global>_SINGLE_CELL_CB`、`@b_need_ptab`が偽（配列添字方式）なら`<ct_global>_CB_tab[<index>]`、真（ポインタテーブル方式）なら`<cell_global>_CB` |
| `$cbp$` | セルのCBへのポインタ式 | CBがあれば`&<cb>`、無くINIBのみなら`&<INIB名>`、どちらも無ければ`((<ct_global>_IDX)0)` |
| `$cb_proto$` | プロトタイプ宣言用のCB名 | `$cb$`とは異なる文字列になりうる（配列添字方式では`<ct_global>_CB_tab[]`のように添字を空にする） |
| `$id$` | **`"<ct>_<cell_global>"`**（セルタイプ名とセルのグローバル名を`_`で連結した文字列） | **旧版の「セル名」という説明は誤り**——単なるセル名ではなくセルタイプ名を前置した合成識別子 |
| `$ID$` | セルID（整数） | `$id$`（小文字、合成文字列）と紛らわしい別物 |
| `$idx$` | セルのIDX式 | `@idx_is_id_act`が真なら整数ID、偽なら`$cbp$`と同じCBP式 |
| `$$` | `$`（エスケープ） | |

**プレースホルダとして公開されていない内部フィールド**: `get_name_array`が組み立てる11要素の配列のうち、`cell_CB_INIT`（CB定義用の変数名、`name_array[3]`）と`cell_INIB_name`/`cell_INIB_proto`（`name_array[5]`/`[11]`）は`subst_name`のどのプレースホルダにも対応せず未使用——CB/INIBの定義側（`_tecsgen.c`生成、`generate_cell_code`）はこれらをRubyの文字列補間で直接使い、`factory{}`のテキスト置換機構とは別経路で扱われる。

### 8.5 `tecsgen.cfg` の生成

> [!warning] 2026-09-15訂正: 「`tecsgen.cfg`の生成」という単一の仕組みではなく、**互いに無関係な2つの生成経路**が慣習的に同じ命名（`tecsgen.cfg`／`*_tecsgen.cfg`）のファイルへ収束していただけだった。`generate.rb`の`Celltype#generate_celltype_factory_code`/`generate_cell_factory_code`（4903-4947・4949-5036行）、`tecslib/plugin/DomainPlugin.rb`（89行）、`tecslib/plugin/HRPPlugin.rb`（159-168行）、`tecslib/plugin/HRMPDomainPlugin.rb`（89-97行）、および`tecs/rpc/tTINETChannel.cdl`（62-110行）を直接読んで訂正。

**経路A: CDLの`FACTORY{}`/`factory{}`宣言による生成**（宣言的）
- `generate_celltype_factory_code`（セルタイプ単位の`FACTORY{ write(...) }`）と`generate_cell_factory_code`（セル単位の`factory{ write(...) }`）が処理する。呼び出し元は`Celltype#generate`（8.1の「celltypeのコードを生成」ステップの内側）——プラグインの`gen_factory`とは無関係。
- 出力先ファイル名は**CDL側が`write(file_name, format, ...)`の第1引数で自由に指定**する。「`tecsgen.cfg`」は多くのCDLが選ぶ**慣習的な名前**にすぎず、機構自体が固定しているわけではない——実例として`tecs/rpc/tTINETChannel.cdl`は`"tinet_tecsgen.cfg"`という別名へ出力している（TOPPERS/TINETの静的API `TCP_CRE_CEP`／`TCP_CRE_REP`等）。`$ct$`/`$ct_global$`/`$id$`等のプレースホルダはこの経路の`format`/`file_name`文字列内で置換される（8.4のプレースホルダとは適用対象が異なる）。

**経路B: プラグイン自身のRubyコードによる生成**（命令的）
- `DomainPlugin`/`ClassPlugin`の基底`gen_factory`は空実装（no-op）。`HRPPlugin`・`HRMPDomainPlugin`・`FMPObjectPlugin`等のカーネル関連プラグインは`gen_factory`を**独自に override**し、その中で直接`AppFile.open("#{$gen}/tecsgen.cfg")`して固定文字列（例: `HRPPlugin`は`#include "extsvc_fncode.h"`を`@@include_extsvc_fncd`フラグで一度だけ出力）を書き込む。
- 呼び出し元は8.1で確認済みの`Namespace#generate`末尾のdomain/classプラグインディスパッチ（`get_domain_type.gen_factory`/`get_class_type.gen_factory`）——経路Aの`Celltype#generate`内呼び出しとは完全に別のタイミング・別の呼び出し階層。

両経路は「セルタイプ内で完結するコード生成の流れの中で動く経路A」と「全体の生成が終わったあとにプラグインが横断的に動く経路B」という、設計上まったく異なる位置づけを持ちながら、結果として同じ`.cfg`ファイルへ書き込むことがあるため、ソースを読まずに挙動だけを見ると「1つの`tecsgen.cfg`生成機構」に見えてしまう。

### 8.6 INITIALIZE_TECS() の生成

> [!note] グローバルヘッダの一部であり、セルタイプ別 `_tecsgen.h` ではない
> `INITIALIZE_TECS()` は 8.1 の `gen_global_header`（`global_tecsgen.h` 生成）の中で出力される（`generate.rb:273`）。8.3 の `_tecsgen.h` はセルタイプごとに生成されるファイルであり、`INITIALIZE_TECS()` はそれとは別のグローバル1ファイルにのみ定義される。

V1.3 以降常に生成される初期化マクロ。全セルタイプの CB 初期化コードを呼び出す。後方互換のため `INITIALZE_TECSGEN()`（原文ママ、`INITIALIZE` のタイポを含む旧名）が `INITIALIZE_TECS()` の別名として併せて定義される（`generate.rb:280`）。

---

