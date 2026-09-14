---
date: 2026-09-05
description: TECSCDE デスクトップアプリ外部仕様書（言語非依存、Electron/Tauri両対応）。TECSCDE外部仕様（ブラウザ単体版）を踏まえ、両フレームワークで実現可能な機能を積極採用。全11章執筆完了。
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---
（生成req - `work/active/TECSCDE外部仕様`をもとに、言語非依存のデスクトップアプリの外部仕様として `work/active/TECSCDE-DT外部仕様`を作って
ただし、実装方法としてはTypeScriptによるElectron、RustによるTauriを想定しているので、どちらでも実現できる仕様は、積極的に採用して。）
# TECSCDE-DT 外部仕様（デスクトップアプリ版）

> [!info] 文書状態
> **全11章執筆完了（2026-09-05）** — [[TECSCDE外部仕様]]（JS版・ブラウザ単体・フレームワーク非依存、全11章）を踏まえ、**デスクトップアプリとしての外部仕様**を新規に起こした。想定する実装方法は **TypeScriptによるElectron** と **RustによるTauri** の2系統であり、本書は**どちらの実装方法でも同一の挙動になること**を要件とする（言語非依存）。
>
> **採用方針**: Electron・Tauriの**両方で実現可能な機能は積極的に採用する**（ユーザ指示）。この方針により、[[TECSCDE外部仕様]]がブラウザのサンドボックス制約から「範囲外」「将来拡張」としていた次の4点を、本書では正式に採用する。
>
> | 機能 | [[TECSCDE外部仕様]]（ブラウザ版） | 本書（デスクトップ版） |
> |---|---|---|
> | ファイルシステムアクセス | File System Access API または download フォールバック | **OSのファイルシステムへ直接読み書き**（Electron: Node.js `fs`、Tauri: Rustの`fs`）。真の上書き保存・ファイル関連付けが可能 |
> | tecsgenの実行 | コマンド文字列の組み立て・提示・コピーのみ（8.4.2「実行はしない」） | **サブプロセスとして直接実行**（Electron: `child_process`、Tauri: `std::process::Command`）。標準出力を解析し9章の警告として提示 |
> | `import_C`のCプリプロセッサ実行 | 非実行（プリプロセッサを起動せず`typedef`/`struct`のみ抽出。2026-09-13改訂） | **利用者の環境にCプリプロセッサがあれば実行可能**（tecsgen実行と同じサブプロセス機構）。無ければブラウザ版と同じ抽出へフォールバック |
> | `import`/`import_C`の参照先追跡 | 追跡しない（ローカルファイルへ任意にアクセスできないため） | **自動追跡する**（`import_path`・`base_dir`を解決） |
> | OSクリップボード連携 | 範囲外（将来拡張として保留） | **採用する**。セル・結合をCDL断片としてOSクリップボードへ書き出し、アプリ間・ウィンドウ間で貼り付け可能にする |
>
> 逆に、**両フレームワークで共通に実現できない、またはOSごとに挙動が割れる機能は採用しない**——例えばTauriのWebView実装はOSごとに異なる（Windows: WebView2、macOS: WKWebView、Linux: WebKitGTK）ため、WebView依存の挙動に頼る規定は置かない。UI描画自体は既存のSVG/DOM方式（Electron・Tauriいずれもフロントエンドは標準のHTML/SVG/JSで構成可能）を踏襲し、特定のUIフレームワーク（React等）には依存しない——この点は[[TECSCDE外部仕様]]の「フレームワーク非依存」の精神を引き継ぐ。
>
> **対応する実装は存在しない。** 本書は設計提案であり、[[TECSCDE-JS-TS実装]]（ブラウザ版の実装）とは別系統。

## 目次

1. [[TECSCDE-DT外部仕様 - 01 概要]]
2. [[TECSCDE-DT外部仕様 - 02 動作環境]] — 最大の差分。デスクトップ実行形態・Electron/Tauri両対応の要件
3. [[TECSCDE-DT外部仕様 - 03 画面構成]] — ネイティブメニュー・終了操作を追加、他は踏襲
4. [[TECSCDE-DT外部仕様 - 04 コンポーネント図の表現]] — [[TECSCDE外部仕様]]と同一（変更なし）
5. [[TECSCDE-DT外部仕様 - 05 ファイル操作]] — 大きな差分。ネイティブファイルI/O、真の上書き保存、解析系の入力制約
6. [[TECSCDE-DT外部仕様 - 06 編集操作]]（[[TECSCDE-DT外部仕様 - 06A 編集操作（前半）|前半]]・[[TECSCDE-DT外部仕様 - 06B 編集操作（後半）|後半]]） — 後半のOSクリップボード連携のみ差分、他は踏襲
7. [[TECSCDE-DT外部仕様 - 07 表示機能]] — [[TECSCDE外部仕様]]と同一（変更なし）
8. [[TECSCDE-DT外部仕様 - 08 CDL 連携]] — 最大の差分。tecsgen直接実行、import自動追跡・`import_C`の2経路
9. [[TECSCDE-DT外部仕様 - 09 エラーと警告]] — tecsgen実行結果の取り込み経路を追加、他は踏襲
10. [[TECSCDE-DT外部仕様 - 10 制約・制限]] — 大きな差分。ブラウザ由来の制約の大半が解消
11. [[TECSCDE-DT外部仕様 - 11 用語集]] — 新規4用語を追加

（章番号は[[TECSCDE外部仕様]]と同一の11章構成。第6章は前半・後半に分割し、目次からは中間ノート経由でリンクする）

## Related

- [[TECSCDE外部仕様]] — 本書の一次情報源（ブラウザ単体版、行動仕様の大半を共有）
- [[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|TECSCDE外部仕様 tree-sitter反映案]] — tree-sitterパーサ採用に伴う外部仕様・DT外部仕様の改訂経緯
- [[TECSCDE内部仕様]] / [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — ブラウザ版の内部設計（関数ベース／クラスベース）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]] — 本書をElectron・クラスベースで実装するための内部仕様（2026-09-05着手）
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]] — 本書をTauri・Rustで実装するための内部仕様（2026-09-05着手）
- [[TECSCDE-JS-TS実装]] — ブラウザ版の実際の実装
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装（本書はデスクトップ版という別ラインの検討であり、現時点では最優先ラインそのものではない）
