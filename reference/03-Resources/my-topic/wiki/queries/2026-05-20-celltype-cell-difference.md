---
date: 2026-05-20
tags: [tecs, toppers, query]
type: query-output
question: "セルタイプとセルの違いは何ですか"
status: filed
description: "TECSにおけるセルタイプ（Celltype）とセル（Cell）の定義・役割・関係性や相違点のまとめ。"
---

# セルタイプとセルの違いは何ですか

TECS（TOPERS Component System）における**セルタイプ（Celltype）**と**セル（Cell）**の違いは、オブジェクト指向プログラミングにおける「**クラス（型）**」と「**インスタンス（実体）**」の関係に相当します。

---

## 1. 基本的な違いの比較

| 項目 | セルタイプ (Celltype) | セル (Cell) |
| :--- | :--- | :--- |
| **概念上の位置づけ** | コンポーネントの**型定義**（クラス） | コンポーネントの**インスタンス**（オブジェクト） |
| **役割** | インタフェース（受け口・呼び口）や内部状態（変数）、定数（属性）の構成要素の宣言。 | 実際の実行単位。属性の具体値の設定 and 他セルとの具体的な接続関係の定義。 |
| **CDLでの定義** | `celltype` キーワードを用いて宣言する。 | `cell` キーワードを用いてインスタンス化する。 |
| **実体（メモリ）** | 定義データであり、それ単体ではメモリを割り当てられない。 | 定義に基づきメモリ（RAM/ROM）上に展開され、属性値や状態変数を保持する。 |
| **C言語ソースへのマッピング** | 各受け口関数の実装（セルタイプコード）の作成。 | `tecsgen`による構造体インスタンスおよびスケルトンコードの自動生成。 |

---

## 2. CDL（コンポーネント記述言語）での表現の違い

### セルタイプの定義（型定義）
[tecs-celltype]([[tecs-celltype]]) は、シグニチャを介してどのようなポート（呼び口・受け口）を持つか、どのような属性（定数）と変数（状態）を持つかを宣言します。

```cdl
/* セルタイプ tTask の定義（型定義） */
celltype tTask {
    entry sTask eTask;            /* 受け口：このセルが提供するインタフェース */
    call  sTaskBody cTaskBody;    /* 呼び口：このセルが依存する他セルのインタフェース */
    attr  int32_t priority;       /* 属性：セルごとに変更可能なコンパイル時定数 */
    var   int32_t state;          /* 変数：実行時状態を保持するメモリ */
};
```

### セルの定義（インスタンス化・組上げ）
[tecs-cell]([[tecs-cell]]) は、定義されたセルタイプを実体化し、属性の具体値を割り当てたり、ポート同士を結合（バインド）したりします。

```cdl
/* セルタイプ tTask をインスタンス化したセル MyTask */
cell tTask MyTask {
    priority = 10;                     /* 属性値の決定 */
    cTaskBody = MyTaskBody.eTaskBody;  /* 呼び口を別セルの受け口へ接続（結合） */
};
```

---

## 3. 両者の関係性

1. **一対多の関係**:
   ひとつの [tecs-celltype]([[tecs-celltype]]) から、属性値や接続先の異なる複数の [tecs-cell]([[tecs-cell]]) を生成（インスタンス化）できます。
2. **実行時状態の独立**:
   複数のセルが同じセルタイプから生成されても、メモリ領域（`var` で定義された内部変数など）はセルごとに個別に割り当てられるため、実行時状態は独立しています。
3. **カプセル化（複合セルタイプ）**:
   [tecs-composite-celltype]([[tecs-composite-celltype]]) を使用することで、内部の複数のセルおよびセル間結合をカプセル化し、外部からはひとつのセルタイプ（型）として扱うこともできます。

---

## Sources

- [tecs-celltype]([[tecs-celltype]]) — セルタイプ概念定義
- [tecs-cell]([[tecs-cell]]) — セル・組上げ記述概念定義
- [tecs-port]([[tecs-port]]) — 呼び口・受け口に関する解説
- [tecs-composite-celltype]([[tecs-composite-celltype]]) — 複合セルタイプ概念定義
- [queries/2026-04-24-celltype-toha-nanika]([[2026-04-24-celltype-toha-nanika]]) — 「セルタイプとは何か」のクエリ結果
- [queries/2026-04-24-cell-toha-nanika]([[2026-04-24-cell-toha-nanika]]) — 「セルとは何か」のクエリ結果
