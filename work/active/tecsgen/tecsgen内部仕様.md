---
date: 2026-05-19
description: "tecsgen（TECS コンポーネント記述コンパイラ）内部仕様書。処理フロー・クラス設計・意味解析・最適化・コード生成の実装を対象とする。全12章、章別ノートに分割済み。2026-08-23、1-3章の再照合を実施し全12章の個別検証パスが完了。"
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

# tecsgen 内部仕様

> [!info] 文書状態
> **ドラフト（2026-05-19 作成、2026-08-15 加筆）** — ソースコード（実体は `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen`、v1.9.0・作成時から変更なしを確認）を直接読んで作成。2026-08-15、tecsgen プラグイン仕様書シリーズ（[[work/active/tecsgen-plugins/PluginCoverageAudit|カバレッジ監査]]完了）で得た知見をもとに実ファイル一覧と全2. 章を突き合わせ、`ctypes.rb`（未記載だった `CType` モジュール）と `MultiPlugin` ディスパッチ機構（9.5・9.6節、`pluginModule.rb` の `load_plugin` を直接読んで確認）を追加。同日、7. 最適化章を `optimize.rb`・`componentobj/port.rb`・`componentobj/celltype.rb` と突き合わせて検証し、`@b_cp_optimized` の所属誤り（Port ではなく Celltype）を修正、CALL/ENTRY 両ポートでの最適化フラグ初期値が逆転している点を追記。**2026-08-21、プラグイン境界の知見をさらに統合**: 4. クラス設計のクラス階層図に `MultiPlugin` が欠落していた点を修正——`MultiPlugin < Node` であり `Plugin` の子ではないため（9.5 で既述）、素直に階層図へ書き足すと誤解を招く箇所だった。9. プラグイン機構に「9.7 既知の問題」を新設し、プラグイン仕様書調査で見つかった3件のリスク（`TransparentRPCSignaturePlugin` 参照切れ、FMP の RPC 死コード、CppIfGen の二重無効化コード）を記録。いずれも実行時の再現確認はしていない。**2026-08-22、5. 字句解析・構文解析を `bnf.y.rb`・`C_parser.y.rb`・`componentobj/import_c.rb`・`tecs_lang.rb` の直接読解で全面検証・訂正**：字句解析は独立ファイルではなく `bnf.y.rb` の `Generator#parse`/`next_token` に内蔵されていること、`tecs_lang.rb` は言語・文字コード解決のみで字句解析に関与しないこと、C 言語パーサは `Import_C`（`componentobj/import_c.rb`）が `cpp` 実行とテンポラリファイル生成を担い `C_parser` は typedef/struct 宣言のみを状態マシンで抽出することを反映。**続けて 6. 意味解析も全面検証・訂正**：`set_require_join` は「未結合エラー検出」ではなく CDL の `require` 節が宣言する結合を singleton セルへ自動生成する処理であり、非optional呼び口の未結合検出（S1042/S1043）は実際には `check_join` が担うことが判明。`tecsgen.rb` の `syntax_analisys`/`semantics_analisys_1`/`semantics_analisys_2` という3段階の呼び出し順序も追記した。**続けて 8. コード生成の一部を検証・訂正**：`CFile` はテンポラリ書き出しではなく文字コード変換専用の `File` ラッパーであり、`.tmp`→比較→リネームの仕組みは `AppFile` 側にあること、テンプレートファイルの生成可否は `-f`（`$force_overwrite`）ではなく `--generate-all-template`/`--generate-no-template` という別オプションで決まること、`INITIALIZE_TECS()` はセルタイプ別の `_tecsgen.h` ではなく単一の `global_tecsgen.h` にのみ定義されることを修正（8.1/8.3/8.5 は未再検証のまま）。**続けて 10. ファイル入出力も全面検証・訂正**：`Import.new` は「キューに積む」のではなくコンストラクタ内で即座に同期パースすること、ファイル探索が `$import_path` 単純走査ではなく過去の import 基点ディレクトリを併用する二段探索であること、`TECSIO` が独立ファイルではなく `bnf.y.rb` 内蔵であることを修正。**続けて 11. エラー・警告処理も全面検証・訂正**：構文解析・意味解析でエラーがあればコード生成フェーズへ進入自体しないゲート（`optimize_and_generate` 386-390行目）、`finalize` がエラー件数0のときのみ `AppFile.update` を呼ぶ最終コミット抑制、G/P/W の3種のみとしていたエラーコードのプレフィックスを実測に基づき10種以上（S/G/W/T/E/I/P/B/H/C/V）へ訂正。**最後に 12. グローバル変数一覧を検証・訂正**：どこにも定義されていない架空の変数 `$KCODE_CDL`/`$KCODE_TECSGEN` を削除し、実在する `$CHARSET_FILE`/`$KCONV_TECSGEN` 等へ置き換え、`$force_overwrite` の説明を8章の訂正に合わせて修正、表になかった `$generate_all_template`/`$generate_no_template` を追加。これで4-12章（4・7・9は先行セッションで、5・6・8・10-12は本セッションで）の個別検証パスが一巡した。**2026-08-23、残っていた1-3章を `tecsgen.rb`・`tecslib/core/tecsgen.rb`・`tecslib/core/`/`componentobj/`/`syntaxobj/` の実ファイル一覧の直接照合で再検証**：2章はファイル配置3件を訂正（`tecs_lang.rb` の「字句解析器」という誤記述、`namespacepath.rb` の配置誤り〔`syntaxobj/`ではなく`componentobj/`〕、一覧から漏れていた`componentobj/generate.rb`の追加）。3章は処理フロー図の実質的な誤りを訂正：`set_require_join` を `semantics_analisys_2` に置いていたのは誤りで実際は `semantics_analisys_1` の最終ステップであること（役割も6章で訂正済みの「require節の自動結合生成」に合わせて修正）、`check_join` の「シグニチャ一致等」という注記が誤りであること、`optimize_and_generate` 全体が `$unopt` でガードされるとしていたのは誤りで実際は内部の `optimize` 呼び出しのみがガードされること、コード生成後に呼ばれる `root_namespace.generate_post` が欠落していたことを修正。1章（概要）は `tecslib/version.rb` の実測と突き合わせた結果、対象バージョンが1.9.0→1.9.1（トランク先行）とずれていたため訂正。これで全12章の個別検証パスが一巡した。

全12章、[[work/active/tecsgen/tecsgen内部仕様 - 01 概要|章別ノート]]に分割済み（2026-08-16、25KB閾値）。

## 目次

- [[work/active/tecsgen/tecsgen内部仕様 - 01 概要|1. 概要]] — 目的、対象バージョン、関連文書
- [[work/active/tecsgen/tecsgen内部仕様 - 02 ソースファイル構成|2. ソースファイル構成]] — tecsgenのソースツリー全体のファイル一覧と役割
- [[work/active/tecsgen/tecsgen内部仕様 - 03 処理フロー|3. 処理フロー]] — トップレベルフロー、run1（構文解析+意味解析）、run2（最適化+コード生成）
- [[work/active/tecsgen/tecsgen内部仕様 - 04 クラス設計|4. クラス設計]] — クラス階層、Generator・Namespace・Cell・Join・Pluginクラス
- [[work/active/tecsgen/tecsgen内部仕様 - 05 字句解析・構文解析|5. 字句解析・構文解析]] — tecs_lang.rb、bnf.y.rb/bnf.tab.rb、C言語パーサ
- [[work/active/tecsgen/tecsgen内部仕様 - 06 意味解析|6. 意味解析]] — set_definition_join・set_require_join・check_join・ポストコード処理
- [[work/active/tecsgen/tecsgen内部仕様 - 07 最適化|7. 最適化（optimize.rb）]] — 最適化フラグ、optimize_call、optimize_entry
- [[work/active/tecsgen/tecsgen内部仕様 - 08 コード生成|8. コード生成（generate.rb）]] — 生成の起点、ファイル出力制御、`_tecsgen.h`/`_factory.h`/`tecsgen.cfg` の生成
- [[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構|9. プラグイン機構（plugin.rb/pluginModule.rb）]] — プラグインの種類・ロード、PluginModule、MultiPluginディスパッチ機構
- [[work/active/tecsgen/tecsgen内部仕様 - 10 ファイル入出力|10. ファイル入出力]] — Import/import_C、文字コード変換（TECSIO）
- [[work/active/tecsgen/tecsgen内部仕様 - 11 エラー・警告処理|11. エラー・警告処理]] — フロー、エラー番号体系
- [[work/active/tecsgen/tecsgen内部仕様 - 12 グローバル変数一覧|12. グローバル変数一覧]] — 実装全体で使われるグローバル変数の一覧表

## Related

- [[tecsgen外部仕様]] — CLI・入出力・エラー形式（外部から見た仕様）
- [[TECS開発]] — 開発進捗全体
- [[North Star]]
- [[reference/03-Resources/my-topic/CLAUDE|TECS Wiki]] — llm-wiki 知識ベース
- [[perf/competencies/技術文書化|技術文書化]] — 仕様書作成の competency 証拠
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — CDL・tecsgen 設計判断の competency 証拠
