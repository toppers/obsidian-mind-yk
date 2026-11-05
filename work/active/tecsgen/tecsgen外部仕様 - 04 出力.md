---
date: 2026-08-16
description: "tecsgen外部仕様書 第4章（出力）— 生成ファイル一覧、セルタイプヘッダ（_tecsgen.h）、INITIALIZE_TECS()マクロ、コード生成の最適化。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 4 of 10.

## 4. 出力

### 4.1 生成ファイル一覧

生成ディレクトリ（デフォルト: `gen/`）に以下のファイルを出力する。

| ファイル | 内容 | 種類 |
|---------|------|------|
| `tCELLTYPE_tecsgen.h` | CELLCB 型・マクロ定義・インライン関数インクルード | 自動生成（上書き） |
| `tCELLTYPE_factory.h` | ファクトリから生成される静的変数・初期化コード | 自動生成（上書き） |
| `tCELLTYPE_templ.c` | 受け口関数テンプレート（tecsmerge のソース） | 自動生成（テンプレート） |
| `tCELLTYPE_inline_templ.h` | インライン関数テンプレート | 自動生成（テンプレート） |
| `tecsgen.cfg` | ファクトリ出力（カーネル静的 API 等） | 自動生成（上書き） |
| `tecsgen.rbdmp` | tecsgen 内部モデルダンプ（tecsflow 用） | 自動生成 |

テンプレートファイル（`_templ.c`, `_templ.h`）は `-f` オプション指定時のみ上書きされる。通常は tecsmerge で既存実装コードに差分マージする。

### 4.2 セルタイプヘッダ（`_tecsgen.h`）の内容

各セルタイプに対して生成される `tCELLTYPE_tecsgen.h` が含む内容:

1. **CELLCB 型定義** — セルの属性・変数を格納する構造体
2. **マクロ定義**
   - `VALID_IDX(idx)` — IDX 正当性チェック
   - `GET_CELLCB(idx)` — CELLCB ポインタ取得
   - `ATTR_属性名` — 属性アクセス（短縮形）
   - `VAR_変数名` — 変数アクセス（短縮形）
   - `cCall_func(...)` — 呼び口関数呼び出し
   - `NCP_cCall` — 呼び口配列サイズ
   - `FOREACH_CELL(i, p_cellcb)` / `END_FOREACH_CELL` — 全セル反復
   - 通常形マクロ（`tCELLTYPE_ATTR_名前(p_cellcb)` 等）
3. **受け口関数プロトタイプ宣言**
4. **インライン関数ヘッダのインクルード**（`tCELLTYPE_inline.h`）

### 4.3 INITIALIZE_TECS() マクロ

V1.3 以降は常に生成される初期化マクロ。アプリケーションの main 関数の先頭で必ず呼び出す必要がある。呼び出しを省略した場合の動作は未定義。

### 4.4 コード生成の最適化

`-U (--unoptimize)` なしの場合（デフォルト）、tecsgen は以下の最適化を適用する:

**呼び口最適化（optimize_call）**

呼び口が参照するすべてのセルの結合先が同一ポートである場合、以下を組み合わせて適用する:

| 最適化名 | 条件 | 効果 |
|---------|------|------|
| cell_unique | 全セルが同一セル・同一ポートに結合 | CELLCB ポインタを CB に格納しない（直接アドレス） |
| VMT_useless | 全セルが同一ポートに結合 | 関数テーブル（VMT）を生成せず受け口関数を直接呼び出す |
| skeleton_useless | VMT 不要かつ cell_unique | スケルトン関数を生成しない |
| omit（省略） | `optional` で未結合 | CB から呼び口フィールドを省略 |

動的結合（`[dynamic]` / `[ref_desc]`）が適用された呼び口は最適化対象外。

**受け口最適化（optimize_entry）**

呼び口最適化の結果を使用して受け口側のスケルトン関数を省略する。`--unoptimize-entry` オプションで受け口最適化のみを個別に無効化できる。

---

