---
date: 2026-08-16
description: "tecsgen内部仕様書 第2章（ソースファイル構成）— tecsgenのソースツリー全体のファイル一覧と役割。tecs_lang.rbの役割誤認、namespacepath.rbの配置誤り、componentobj/generate.rbの欠落を訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 2 of 12. 2026-08-23、`tecslib/core/` 以下の実ファイル一覧と突き合わせて訂正。

> [!warning] 2026-08-23、ファイル配置と役割記述を3件訂正
> - `tecs_lang.rb` を「字句解析器（Lexer）」としていたのは誤り（5.1 で訂正済みの通り、字句解析は `bnf.y.rb` の `Generator#parse`/`next_token` に内蔵）。`tecs_lang.rb` の役割は `LANG`/文字コード解決のみ
> - `namespacepath.rb` を `syntaxobj/` に分類していたのは誤り。実ファイルは `componentobj/namespacepath.rb`（`syntaxobj/` には存在しない）
> - `componentobj/generate.rb`（74行、`Generate < Node` クラス — `generate` 文/指定子の CDL ノード）が一覧から漏れていた

## 2. ソースファイル構成

```
trunk/tecsgen/
├── tecsgen.rb              # エントリポイント（TECSGEN クラス定義・起動）
├── tecsmerge.rb            # tecsmerge コマンド本体
├── tecsflow.rb             # tecsflow コマンド本体
├── tecscde.rb              # TECSCDE 起動スクリプト
├── tecslib/
│   ├── version.rb          # バージョン定義（$version, $package）
│   ├── core/
│   │   ├── tecs_lang.rb    # LANG/文字コード解決のみ（字句解析には関与しない、5.1）
│   │   ├── bnf.y.rb        # YACC 文法定義（Parser + Generator クラス）
│   │   ├── bnf.tab.rb      # racc 生成パーサテーブル（同梱済み）
│   │   ├── C_parser.y.rb   # C 言語パーサ文法定義（import_C 用）
│   │   ├── C_parser.tab.rb # C パーサテーブル（同梱済み）
│   │   ├── tecsgen.rb      # TECSGEN クラス（パス管理・処理制御）
│   │   ├── generate.rb     # コード生成（最大ファイル、5400行）
│   │   ├── optimize.rb     # 最適化処理
│   │   ├── plugin.rb       # Plugin 基底クラス
│   │   ├── pluginModule.rb # PluginModule モジュール（ポストコード生成）
│   │   ├── messages.rb     # ローカライズ済みメッセージ定義
│   │   ├── types.rb        # 型システム（CDL 型クラス群）
│   │   ├── ctypes.rb       # CType モジュール（C 型指定子のマージ、import_C 用）
│   │   ├── value.rb        # 値クラス群
│   │   ├── expression.rb   # 式クラス群（42KB）
│   │   ├── location.rb     # ソースコード位置（locale）管理
│   │   ├── gen_xml.rb      # XML 出力（tecsflow 用）
│   │   ├── tecsinfo.rb     # TECSInfo 実行時情報（30KB）
│   │   ├── tool_info.rb    # TOOL_INFO 機能
│   │   ├── unjoin_plugin.rb# unjoin プラグイン
│   │   ├── syntaxobj.rb    # syntaxobj/ ディレクトリのロード
│   │   ├── componentobj.rb # componentobj/ ディレクトリのロード
│   │   ├── syntaxobj/      # 構文オブジェクト（CDL パースツリーノード）
│   │   │   ├── node.rb         # Node 基底クラス（locale 管理・エラー出力）
│   │   │   ├── decl.rb         # 型・属性・変数宣言
│   │   │   ├── funchead.rb     # 関数ヘッダ（シグニチャ関数）
│   │   │   ├── paramdecl.rb    # パラメータ宣言
│   │   │   ├── paramlist.rb    # パラメータリスト
│   │   │   ├── typedef.rb      # typedef 宣言
│   │   │   ├── namedlist.rb    # 名前→オブジェクト マップ（NamedList）
│   │   │   ├── cdlinitializer.rb # CDL 初期化子
│   │   │   └── cdlstring.rb    # CDL 文字列
│   │   └── componentobj/   # コンポーネントモデルオブジェクト
│   │       ├── namespace.rb    # Namespace（名前空間）
│   │       ├── namespacepath.rb # 名前空間パス
│   │       ├── region.rb       # Region（リンクルート・ドメイン）
│   │       ├── signature.rb    # Signature（シグニチャ）
│   │       ├── celltype.rb     # Celltype（セルタイプ）
│   │       ├── compositecelltype.rb # CompositeCelltype（複合セルタイプ）
│   │       ├── compositecelltypejoin.rb # 複合セルタイプの結合処理
│   │       ├── cell.rb         # Cell（セルインスタンス、1930行）
│   │       ├── port.rb         # Port（呼び口・受け口）
│   │       ├── join.rb         # Join（結合記述、1363行）
│   │       ├── reversejoin.rb  # ReverseJoin（逆 require 結合）
│   │       ├── factory.rb      # Factory（ファクトリ記述）
│   │       ├── generate.rb     # Generate（generate 文/指定子ノード、74行。core/generate.rbとは別物）
│   │       ├── import.rb       # Import ディレクティブ処理
│   │       ├── import_c.rb     # import_C ディレクティブ処理（C ヘッダ解析）
│   │       ├── importable.rb   # Importable モジュール
│   │       ├── domaintype.rb   # DomainType（ドメイン）
│   │       ├── classtype.rb    # ClassType（クラス）
│   │       └── celltypeModule.rb # CelltypeModule モジュール
│   └── plugin/             # 標準付属プラグイン群（79 ファイル、r3301時点）
```

---

