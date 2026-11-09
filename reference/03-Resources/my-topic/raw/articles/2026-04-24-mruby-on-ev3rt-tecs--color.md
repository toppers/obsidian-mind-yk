---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\color.html
title: カラーセンサ - Color
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: カラーセンサ - Color"
---

# カラーセンサ - Color

# カラーセンサ - `Color`

カラーセンサに関するAPIです．

## インスタンスメソッド一覧

- 
initialize( port )

- 
color

- 
refrect

- 
ambient

- 
rgb

## シンボル

- 
**color**

カラーセンサで識別できるカラーのシンボル

| 
シンボル
 | 
| 
:black
 | 
黒
 | 
| 
:blue
 | 
青
 | 
| 
:green
 | 
緑
 | 
| 
:yellow
 | 
黄
 | 
| 
:red
 | 
赤
 | 
| 
:white
 | 
白
 | 
| 
:brown
 | 
茶
 | 
| 
:none
 | 
識別できなかった
 | 
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

カラーセンサポートを設定する．
**引数**
`port`  センサポートのシンボル
**戻り値**
nil

### color -> Symbol

カラーセンサでカラーを識別する．
**引数**
なし
**戻り値**
識別したカラーのシンボルを返す．

### reflect -> nil

カラーセンサで反射光の強さを測定する．
**引数**
なし
**戻り値**
反射光の強さ（0〜100）

### ambient -> Fixnum

カラーセンサで環境光の強さを測定する．
**引数**
なし
**戻り値**
環境光の強さ（0〜100）

### rgb -> Fixnum

カラーセンサでRGB値を測定する．
**引数**
なし
**戻り値**
レッド（R)値，グリーン(G)値，ブルー(B)値
color_sample.rb
```

```

---

Source: [[index]]
