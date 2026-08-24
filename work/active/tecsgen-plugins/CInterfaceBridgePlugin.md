---
date: 2026-08-14
description: "tecsgen 標準付属プラグイン C2TECSBridgePlugin・TECS2CBridgePlugin の仕様書。プレーンな C コードと TECS 受け口/呼び口の間で相互に呼び出しブリッジセルを自動生成する、対になる2つの SignaturePlugin"
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

# C2TECSBridgePlugin / TECS2CBridgePlugin 仕様書

> [!info] 文書状態
> [[North Star]] の C インタフェース系2件（プラグイン仕様書シリーズの最終カテゴリ）。両クラスとも単一ファイル・`< SignaturePlugin`（`tecslib/plugin/C2TECSBridgePlugin.rb` 215行、`tecslib/plugin/TECS2CBridgePlugin.rb` 186行）で、`MultiPlugin` 対応表どおり signature への statement 形式でのみ呼び出せる。`C2TECSBridgePlugin` には一次資料 `doc/C2TECSBrdigePlugin.txt`（ファイル名のタイポ "Brdige" は原文ママ）と実使用例2件（`test/signaturePlugin/generate.cdl`、`test/mruby/MrubyBridge-ASP3/test.cdl`）が存在するが、`TECS2CBridgePlugin` には一次資料も単独使用例も一切なく、リポジトリ内での唯一の実使用は [[work/active/tecsgen-plugins/Mruby2CBridgePlugin|Mruby2CBridgePlugin]] が内部で生成する CDL のみ（詳細は5節）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 概要

**両プラグインは名前どおり対称的な、TECS と C の橋渡しを行う一対のシグニチャプラグインである。**

- **`C2TECSBridgePlugin`**（C → TECS）: プレーンな C コードから TECS セルの受け口を直接呼び出せるようにする。呼び口 `cCall` を持つブリッジセルタイプ `nC2TECS::t<シグニチャ名>` を生成し、CDL でこれを目的セルの受け口へ結合する。生成されたヘッダをインクルードした C コードから、通常の C 関数として呼べる。
- **`TECS2CBridgePlugin`**（TECS → C）: 逆方向。受け口 `eEnt` を持つブリッジセルタイプ `nTECS2C::t<シグニチャ名>` を生成し、その受け口関数本体はプレーンな C 関数（同名・ユーザまたは他ジェネレータが実装）を素通しで呼び出すだけになる。TECS の join 経由の呼び出しを最終的に「同名のグローバル C 関数呼び出し」に変換する。

## 2. CDL構文

### 2.1 C2TECSBridgePlugin（`doc/C2TECSBrdigePlugin.txt` より）

```tecs-cdl
// signature sSignature, cell CellToBeCalledFromC は定義済みとする
generate( C2TECSBridgePlugin, sSignature, "prefix='Sig'" );  // nC2TECS::tsSignature セルタイプを生成
cell nC2TECS::tsSignature C2TECSBridge {                     // ブリッジセルを生成（目的セルに結合）
   cCall = CellToBeCalledFromC.eEntry;
};
```

生成される `gen/sSignature.h`（または `header_name` オプションで指定した名前）を C コード側で `#include` すると、シグニチャの各関数を通常の C 関数として呼び出せる（`test/signaturePlugin/generate.cdl` 実例: `generate( C2TECSBridgePlugin, sTest, "prefix='X_', header_name='TestProto.h'" );`）。

実運用例として `test/mruby/MrubyBridge-ASP3/test.cdl`（154〜160行）は POSIX の `main()` 相当のコードから mruby VM の受け口 `eMain` を直接呼び出すために使っている——[[work/active/tecsgen-plugins/MrubyBridgePlugin|mruby ブリッジ]]系との実際の接続点。

### 2.2 TECS2CBridgePlugin（単独使用例なし、`Mruby2CBridgePlugin.rb` 内の生成 CDL から再構成）

```tecs-cdl
generate( TECS2CBridgePlugin, sMySignature, "silent=true" );
// nTECS2C::tsMySignature セルタイプが生成される
cell nTECS2C::tsMySignature TECS2C_MySignature {};
// 呼び出し側セルの呼び口を、このセルの受け口 eEnt へ結合する
```

## 3. 動作

### 3.1 C2TECSBridgePlugin（`gen_cdl_file` 68〜85行、`gen_postamble` 114〜195行）

1. `[singleton, active]` セルタイプ `nC2TECS::t<シグニチャ名>` を生成。呼び口 `cCall` のみを持つ（受け口はなし）。
2. `gen_postamble` で、シグニチャの各関数について `#{prefix}#{func_name}#{suffix}(...)` というグローバル C 関数を .c ファイルとヘッダファイルの両方に生成する。関数本体は `cCall_#{func_name}(...)` を呼ぶだけ（呼び口経由で結合先セルの受け口へ転送）。
3. **呼び出し経路**: プレーン C コード → 自動生成された `prefix_funcname_suffix()` → `cCall_funcname()`（呼び口マクロ） → 結合先セルの受け口関数。
4. `[singleton, active]` の `active` 指定はソースコードコメントで明言されている通り実際にアクティブセルにする意図ではなく、警告 `W1002` を抑制するためだけの回避策（113行付近のコメント「this celltype is not active actually. 'active' is specified to prevent W1002」）。

### 3.2 TECS2CBridgePlugin（`gen_cdl_file` 58〜76行、`gen_ep_func_body` 98〜143行、`gen_postamble` 146〜182行）

1. `[singleton, inline]` セルタイプ `nTECS2C::t<シグニチャ名>` を生成。受け口 `eEnt` のみを持つ（呼び口はなし）。
2. `gen_ep_func_body` で、受け口の各関数本体を「同名のグローバル C 関数を引数そのまま渡して呼び、戻り値があればそのまま返す」だけのコードとして生成する（ユーザコードを一切書かなくてよい）。
3. `gen_postamble` で、その「同名のグローバル C 関数」のプロトタイプ宣言をヘッダファイル（固定パス `#{$gen}/#{シグニチャのグローバル名}.#{$h_suffix}`、オプションで変更不可）へ出力する。実装はユーザまたは他のジェネレータ（[[work/active/tecsgen-plugins/Mruby2CBridgePlugin|Mruby2CBridgePlugin]] の場合は mruby ブリッジの C 側グルーコード）が別途行う。
4. **呼び出し経路**: 呼び出し元セル → join → `nTECS2C::t<シグニチャ名>` セルの受け口 → 自動生成された素通しコード → 同名グローバル C 関数（別途実装）。

## 4. プラグイン引数

| プラグイン | 対応オプション | 根拠 |
|---|---|---|
| `C2TECSBridgePlugin` | `prefix`, `suffix`, `header_name`（`C2TECSBridgePluginArgProc`、46〜50行） | 生成される C 関数名・ヘッダファイル名が衝突しないよう変更するため（`doc/C2TECSBrdigePlugin.txt` 「コンパイル時、リンク時に名前衝突が発生する可能性があります」） |
| `TECS2CBridgePlugin` | **`silent` のみ**（クラス固有の `@plugin_arg_check_proc_tab` を一切設定しない） | `tecslib/core/plugin.rb` の `check_plugin_arg`（250〜272行）を確認: `@plugin_arg_check_proc_tab` が `nil` の場合、基底 `Plugin::PluginArgProc`（`"silent"` のみ登録）へフォールバックする。それ以外の識別子を渡すと `P1004` エラーになる。`Mruby2CBridgePlugin.rb` が実際に渡している唯一の引数が `"silent=true"` であることと整合する |

## 5. 発見: 一次資料・実使用例の非対称性

- `C2TECSBridgePlugin` には正式なユーザ向けドキュメント `doc/C2TECSBrdigePlugin.txt`（ファイル名タイポ "Brdige" は原文のまま、内容は正確）と、独立した CDL 使用例が2件（`test/signaturePlugin/generate.cdl`、`test/mruby/MrubyBridge-ASP3/test.cdl`）存在する。
- `TECS2CBridgePlugin` には対応するドキュメントが存在せず（`doc/` 配下を `*2*.txt` で検索しても該当なし）、独立した CDL 使用例もリポジトリ内に一切見つからない。唯一の実使用は [[work/active/tecsgen-plugins/Mruby2CBridgePlugin|Mruby2CBridgePlugin]] が `gen_cdl_file` 内で動的に `generate( TECS2CBridgePlugin, ..., "silent=true" )` として自動生成するケースのみ（`Mruby2CBridgePlugin.rb` 77行）。
- `doc/C2TECSBrdigePlugin.txt` の「関連」節は `TECS2CBridgePlugin` と `test/signatureBridge/generate.cdl` を挙げているが、後者のパスは実在せず、実際の使用例は `test/signaturePlugin/generate.cdl`（`signatureBridge` ではなく `signaturePlugin`）だった——ドキュメント側のパス誤記と判断される。

## 6. 制約・注意点

- `C2TECSBridgePlugin` の `[singleton, active]` の `active` 指定は実体を反映しない警告回避策（3.1節）。celltype の意味論を読む際に誤解しないよう注意。
- `doc/C2TECSBrdigePlugin.txt` は「別々にジェネレートされた cdl ファイルのコンポーネントを結合させるのに使用できる」用途にも言及しており、その場合両方の cdl ファイルで使われているセルタイプの `.o` を二重リンクしないよう注意が必要と明記している（未検証、原文の記載のみ）。
- `TECS2CBridgePlugin` はプラグイン固有オプションを一切持たない（4節）ため、ヘッダファイル名・セルタイプ名はシグニチャ名から自動導出される固定値であり、名前衝突を避ける手段が `C2TECSBridgePlugin` 側のように用意されていない。

## Related

- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧（本ノートでリンク・訂正）
- [[work/active/tecsgen-plugins/Mruby2CBridgePlugin]] — `TECS2CBridgePlugin` の唯一の実使用元。両者を組み合わせて mruby インタプリタなしの C 駆動を実現する合成プラグイン
- [[work/active/tecsgen-plugins/MrubyBridgePlugin]] — `C2TECSBridgePlugin` の実運用例（`MrubyBridge-ASP3/test.cdl`）が接続する mruby ブリッジ本体
- [[North Star]] — プラグイン仕様書化の進捗管理
