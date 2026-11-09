---
date: 2026-04-24
tags: [tecs, toppers, cdl, query]
type: query-output
question: "CDLの書き方を教えて"
status: filed
description: "TECS CDLの記述方法。前置部・シグニチャ・セルタイプ・組上げ記述の構文と名前付け慣習を網羅。"
---

# CDLの書き方

[[tecs-cdl]] (TECS CDL) は `.cdl` 拡張子のファイルに記述します。C言語文法と親和性があり、UTF-8文字コードを使用します。

## 記述順序

CDLファイルは**前方参照制約**があるため、以下の順序で記述します。

```
1. 前置部       (import / import_C / typedef / struct / enum / const)
2. シグニチャ記述
3. セルタイプ記述
4. 複合セルタイプ記述
5. 組上げ記述（セル記述）
6. ネームスペース記述
7. リージョン記述
```

## 1. 前置部

型定義や他ファイルのインポートを行います。

```cdl
import_C("kernel.h");           /* Cヘッダから型定義だけ取込む */
import("mycomponent.cdl");      /* 他のCDLファイルを取込む */

typedef int32_t INT;            /* 型定義 */

const int32_t MAX_SIZE = 256;   /* 定数定義 */
```

> **注意:** `import_C` で取り込まれるのは `typedef` のみ。`#define` マクロは取り込まれない。マクロを参照するには `C_EXP("...")` を使う。

## 2. [[tecs-signature]]（シグニチャ記述）

コンポーネント間のインタフェース（関数の集合）を定義します。慣習としてシグニチャ名は `s` で始めます。

```cdl
signature sInputOutput {
    ER setOutput([in]  int8_t  val);   /* 入力: 呼び元→呼び先 */
    ER getInput ([out] int8_t *val);   /* 出力: 呼び先→呼び元 */
    ER noParam  (void);
};
```

**引数の基本指定子:**

| 指定子 | 方向 | 備考 |
|-------|------|------|
| `in` | 呼び元→呼び先 | ポインタ型は `const` 必須 |
| `out` | 呼び先→呼び元 | ポインタ必須 |
| `inout` | 双方向 | ポインタ必須 |
| `send` | 呼び元→呼び先 | 呼び先がdealloc |
| `receive` | 呼び先→呼び元 | 呼び先がalloc |

## 3. [[tecs-celltype]]（セルタイプ記述）

コンポーネントの型を定義します。慣習として名前は `t` で始め、受け口は `e`、呼び口は `c` で始めます。

```cdl
[singleton]
celltype tMyCelltype {
    entry sInputOutput eEntry;   /* 受け口: サービス提供 */
    call  sInputOutput cCall;    /* 呼び口: サービス呼出し */

    attr {
        int16_t  len       = 256;
        char*    bufName;
        int8_t   initState = 0;
    };

    var {
        [size_is(len)] int8_t* buf;
        int16_t rdPoint;
        int8_t  stateNo = initState;
    };

    factory {
        write("tecsgen.cfg", "CRE_XXX(ID_$id$, { %s });", attribute);
    };
};
```

**属性 vs 変数:**

| | 属性 (`attr`) | 変数 (`var`) |
|--|---|---|
| 配置 | ROM | RAM |
| 実行時書換え | 不可 | 可 |
| セルでの初期値指定 | 可 | 不可（属性参照のみ） |

## 4. [[tecs-cell]]（組上げ記述）

セルタイプをインスタンス化し、セル間の呼び口と受け口を結合します。慣習としてセル名は大文字で始めます。

```cdl
cell tMyCelltype MyCell {
    cCall       = OtherCell.eEntry;
    cCallArray[]= Cell0.eEntry;
    len         = 512;
    bufName     = C_EXP("\"MyBuf\"");
};
```

## 5. 名前付け慣習

| 対象 | 先頭文字 | 例 |
|-----|---------|---|
| シグニチャ | `s` | `sTask`, `sInputOutput` |
| セルタイプ | `t` | `tTask`, `tMyCelltype` |
| 受け口 | `e` | `eTask`, `eEntry` |
| 呼び口 | `c` | `cTask`, `cCall` |
| セル | 大文字 | `MyTask`, `SampleCell` |
| 属性・変数 | 小文字 | `stackSize`, `priority` |

## 6. tecsgenで処理する

[[tecsgen]] にCDLファイルを渡してCコードを生成します。

```sh
tecsgen -I include/ app.cdl
```

## 完全な例（ASP3タスク）

```cdl
signature sTaskBody { void main(void); };

celltype tMyTask {
    call sTaskBody cBody;
    attr {
        PRI    priority  = 10;
        size_t stackSize = 1024;
    };
    factory {
        write("tecsgen.cfg",
              "CRE_TSK(TSKID_$id$, { TA_ACT, $cb$, tMyTask_main, %s, %s, NULL });",
              priority, stackSize);
    };
};

cell tMyTask MainTask {
    cBody    = App.eBody;
    priority = 5;
};
```

## Sources

- [[tecs-cdl]]
- [[tecs-signature]]
- [[tecs-celltype]]
- [[tecs-cell]]
- [[tecs--cdlref-signature]]
- [[tecs--cdlref-celltype]]
- [[tecs--cdlref-cell]]
- [[tecs--cdlref-preface]]
- [[tecsgen]]
