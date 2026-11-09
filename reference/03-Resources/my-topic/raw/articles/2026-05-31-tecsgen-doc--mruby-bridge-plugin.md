---
date: 2026-05-31
source-type: article
source-url: E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\tecs\mruby\mrubyBridge.txt
title: MrubyBridgePlugin — mrubyとTECSのブリッジプラグイン詳細リファレンス
compiled: true
tags: [tecs, toppers, mruby, plugin]
description: "MrubyBridgePluginの構造・データ型対応・CDL記述・mrubyコードの詳細リファレンス（大山博司 2013）"
---

# MrubyBridgePlugin — mrubyとTECSのブリッジプラグイン詳細リファレンス

MrubyBridgePlugin は、TECS CDL の signature 記述に基づき、mruby と TECS コンポーネントをブリッジする、mruby の C 言語実装クラスであり TECS のセルタイプとなるコンポーネントを生成する、TECS のシグニチャプラグインである。

## 構造

```
     +--------------------------+              +-------------------+
     |     (ブリッジセル)         |              |    (目的セル)      |
     |                          |              |                   |
mruby| nMruby::tsSignatureBridge|  sSignature  |  tTargetCelltype  |
 --> |       BridgeCell         |--------------|>   TargetCell     |
     |                          |cTECS    eTest|                   |
     | mruby クラス：            |              |                   |
     |  TECS::TSignatureBridge  |              |                   |
     +--------------------------+              +-------------------+
```

## 対応データ型

### スカラー型
- `bool_t`, `char_t`, `intN_t` (N=8,16,32,64), `double64_t`, `float32_t`
- `int`, `short`, `long`, `char`（TECS非推奨）

### ポインタ型
- `bool_t*`, `char_t*`, `intN_t*`, `double64_t*`, `float32_t*`
- 構造体型へのポインタ（構造体型と同じ制限あり）
- `size_is`, `string` 指定子あり/なし両方対応
- ポインタ値を渡す場合は `intptr_t`, `uintptr_t` を使用

### 構造体型
- メンバはスカラー型のみ
- `typedef` された型も扱える（元の型として扱われる）

## mruby 型との対応

| TECS型 | mruby型 |
|--------|---------|
| `bool_t` | true/false |
| `char_t`, `intN_t`, `int`等 | FIXNUM |
| `double64_t`, `float32_t` | FLOAT |
| `bool_t*` | TECS::BoolPointer |
| `intN_t*` | TECS::IntNPointer |
| `float32_t*` | TECS::Float32Pointer |
| `struct TAG` / `struct TAG*` | TECS::StructTAG |

## CDL記述

### ブリッジプラグインの呼び出し
```cdl
generate( MrubyBridgePlugin, sSignature, "" );
```

### ブリッジセルの設置
```cdl
cell nMruby::tsSignature BridgeCell {
  cTECS = Cell.eEnt;
};
```

### プラグイン引数
- `ignoreUnsigned=true` — 無符号整数ポインタに有符号クラスを使用
- `include='func1,func2'` — 含める関数を指定
- `exclude='func99'` — 除外する関数を指定

## mrubyコード

```ruby
# ブリッジインスタンスの生成
bridge = TECS::TsSignature.new( "BridgeCell" )
# メソッド呼び出し
bridge.someMethod(arg)
```

## 制約

- `initialize` 関数名は `initialize_cell` に置換される（rubyの予約語との衝突回避）
- 戻り値: `void`, `bool_t`, `char_t`, `intN_t`, `float32_t`, `double64_t`, `int`, `short`, `long`, `char` のみ
- 引数指定子: `in`, `inout`, `out` のみ（`send`/`receive` 不可）
- 構造体に `TAG` 名がないものは扱えない
- `void *` は扱えない

## Makefile設定

tecsgen生成の `gen/Makefile.templ` に以下を追加:
```makefile
OTHER_OBJS = $(_TECS_OBJ_DIR)vasyslog.o  # tSysLog使用時
```

## 関連

- [[plugin-mruby-bridge]]
- [[mruby-tecs]]
- [[tecs-signature]]
- [[tecs-plugin]]
