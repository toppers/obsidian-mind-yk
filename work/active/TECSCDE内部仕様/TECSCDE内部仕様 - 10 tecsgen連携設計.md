---
date: 2026-08-30
description: "TECSCDE内部仕様書 第10章（tecsgen連携設計）— コマンド文字列組み立て、非実行の境界"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE内部仕様]] (2026-08-30, 25KB threshold). Chapter 10 of 12.

## 10. tecsgen連携設計

### 10.1 コマンド文字列組み立て

モジュールI（葉ノード）は`toolInfoTecsgen`（3.2で解釈せず保持すると規定した値）と8.1.2で新設した参照専用ファイル一覧のみを読み、tecsgenのコマンドライン文字列を組み立てて提示・コピーする（8.4.2）。

```ts
function buildTecsgenCommand(doc: TecscdeDocument, referenceFiles: string[]): string {
  // 例: tecsgen -I <import_path> -D <macro> -c <cpp> <参照専用ファイル…> <編集対象ファイル>
  // base_dirはCLIに出さない（詳細: [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携#8.4.2 JS 版の規定]]）
}
```

### 10.2 非実行の境界

このモジュールは`TecscdeDocument`を含むどの状態にも書き戻さない。実装上も、`tecsgen-link/`ディレクトリからは`store.ts`への書き込みAPI（コマンドのdispatch）を一切importしないことをdependency-cruiserルールで強制し、「提示するが実行しない」という外部仕様の言葉をビルド時検証可能な制約にする。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|TECSCDE-TS内部仕様 第9章（クラスベース代替設計）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様 8. CDL連携]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様（目次）]]
