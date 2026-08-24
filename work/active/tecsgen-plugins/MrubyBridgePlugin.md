---
date: 2026-08-14
description: "tecsgen 標準付属プラグイン MrubyBridgePlugin（実体5ファイル）の仕様書。mruby スクリプトから TECS シグニチャの受け口を呼び出すブリッジセルタイプを自動生成する、シグニチャ単位のプラグイン。1つのプラグイン名が付与位置により異なる具象クラスへ自動解決される MultiPlugin ディスパッチ機構の実例でもある"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
  - plugin
---

# MrubyBridgePlugin 仕様書

> [!info] 文書状態
> [[North Star]] の「未記載プラグイン」リストが1項目として挙げる「MrubyBridgePlugin」は、実際には `tecslib/plugin/` 配下の5ファイル（`MrubyBridgePlugin`・`MrubyBridgeSignaturePlugin`・`MrubyBridgeCelltypePlugin`・`MrubyBridgeCompositePlugin`・`MrubyBridgeCellPlugin`）＋共有モジュール（`tecslib/plugin/lib/MrubyBridgeCelltypePluginModule.rb`）の集合である。[[work/active/tecsgen-plugins/ATK1Plugin|ATK1Plugin]] と同じ理由（実態が北極星の1行より多い）で1本の横断ノートに統合する。一次資料はこれら5ファイル・`tecslib/core/pluginModule.rb`（`load_plugin`/`MultiPlugin`）・`tecslib/plugin/MultiPlugin.rb`・呼び出し元4ファイル（`cell.rb`・`celltypeModule.rb`・`signature.rb`・`join.rb`・`domaintype.rb`・`classtype.rb`）。加えて、他のプラグインと異なり**作者自身による設計メモ `tecs/mruby/mrubyBridge.txt`（大山博司、2012年11月初版・2013年5月改訂）が同梱されている**ため、CDL 記述例・型対応表・既知の課題は推測ではなくこの一次資料から直接採録した。使用例の実物は `tecs/mruby/tMruby.cdl`（mruby VM 側のセルタイプ定義。ブリッジ呼び出しそのものはアプリケーション固有のため同梱されていない）。ソースの位置は [[TECSCDE外部仕様]] と同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 概要

**MrubyBridgePlugin は、TECS の signature 定義に基づき、mruby スクリプトから TECS セルの受け口を呼び出すための「ブリッジセルタイプ」を自動生成する、シグニチャプラグインである。**

```
         +--------------------------+              +-------------------+
         |     (ブリッジセル)         |              |    (目的セル)      |
         |                          |              |                   |
mruby    | nMruby::tsSignatureBridge|  sSignature  |  tTargetCelltype  |
 - - - > |       BridgeCell         |--------------|>   TargetCell     |
         |                          |cTECS    eTest|                   |
         | mruby クラス：            |              |                   |
         |  TECS::TSignatureBridge  |              |                   |
         +--------------------------+              +-------------------+
```
（`tecs/mruby/mrubyBridge.txt` 15〜23行より）

## 2. 発見: MultiPlugin ディスパッチ機構

**「MrubyBridgePlugin」という1つの CDL 上の名前は、それがどこに付与されるかによって、実際にインスタンス化される Ruby クラスが自動的に切り替わる。** この仕組みは Mruby 系列に限らず tecsgen プラグインシステム全体に存在する基盤機構であり、[[tecsgen外部仕様]] 6.2（`generate` の specifier/statement 2形式）ともまた別の層にある。

### 2.1 仕組み

`tecslib/core/pluginModule.rb` の `load_plugin(plugin_name, superClass)` が全プラグインのロード窓口である。指定されたクラスが `superClass` を継承していればそのまま使うが、`MultiPlugin` を継承している場合は `plClass.get_plugin(superClass)` を呼び、返ってきたクラスを代わりに使う（79〜93行）。`MultiPlugin < Node`（`Plugin` の系列ではない）であり、`self.get_plugin` をオーバーライドすることで「呼ばれた文脈に応じた実体を返す」ディスパッチャとして機能する。

### 2.2 呼び出し元と `superClass` の対応

`load_plugin` の呼び出し元を全て特定した結果、CDL 上の付与位置と `superClass` は次のように対応する。

| CDL 上の付与位置 | 呼び出し元 | `superClass` |
|---|---|---|
| `celltype` の `[generate(...)]` | `celltypeModule.rb:60`（`kind_of? Celltype`） | `CelltypePlugin` |
| `composite celltype` の `[generate(...)]` | `celltypeModule.rb:60`（`kind_of? CompositeCelltype`） | `CompositePlugin` |
| `cell` の `[generate(...)]` | `cell.rb:683` | `CellPlugin` |
| `generate(Plugin, sSignature, "opts");` 独立文（statement 形式） | `signature.rb:314` | `SignaturePlugin` |
| `join` の `through` 指定子 | `join.rb:744` | `ThroughPlugin` |
| `region` の `domain(...)` 指定子 | `domaintype.rb:62` | `DomainPlugin`（[[work/active/tecsgen-plugins/HRP2Plugin\|HRP2Plugin]] 参照） |
| `class`（HRMP）指定子 | `classtype.rb:63` | `ClassPlugin` |

### 2.3 MrubyBridgePlugin の場合

`MrubyBridgePlugin.get_plugin` は4分岐のみ実装する（`ThroughPlugin`・`DomainPlugin` はコメントアウトで未対応）。

| `superClass` | 返すクラス |
|---|---|
| `SignaturePlugin` | `MrubyBridgeSignaturePlugin` |
| `CelltypePlugin` | `MrubyBridgeCelltypePlugin` |
| `CompositePlugin` | `MrubyBridgeCompositePlugin` |
| `CellPlugin` | `MrubyBridgeCellPlugin` |

つまり CDL 記述者は `generate(MrubyBridgePlugin, sSignature, "opts");`（シグニチャへの statement 形式、後述 4 章の主用途）だけでなく、`[generate(MrubyBridgePlugin, "opts")]` を celltype／composite celltype／cell のいずれに書いても、同じプラグイン名のまま正しい実装が自動選択される。

## 3. 5ファイル構成

| クラス | 親クラス | 役割 |
|---|---|---|
| `MrubyBridgePlugin` | `MultiPlugin` | ディスパッチャ本体。それ自身はインスタンス化されない。`initialize`／`gen_factory` を持たない |
| `MrubyBridgeSignaturePlugin` | `SignaturePlugin` | **本体**。シグニチャ単位で呼ばれ（4章の CDL 記述）、mruby ブリッジセルタイプ・mruby 初期化セルタイプ・構造体アクセス用セルタイプを生成する |
| `MrubyBridgeCelltypePlugin` | `CompositePlugin` | celltype に付与した場合の実装。**単体では何もせず**、そのセルタイプの各セルごとに `generate(MrubyBridgeCellPlugin, セルパス, "opts");` という CDL コード片を動的に書き出し `Import.new` で取り込む（`lib/MrubyBridgeCelltypePluginModule.rb` 118〜127行）——セル単位の処理へのファンアウトを、コード生成ではなく CDL の動的インポートで実現している |
| `MrubyBridgeCompositePlugin` | `CompositePlugin` | composite celltype に付与した場合の実装。`MrubyBridgeCelltypePlugin` と**完全に同一の実装**（同じ `MrubyBridgeCelltypePluginModule` を `include` し、同じ `CompositePlugin` を継承）——後述5.1参照 |
| `MrubyBridgeCellPlugin` | `CellPlugin` | 実際の1セル分のブリッジコード（受け口関数の呼び出し変換等）を生成する。`ignoreUnsigned`／`exclude_port`／`exclude_port_func`／`auto_exclude` オプションを保持 |

## 4. CDL 記述（`tecs/mruby/mrubyBridge.txt` より正確に採録）

### 4.1 ブリッジプラグインの呼び出し（signature への statement 形式）

```tecs-cdl
generate( MrubyBridgePlugin, sSignature, "" );
```

シグニチャ `sSignature` は、この記述より前に定義済みでなければならない。第3引数（プラグイン引数）：

| 引数 | 意味 |
|---|---|
| `ignoreUnsigned` | `true` で無符号整数へのポインタ型に有符号ポインタクラスを使用（メモリ節約） デフォルト `false` |
| `include` | ブリッジに含める関数を指定。`exclude` と同時指定不可 |
| `exclude` | ブリッジから除外する関数を指定。`include` と同時指定不可 |

```tecs-cdl
generate( MrubyBridgePlugin, sSignature, "exclude=fun99" );

generate( MrubyBridgePlugin, sSignature,
    "ignoreUnsigned=true, "
    "include='func1,func2', "
    "include='func3,func4', "
 );
```

### 4.2 自動生成されるブリッジセルタイプ

ネームスペース `nMruby` の下に、シグニチャ名へ `t` を前置した名前で生成される（例: `sSignature` → `nMruby::tsSignature`、呼び口 `cTECS` を持つ）。

```tecs-cdl
// 内部で生成・解釈される（記述者が書く必要はない）
namespace nMruby {
  celltype tsSignature {
    call sSignature cTECS;
  };
};
```

### 4.3 ブリッジセルの設置（記述者が書く）

```tecs-cdl
cell nMruby::tsSignature BridgeCell {
    cTECS = Cell.eEnt;
};

// mruby VM 名を指定する場合
cell nMruby::tsSignature BridgeCell {
    cTECS = Cell.eEnt;
    VMname = "VM2";       // 未指定時は "VM" が仮定される
};
```

`VMname` は、ブリッジを mruby VM の初期化セル（`VM_TECSInitializer` 等）へ登録する際のセル名指定。tecsgen 実行時に次の案内が出力され、記述者が手動で結合する必要がある。

```
MrubyBridgePlugin: join your VMs cInitialize to VM_TECSInitializer.eInitialize
```

### 4.4 mruby 側

生成されたブリッジクラスはモジュール `TECS` の下、シグニチャ名へ `T` を前置した名前になる（例: `TECS::TsSignature`）。ブリッジセル名を引数に `new` するとインスタンスが得られる。

```ruby
bridge = TECS::TsSignature.new( "BridgeCell" )
```

## 5. 発見

### 5.1 `MrubyBridgeCelltypePlugin` と `MrubyBridgeCompositePlugin` は実装が同一

両クラスはともに `CompositePlugin` を継承し、ともに `MrubyBridgeCelltypePluginModule` を `include` する——ソース上は完全に同じ実装である。`MultiPlugin#get_plugin` は `superClass == CelltypePlugin` の分岐で `MrubyBridgeCelltypePlugin` を返すが、そのクラス自身は `CelltypePlugin` ではなく `CompositePlugin` を継承しており、クラス名と継承関係が食い違っている。実害がないのは、`load_plugin` が返り値クラスに対して `superClass` との継承関係を再検証しないこと（2.1 参照）、かつ `CelltypePlugin` と `CompositePlugin` のメソッド契約（`initialize(celltype,option)`／`new_cell`／`gen_factory`／`self.gen_post_code`）が完全に一致することによる——Ruby のダックタイピングの上に成り立つ設計。`MrubyBridgeCelltypePlugin.rb` 内には旧実装（`< CelltypePlugin` で独自のオプション解析コードを持つ版）がコメントアウトのまま残っており、共有モジュールへのリファクタリング過程で生じた命名の残骸と見られる。

### 5.2 celltype 単位の適用は「セルごとの CDL コード片を書き出して Import する」

`MrubyBridgeCelltypePluginModule#new_cell` は、C コードや OIL を直接出力するのではなく、`$gen/tmp_MrubyBridgeCelltypePluginModule_<celltype>_<n>.cdl` という一時ファイルに `generate( MrubyBridgeCellPlugin, <セルの namespace path>, "<opts>" );` という CDL 文そのものを書き出し、`Import.new` でその場に取り込む。CDL 処理系がセル単位のプラグイン適用を実行時に動的展開するマクロ的な仕組みとして `Import` 機構を使っている——他のプラグイン（ATK1・HRP2・Notifier）にはない手法。

### 5.3 プラグイン引数は2つの独立した語彙を持つ

シグニチャレベル（`MrubyBridgeSignaturePlugin`、4.1 節）の `include`/`exclude` は**関数**を対象とするのに対し、celltype/composite レベル（`MrubyBridgeCelltypePluginModule`）の `exclude_cell`/`exclude_port`/`exclude_port_func`/`include_inner_cell`/`auto_exclude` は**セル・ポート**を対象とする——同じ「exclude」という語が付与位置によって指す対象が異なる。両者とも [[tecsgen外部仕様]] 6.4 の `param=value` カンマ区切り文法に従う。

## 6. データ型対応（`mrubyBridge.txt` より抜粋）

| TECS 型 | 対応する mruby 型（クラス） |
|---|---|
| `bool_t` | `true`/`false`（mruby の `false`/`nil` を C の `false` として扱う） |
| `char_t`/`uintN_t`/`int`/`short`/`long` | `FIXNUM` |
| `double64_t`/`float32_t` | `FLOAT` |
| `intN_t*`/`uintN_t*` 等のポインタ型 | `TECS::IntNPointer`/`TECS::UIntNPointer` 等の専用クラス |
| タグ付き構造体・構造体ポインタ | `TECS::構造体タグ名`（タグなし構造体・typedef 名での構造体は不可） |
| `void*` | **非対応** |

戻り値に使えるのは `void`／スカラー型／スカラー型に typedef された型のみ。引数指定子は `in`/`inout`/`out` のみ（`send`/`receive` 不可）。関数名 `initialize` は ruby の予約メソッド名と衝突するため `initialize_cell` に自動置換される。

## 7. 制約・注意点

- `void*` は扱えない。ポインタ値そのものを渡したい場合は `intptr_t`/`uintptr_t` を使う（ポインタ型は「指す先の値」を扱うためのものであり、アドレス値そのものの受け渡しには使えない）。
- 構造体はタグ付き（`struct TAG`）のみ対応。typedef された構造体名では扱えない。
- 作者自身が「残課題」として明記している未解決事項（`mrubyBridge.txt` 308行以降）: VM が異なる場合にブリッジ名のアクセス制限が不十分（他 VM に割り付けたブリッジ名が見える）、`send`/`receive` 未対応、構造体メンバの型制限（`string`/`size_is` 指定 `char*` 等）が残る。
- `MrubyBridgeCelltypePlugin`/`MrubyBridgeCompositePlugin` の継承関係とディスパッチ元の食い違い（5.1）は実害こそないが、クラス名から想定される継承関係と実際が異なる点で読解を妨げる。

## Related

- [[tecsgen外部仕様]] — 6.2 プラグイン呼び出し規約（`generate` 2形式）・6.3 標準付属プラグイン一覧・6.4 プラグイン引数の文法
- [[work/active/tecsgen-plugins/ATK1Plugin]] — 同じ「北極星1行 = 実体複数ファイル」パターンで統合ノート化した先例
- [[work/active/tecsgen-plugins/HRP2Plugin]] — `MultiPlugin` ディスパッチ表の `DomainPlugin` 行の参照元
- [[work/active/tecsgen-plugins/NotifierPlugin]] — `ClassPlugin`（HRMP class 指定子）の参照元
- [[reference/03-Resources/my-topic/wiki/plugin-mruby-bridge]] — 概念スタブページ（本ノートへ相互リンク）
- [[North Star]] — カーネル対応プラグイン仕様書化の進捗管理
