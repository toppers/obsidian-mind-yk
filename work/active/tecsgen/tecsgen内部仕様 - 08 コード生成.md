---
date: 2026-08-22
description: "tecsgen内部仕様書 第8章（コード生成、generate.rb）— 生成の起点、ファイル出力制御、_tecsgen.h/_factory.h/tecsgen.cfg/INITIALIZE_TECS()の生成。CFile/AppFileの役割誤認とテンプレート出力オプションの誤りを訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 8 of 12. 2026-08-22、`generate.rb`・`plugin.rb`・`tecsgen.rb`（オプション解析部）を直接読んで 8.2/8.4/8.6 を検証・訂正。8.1/8.3/8.5 は未再検証（旧内容を維持）。

## 8. コード生成（generate.rb）

### 8.1 生成の起点

`root_namespace.generate`（`Namespace#generate`）が起点。1回の呼び出しの中で「`global_tecsgen.h`（typedef/struct/const の生成）→ 各 Signature の `generate` → 各 Celltype の `generate` → サブ Namespace への再帰」の順に処理し、最後に（`Region` の場合のみ）domain/class プラグインの `gen_factory` を呼ぶ。domain/class の `gen_factory` を末尾に回しているのは、他の生成コードが出力し終わった後でなければ正しく生成できないという V1.8 での設計判断（ソースコメント「ドメインプラグインの gen_factory は、諸々のコードの出た後で呼び出す」）。

### 8.2 ファイル出力制御（AppFile / CFile）

> [!warning] CFile はテンポラリ書き出し用ではない
> 旧版は「`CFile`: テンポラリファイルに生成内容を書き出す」としていたが誤り。`CFile`（`plugin.rb:297`）は `File` の薄いラッパーで、`kconv` による文字コード変換（`$KCONV_CDL` へ変換して出力）を担うだけの汎用出力クラス。`.tmp` へ書いてから比較・リネームする仕組みを持つのは `AppFile` の側であり、`CFile` とは無関係の独立した2つのクラス。

- `AppFile.open`：`$force_overwrite`（`-f`）が偽の場合、常に `<name>.tmp` へ書き込む（同名を2回目以降 open した場合は追記モード）
- `AppFile.update`：生成完了後、`.tmp` と既存ファイルを行単位で比較し、完全一致すれば `.tmp` を削除、差分があれば `.tmp` を実ファイルへ `rename`（不要なタイムスタンプ更新を避けビルド差分を最小化）。`$force_overwrite` が真なら比較を行わず常に上書き
- テンプレートファイル（`_templ.c` 等）の生成可否は `-f`（`$force_overwrite`）とは無関係で、`--generate-all-template`（`$generate_all_template`）/ `--generate-no-template`（`$generate_no_template`）という別系統のオプションと `@b_reuse`（reuse セルタイプか）で決まる（`generate_template_code` 冒頭のガード節）

### 8.3 `_tecsgen.h` の生成

各セルタイプに対して以下の順序でコードを出力:

1. インクルードガード
2. CELLCB 型定義（属性・変数・呼び口ポインタ）
3. セルの宣言（extern）・初期化子
4. VALID_IDX / GET_CELLCB マクロ
5. 属性・変数アクセスマクロ（短縮形・通常形）
6. 呼び口関数マクロ（最適化結果により VMT 経由 or 直接呼び出し）
7. 受け口関数プロトタイプ
8. FOREACH_CELL / END_FOREACH_CELL マクロ
9. `#include "tCELLTYPE_inline.h"` のインクルード行

### 8.4 `_factory.h` の生成

- `factory{}` / `FACTORY{}` 記述から静的変数・初期化コードを生成
- プレースホルダは `$id$`（セル名。composite 内では複合セルタイプのセル名に展開）だけでなく `$ct$` / `$cb$` / `$idx$` も存在する（`generate.rb:5234` 付近「$id$, $ct$, $cb$, $idx$ 置換」、詳細な対応関係は未再検証）

### 8.5 `tecsgen.cfg` の生成

- ファクトリ記述のうちカーネル設定向け出力（`TOPPERS/ASP3` の静的 API 等）
- `FACTORY{}` 記述（セルタイプ単位）と `factory{}` 記述（セル単位）の両方を処理

### 8.6 INITIALIZE_TECS() の生成

> [!note] グローバルヘッダの一部であり、セルタイプ別 `_tecsgen.h` ではない
> `INITIALIZE_TECS()` は 8.1 の `gen_global_header`（`global_tecsgen.h` 生成）の中で出力される（`generate.rb:273`）。8.3 の `_tecsgen.h` はセルタイプごとに生成されるファイルであり、`INITIALIZE_TECS()` はそれとは別のグローバル1ファイルにのみ定義される。

V1.3 以降常に生成される初期化マクロ。全セルタイプの CB 初期化コードを呼び出す。後方互換のため `INITIALZE_TECSGEN()`（原文ママ、`INITIALIZE` のタイポを含む旧名）が `INITIALIZE_TECS()` の別名として併せて定義される（`generate.rb:280`）。

---

