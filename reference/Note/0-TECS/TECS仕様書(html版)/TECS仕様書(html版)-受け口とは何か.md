---
date: 2026-06-18
description: "TECSにおける受け口（Entry）の定義 — 提供側ポート、シグニチャを実装して外部に公開するポート（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 受け口とは何か

**受け口 (Entry)** は、シグニチャを実装して外部に提供するポートです。コンポーネントの**提供側**（サービスを提供する側）のポートで、他のコンポーネントの呼び口から呼び出されます。

## 特性

- シグニチャで定義された関数群を実装する
- セルタイプに宣言し、セルタイプコード（Cコード）で受け口関数を実装する
- TCD（コンポーネント図）では長方形の辺に**塗りつぶした三角形**（内向き）で表現
- 命名慣習: `e` 接頭辞（例: `eTask`, `eSysLog`）

## CDLでの宣言

```cdl
celltype tMyCell {
    entry sMySignature eMain;       // 通常受け口
    entry sMySignature eArr[];      // 受け口配列
};
```

## 実装（Cコード）

```c
ER eMain_funcName(CELLIDX idx, int32_t param) {
    CELLCB *p_cellcb = GET_CELLCB(idx);
    // 受け口関数の実装
    return E_OK;
}
```

## 呼び口との違い

| | 受け口 (Entry) | 呼び口 (Call) |
|--|---------------|--------------|
| **役割** | サービスを提供する | サービスを利用する |
| **方向** | 提供側（受ける） | 利用側（呼ぶ） |
| **TCD** | 塗りつぶし三角形 | 線分（矢印） |
| **接頭辞** | `e` | `c` |

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-呼び口とは何か]] | [[TECS仕様書(html版)-シグニチャとは何か]] | [[TECS仕様書(html版)-受け口配列とは何か]] | [[TECS仕様書(html版)-目次]]
