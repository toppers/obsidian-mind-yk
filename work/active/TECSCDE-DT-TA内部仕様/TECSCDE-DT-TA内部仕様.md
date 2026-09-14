---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書。TECSCDE-DT外部仕様（デスクトップ版）を、Rust（Tauri）で実装するための内部仕様。struct/impl/traitによるイディオマティックなRust設計とbackend/frontendの2層アーキテクチャが中心。全11章執筆完了。"
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

# TECSCDE-DT-TA 内部仕様（Tauri・Rust）

> [!info] 文書状態
> **全11章執筆完了（2026-09-05）** — [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（デスクトップ版、Electron/Tauri言語非依存）を、**Rustで、Tauriに固有化して**実装するための内部仕様として起こした。姉妹文書[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]（Electron・TypeScriptクラスベース）と対をなすが、**単純な言語の置き換えではない**——次の2点で設計そのものが変わる。
>
> | 観点 | [[TECSCDE-DT-EL内部仕様]]（Electron/TS） | 本書（Tauri/Rust） |
> |---|---|---|
> | クラス設計の可否 | TypeScriptは`class`を持つため、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様\|TECSCDE-TS内部仕様]]のクラス設計をそのまま踏襲できた | **Rustに`class`は存在しない**。`struct`＋`impl`＋`trait`によるイディオマティックなRust設計に置き換える（第3・4章） |
> | プロセス境界 | main（Node.js）／preload（ブリッジ）／renderer（Chromium）の**3層** | backend（Rustネイティブ）／frontend（Rust+WASM）の**2層のみ**。Tauriには「preload」に相当する層がなく、クリップボードを含む全てのネイティブ操作が`invoke`という単一の経路に統一される（第2章） |
>
> **フロントエンドもRustで統一する。** TauriはHTML/JSフロントエンド＋Rustバックエンドという構成も一般的だが、ユーザ指示（「Rustで実装する場合」）に従い、**UI層（DOM/SVG操作を含む）もRust（`wasm32-unknown-unknown`ターゲット、`web-sys`/`wasm-bindgen`によるWeb API直接バインディング）で実装する**構成を採用する。大規模なリアクティブUIフレームワーク（Leptos・Yew等）は導入せず、[[TECSCDE-TS内部仕様]]の`SvgRenderer`が採る「要素の対応表を持ち属性のみ更新する」という命令的な描画方式をそのままRustに移植する——これは[[TECSCDE外部仕様]]が一貫して求めてきた「フレームワーク非依存」の精神をRust側でも保つ選択である(unverified／設計判断であり実装時に再検討の余地がある)。
>
> **対応する実装は未着手**（2026-09-07に`E:\Ccur\typescript\TECSCDE-DT-TA`をリポジトリ初期化のみ実施。進捗は[[TECSCDE-DT-TA実装]]）。

## 目次

1. [[TECSCDE-DT-TA内部仕様 - 01 概要]]
2. [[TECSCDE-DT-TA内部仕様 - 02 モジュール構成とプロセス境界]] — 本書の中心。backend/frontendへのモジュール配置とinvoke契約
3. [[TECSCDE-DT-TA内部仕様 - 03 モデル設計]] — struct/implによるRust設計（[[TECSCDE-TS内部仕様]]のクラス設計をRustへ移植）
4. [[TECSCDE-DT-TA内部仕様 - 04 編集コマンドとUndo-Redo設計]] — `Command`トレイト＋`History`構造体
5. [[TECSCDE-DT-TA内部仕様 - 05 描画・インタラクション設計]] — `web-sys`によるSVG直接操作
6. [[TECSCDE-DT-TA内部仕様 - 06 表示制御設計]] — `ViewState`構造体
7. [[TECSCDE-DT-TA内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-TA内部仕様 - 07 ファイルI/O設計]] — Tauri commandによるネイティブファイルI/O
8. [[TECSCDE-DT-TA内部仕様 - 08 整合性チェックとメッセージ設計]] — `Diagnostic`/`DiagnosticsCollector`
9. [[TECSCDE-DT-TA内部仕様 - 09 tecsgen連携設計]] — Tauri commandによるサブプロセス直接実行
10. [[TECSCDE-DT-TA内部仕様 - 10 モジュール間インタフェース一覧]] — Cargoワークスペース構成とinvokeコマンド一覧
11. [[TECSCDE-DT-TA内部仕様 - 11 未決事項と実装単位案]]

## Related

- [[TECSCDE-DT-TA実装]] — 本書に対応する実装（2026-09-07リポジトリ初期化）
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]] — 本書が実装する外部仕様（デスクトップ版）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]] — 姉妹文書（Electron・TypeScriptクラスベース）。同じ外部仕様・同じモジュール分割から出発するが、言語・プロセスモデルの違いにより設計が分岐する
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — クラス設計の一次情報源（ブラウザ版、TypeScript）。本書はこれをRustへ移植する
- [[TECSCDE内部仕様]] — さらに元となる関数/インタフェースベースの内部仕様（ブラウザ版）
- [[TECSCDE-JS-TS実装]] — ブラウザ版の実際の実装（本書はこれとは別系統）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装（本書はデスクトップ・Tauri版という別ラインの検討）
