---
date: 2026-09-30
description: "tecsgen-python3移植計画のP5のうち、P5a〜P5d（プラグイン読み込み基盤・ThroughPlugin・TracePlugin・RPCPlugin、2026-09-27）の進捗記録。P5 進捗ログから25KB閾値で verbatim 分離したイベントログ"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
---

# tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d

[[tecsgen-python3移植計画 — P5 進捗ログ]] から、P5a〜P5d（2026-09-27）の段落を verbatim で移した（2026-09-30、25KB閾値による分離）。P5e 以降は元のログに残っている。

## P5a（2026-09-27）

**進捗（as of 2026-09-27、P5a）**: 「最初に」の一致一覧を `tools/port/p4_progress.py` に実装、`Plugin` 基底クラス（`core/plugin.py`。`parse_plugin_arg`・`check_plugin_arg`・set_locale までの backlog）、`PluginModule.load_plugin`/`generate_and_parse`/`gen_plugin_post_code`/`sort_and_load`（`core/plugin_module.py`。プラグイン名から `tecsgen.plugin.<Name>` を `importlib` で解決）、`MultiPlugin`・`CelltypePlugin`・`SignaturePlugin`・`CellPlugin` の基底クラス（`plugin/`、Ruby と同名のファイル）を移植。`signaturePlugin` オラクルケースで、`SignaturePlugin` がプラグイン生成 CDL（identity celltype）を生成→インポートするところまで Ruby と一致することを確認（同ケースの残る不一致は未移植の `C2TECSBridgePlugin` のみ）。pytest 908 passed / 72 skipped（回帰なし）、`ruff`・`ty` とも通過。

## P5b（2026-09-27）

**進捗（as of 2026-09-27、P5b）**: `ThroughPlugin` 基底クラス（`plugin/ThroughPlugin.py`）を移植。`set_through_info`（P3 で用意済みの `Join.set_through_info` から呼ばれる）、`gen_plugin_decl_code`/`gen_through_cell_code`、`gen_ep_func_body`、`$source$`/`$destination$`/`$next$`/`$*_region$`/`$count$` 置換を含む。`through` オラクルケースで、プラグイン名を指定しない素の through（`ThroughPlugin` 自身）の生成トレース・生成セルコードが Ruby と完全一致することを実行で確認（WSL の実 Ruby でも同じ trace を再現して検証）。既知の小さな不一致1件（**2026-10-03 解消**: 原因は `Plugin1.rb` がクラス本体で `@@generated_celltype = {}` を実行することで、P5j で判明、P5q の `-L` ユーザプラグイン移植で一致。[[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k]]）: Ruby の `gen_plugin_decl_code` の重複生成防止キャッシュ（`@@generated_celltype`）が、同じセルタイプ名を共有する2つ目の `ThroughPlugin` インスタンスでも `import(...)` 行を出す場合があり、この移植ではまだ再現できていない（3インスタンス中、Ruby は1・2番目に import を出し3番目だけ省略。単純な「初回だけ出す」ロジックでは説明できないことを実 Ruby 実行で確認済み、原因未特定だった。上記のとおり解消）。Import 側で二重 import は既に無害化されるため、最終生成物には影響しない中間ファイルだけの差分。この through ケースの残りの不一致は、未移植の `TracePlugin`（標準プラグイン）と、テストケース固有の `Plugin1`/`Plugin2`（`-L` で追加されるユーザプラグイン。この移植のプラグインローダはまだ `tecsgen.plugin.*` 以外を探索しない）による。pytest 908 passed / 72 skipped（回帰なし）、`ruff`・`ty` とも通過。

## P5c（2026-09-27）

**進捗（as of 2026-09-27、P5c）**: 標準プラグイン第1号 `TracePlugin`（`plugin/TracePlugin.py`）を移植。`ThroughPlugin` を継承し、呼び出しの前後を syslog にトレース出力するセルを挿入する。パラメータの型ごとの再帰的な C コード生成（bool/int/float/enum/struct/pointer、`size_is`/`count_is` 配列、nullable pointer）を含む。`through` オラクルケースで、3つの `TracePlugin` インスタンスの生成トレース（`maxArrayDisplay` などのプラグイン引数込み）と生成セルコードが Ruby と完全一致することを確認。P5b で見つけた `gen_plugin_decl_code` の import 行キャッシュの既知差異が `TracePlugin` でも同じ形で再現し、`ThroughPlugin` 固有の問題ではなく共通の未解明ギャップであることを確認した。この through ケースの残りの不一致は、テストケース固有の `Plugin1`/`Plugin2`（`-L` 読み込み、未対応）のみ。pytest 908 passed / 72 skipped（回帰なし）、`ruff`・`ty` とも通過。

## P5d（2026-09-27）

**進捗（as of 2026-09-27、P5d）**: `RPCPlugin`（Transparent RPC チャンネル）と、共有 mixin `GenParamCopy`（`plugin/lib/GenParamCopy.py`、パラメータ転送コードの再帰的な型分岐、全量移植）・`GenTransparentMarshaler` の一部（`plugin/lib/GenTransparentMarshaler.py`。実際に呼ばれる `initialize_transparent_marshaler` とプラグイン引数解析まで）を移植。既知の問題9.7.1により、この155ケース中で RPCPlugin を使うケース（`rpc`・`class`・`DataPumpHolder`）は Ruby 版自身も `TransparentRPCSignaturePlugin` 未存在で必ず失敗するため、マーシャラの実コード生成（`gen_marshaler_celltype`・`gen_ep_func_body*`・`print_params` 等）はどのケースからも呼ばれない——それらは `PluginNotPorted` を送出するスタブに留め、実行されない領域を推測で埋めることを避けた。

この過程で `PluginModule.load_plugin` の本物のバグを発見・修正: 同じ未移植プラグインを2回目にロードしようとしたとき、Ruby 版は再 require せず定数参照のみ行い `P2003` を出すが、この移植は2回目も `P2001` を出していた。`_lookup_loaded_plugin_class`（`sys.modules` だけを見て再インポートしない）を追加して修正。`rpc`・`class` オラクルケースの標準出力が、残る不一致（未移植の `TECSInfoPlugin` のみ）を除いて Ruby 版と一致することを確認。`tools/port/p4_progress.py` の一致数は 4/35（プラグイン使用ケース）、119/119（プラグイン不使用）。pytest 908 passed / 72 skipped（回帰なし）、`ruff`・`ty` とも通過。

## Related

- [[tecsgen-python3移植計画 — P5 進捗ログ]] — 親ログ（P5e 以降）
- [[tecsgen-python3移植計画]] — 本体（P5 節に索引）
- [[tecsgen-python3]]
