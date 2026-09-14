---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第1章（概要）— Rust/Tauri固有化の位置づけ、struct/impl/traitへの設計転換、想定するプロセスモデル、対象読者。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 1 of 11（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]と同一の11章構成の姉妹文書）。

## 1. 概要

### 1.1 目的

本書は、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（TECSCDEのデスクトップアプリ版外部仕様、Electron/Tauri言語非依存）を実現するための内部設計のうち、**Rustで、かつTauriに固有化した設計**を提案するものである。

### 1.2 「クラスベース」からの転換

[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]はTypeScriptの`class`を用いて、不変条件の一部（呼び口=結合1本まで等）を型階層で表現する設計を提案していた。**Rustには`class`という概念が存在しない。** 本書はこの設計思想を、Rustのイディオムである`struct`（データ）＋`impl`（メソッド）＋`trait`（多相性が必要な箇所のみ）に翻訳する。

| TypeScript版の概念 | Rust版での対応 |
|---|---|
| `class Cell { ... }`（フィールド＋メソッド） | `struct Cell { ... }` ＋ `impl Cell { ... }` |
| `abstract class Port` → `CPort extends Port` / `EPort extends Port` | 継承ではなく、独立した`struct CPort` / `struct EPort`（Rustに継承はなく、コンポジションが標準のため、この点はむしろ自然に表現できる） |
| `abstract class Command { apply(doc): doc }` | `trait Command { fn apply(&self, doc: TecscdeDocument) -> TecscdeDocument; }`。`History`は`Vec<Box<dyn Command>>`でトレイトオブジェクトとして保持する |
| `private`コンストラクタ＋`static create()`ファクトリ | Rustのモジュールプライバシー（`pub(crate)`なコンストラクタ関数）＋関連関数`Cell::create(...)` |
| 新しいインスタンスを返すメソッド（イミュータブル方針） | Rustの所有権システムが**自然に**同じ結果をもたらす——`fn move_to(self, x: f64, y: f64) -> Cell { Cell { x: align_round(x), ..self } }`という構造体更新構文（struct update syntax）は、`self`を消費（move）して新しい値を返す。これはTypeScript版が`readonly`修飾と明示的な新規オブジェクト生成で意図的に実現していたものを、Rustでは所有権の規則が言語レベルで後押しする |

詳細は第3・4章で規定する。

### 1.3 プロセスモデル: Tauriの2層構造

Electron（[[TECSCDE-DT-EL内部仕様]]第1章1.3節）はmain・preload・rendererの3層に分かれていたが、**Tauriはbackend（Rustネイティブ、Tauriの用語では「core」）とfrontend（WebView内で動くコード）の2層のみ**である。

| 層 | 特徴 | 本書での役割 |
|---|---|---|
| **backend**（Rustネイティブ） | OSへのフルアクセス。`#[tauri::command]`属性でフロントエンドから呼び出せる関数を定義する | ファイルシステム・サブプロセス起動・クリップボードなど、OSリソースへの唯一のアクセス点 |
| **frontend**（Rust＋WASM、OSネイティブWebView上で動作） | 既定でOS APIへのアクセスを持たない。`invoke()`経由でのみbackendの`#[tauri::command]`を呼べる | UI・モデル・コマンド・描画の実行コンテキスト |

Electronのpreload層（`contextBridge`で個別にAPIを橋渡しする層）に相当するものはない。**全てのネイティブ操作は`invoke::<T>(command_name, args)`という単一の経路を通る**——[[TECSCDE-DT-EL内部仕様]]がクリップボードだけpreloadから直接ブリッジできたのとは異なり、本書ではクリップボード操作も他のTauri commandと同じ経路で呼ぶ（第2章参照）。

### 1.4 対象読者

- TECSCDEをTauri・Rustで実装することを検討する開発者
- [[TECSCDE-DT-EL内部仕様]]（Electron・TypeScript版）と比較し、言語・プロセスモデルの違いによる設計差分を把握したい設計者

### 1.5 関連文書

| 文書 | 内容 |
|------|------|
| [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様\|TECSCDE-DT外部仕様]] | 本書が実装する外部仕様（デスクトップ版） |
| [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様\|TECSCDE-TS内部仕様]] | 本書が翻訳するクラス設計の一次情報源（ブラウザ版、TypeScript） |
| [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様\|TECSCDE-DT-EL内部仕様]] | 姉妹文書（Electron・TypeScript版）。プロセス境界の設計思想を対比する際の参照先 |

---
