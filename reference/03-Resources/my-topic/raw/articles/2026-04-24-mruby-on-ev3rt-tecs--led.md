---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\led.html
title: LEDライト - LED
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: LEDライト - LED"
---

# LEDライト - LED

# LEDライト - `LED`

LEDライトに関するAPIです．

## 特異メソッド一覧

- 
LED.color = (clr)

- 
LED.off

## シンボル

- 
**clr**

設定できるLEDライトのカラーを表わすシンボル

| 
シンボル
 | 
| 
:off
 | 
オフにする
 | 
| 
:red
 | 
赤
 | 
| 
:green
 | 
緑
 | 
| 
:orange
 | 
オレンジ
 | 
## 特異メソッド

### LED.color = ( clr ) -> nil

LEDライトのカラーを設定する.
不正の設定値を指定した場合，LEDライトのカラーを変えない．
**引数**
`clr` LEDカラーの設定値 （シンボル）
**戻り値**
nil

### LED.off -> nil

LEDをオフにする．
**引数**
なし
**戻り値**
nil
led_sample.rb
```

```

---

Source: [[index]]
