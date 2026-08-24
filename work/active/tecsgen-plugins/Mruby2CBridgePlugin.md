---
date: 2026-08-14
description: "tecsgen 標準付属プラグイン Mruby2CBridgePlugin の仕様書。TECS シグニチャを、mruby インタプリタなしに C コードから mruby ブリッジ流儀（オブジェクト生成＋メソッド呼び出し）で駆動できるようにする、MrubyBridgePlugin・TECS2CBridgePlugin・C2TECSBridgePlugin を内部で組み合わせる合成プラグイン"
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

# Mruby2CBridgePlugin 仕様書

> [!info] 文書状態
> [[North Star]] の mruby ブリッジ系2件目。[[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]]・[[work/active/tecsgen-plugins/ATK1Plugin|ATK1Plugin]]と異なり、本体は `tecslib/plugin/Mruby2CBridgePlugin.rb` 1ファイル（89行）のみ。ただし内部で `MrubyBridgePlugin`・`TECS2CBridgePlugin`・`C2TECSBridgePlugin` の3プラグインを CDL コードとして動的に呼び出すため、単独では完結しない合成プラグインである。一次資料は `Mruby2CBridgePlugin.rb`・`TECS2CBridgePlugin.rb`・`C2TECSBridgePlugin.rb`（いずれも `SignaturePlugin` 系列）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 概要

**Mruby2CBridgePlugin は、TECS シグニチャを「mruby インタプリタを介さずに、プレーンな C コードから」mruby ブリッジと同じ流儀（`TECS::TSignature.new("CellName")` でオブジェクトを作り、メソッドとして受け口関数を呼び出す）で駆動できるようにする合成プラグインである。** [[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]]（mruby ↔ TECS）・`TECS2CBridgePlugin`（TECS → C 変換）・`C2TECSBridgePlugin`（C → TECS 受け口呼び出し）の3プラグインを内部で `generate(...)` 文として動的に呼び出すことで実現している。

## 2. CDL構文

### 2.1 呼び出し形式（statement 形式、シグニチャ単位）

```tecs-cdl
generate( Mruby2CBridgePlugin, sMySignature, "" );
```

`Mruby2CBridgePlugin < SignaturePlugin` であり、[[tecsgen外部仕様]] 6.2 の `MultiPlugin` 対応表どおり signature への statement 形式でのみ呼び出せる。

### 2.2 内部で自動生成される CDL（`gen_cdl_file`、76〜85行）

```tecs-cdl
generate( MrubyBridgePlugin, sMySignature, "silent=true" );
generate( TECS2CBridgePlugin, sMySignature, "silent=true" );
// このプロセスで初めて Mruby2CBridgePlugin が使われた場合のみ、以下も追加生成される
generate( C2TECSBridgePlugin, nMruby::sInitializeBridge, "silent=true" );

cell nMruby::tMySignature CMySignature {
    cTECS = TECS2C_MySignature.eEnt;
};
cell nTECS2C::tMySignature TECS2C_MySignature {};

import( "Mruby2C_tsInitializerBridge.cdl" );  // C2TECS_tsInitializeBridge セルを VM_TECSInitializer.eInitialize へ結合するコードを含む
```

## 3. 動作

1. **`MrubyBridgePlugin` の呼び出し**（`silent=true` — [[work/active/tecsgen-plugins/MrubyBridgePlugin#4.3|4.3節]]の「VMs cInitialize を結合してください」案内メッセージを抑制): シグニチャに対応する mruby ブリッジセルタイプ `nMruby::tMySignature` を生成する。
2. **`TECS2CBridgePlugin` の呼び出し**: 同じシグニチャに対応する、プレーン C から呼び出し可能なセルタイプ `nTECS2C::tMySignature` を生成する。
3. **セル結線**: mruby ブリッジセル `CMySignature`（手順1の産物）の呼び口 `cTECS` を、TECS2C セル `TECS2C_MySignature`（手順2の産物）の受け口 `eEnt` に結合する。**この結線により、C コードから mruby ブリッジ流儀のオブジェクト・メソッド呼び出しインタフェースを経由してシグニチャの受け口を呼べるようになる**（呼び出し経路: C コード → `TECS2C_MySignature` の C 関数 → `eEnt` → `CMySignature.cTECS` → mruby ブリッジのディスパッチ機構 → 目的セル）。
4. **`C2TECSBridgePlugin` の呼び出しは1プロセスにつき1回だけ**（`@@signature_list.length == 0` で判定、47〜55行）: `initializeBridge(mrb_state *mrb)` という C 関数（`nMruby::sInitializeBridge` シグニチャ）を生成し、mruby VM の初期化セル `VM_TECSInitializer.eInitialize` へ自動結合する（`Mruby2C_tsInitializerBridge.cdl` を動的に書き出し `import` — [[work/active/tecsgen-plugins/MrubyBridgePlugin#5.2|MrubyBridgePlugin 5.2節]]と同じ「CDL コード片を書き出して Import する」手法）。**C コードはこの `initializeBridge()` を呼んでから、生成されたブリッジオブジェクトを使う**という初期化順序になる。
5. **重複適用の警告**: 同じシグニチャに2回目の `generate(Mruby2CBridgePlugin, ...)` が呼ばれた場合、2回目は無視され警告 `MRCW001` が出る（`@@signature_list` によるシグニチャ単位の重複検出、57〜61行）。

## 4. プラグイン引数

`Mruby2CBridgePlugin` 自身は `@plugin_arg_check_proc_tab`（[[tecsgen外部仕様]] 6.4 の `param=value` 引数を解釈するための対応表）を定義していない。`initialize` は `parse_plugin_arg` を呼ぶ（`tecslib/core/plugin.rb`）ため、空文字列 `""` 以外の引数を渡した場合の挙動は未検証——内部的に呼び出す3プラグインへは `"silent=true"` が固定で渡されるのみで、`Mruby2CBridgePlugin` 呼び出し側が指定した引数がそれらへ伝播する経路はソース上に見当たらない。

## 5. 発見: 訂正 — `TECS2CPlugin` ではなく `TECS2CBridgePlugin`

[[tecsgen外部仕様]] 6.3 の C インタフェース欄「TECS2CPlugin」は誤り。実際のクラス名は `TECS2CBridgePlugin`（`tecslib/plugin/TECS2CBridgePlugin.rb`、`< SignaturePlugin`、コメント「TECS => C 呼び出しプラグイン」）であり、`C2TECSBridgePlugin` と対になる命名規則（`C2TECS`/`TECS2C` + `Bridge` + `Plugin`）に統一されている。本ノート執筆にあたり `Mruby2CBridgePlugin.rb` が両クラスを直接参照していたため判明した。6.3 を訂正する。

## 6. 制約・注意点

- 単独では完結しない合成プラグインであり、正しく理解するには `MrubyBridgePlugin`（[[work/active/tecsgen-plugins/MrubyBridgePlugin]]）・`TECS2CBridgePlugin`・`C2TECSBridgePlugin` の3者の役割を前提とする。後2者は本ノートの範囲では概要のみ確認しており、詳細仕様は未着手（[[North Star]] の Cインタフェースカテゴリ）。
- プラグイン引数の効果が未検証（4章）。
- 同一シグニチャへの重複適用は2回目以降無視される（3.5節、`MRCW001`）。

## Related

- [[tecsgen外部仕様]] — 6.2 `MultiPlugin` ディスパッチ対応表・6.3 標準付属プラグイン一覧（本ノートで訂正）
- [[work/active/tecsgen-plugins/MrubyBridgePlugin]] — 本プラグインが内部で呼び出す mruby ↔ TECS ブリッジ本体。CDL コード片の動的 Import 手法も共通
- [[North Star]] — カーネル対応プラグイン仕様書化の進捗管理
