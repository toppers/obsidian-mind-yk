---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\ultrasonic.html
title: 超音波センサ - Ultrasonic
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: 超音波センサ - Ultrasonic"
---

# 超音波センサ - Ultrasonic

# 超音波センサ - `Ultrasonic`

超音波センサに関するAPIです．

## インスタンスメソッド一覧

- 
initialize( port )

- 
distance

- 
listen

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

超音波センサポートを設定する．
**引数**
`port`  センサポートのシンボル
**戻り値**
nil

### distance -> Fixnum

超音波センサで距離を測定する．
**引数**
なし
**戻り値**
距離 (単位はセンチ）

### listen-> bool

超音波センサで超音波信号を検出する．
**引数**
なし
**戻り値**
`true` 超音波信号を検出した

`false` 超音波信号を検出しなかった
ultrasonic_sample.rb
```

```

---

Source: [[index]]
