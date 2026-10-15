---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第1章（概要）— Ruby版tecsgenのPython3移植の目的、Ruby版との互換方針、構成物（tecsgen・tecsmerge）、対象読者。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第1章（全10章）。移植元は [[work/active/tecsgen/tecsgen外部仕様 - 01 概要|Ruby版 第1章]]。

## 1. 概要

### 1.1 目的

tecsgen-python3 は、TECS のコンポーネント記述コンパイラ tecsgen（Ruby 実装、v1.9.1）を Python 3 へ移植したものです。CDL で書いたコンポーネント構成を入力として、C のセルタイプ実装用コードとカーネル設定コードを生成します。

### 1.2 Ruby 版との関係

| 項目 | 方針 |
|---|---|
| コマンドライン | Ruby 版と完全互換（コマンド名 `tecsgen`、オプション、環境変数）。例外は [[tecsgen-python3外部仕様 - 05 コマンドラインインターフェース\|5章]]の `RUBYLIB` と `-L` |
| 入力 | 受理する CDL の範囲、構文エラーの位置・件数は Ruby 版と一致（Ruby 版の racc 生成表をそのまま使うため） |
| 出力 | 同じ入力に対し `gen/` 以下の生成物がバイト単位で一致。エラー・警告のコード・件数・終了コードも一致（受入基準、[[tecsgen-python3外部仕様 - 04 出力\|4章]]） |
| プラグイン | 利用者が書くプラグインの言語が Ruby から Python に変わる（[[tecsgen-python3外部仕様 - 06 プラグインシステム\|6章]]） |

正解は常に Ruby 版の実行結果です。Ruby 版の癖（例外で落ちる入力、エラー番号の付き方など）も、まず同じに再現します。

### 1.3 構成物

| コマンド | 内容 |
|---|---|
| `tecsgen` | CDL からコードを生成する本体 |
| `tecsmerge` | 生成されたテンプレート（`*_templ.c`・`*_templ.h`）を、保守中のセルタイプコードへマージする |

`tecscde`（旧版）は移植しません。`tcflow`(C ソースの関数呼び出しと参照グローバル変数を抽出するコマンド)と `tecsflow`(呼び出しフローの表示)は、`tecsgen` とは別のコマンドとして移植しました(移植状況は [[tecsgen-python3移植計画]])。TECSCDE は TypeScript 版（[[TECSCDE-JS-TS実装]]）が置き換えます。

### 1.4 対象読者

- Python 版 tecsgen を利用して組込みシステムを開発するアプリケーション開発者
- TECS カーネルライブラリ（ASP3 等）の組み込み担当者
- Ruby 版からの移行者（差異は各章の「Ruby版との差異」を参照）

### 1.5 ビルドシステムにおける位置付け

```
.cdl ファイル
    ↓ tecsgen
生成コード（_tecsgen.h, _factory.h, tecsgen.cfg, テンプレート .c/.h, Makefile 類）
    ↓ tecsmerge（手書きコードへのマージ）
セルタイプ実装コード
    ↓ C コンパイラ
実行ファイル
```

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3]] — 親ノート
- [[tecsgen-python3移植計画]] — 移植の方針とフェーズ
