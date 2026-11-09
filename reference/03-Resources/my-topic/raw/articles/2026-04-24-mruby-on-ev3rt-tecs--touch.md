---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\touch.html
title: タッチセンサ - Touch
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: タッチセンサ - Touch"
---

# タッチセンサ - Touch

# タッチセンサ - `Touch`

タッチセンサに関するAPIです．

## インスタンスメソッド一覧

- 
initialize( port )

- 
pressed?

## シンボル

- 
**port**

センサポートを表わすシンボル

| 
シンボル
 | 
| 
:port_1
 | 
ポート 1
 | 
| 
:port_2
 | 
ポート 2
 | 
| 
:port_3
 | 
ポート 3
 | 
| 
:port_4
 | 
ポート 4
 | 
## インスタンスメソッド

### initialize ( port ) -> object

タッチセンサポートを設定する．
**引数**
`port` センサポートのシンボル
**戻り値**
nil

### pressed? -> bool

タッチセンサの状態を検出する．
**引数**
なし
**戻り値**
`true`  押されている状態

`false` 押されていない状態
touch_sample.rb
```

```

---

Source: [[index]]
