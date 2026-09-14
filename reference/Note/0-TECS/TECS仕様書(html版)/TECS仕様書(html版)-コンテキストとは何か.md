---
date: 2026-06-18
description: "TECSにおけるコンテキスト（Context）の定義 — シグニチャの呼び出しコンテキスト指定子（task/non-task/any）（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# コンテキストとは何か

**コンテキスト (Context)** は、シグニチャ（インタフェース）がどの実行コンテキストから呼び出せるかを示す指定子です。シグニチャに `[context(...)]` として付与します。

## コンテキストの種類

| 値 | 意味 |
|----|------|
| `task` | タスクコンテキストからのみ呼び出し可能 |
| `non-task` | 非タスクコンテキスト（割込みハンドラ等）からのみ呼び出し可能 |
| `any` | タスク・非タスク両方から呼び出し可能 |

## CDLでの指定

```cdl
[context(task)]
signature sTask {
    ER activate(void);
};

[context(non-task)]
signature sInterruptService {
    void notify(void);
};

[context(any)]
signature sFlexible {
    void doWork([in] int32_t x);
};
```

## 命名慣習

割込みコンテキスト用受け口には `i` を接頭辞として追加する慣習があります：

```cdl
entry sTask eTask;       // タスクコンテキスト用
entry siTask eiTask;     // 割込みコンテキスト用
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-シグニチャとは何か]] | [[TECS仕様書(html版)-アクティブセルとは何か]] | [[TECS仕様書(html版)-目次]]
