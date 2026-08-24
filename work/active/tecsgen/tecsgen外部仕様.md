---
date: 2026-05-19
description: "tecsgen（TECS コンポーネント記述コンパイラ）外部仕様書の骨子。CDL 入力・生成コード出力・CLI・プラグイン・エラー処理を対象とする。全10章、章別ノートに分割済み。"
project: TECS
quarter: Q2-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
  - index
---

# tecsgen 外部仕様

> [!info] 文書状態
> **ドラフト（2026-05-19）** — 動作環境・メッセージ形式・最適化内容をコードベース調査済み（`trunk/tecsgen/`）。

全10章、[[work/active/tecsgen/tecsgen外部仕様 - 01 概要|章別ノート]]に分割済み（2026-08-16、25KB閾値）。

## 目次

- [[work/active/tecsgen/tecsgen外部仕様 - 01 概要|1. 概要]] — 目的、ビルドシステムにおける位置付け、対象読者、関連文書
- [[work/active/tecsgen/tecsgen外部仕様 - 02 動作環境|2. 動作環境]] — tecsgenの実行環境
- [[work/active/tecsgen/tecsgen外部仕様 - 03 入力|3. 入力]] — CDLファイル、Cプリプロセッサ連携
- [[work/active/tecsgen/tecsgen外部仕様 - 04 出力|4. 出力]] — 生成ファイル一覧、セルタイプヘッダ（`_tecsgen.h`）、`INITIALIZE_TECS()` マクロ、コード生成の最適化
- [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|5. コマンドラインインターフェース]] — 書式、オプション一覧、環境変数、終了ステータス
- [[work/active/tecsgen/tecsgen外部仕様 - 06 プラグインシステム|6. プラグインシステム]] — 概要、プラグイン呼び出し規約、標準付属プラグイン、プラグイン引数の文法
- [[work/active/tecsgen/tecsgen外部仕様 - 07 エラーと警告|7. エラーと警告]] — メッセージ形式、主要エラーカテゴリ、警告カテゴリ
- [[work/active/tecsgen/tecsgen外部仕様 - 08 制約・制限|8. 制約・制限]] — CDLに関する制約、生成コードに関する制約、既知の制限
- [[work/active/tecsgen/tecsgen外部仕様 - 09 使用例|9. 使用例]] — 最小構成、ディレクトリ指定、カーネルヘッダ、ドライラン、典型的なビルドフロー
- [[work/active/tecsgen/tecsgen外部仕様 - 10 用語集|10. 用語集]] — CDL・セル・セルタイプ・呼び口・受け口ほかCDL言語一般の用語集

## Related

- [[TECS開発]] — 開発進捗全体
- [[North Star]]
- [[reference/03-Resources/my-topic/CLAUDE|TECS Wiki]] — llm-wiki 知識ベース（tecsgen-commands, cdl-language, implementation-patterns 等）
- [[perf/competencies/技術文書化|技術文書化]] — 仕様書作成の competency 証拠
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — CDL・tecsgen 設計判断の competency 証拠
