---
date: 2026-05-31
source-type: article
source-url: E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\tecs\mruby\mrubyTECSPointer.txt
title: TECS::Pointer クラス群 — mrubyポインタ型クラスリファレンス
compiled: true
tags: [tecs, toppers, mruby, plugin]
description: "MrubyBridgePluginが生成するTECS::Pointer型クラス群のリファレンス。整数・浮動小数・文字型ポインタを網羅。"
---

# TECS::Pointer クラス群 — mrubyポインタ型クラスリファレンス

MrubyBridgePlugin が必要に応じて生成する TECS のポインタ値を扱うための mruby クラス群。使用されているクラスだけが生成される。

## クラス一覧

| クラス | 対応C型 |
|--------|---------|
| `TECS::Int8Pointer` | `int8_t*` |
| `TECS::Int16Pointer` | `int16_t*` |
| `TECS::Int32Pointer` | `int32_t*` |
| `TECS::Int64Pointer` | `int64_t*` |
| `TECS::UInt8Pointer` | `uint8_t*` |
| `TECS::UInt16Pointer` | `uint16_t*` |
| `TECS::UInt32Pointer` | `uint32_t*` |
| `TECS::UInt64Pointer` | `uint64_t*` |
| `TECS::CharPointer` | `char_t*` / `char*` |
| `TECS::SCharPointer` | `schar_t*` |
| `TECS::UCharPointer` | `uchar_t*` |
| `TECS::IntPointer` | `int*` |
| `TECS::UIntPointer` | `unsigned int*` |
| `TECS::ShortPointer` | `short*` |
| `TECS::UShortPointer` | `unsigned short*` |
| `TECS::LongPointer` | `long*` |
| `TECS::ULongPointer` | `unsigned long*` |
| `TECS::BoolPointer` | `bool_t*` |
| `TECS::Float32Pointer` | `float32_t*` |
| `TECS::Double64Pointer` | `double64_t*` |

## 用途

TECS の整数・浮動小数点・文字データのポインタ型引数を mruby から扱うためのクラス。
ポインタ値（アドレス）を渡す場合は `intptr_t` を使用（Pointer クラスは使用不可）。

## 関連

- [[plugin-mruby-bridge]]
- [[mruby-tecs]]
- [[tecs-signature]]
