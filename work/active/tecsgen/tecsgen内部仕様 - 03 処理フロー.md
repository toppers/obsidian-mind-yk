---
date: 2026-08-16
description: "tecsgen内部仕様書 第3章（処理フロー）— トップレベルフロー、run1（構文解析+意味解析）、run2（最適化+コード生成）。set_require_joinの所属フェーズ・役割誤認、check_joinのシグニチャ一致誤記、optimize_and_generateの条件付け誤りとgenerate_post欠落を訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 3 of 12. 2026-08-23、`tecslib/core/tecsgen.rb` の `syntax_analisys`/`semantics_analisys_1`/`semantics_analisys_2`/`optimize_and_generate` を直接読んで全面検証・訂正。

> [!warning] 2026-08-23、run1/run2 のステップ所属と条件を訂正
> - `set_require_join` は旧版で `semantics_analisys_2` に置かれていたが誤り。実際は `semantics_analisys_1` の最終ステップ（`tecsgen.rb` 285行目）。役割も「必須呼び口の結合確認」ではなく、6.2 の通り `require` 節で宣言された呼び口へ singleton セル等への `Join` を自動生成する処理で、エラー検出ではない
> - `check_join` の「シグニチャ一致等」という注記は誤り。6.3 で確定した通り主眼は未結合・配列要素数・`size_is`・到達可能リージョンの4点で、シグニチャ一致は結合時など別箇所で行われる
> - `optimize_and_generate` 全体が `$unopt == false` の場合にのみ実行されるとしていたのは誤り。`optimize_and_generate` 自体は無条件に呼ばれ、内部の `root_namespace.optimize` 呼び出しのみが `$unopt` でガードされる（`set_cell_id_and_domain`/`optimize` はさらに `Generator.get_n_error == 0` の場合のみ）
> - コード生成後に呼ばれる `root_namespace.generate_post` が旧版から欠落していたため追加
> - 3.2 の「Lexer(tecs_lang.rb)」という記述は 5.1 で訂正済みの通り誤り（字句解析は `bnf.y.rb` 内蔵）

## 3. 処理フロー

### 3.1 トップレベルフロー

```
tecsgen.rb (エントリポイント)
  │
  ├─ TECSGEN.init
  │    ├─ initialize_global_var   # グローバル変数初期化
  │    ├─ analyze_option          # コマンドラインオプション解析 (optparse)
  │    ├─ load_modules            # tecslib/* の require
  │    └─ setup                   # パス調整・gen ディレクトリ作成
  │
  ├─ tecsgen = TECSGEN.new
  ├─ tecsgen.run1                 # 構文解析 + 意味解析フェーズ1・2
  ├─ tecsgen.run2                 # 最適化 + コード生成フェーズ
  └─ tecsgen.dump_tecsgen_rbdmp   # 内部モデルダンプ（tecsgen.rbdmp）
```

### 3.2 run1（構文解析 + 意味解析）

```
run1
  ├─ syntax_analisys(ARGV)
  │    ├─ @root_namespace = Region.new("::")
  │    ├─ ARGV.each { Import.new(f) }   # 全 CDL ファイルを順次パース
  │    │    ├─ Lexer → bnf.y.rb の Generator#parse/next_token に内蔵（5.1。独立ファイルなし）
  │    │    └─ Parser(bnf.tab.rb)  → AST を経由せずコンポーネントオブジェクトを直接構築
  │    │         ※ パース中にプラグインの gen_cdl_file も逐次呼ばれる
  │    └─ Generator.end_all_parse         # 全 CDL パース完了報告（post コードのパースはこの後も続く）
  │
  ├─ semantics_analisys_1
  │    ├─ Cell.create_reverse_join
  │    ├─ DescriptorType.check_signature / Signature.set_descriptor_list / Celltype.check_dynamic_join
  │    ├─ root_namespace.set_definition_join (1回目)
  │    │    # 結合の左辺（呼び口/属性名）を Port/Decl に解決
  │    ├─ [ポストコード生成]（ARGV.length > 0 の場合のみ）
  │    │    └─ PluginModule.gen_plugin_post_code
  │    │         → tmp_plugin_post_code.cdl 生成 → Import でパース
  │    ├─ Cell.create_reverse_join（再実行、ポストコード分）
  │    ├─ root_namespace.set_definition_join (2回目・ポストコード分)
  │    ├─ root_namespace.set_max_entry_port_inner_cell
  │    └─ root_namespace.set_require_join
  │         # require 節で宣言された呼び口へ singleton セル等への Join を自動生成（6.2）。エラー検出ではない
  │
  └─ semantics_analisys_2
       ├─ Cell.make_cell_list2
       ├─ Cell.create_reverse_require_join   # 逆 require 結合構築
       ├─ root_namespace.set_port_reference_count
       ├─ root_namespace.check_join          # 未結合・配列要素数・size_is・到達可能リージョンの検出（6.3）。シグニチャ一致は別箇所
       └─ root_namespace.check_ref_but_undef # 参照されているが未定義のセルチェック
```

### 3.3 run2（最適化 + コード生成）

```
run2（リンクルート Region ごとに繰り返し）
  │
  ├─ optimize_and_generate（無条件に呼ばれる）
  │    ├─ root_namespace.reset_optimize      # 最適化フラグリセット（無条件）
  │    ├─ Generator.get_n_error == 0 の場合のみ：
  │    │    ├─ root_namespace.set_cell_id_and_domain  # セル ID 割付・ドメイン設定
  │    │    └─ !$unopt の場合のみ： root_namespace.optimize  # 呼び口最適化 + 受け口最適化
  │    ├─ Generator.get_n_error != 0 なら print_report → exit 1  # コード生成フェーズへのゲート（11章）
  │    ├─ root_namespace.generate            # C コード生成（generate.rb）
  │    │    ├─ 各 Celltype の _tecsgen.h / _factory.h 生成
  │    │    ├─ 各 Celltype の _templ.c / _inline_templ.h 生成
  │    │    └─ tecsgen.cfg 生成（ファクトリ出力）
  │    └─ root_namespace.generate_post       # generate 後処理（8章8.1/8.3/8.5、2026-09-15検証済み。celltype/signature の post 処理＝ヘッダの#include/#undef/インクルードガード閉じ等）
  │
  └─ finalize
       ├─ AppFile.update   # エラー0件のときのみ、変更のあったファイルを上書き
       └─ print_report     # エラー・警告件数出力
```

---

