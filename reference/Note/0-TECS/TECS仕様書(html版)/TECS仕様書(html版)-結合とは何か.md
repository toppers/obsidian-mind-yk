---
date: 2026-06-18
description: "TECSにおける結合（Join）の定義 — 呼び口と受け口を接続してコンポーネント間の依存関係を宣言する仕組み（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 結合とは何か

**結合 (Join)** は、呼び口と受け口を接続してコンポーネント間の依存関係を宣言することです。CDLの組上げ記述（セル記述）で定義します。

## 結合の制約

- **一対一**: 一つの呼び口が接続できる受け口は**一つだけ**
- **多対一（合流）**: 一つの受け口に**複数の呼び口**を結合できる
- **型の一致**: 呼び口と受け口は同じシグニチャを持つ必要がある

## CDLでの記述

```cdl
cell tCellA CellA {
    // 通常結合
    cPort = OtherCell.ePort;

    // 呼び口配列の結合
    cArr[0] = Cell0.ePort;
    cArr[1] = Cell1.ePort;

    // 逆結合（callbackシグニチャのみ）
    cCallback <= eCallbackPort;

    // スルー結合（リージョン間RPC等）
    [through(PluginName, "opt")]
    cThrough = Cell.ePort;
};
```

## 結合の種類

| 種類 | 構文 | 説明 |
|------|------|------|
| 通常結合 | `cPort = Cell.ePort` | 標準の結合 |
| 配列結合 | `cArr[n] = Cell.ePort` | 呼び口配列の特定要素を結合 |
| 逆結合 | `cCallback <= eCallbackPort` | callbackシグニチャ専用 |
| スルー結合 | `[through(Plugin)] cPort = Cell.ePort` | プラグイン経由の結合 |

## TCD表記

```
+------------------+      sSignature      +------------------+
| tCellA           |                      | tCellB           |
|    cCall ------->|--------------------->|> eEntry          |
+------------------+                      +------------------+
```

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-呼び口とは何か]] | [[TECS仕様書(html版)-受け口とは何か]] | [[TECS仕様書(html版)-合流の書き方を教えて]] | [[TECS仕様書(html版)-目次]]
