---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-gr-peach+tecs\howtobuild.html
title: ビルド方法
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: ビルド方法"
---

# ビルド方法

# ビルド方法

- 
準備 （環境構築）:

以下のものをインストールしてください．

- Cygwin
- 
Ruby

- 
GNU Make

- 
bison

- GNUARM-NONE v16.01 Windows Toolchain (ELF)
- 
クロスコンパイラ

- 
PATHを通しておいてください．(arm-none-eabi-gcc等が実行できる状態)

- (ターミナルソフトウェア)
- 
シリアル経由で文字を出力する場合に使用します．

- 
Tera Term等をインストールしてください．

**Note: Mac や Linux でも開発可能と思いますが，まだ動作確認できていません．**

- パッケージのダウンロード:
以下のURLから，mruby-on-gr-peach-tecs-package をダウンロードしてください．

または，Githubからもダウンロード可能です．

```
$ git clone https://github.com/robotan0921/mruby_on_GR-PEACH-TECS.git

```

- mrubyのビルド
パッケージをダウンロードしたら，まず mruby のビルドを行います．
mruby-1.3.0 のディレクトリに移動し，ビルドしてください．

```
$ cd mruby-1.3.0
$ make

```

- アプリ・プラットフォームのビルド:
次に，アプリケーションを含むプラットフォーム部分のビルドを行います．
asp3/workspace/build へ移動し，ビルドしてください．

```
$ cd ../asp3/workspace/build    (mruby-1.3.0からの相対ディレクトリ)
$ make

```

アプリケーションは，デフォルトで led_sample.rb が指定されています．

- バイナリのコピー・起動:
ビルドが終わると， `asp3/workspace/build` の中に `asp.bin` というバイナリが出来上がります．
このバイナリを GR-PEACH にコピーします．
（PCとGR-PEACHをUSBケーブルで接続すると， `MBED` というドライブが立ち上がります)
エクスプローラーを開いてドラッグ&ドロップしてください．
Cygwin上のコマンドでコピーする場合は，以下のコマンドを叩いてください．

```
$ cp asp.bin /cygdrive/d/               (自環境でのMBEDドライブ名を指定してください)

```

---

Source: [[index]]
