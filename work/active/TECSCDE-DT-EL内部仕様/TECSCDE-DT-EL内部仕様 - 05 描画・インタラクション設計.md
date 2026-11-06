---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第5章（描画・インタラクション設計）— TS内部仕様を基本とし、複合セルタイプを3B章、検索ハイライトを6.4節で具体化。rendererプロセスで動作。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

> [!info] V0.2.0差分設計（2026-11-06）
> V0.2.0の青背景・赤い結合強調・リージョン矩形外周は[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]を追加設計とします。外部仕様のTBCを維持します。差分章は実装前の内部設計です。


Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 5 of 11。

## 5. 描画・インタラクション設計

`SvgRenderer`・`CellRenderer`/`JoinRenderer`・`HitTester`・`GestureController`のクラス設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様第5章]]と**複合セルタイプおよび検索ハイライトの具体化を除き同一**。SVG/DOMへのアクセスを要するため本モジュール（E）はrendererプロセスでのみ動作し、Electronのmain/preloadとは無関係である。

`GestureController.state`をUI一時状態としてイミュータブル方針の対象外とする扱いも変更なし（[[TECSCDE-TS内部仕様]]5.3節参照）。

複合セルタイプの外側表示と内部図への遷移禁止は[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B章]]で定める。

検索ハイライトの描画オプション`SearchHighlights`、セルの破線枠・結合の背面強調線、選択表示との重なり順、差分更新とプレビュー追従は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 06 表示制御設計#6.4 検索ハイライトと解除（2026-10-25具体化）|第6章6.4節]]を優先する。Escによる検索解除は`AppShell`が扱い、`GestureController`の既存キャンセル処理と両立させる。

その他の詳細は[[TECSCDE-TS内部仕様]]第5章を参照。

> [!note] 実装での設計更新（2026-09-09）
> - **`HitTester`**: `SvgRenderer` ではなく、ズーム比率のみを参照する `CanvasView` を受け取る疎結合な構造に変更。
> - **`GestureController`**: コンストラクタで DOM リスナを張らず、イベント処理メソッドを公開した上で `attach(svg)` メソッドで明示的に結線する設計に変更（状態機械をヘッドレスで単体テスト可能にするため）。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様 第5章（基礎設計。複合セルタイプ・検索ハイライトはDT-ELの具体化を優先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
