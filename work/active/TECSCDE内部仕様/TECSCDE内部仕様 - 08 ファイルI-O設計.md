---
date: 2026-08-30
description: "TECSCDE内部仕様書 第8章（ファイルI/O設計）— File System Access API分岐、ドラッグ&ドロップ、エクスポート"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE内部仕様]] (2026-08-30, 25KB threshold). Chapter 8 of 12.

## 8. ファイルI/O設計

### 8.1 読み込み経路

| 経路 | 実装 |
|---|---|
| ファイル選択 | `<input type="file" multiple>` |
| ドラッグ＆ドロップ | キャンバス領域への`drop`イベント |

いずれも複数ファイルを受け付け、8.1.2の規則（最後に選択／ドロップされたファイルを編集対象、他は参照専用）を`file-open.ts`で確定する。参照専用ファイルのセルは`editable: false`としてモデルへ取り込む（10.2.1）。

### 8.2 保存経路

```ts
const canUseFSAccess = 'showOpenFilePicker' in window
                     && 'showSaveFilePicker' in window;
```

- 利用可能な場合: 開いた際のファイルハンドルを保持し、「保存」はハンドルへの書き戻し、「名前を付けて保存」は`showSaveFilePicker`で新規ハンドルを取得する。
- 利用不可の場合: 「保存」は直近のダウンロードファイル名を使ったダウンロードにフォールバックし、「名前を付けて保存」はファイル名入力後にダウンロードする。

どちらの経路でも、書き込み完了前に既存内容を破棄しないこと（5.4.2）を保証する——File System Access API利用時は一時バッファへ全体を書き終えてからハンドルへ書き込む。

### 8.3 エクスポート

SVG（第一形式）・PNG（SVG経由のラスタライズ、出力倍率指定可）を`file-save.ts`と同じ保存経路に載せる。「用紙に合わせる」「内容に合わせる」の出力範囲選択を提供する（5.6.2）。PDFは対象外とし、印刷用スタイルシート（`@media print`）で代替する。

### 8.4 未保存確認

`store.ts`が保存操作完了時点を基準に「未保存」フラグを保持し、`beforeunload`イベント・新規作成・読み込み操作の直前チェックに反映する（5.7.2）。この状態は5章のUndo履歴とは独立に持つ（現行版のChangeSetを保存要否フラグに流用しない方針を踏襲、6.6.1）。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様 第7章（クラスベース代替設計）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 05 ファイル操作|TECSCDE外部仕様 5. ファイル操作]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様（目次）]]
