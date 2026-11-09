---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\gyro.html
title: ジャイロセンサ - Gyro
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: ジャイロセンサ - Gyro"
---

# ジャイロセンサ - Gyro

# ジャイロセンサ - `Gyro`

ジャイロセンサに関するAPIです．

## インスタンスメソッド一覧

- 
initialize( port )

- 
angle

- 
rate

- 
reset

- 
calibrate ( n=200 )

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

ジャイロセンサポートを設定する．
**引数**
`port`  センサポートのシンボル
**戻り値**
nil

### angle -> Fixnum

ジャイロセンサで角位置を測定する．
**引数**
なし
**戻り値**
角位置 (単位は度)

### rate -> Fixnum

ジャイロセンサで角速度を測定する．
**引数**
なし
**戻り値**
角位置 （単位は度/秒）

### reset -> nil

ジャイロセンサの角位置をゼロにリセットする．
**引数**
なし
**戻り値**
nil

### calibrate ( n=200 ) -> Float | Symbol

ジャイロセンサのキャリブレーション．
複数回測定した値の平均値
**引数**
n 測定回数：デフォルトは200（小数点以下切り捨て）
**戻り値**
`offset` 測定回数の平均値

`：E_OBJ` 測定値の最大・最小の値が5以上の場合
gyro_sample.rb
```

```

---

Source: [[index]]
