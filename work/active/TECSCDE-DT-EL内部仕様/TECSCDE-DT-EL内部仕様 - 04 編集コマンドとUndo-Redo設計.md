---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第4章（編集コマンドとUndo-Redo設計）— Command/Historyクラスはrendererで動作しTECSCDE-TS内部仕様と同一。Copy/Paste/CutのみOSクリップボード連携を追加。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 4 of 11。

## 4. 編集コマンドとUndo-Redo設計

`Command`抽象クラス（`apply`のみ、`invert()`は持たない）、`History`クラス（replay計算・past/future操作のカプセル化）、および大半のコマンドクラス（`AddCellCommand`・`MoveCellCommand`・`DeleteCommand`・`CreateJoinCommand`等）は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様第4章]]と**完全に同一、変更なし**。第2章2.3節のとおり本モジュール（D）はrendererプロセスで動作する。

### 4.1 差分: `CopyCommand`/`CutCommand`のOSクリップボード連携

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 06B 編集操作（後半）|TECSCDE-DT外部仕様6.7節]]が採用したOSクリップボード連携を、コマンドクラスに反映する。

```ts
class CopyCommand extends Command {
  readonly kind = 'Copy';
  constructor(private readonly cellIds: readonly CellId[], private readonly clipboard: ClipboardGateway) { super(); }

  apply(doc: TecscdeDocument): TecscdeDocument {
    // 履歴を作らない特殊なコマンド（TECSCDE-TS内部仕様4.5節の表と同一の位置付け）
    const fragment = serializeCellsAsCdl(doc, this.cellIds); // CDLのcellブロック構文（TECSCDE-DT外部仕様6.7節）
    this.clipboard.writeText(fragment); // preloadが直接ブリッジするOSクリップボード（第2章2.4節）
    return doc; // ドキュメントは変更しない
  }
}

class PasteCommand extends Command {
  readonly kind = 'Paste';
  constructor(private readonly appClipboard: readonly Cell[], private readonly clipboard: ClipboardGateway) { super(); }

  apply(doc: TecscdeDocument): TecscdeDocument {
    // アプリ内クリップボードが空の場合のみ、OSクリップボードのCDL断片を解析して貼り付ける
    if (this.appClipboard.length > 0) {
      return pasteFromAppClipboard(doc, this.appClipboard);
    }
    const text = this.clipboard.readText();
    const parsed = tryParseCdlFragment(text); // 解析できない場合は何もしない（TECSCDE-DT外部仕様6.7節）
    return parsed ? pasteFromCdlFragment(doc, parsed) : doc;
  }
}
```

`ClipboardGateway`は第2章2.4節で設計したとおり、preloadスクリプトが直接ブリッジする（`ipcMain`を介さない）薄いラッパーである。

```ts
class ClipboardGateway {
  writeText(text: string): void { window.tecscde.clipboard.writeText(text); }
  readText(): string { return window.tecscde.clipboard.readText(); }
}
```

`CutCommand`は[[TECSCDE-TS内部仕様]]4.5節の設計（内部で`CopyCommand`相当の処理と`DeleteCommand`相当を1コマンドに合成）を踏襲し、`CopyCommand`側の変更がそのまま反映される。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様 第4章（一次情報源、Copy/Paste/Cut以外は同一）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 06B 編集操作（後半）|TECSCDE-DT外部仕様 第6章後半（OSクリップボード連携の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（ClipboardGatewayの設計根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
