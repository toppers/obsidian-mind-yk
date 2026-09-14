---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第9章（tecsgen連携設計）— TecsgenCommandBuilderクラス（静的メソッドのみ、副作用なし・非実行）。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 9 of 11（[[TECSCDE内部仕様]]の第10章に対応）。

## 9. tecsgen連携設計

### 9.1 `TecsgenCommandBuilder`クラス

モジュールI（葉ノード）は`toolInfoTecsgen`（第3章、解釈せず保持すると規定した値）と第7章7.1節で定めた参照専用ファイル一覧のみを読み、tecsgenのコマンドライン文字列を組み立てて提示・コピーする（外部仕様8.4.2）。

```ts
class TecsgenCommandBuilder {
  // 状態を持たないため全メソッドをstaticにする——インスタンス化する意味がない
  static build(doc: TecscdeDocument, referenceFiles: readonly string[]): string {
    // 例: tecsgen -I <import_path> -D <macro> -c <cpp> <参照専用ファイル…> <編集対象ファイル>
    // base_dirはCLIに出さない（詳細: [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携#8.4.2 JS 版の規定]]）
    return '';
  }
}
```

第2章2.2節で述べたとおり、このクラスは実質的にnamespaceと同等であり、クラス化による設計上の差分はない。「クラスにする」こと自体よりも、次の9.2節の非実行境界をモジュール構造として強制することが本章の要点である。

### 9.2 非実行の境界

`TecsgenCommandBuilder`は`TecscdeDocument`を含むどの状態にも書き戻さない。[[TECSCDE内部仕様]]第10章と同じく、`tecsgen-link/`ディレクトリからは`store.ts`（`Store`クラス）への書き込みAPI（コマンドのdispatch）を一切importしないことをdependency-cruiserルールで強制し、「提示するが実行しない」という外部仕様の言葉をビルド時検証可能な制約にする。クラスベースであってもこの境界は`import`文のレベルで検証するため、モジュールIの内部表現がクラスか関数かは境界の強制方法に影響しない。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様 8. CDL連携]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 10 tecsgen連携設計|TECSCDE内部仕様 第10章（対応する既存設計）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]
