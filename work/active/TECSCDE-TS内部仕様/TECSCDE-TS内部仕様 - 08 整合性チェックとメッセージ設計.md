---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第8章（整合性チェックとメッセージ設計）— Diagnostic値クラスとDiagnosticsCollectorクラスによる診断パイプラインの集約。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 8 of 11（[[TECSCDE内部仕様]]の第9章に対応）。

## 8. 整合性チェックとメッセージ設計

診断の集約方針（1件のレポートに集約する、外部仕様8.3.2）は実装方式に依存しないため[[TECSCDE内部仕様]]第9章と同一である。本章はこれをクラスとして表現する。

### 8.1 `Diagnostic`値クラス

```ts
class Diagnostic {
  private constructor(
    readonly severity: 'error' | 'warning',
    readonly code: string,        // tecsgenのG-code/S-code、または新規警告コード（8.2節）
    readonly message: string,     // 9.1.2: tecsgenのメッセージカタログを踏襲
    readonly location?: { file: string; line: number; column: number },
    readonly relatedElement?: CellId | PortId | JoinId,
  ) {}

  static error(code: string, message: string, opts?: Partial<Diagnostic>): Diagnostic {
    return new Diagnostic('error', code, message, opts?.location, opts?.relatedElement);
  }
  static warning(code: string, message: string, opts?: Partial<Diagnostic>): Diagnostic {
    return new Diagnostic('warning', code, message, opts?.location, opts?.relatedElement);
  }
}
```

`Diagnostic`はフィールドしか持たない値クラスであり、既存内部仕様の`interface Diagnostic`と実質的な差はない——診断データそのものにクラス化の恩恵は小さい。差分が生じるのは次の`DiagnosticsCollector`側である。

### 8.2 `DiagnosticsCollector`クラス

現行実装（[[TECSCDE-JS-TS実装]]）の`diagnostics/collector.ts`は既にクラスとして存在する。本書はこれを、モジュールB（パーサ）・H自身（整合性チェック実行）という複数の発生源からの`report()`呼び出しを1つの`DiagnosticReport`に集約する役割として明確化する。

```ts
class DiagnosticsCollector {
  private readonly diagnostics: Diagnostic[] = [];

  report(diagnostic: Diagnostic): void { this.diagnostics.push(diagnostic); } // 発生源ごとに随時追加
  toReport(): DiagnosticReport { return new DiagnosticReport([...this.diagnostics]); }
  clear(): void { this.diagnostics.length = 0; } // 新規読込・チェック再実行のたびにリセット
}

class DiagnosticReport {
  constructor(readonly items: readonly Diagnostic[]) {}
  get errorCount(): number { return this.items.filter(d => d.severity === 'error').length; }
  get warningCount(): number { return this.items.filter(d => d.severity === 'warning').length; }
}
```

`DiagnosticsCollector`自身は内部状態（`diagnostics`配列）を可変で保持する——これは第5章5.3節の`GestureController.state`と同様、外部に公開されず、モデル（第3章）や履歴（第4章）に反映されない診断パイプライン内部の一時状態であるため、イミュータブル方針の対象外として扱う。`toReport()`が返す`DiagnosticReport`自体は不変な値クラスであり、モジュールG（UIシェル）はこの不変スナップショットのみを参照する。

### 8.3 警告コード表

外部仕様9.2.2の表をそのままコードの警告コード表として実装する（[[TECSCDE内部仕様]]9.3節と同一）。

| コード | 警告 | 生成モジュール |
|---|---|---|
| `W-DUP-CELL` | セル名が重複 | B（`CdlDocumentBuilder`） |
| `W-UNRESOLVED-CELLTYPE` | セルタイプが解決できない | B |
| `W-MISSING-JOIN-TARGET` | 結合先のセルが存在しない | B |
| `W-COMPOSITE-UNSUPPORTED` | 複合セルタイプを含む | B |
| `W-LAYOUT-DISCARDED` | 保存済みレイアウトを破棄 | B（`ToolInfoValidator`） |
| `W-UNRESOLVED-REF-FILE` | 参照専用ファイルが未解決 | H（`DiagnosticsCollector`、整合性チェック実行時） |

### 8.4 ジャンプ機構

各`Diagnostic.relatedElement`を第6章6.4節の検索ハイライト巡回機構にそのまま渡し、専用のハイライト表現を新設しない（外部仕様8.3.2・9.3.2）。CDL解析エラーで図要素に対応しない場合（`location`のみ持つ場合）は、テキスト位置の提示に留める。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 09 エラーと警告|TECSCDE外部仕様 9. エラーと警告]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 09 整合性チェックとメッセージ設計|TECSCDE内部仕様 第9章（対応する既存設計）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]
