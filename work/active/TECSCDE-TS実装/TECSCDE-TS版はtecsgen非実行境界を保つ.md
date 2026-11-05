---
date: 2026-09-14
description: TECSCDE-TS（ブラウザ版）のtecsgen連携モジュールIは、DT-EL版と実行APIを共有せず、コマンド文字列の組み立て・提示のみに留める非実行境界を保つと決定。
project: TECS
quarter: Q3-2026
status: accepted
tags:
  - decision
  - tecs
  - tecscde
---

# Decision: TECSCDE-TS版はtecsgen非実行境界を保つ

## Context

[[TECSCDE-TS モジュールI 二重実装の保留]]で発覚したとおり、[[TECSCDE-TS実装]]のモジュールI（tecsgen連携）は並行セッションによる[[TECSCDE-DT-EL実装]]からの逆移植と衝突した。逆移植側の`buildArgs()`は`execFile`へそのまま渡せる実行用の形をしており、`tecsgen-result-parser.ts`もデスクトップ版の実行結果解析を前提にしていた。

TS版がDT-EL版と「共有する一次情報源」を兼ねてtecsgen実行APIを持つのか、それともブラウザ版として非実行境界を保つのかを決める必要があった。これは統合方針（コマンド文字列組み立てロジックの公開面）を左右する分岐点だった。

## Options Considered

1. **TS版もexecFile相当の実行用APIを公開する** — DT-EL版とロジックを最大限共有できるが、[[work/active/TECSCDE外部仕様/TECSCDE外部仕様|TECSCDE外部仕様]]2.3節が定める「JS/ブラウザ版はtecsgenを直接起動できない」という制約と矛盾する。ブラウザにはサブプロセス起動手段がなく、実装しても動作しない。
2. **TS版はコマンド文字列の組み立て・提示・コピーのみに留め、実行は一切持たない** — 外部仕様2.3・8.4.2の制約にそのまま従う。DT-EL版とはコマンド文字列組み立てロジック（`import_path`・`define_macro`・`cpp`からの構築、`base_dir`除外）のみを概念的に共有し、`execFile`呼び出しや実行結果解析はDT-EL固有のまま重複を許容する。

## Decision

**オプション2を採用する。** TECSCDE-TS版の`TecsgenCommandBuilder`は`buildArgs()`／`buildCommandLine()`によるコマンド文字列の組み立て・提示・コピーのみを提供し、`execFile`等によるサブプロセス実行APIは一切公開しない（`TECSGEN_DISCLAIMER`で「実行はしません」と明記）。

根拠: TS版はブラウザ版であり、外部仕様2.3節の非実行制約はTECSCDEの「設計環境」という位置付けそのものに由来する（現行版Ruby実装から一貫）。DT-EL版（Electron/Tauri）はサブプロセス起動が可能な別カテゴリの製品であり、8.4.2はJS版・デスクトップ版それぞれに別節で規定を持つ（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.4.2]]参照）。実行APIを共有すると、TS版のコード内に到達不能な（ブラウザでは動かない）実行経路を抱えることになり、[[TECSCDE共通ロジック]]で言う「実装間で何を共有するか」の判断を誤らせる。

## Consequences

- [[TECSCDE-TS実装]]の`src/tecsgen-link/commandBuilder.ts`は`baseDirHint()`のような文脈情報提示ヘルパーを持ちうるが、`execFile`を呼ぶAPIは今後も追加しない。
- [[TECSCDE-DT-EL実装]]の`tecsgen/command-builder.ts`とはロジックの「型」（`import_path`/`define_macro`/`cppからのコマンドライン構築、base_dir除外）のみを仕様レベルで共有し、コードの共有（同一パッケージ化など）はしない。両リポジトリが別々に実装を保守する。
- 外部仕様8.4.2の生成コマンド例の誤り（`-I <base_dir>`）はこの決定と独立に訂正済み（[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携#8.4.2 JS 版の規定]]、2026-09-14）。[[TECSCDE-DT-EL実装]]側の`tecsgen/command-builder.ts`は同じ誤りを引き継いでいる可能性があり、次回着手時に確認・修正が必要。

## Related

- [[TECSCDE-TS モジュールI 二重実装の保留]] — この決定が解消した保留事項
- [[TECSCDE-TS実装]]
- [[TECSCDE-DT-EL実装]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様 第8章]]
- [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|TECSCDE共通ロジック]]
