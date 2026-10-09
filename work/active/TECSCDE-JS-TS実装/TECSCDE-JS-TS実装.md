---
date: 2026-08-30
description: TECSCDE（JS版）TypeScript実装の進捗ノート — 全9モジュール（A〜I: ファイルI/O・CDLパーサ/シリアライザ・モデル・編集コマンド/Undo-Redo・SVG描画・表示制御・UIシェル・診断/整合性チェック・tecsgen連携）およびdependency-cruiser境界強制まで全実装完了、全26テストスイート105テストpass、checkスクリプト（build+test+depcruise）検証完了
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - 1｜みかんのうえ
---

# TECSCDE-JS-TS実装

## Context
- 対象ローカルリポジトリ: `E:\Ccur\typescript\TECSCDE-JS`（2026-09-14以降のいずれかの時点で`TECSCDE`から改称されているのを2026-09-15確認。Gitの追跡・コミット履歴は連続している）
- 対象リモートリポジトリ: "https://github.com/ykominami/tecscde-js.git"
- [`Racc`](https://docs.ruby-lang.org/en/3.1/Racc.html) is a LALR(1) parser generator. It is written in Ruby itself, and generates Ruby programs
	- https://docs.ruby-lang.org/en/3.1/Racc.html
- Tree-sitter is a parser generator tool and an incremental parsing library
	- https://tree-sitter.github.io/tree-sitter/index.html
## Notes

### UI実装の参考: Konva.js（HTML5 Canvas 2Dライブラリ）

2026-08-30 の UI 実装調査メモから統合（元: `TECSCDE-JS-TS実装 UI実装.md`）。現行は SVG 描画を採用したため未使用だが、記録として残す。

- [Konva\.js入門｜Canvasを使った高度なUI実装方法を徹底解説 – モナカプレス](https://press.monaca.io/atsushi/35624)
- [Konva \- JavaScript Canvas 2d Library](https://konvajs.org/)
- [GitHub \- konvajs/konva](https://github.com/konvajs/konva)

## 実装進捗

日次の実装進捗記録は[[work/active/TECSCDE-JS-TS実装/TECSCDE-JS-TS実装 — 実装進捗ログ|実装進捗ログ]]に分離（2026-09-14、25KB閾値）。全9モジュール（A〜I）・dependency-cruiser境界強制・tree-sitter移行を2026-08-30〜09-14の日付順に記録。

## Action Items
- [x] 5.5節の未実装コマンド`MoveJoinBarCommand`を実装する（2026-08-30時点で既に実装済みと判明、2026-09-01にコミット`8b86f8a`）
- [x] `ChangePortEdgeCommand` / `MovePortCommand`（portOps.ts）をUIに配線する（2026-09-13モジュールD実装完了）
- [x] OSクリップボード連携（CDL断片シリアライズ・パース）を実装する（2026-09-13モジュールD実装完了）
- [x] 複数セル整列（Align）およびプロパティパネル一括編集を実装する（2026-09-13モジュールD実装完了）
- [x] Undo/Redo設計の変更（invert()方式→replay方式）をTECSCDE内部仕様5章に反映する（コミット`800d601`で反映済み、[[work/active/tecs/TECSCDE Undo-Redo設計決定|Decision Record]]も追加、2026-08-31）
- [x] `E:\Ccur\typescript\TECSCDE` のgit初期化・初回コミットの要否を判断する（既に初期化・初回コミット`3f7ecd9`済みと判明、2026-09-01）

## Related
- [[TECSCDE内部仕様]] — 本実装が準拠する内部仕様
- [[TECSCDE-実装アーキテクチャ案]] — 本実装が踏まえたパッケージ構成・型設計・テスト戦略案
- [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|TECSCDE共通ロジック]] — 本実装と[[TECSCDE-DT-EL実装]]が共有するロジックの棚卸しと共有方法の未決事項
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装
