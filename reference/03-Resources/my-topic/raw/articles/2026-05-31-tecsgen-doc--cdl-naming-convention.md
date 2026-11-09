---
date: 2026-05-31
source-type: article
source-url: E:\Crepo\ykominami-svn-2\tecsgen\trunk\test\sample\naming-convention.txt
title: CDL Naming Convention — TECSコンポーネント記述の命名規則
compiled: true
tags: [tecs, toppers, cdl, convention]
description: "TECS CDLの命名規則。signature・セルタイプ・セル・呼び口・受け口・属性・型などの命名ルールを定義。"
---

# CDL Naming Convention — TECSコンポーネント記述の命名規則

TECS CDL における各識別子の命名規則。（筆者: 小南 2006-01-31）

## 命名規則一覧

| 識別子 | 命名規則 |
|--------|---------|
| signature 名 | `'s'` + 大文字の英字で始まる（例: `sTask`） |
| 関数名 | 小文字の英字で始まる |
| 仮引数名 | 小文字の英字で始まる |
| 変数名 | 小文字の英字で始まる |
| セルタイプ名（シングルトン） | `'t'` + セル名 |
| セルタイプ名（マルチインスタンス） | `'t'` + 大文字の英字で始まる（例: `tTask`） |
| セル名 | 大文字の英字で始まる（例: `Task1`） |
| マクロ（定数マクロ） | 全て大文字 |
| 呼び口名 | `'c'` + 大文字の英字で始まる（例: `cTaskBody`） |
| 受け口名 | `'e'` + 大文字の英字で始まる（例: `eTask`） |
| 属性名 | 小文字の英字で始まる |
| 構造体タグ名 | 任意の文字列 |
| 構造体フィールド名 | 任意の文字列 |
| 型名 | 全て大文字（ただし基本型は全て小文字） |
| ネームスペース名 | 大文字で始まる |
| 列挙定数 | 全て大文字 |

## 関連

- [[tecs-cdl]]
- [[tecs-signature]]
- [[tecs-celltype]]
- [[tecs-cell]]
- [[tecs-port]]
- [[tecs-namespace]]
