---
date: 2026-06-18
description: "TECSにおける呼び口（Call）の定義 — 利用側ポート、シグニチャに対応する外部サービスを呼び出すポート（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 呼び口とは何か

**呼び口 (Call)** は、シグニチャに対応する外部サービスを利用するポートです。コンポーネントの**利用側**（サービスを呼び出す側）のポートで、他のコンポーネントの受け口に結合します。

## 特性

- シグニチャで定義された関数群を呼び出す
- セルタイプに宣言し、組上げ記述で接続先（受け口）を指定する
- 一つの呼び口が接続できる受け口は**一つだけ**（一対一）
- TCD（コンポーネント図）では長方形の辺から始まる**線分**（矢印）で表現
- 命名慣習: `c` 接頭辞（例: `cTask`, `cSysLog`）

## CDLでの宣言

```cdl
celltype tMyCell {
    call sMySignature cMain;          // 通常呼び口
    [optional] call sMySignature cOpt; // オプション呼び口（未結合可）
    [omit] call sMySignature cOmit;   // 省略可能呼び口
    call sMySignature cArr[];          // 呼び口配列
    call[3] sMySignature cFixed;       // 固定サイズ呼び口配列
};
```

## 組上げ記述（結合）

```cdl
cell tMyCell MyCell {
    cMain = OtherCell.eEntry;          // 呼び口を受け口に結合
    cArr[0] = Cell0.ePort;             // 呼び口配列の結合
    cCallback <= eCallbackPort;        // 逆結合（callbackシグニチャ）
};
```

## 実装（Cコード）での呼び出し

```c
// セルタイプコード内で呼び口関数を呼び出す
ER result = cMain_funcName(arg1, arg2);
```

## 受け口との違い

| | 呼び口 (Call) | 受け口 (Entry) |
|--|--------------|---------------|
| **役割** | サービスを利用する | サービスを提供する |
| **方向** | 利用側（呼ぶ） | 提供側（受ける） |
| **TCD** | 線分（矢印） | 塗りつぶし三角形 |
| **接頭辞** | `c` | `e` |

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-受け口とは何か]] | [[TECS仕様書(html版)-シグニチャとは何か]] | [[TECS仕様書(html版)-呼び口配列とは何か]] | [[TECS仕様書(html版)-目次]]
