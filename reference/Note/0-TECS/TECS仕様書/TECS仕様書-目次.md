---
date: 2026-06-07
description: "TECS（TOPPERS Embedded Component System）仕様書の目次 — 第0章 表紙・前文から各章の構成ファイル（Chap0/00-cover.txt 等）までを列挙"
tags:
  - reference
  - tecs
  - index
---

  TECS: TOPPERS Embedded Component System 仕様書 — 目次

  第0章：表紙・前文

  - 表紙 (Chap0/00-cover.txt)
  - 裏表紙 (Chap0/01-incover.txt)
  - 序 (Chap0/10-preface.txt) — 著作権・免責規定・ステータス

  ---
  第1章：概要

  - TECS 仕様の概要 (Chap1/10-1st.txt) — 名前の由来・開発母体・目標・方針・開発物一覧

  ---
  第2章：TECSコンポーネントモデル

  - はじめに (Chap2/00-readme.txt)
  - 構成要素 (Chap2/10-elements.txt)
  - 用語（呼び元と呼び先） (Chap2/11-term.txt)
  - コンポーネント図 (Chap2/20-figure.txt)
  - リモート呼出し（分散） (Chap2/30-rpc.txt)

  ---
  第3章：コンポーネント記述言語（CDL）

  導入

  - はじめに (Chap3/00-readme.txt) — 位置づけ・制限・ジェネレータ実装との相違
  - 定義 (Chap3/01-total.txt)
  - 字句構造 (Chap3/02-lex.txt)
  - 名前空間 (Chap3/03-name-space.txt)

  コンポーネント記述

  - コンポーネント記述 (Chap3/11-component-description.txt)
    - import 文 (Chap3/11.1-import.txt)
    - import_C 文 (Chap3/11.2-import_C.txt)
    - 文指定子 (Chap3/11.3-statement-specifier.txt)
  - 型定義 (Chap3/12-typedef.txt)
  - ネームスペース (Chap3/13-namespace.txt)

  シグニチャ

  - シグニチャ (Chap3/14-signature.txt)

  セルタイプ

  - セルタイプ (Chap3/15-celltype.txt)
    - 呼び口・受け口 (Chap3/15.1-port.txt)
    - 属性 (Chap3/15.2-attribute.txt)
    - 内部変数 (Chap3/15.3-var.txt)
    - リクワイア (Chap3/15.4-require.txt)
    - ファクトリ (Chap3/15.5-factory.txt)

  セル

  - セル生成 (Chap3/16-cell.txt)
    - 結合 (Chap3/16.1-join.txt)

  複合セルタイプ

  - 複合セルタイプ (Chap3/17-composite.txt)
    - 複合セルタイプ属性 (Chap3/17.1-composite-attribute.txt)
    - 内部セル (Chap3/17.2-internal-cell.txt)
    - 外部結合 (Chap3/17.3-external-join.txt)

  リージョン

  - リージョン (Chap3/18-region.txt)

  C言語要素

  - 宣言 (Chap3/21-declaration.txt)
    - 初期化子 (Chap3/21.1-initializer.txt)
  - 型 (Chap3/22-type.txt)
    - 構造体 (Chap3/22.1-struct.txt)
    - ポインタ (Chap3/22.2-pointer.txt)
    - 列挙 (Chap3/22.3-enum.txt)
    - 宣言子 (Chap3/22.4-declarator.txt)
    - パラメータ (Chap3/22.5-parameter.txt)
  - 式 (Chap3/23-expression.txt)

  付録

  - 補則 (Chap3/30-append.txt)
  - 名前付け規則 (Chap3/31-name-conv.txt)

  ---
  第4章：アプリケーション実装モデル

  概要

  - アプリケーションの実装 (Chap4/01-implementation.txt) — ソースコード互換性・バイナリ互換性
  - ファイル (Chap4/02-files.txt)
  - 定義（IDX） (Chap4/05-definition.txt)

  セルタイプコード

  - セルタイプコード (Chap4/10-celltype-code.txt)
  - マクロ (Chap4/11-macros.txt)
  - FOREACH_CELL マクロ (Chap4/12-foreach.txt)
  - 初期化コード (Chap4/13-initialize-code.txt)

  インポート・アロケータ

  - プリプロセッサコマンド（import） (Chap4/20-import.txt)
  - アロケータコード (Chap4/21-allocator.txt)

  ビルド・データ構造

  - Makefile (Chap4/30-makefile.txt)
  - データ構造 (Chap4/40-data-struct.txt)
  - ROM/RAM 配置 (Chap4/41-romram.txt)
  - 最適化 (Chap4/42-optimize.txt)

  付録

  - インタフェースジェネレータ（tecsgen） (Chap4/A1-tecsgen.txt)
  - verbose メッセージ (Chap4/A2-verbose.txt)

  ---
  Sources used:
  - TECS: TOPPERS Embedded Component System 仕様書
  (raw/articles/2026-05-17-tecs-toppers-embedded-component-system-spec-index.md) (confidence: high) —
  全章ファイル構成の完全リスト

  Knowledge gaps:
  - 第1章の「目標・方針」セクションは仕様書内で「未記述」のまま
  - 第0章の著作権ステータスは「未定」。本仕様書は TOPPERS プロジェクト会員限定で公開されたもの
