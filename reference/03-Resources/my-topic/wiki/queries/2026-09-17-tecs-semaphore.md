---
date: 2026-09-17
tags: [tecs, asp3, rtos, query]
type: query-output
question: "TECSのセマフォについて教えて"
status: filed
description: "TECS（TOPPERS Component System）におけるセマフォ（tSemaphore、sSemaphore、siSemaphore）の概要・使用方法・CDL定義・サービスコールマッピングのまとめ。"
---

# TECSのセマフォについて

TECS（TOPPERS Component System）において、セマフォは資源の排他制御や同期を行うためのコンポーネント（[[tecs-celltype]]）として提供されています。主に **TOPPERS/ASP3** などのリアルタイムOS連携（[[asp3-tecs]]）において、カーネルオブジェクトをセル（[[tecs-cell]]）として扱えるように抽象化・カプセル化されています。

---

## 1. 概要と特徴

- **セルタイプ名**: `tSemaphore` ([[asp3-tsemaphore]])
- **目的**: 使用されていない資源の有無や数量を数値で表現し、タスク間の排他制御や同期を実現。
- **静的生成メカニズム**:
  TECSジェネレータ（[[tecsgen]]）のファクトリ機構（[[imp-factory]]）により、静的APIである `CRE_SEM` 記述（`tecsgen.cfg`）が自動生成されます。
- **実行時最適化**:
  セマフォ属性（`attribute`、`count`、`max` など）はコンパイル時・静的API生成時にのみ使用され、実行時には不要なため `[omit]` 指定によってRAM/ROMメモリ消費が最適化（削減）されます。

---

## 2. セルタイプ定義 (`tSemaphore`)

### 属性 (Attributes)
| 属性名 | 型 | 説明・既定値 |
| :--- | :--- | :--- |
| `id` | `ID` | セマフォのID番号識別子（既定: `C_EXP("SEMID_$id$")`） |
| `attribute` | `ATR` | セマフォ属性（`TA_NULL`: FIFO待ち、`TA_TPRI`: 優先度順待ち など） |
| `count` | `uint32_t` | 初期資源数 |
| `max` | `uint32_t` | 最大資源数（既定: `1`） |

### 受け口 (Entry Ports)
- **`eSemaphore`** (`sSemaphore` シグニチャ): タスクコンテキスト用のセマフォ制御・状態参照。
- **`eiSemaphore`** (`siSemaphore` シグニチャ): 非タスクコンテキスト（割込みハンドラ等）用のセマフォ返却。

---

## 3. シグニチャと提供機能

### `sSemaphore`（タスク用）
| 関数 | 対応サービスコール | 説明 |
| :--- | :--- | :--- |
| `signal()` | `sig_sem` | セマフォ資源を返却（待ちタスクがあれば先頭を解除） |
| `wait()` | `wai_sem` | セマフォ資源を獲得（資源がなければタスク待ち） |
| `waitPolling()` | `pol_sem` | ポーリングによる資源獲得 |
| `waitTimeout(timeout)` | `twai_sem` | タイムアウト付き資源獲得 |
| `initialize()` | `ini_sem` | セマフォを再初期化（資源数を初期値へ戻す） |
| `refer(pk_semaphoreStatus)` | `ref_sem` | セマフォの現在状態（`T_RSEM`）を参照 |

### `siSemaphore`（非タスクコンテキスト用）
| 関数 | 対応サービスコール | 説明 |
| :--- | :--- | :--- |
| `signal()` | `sig_sem` | 非タスク側から資源を返却 |

---

## 4. CDL記述例とC言語コード例

### CDL記述 (app.cdl)
```cdl
/* 呼び出し側セルタイプの宣言 */
celltype tMyCellType {
    call sSemaphore cSemaphore;  /* セマフォ呼び口 */
};

/* セマフォセルの生成 */
cell tSemaphore MySemaphore {
    attribute = C_EXP("TA_NULL");
    count = 0;
    max = 1;
};

/* セル同士の結合（バインド） */
cell tMyCellType MyCell {
    cSemaphore = MySemaphore.eSemaphore;
};
```

### C言語ソースでの利用 (tMyCellType.c)
```c
/* 資源の獲得（待機） */
ER ercd = cSemaphore_wait();
if (ercd == E_OK) {
    /* クリティカルセクション処理 */
    ...

    /* 資源の返却 */
    cSemaphore_signal();
}
```

---

## Sources

- [[asp3-tsemaphore]] — tSemaphore セルタイプ定義
- [[asp3--semaphore]] — ASP3 セマフォ ソースサマリー
- [[asp3-tecs]] — ASP3+TECS 統合仕様
- [[tecs-overview]] — TECS 概要
- [[tecs-signature]] — シグニチャ仕様
- [[tecs-celltype]] — セルタイプ仕様
- [[imp-factory]] — ファクトリ記述による静的生成
