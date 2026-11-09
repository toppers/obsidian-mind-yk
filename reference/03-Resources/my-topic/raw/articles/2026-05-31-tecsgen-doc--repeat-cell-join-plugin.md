---
date: 2026-05-31
source-type: article
source-url: E:\Crepo\ykominami-svn-2\tecsgen\trunk\doc\RepeatCellPlugin+RepeatJoinPlugin.txt
title: RepeatCellPlugin / RepeatJoinPlugin — セル繰り返しプラグインリファレンス
compiled: true
tags: [tecs, toppers, plugin]
description: "RepeatCellPlugin（セルを繰り返し生成）とRepeatJoinPlugin（セル内結合を繰り返す）の使用方法・オプション詳細"
---

# RepeatCellPlugin / RepeatJoinPlugin — セル繰り返しプラグインリファレンス

## RepeatCellPlugin — セルを繰り返すセルプラグイン

セルを `count` 個数繰り返す。セル名の末尾数字をカウントアップする。

### 使用方法

```cdl
[generate(RepeatCellPlugin,"count=5")]
cell tCelltype Cell_000 {
    cCall  = Cell.eEntry;       // (1) セル名がカウントアップ
    cCall2 = Cell_010.eEntry;   // (2) 右辺セル名がカウントアップ
    cCall3 = CellA.eEntryArray[50]; // (3) 配列添数がカウントアップ
    size   = SIZE_000;          // (4) 定数識別子がカウントアップ
};
```

### カウントアップ対象

- `(1)` セル名の末尾数字（1桁以上）→ カウント番号に置換
- `(2)` 右辺セル名の末尾数字 → カウントアップ
- `(3)` 右辺受け口が配列の場合の添数 → カウントアップ
- `(4)` 右辺が単一識別子で末尾が数字 → カウントアップ

### オプション

- `count=N` — N は整数リテラルまたは定数名

### 制約

- アロケータ指定子・`through` 指定子には非対応
- `count` 右辺は整数リテラルまたは単一識別子（定数名）のみ

---

## RepeatJoinPlugin — セル内部の結合を繰り返すセルプラグイン

呼び口配列の添数 `[0]` の結合を `count` 個数繰り返す。

### 使用方法

```cdl
[generate(RepeatJoinPlugin,"count=5")]
cell tCelltype Cell_000 {
    cCall[0] = Cell000.eEntry;   // → cCall[1]=Cell001.eEntry, ...
    cCallX[0] = CellX.eEntry[0]; // → cCallX[1]=CellX.eEntry[1], ...
};
```

### カウントアップ対象

- 添数 `[0]` → カウント番号に置換（`[0]` 以外は繰り返されない）
- 右辺セル名が 1個以上の `0` で終わっている場合 → カウント番号に置換
- 右辺受け口が配列で添数 `[0]` の場合 → カウントアップ

### 制約

- `count` 右辺は整数リテラルまたは単一識別子（定数名）のみ
- CDL ファイルは生成されない（ジェネレータ内部処理）

### オプション

- `count=N` — N は整数リテラルまたは定数名

## 関連

- [[plugin-repeat-cell]]
- [[tecs-plugin]]
- [[tecs-cell]]
- [[tecs-celltype]]
