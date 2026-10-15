---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第5章（描画・インタラクション設計）— TECSCDE-TS内部仕様を基本とし、複合セルタイプは3B章で拡張。rendererプロセスで動作。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 5 of 11。

## 5. 描画・インタラクション設計

`SvgRenderer`・`CellRenderer`/`JoinRenderer`・`HitTester`・`GestureController`のクラス設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様第5章]]と**複合セルタイプを除き同一**。SVG/DOMへのアクセスを要するため本モジュール（E）はrendererプロセスでのみ動作し、Electronのmain/preloadとは無関係である。

`GestureController.state`をUI一時状態としてイミュータブル方針の対象外とする扱いも変更なし（[[TECSCDE-TS内部仕様]]5.3節参照）。

複合セルタイプの外側表示と内部図への遷移禁止は[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B章]]で定める。

その他の詳細は[[TECSCDE-TS内部仕様]]第5章を参照。

> [!note] 実装での設計更新（2026-09-09）
> - **`HitTester`**: `SvgRenderer` ではなく、ズーム比率のみを参照する `CanvasView` を受け取る疎結合な構造に変更。
> - **`GestureController`**: コンストラクタで DOM リスナを張らず、イベント処理メソッドを公開した上で `attach(svg)` メソッドで明示的に結線する設計に変更（状態機械をヘッドレスで単体テスト可能にするため）。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様 第5章（一次情報源、本章はこれと同一）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
