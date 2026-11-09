---
date: 2026-05-31
source-type: article
source-url: E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\tecs\mruby\mrubyTECSStruct.txt
title: TECS::StructTAG クラス — mruby構造体型クラスリファレンス
compiled: true
tags: [tecs, toppers, mruby, plugin]
description: "MrubyBridgePluginが生成するTECS::StructTAGクラスのリファレンス。C言語構造体をmrubyから操作する。"
---

# TECS::StructTAG クラス — mruby構造体型クラスリファレンス

C 言語の構造体を扱うためのクラス。signature に現れる構造体に合わせて MrubyBridgePlugin により生成される。TAG の部分は構造体のタグ名に置き換える。

## スーパークラス

Object

## クラスメソッド

```ruby
TECS::StructTAG.new()
```

## インスタンスメソッド

```ruby
obj.MEMBER        # 構造体メンバの値を読み出す
obj.MEMBER = val  # 構造体メンバの値を書き込む
```

`MEMBER` はメンバ名に置き換える。

## 制約

- メンバはスカラー型のみ
- TAG 名がない構造体は扱えない
- `typedef` した名前で構造体を扱うことはできない（元の `struct TAG` 名を使用）

## 関連

- [[plugin-mruby-bridge]]
- [[mruby-tecs]]
- [[tecs-signature]]
