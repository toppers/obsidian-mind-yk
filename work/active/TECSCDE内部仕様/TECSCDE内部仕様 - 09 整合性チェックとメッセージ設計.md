---
date: 2026-08-30
description: "TECSCDE内部仕様書 第9章（整合性チェックとメッセージ設計）— 診断収集パイプライン、メッセージ一覧"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE内部仕様]] (2026-08-30, 25KB threshold). Chapter 9 of 12.

## 9. 整合性チェックとメッセージ設計

### 9.1 診断パイプライン

モジュールH（診断）はB・Cに対する読み取り専用オブザーバとして、`diagnostics/collector.ts`に一元化する。発生源は次のとおり分散しているが、集約先は1箇所にする（8.3.2の「1件のレポート」要件）。

```
パーサ（B）         ─┐
スキーマ検証（B）    ─┤
インポート時整合性(H)─┼→ collector.ts → 1件のDiagnosticReport → 9.3のUI一覧・ステータス集計
整合性チェック実行(H)─┤
レイアウト復元（B）  ─┘
```

### 9.2 診断の型

```ts
interface Diagnostic {
  readonly severity: 'error' | 'warning';
  readonly code: string;       // tecsgenのG-code/S-code、または新規警告コード
  readonly message: string;    // 9.1.2: tecsgenのメッセージカタログを踏襲
  readonly location?: { file: string; line: number; column: number };
  readonly relatedElement?: CellId | PortId | JoinId;
}
```

### 9.3 警告一覧の実装対応

外部仕様9.2.2の表をそのままコードの警告コード表として実装する。

| コード | 警告 | 生成モジュール |
|---|---|---|
| `W-DUP-CELL` | セル名が重複 | B（パーサ） |
| `W-UNRESOLVED-CELLTYPE` | セルタイプが解決できない | B |
| `W-MISSING-JOIN-TARGET` | 結合先のセルが存在しない | B |
| `W-COMPOSITE-UNSUPPORTED` | 複合セルタイプを含む | B |
| `W-LAYOUT-DISCARDED` | 保存済みレイアウトを破棄 | B（tool-info検証） |
| `W-UNRESOLVED-REF-FILE` | 参照専用ファイルが未解決 | H（整合性チェック実行時） |

### 9.4 ジャンプ機構

各`Diagnostic`の`relatedElement`を7.4の検索ハイライト巡回機構にそのまま渡し、専用のハイライト表現を新設しない（8.3.2・9.3.2）。CDL解析エラーで図要素に対応しない場合（`location`のみ持つ場合）は、テキスト位置の提示に留める。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-TS内部仕様 第8章（クラスベース代替設計）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 09 エラーと警告|TECSCDE外部仕様 9. エラーと警告]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様（目次）]]
