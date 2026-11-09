---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\motor.html
title: モータ - Motor
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: モータ - Motor"
---

# モータ - Motor

# モータ - `Motor`

モータを制御するためのAPIです．

## インスタンスメソッド一覧

- 
initialize( port, type=:large )

- 
type

- 
power = ( pwm )

- 
power

- 
stop( brake )

- 
rotate( deg, spd, blk )

- 
count

- 
reset_count

## シンボル

- 
**port**

モータポートを表すシンボル

| 
シンボル
 | 
| 
:port_a
 | 
ポートA
 | 
| 
:port_b
 | 
ポートB
 | 
| 
:port_c
 | 
ポートC
 | 
| 
:port_d
 | 
ポートD
 | 
- 
**type**

サポートするモータタイプのシンボル

| 
シンボル
 | 
| 
:large
 | 
サーボモータ L
 | 
| 
:medium
 | 
サーボモータ M
 | 
## インスタンスメソッド

### initialize( port, type=:large ) -> object

モータポートを設定する．

モータポートに接続しているモータのタイプを設定する．既に設定した場合も新しいモータタイプを指定できる．
**引数**
`port`  モータポート番号（シンボル）

`type`  モータタイプ （シンボル）
**戻り値**
nil

### type -> Symbol

モータポートのモータタイプを取得する．
**引数**
なし
**戻り値**
`:large`  サーボモータL

`:medium` サーボモータM

### power = ( pwm ) -> nil

モータのパワーを設定し，モータが回転する．
**引数**
`pwm` モータのフルパワーのパーセント値．範囲：-100から+100．マイナスの値でモータを逆方向に回転させることができる．範囲外の場合±100が適用される．
**戻り値**
nil

### power -> Fixnum

モータのパワーを取得する．
**引数**
なし
**戻り値**
モータのパワー

### stop( brake=true ) -> nil

モータを停止する．
**引数**
`brake` ブレーキモードの指定．`true` （ブレーキモード）, `false` （フロートモード）
**戻り値**
nil

### rotate( deg, spd, blk=false ) -> nil

モータを指定した角度だけ回転させる
**引数**
`deg` 回転角度，マイナスの値でモータを逆方向に回転させることができる（小数点以下切り捨て）

`spd` 回転速度，モータポートのフルスピードのパーセント値．範囲：-100から+100（小数点以下切り捨て）．マイナスの場合回転が逆になる．範囲外の場合±100として扱われる．

`blk` モード指定．`true` (関数は回転が完了してからリターン)，`false` (関数は回転操作を待たずにリターン)
**戻り値**
nil 正常終了

### count -> Fixnum

モータの角位置を取得する．
**引数**
なし
**戻り値**
モータの角位置（単位は度），マイナスの値は逆方向に回転されたことを指す．

### reset_count -> nil

モータの角位置をゼロにリセットする．

モータの角位置センサの値を設定するだけ，モータの実際のパワーと位置に影響を与えない．
**引数**
なし
**戻り値**
nil
motor_sample.rb
```
includeEV3RT_TECSbeginLCD.font=:mediumLCD.draw("motor sample",0,0)# Sensors and Actuatorsleft_port=:port_aright_port=:port_bultrasonic_port=:port_3LCD.draw("left motor:#{left_port} ",0,2)LCD.draw("right motor:#{right_port} ",0,3)LCD.draw("ultrasonic :#{ultrasonic_port}",0,4)$left_motor=Motor.new(left_port)$right_motor=Motor.new(right_port)$ultrasonic_sensor=UltrasonicSensor.new(ultrasonic_port)includeEV3RT_TECSloop{distance=$ultrasonic_sensor.distanceLCD.draw("distance = #{distance} ",0,6)ifdistance<15then$left_motor.stop$right_motor.stopelse$left_motor.power=30$right_motor.power=30end}rescue=>eLCD.error_putseend
```

---

Source: [[index]]
