---
date: 2026-09-28
description: "tecsgen-python3移植計画のP5（プラグイン機構と標準プラグイン）の段階ごとの進捗記録（P5a〜P5p、2026-09-27〜10-01。P5a〜P5d は [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d|別ノート]]、P5e〜P5i は [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i|別ノート]]）。移植計画本体から25KB閾値で verbatim 分離したイベントログ"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
---

# tecsgen-python3移植計画 — P5 進捗ログ

[[tecsgen-python3移植計画]] の P5 節から、段階ごとの進捗段落を verbatim で移したイベントログ（2026-09-28、25KB閾値による分離）。本体の P5 節には段階ごとの1行索引を残している。段落の中身は変更しておらず、段階ごとの見出しだけを足した。

## P5a〜P5d（2026-09-27）

P5a〜P5d の段落は [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d]] へ移した（verbatim、2026-09-30、25KB閾値）。


## P5e〜P5i（2026-09-28）

P5e〜P5i の段落は [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i]] へ移した（verbatim、2026-09-30、25KB閾値）。


## P5j（2026-09-28）

P5j の段落は [[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k]] へ移した（verbatim、2026-10-01、25KB閾値）。

## P5k（2026-09-30）

P5k の段落は [[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k]] へ移した（verbatim、2026-10-01、25KB閾値）。

## P5l〜P5p（2026-10-01）

**進捗（as of 2026-10-01、P5p）**: カーネル依存系プラグイン（HRP・FMP・HRMP・HRP2、および ATK1 の `ATK1EventPlugin`）を移植し、**カーネルの11ケースすべてで生成物・標準出力・終了コードが Ruby 版とバイト一致**した（`tools/port/p4_progress.py` の表示が 119/119（プラグインなし）、34/46（プラグインあり。P5j 後は 20/35）。外部リポジトリ `main` のコミット6件＋ドキュメント1件、いずれもプッシュなし）。pytest は Windows 908 passed / 72 skipped、WSL 903 passed / 77 skipped、ruff・ty も通る。
- **P5l（`d226b8f`）基盤**: P5k の正解データを Python 版から再生する手段が無かったので、カーネルのケースにも P3 オラクルの記録（Ruby 版の外界とのやりとり）を採った。`collect_kernel.py --p3-oracle`（`wsl_check.ps1 -KernelP3`）が、`tests/ruby/p3_oracle.rb` を `RUBYOPT` で差し込んで同じケースを実行し、出力がコミット済みの正解データと一致したときだけ `tests/golden/kernel/p3/<ID>.jsonl.gz`（11本、計2.3MB）を置く。`p3_oracle.rb` は環境変数 `P3_ORACLE_LOG` があれば記録を標準エラーでなくそのファイルへ書く（`stderr.txt` を変えないため）。再生側は `p3_oracle_data.case_ids(include_kernel=True)`・`p4_gen_check.golden_dir/work_root`（ケース ID は `kernel/<ID>`）。既存の pytest にはカーネルのケースを入れていない。正解の標準出力は `make` 経由なので、`golden_stdout` が make の呼び出し行（バックスラッシュ続きを含む）と末尾の `touch …` を除き、`tecs.timestamp`（`touch` の産物）を比較から外す。採取の所要は全11ケースで約30分。
- **P5l 続き（`bf88ce6`）HRP**: `HRPPlugin`（ドメイン）・`HRPKernelObjectPlugin`・`HRPObjectPlugin`・`HRPTaskPlugin`・`HRPHandlerPlugin`・`HRPSVCThroughPlugin`・`HRPSVCSignaturePlugin`・`HRPSVCBodyCellPlugin`、基盤の `DomainPlugin`・`lib/GenAttMod`（`GenAttMod`・`GenDefSvc`）・`HRPKernelObjectManager`（`HRPSVCManage`）。hrp3 の2ケースが一致。Ruby 版の `gen_caller_check_code` は呼ばれない（`=begin` で隠れている）ので移植していない。
- **P5m（`bf83e78`）FMP と `__tool_info__`**: `FMPPlugin`（クラスプラグイン）・`FMPObjectPlugin`・`FMPHandlerPlugin`、基盤の `ClassPlugin`。クラス定義を `__tool_info__( "FMP_class_def" )` から読むので、これまで例外を出すだけのスタブだった `TOOL_INFO` と `VALIDATOR` を `core/tool_info.py` に移植した（持ち越しの「`class` の `__tool_info__`」の前提）。fmp3 の2ケースが一致。Ruby 版の癖はそのまま再現: `FMPObjectPlugin#gen_factory` の `indent` はブロック内の局所変数で周回ごとに nil に戻る（2セル目以降のインデントが出ない）、クラス名の `"root"`（String）と `:root`（Symbol）は等しくない。
- **P5n（`6765ed5`）HRMP**: `HRMPPlugin`（MultiPlugin。付与位置が domain か class かで `HRMPDomainPlugin`・`HRMPClassPlugin` に振り分ける。結合の通り道は `HRMPJoinManager`）・`HRMPKernelObjectPlugin`。`NotifierPlugin#gen_sac` が `PluginNotPorted` を返していたのをやめ、読み込み済みのドメインプラグインの `get_sac_str` を呼ぶようにした（hrmp3 の tSample2 が通る）。hrmp3 の2ケースが一致。
- **P5o（`cbb07c3`）HRP2**: `HRP2Plugin`・`HRP2KernelObjectPlugin`・`HRP2ObjectPlugin`・`HRP2HandlerPlugin`・`HRP2TaskPlugin`。Ruby 版は進行状況を `puts`/`print`/`p` で標準出力へ書き、それが正解の標準出力に入っているので、同じ文面をそのまま書く。ev3rt の3ケースが一致。
- **P5p（`bd85e74`）`ATK1EventPlugin` と `-v` の文言**: `ATK1EventPlugin`（`EVENT_tecsgen.oil`）を移植し、kernel の atk1 2ケースが一致（出力は空の経路。AUTO のマスク割り当て部分は入力が無く検証できていない）。`-v` の表示 `new … plugin: plugin_object = Class.new(`（Ruby は「クラスのクラス」で `Class`）と `gen_plugin_post_code: plClass.name}.gen_post_code( file )`（Ruby の文字列は `#{` が欠けている）を Ruby どおりにし、持ち越しだった「標準出力のデバッグ文言の差」のうち `optimize/*` 3件も直った。
- **範囲外のまま**: 正解データの無い HRP2 のカーネルオブジェクト系7・`HRP2RPCPlugin`・`HRP2SVCPlugin`・`HRPRPCPlugin`・`lib/GenHRP2Marshaler`、`ATK1DelayTaskPlugin` など（P5k の「正解データが無い」一覧と同じ）。これらは入力が見つかるまで移植しない。
- **残り12件（プラグインあり）**: `-L` ユーザプラグイン待ち8件（CPPBridge・SWIGBridge・domainPlugin・ErrorCase/domainPlugin-err・generate・region・restrict・through）、`ErrorCase/cell-err`（Ruby の例外メッセージ）、`TECSInfoAccessor/*` 2件（W1008）、`class`。

## P5q（2026-10-01）

**進捗（as of 2026-10-02、P5q）**: `-L` による利用者プラグインの探索を実装し、同梱プラグインの Python 版を `tests/user_plugins/<ケースID>/` に置いて、`-L` ユーザプラグイン待ちだった8ケースがすべて Ruby 版とバイト一致した。続けて持ち越しだった4件（`class`・`ErrorCase/cell-err`・`TECSInfoAccessor/*` 2件）も解消し、**プラグインありの全46ケースが一致**した。プラグイン使用ケースの一致は 34/46 → **46/46**、不使用は 119/119 のまま。pytest 908 passed / 72 skipped（Windows）・903 passed / 77 skipped（WSL、`wsl_check.ps1`）、`ruff`・`ty` とも両環境で通過。外部リポジトリのブランチ `ykominami/tecsgen-python3-Loption` に4コミット（`f78de87` 探索・`through`/`region`/`restrict`/`domainPlugin`/`ErrorCase/domainPlugin-err`/`generate`、`f18c6ae` `CPPBridge`・`SWIGBridge`、`279ee50` `class` の `MyClassPlugin`、`8f7f3c1` `cell-err`・`TECSInfoAccessor` の修正。プッシュなし）。WSL は `8f7f3c1` 時点で再検証した。設計と決定は [[tecsgen-python3 -L ユーザプラグイン探索設計]]。

- **探索**: 組み込み（`tecsgen.plugin.<名前>`）を先に、続いて `ctx.library_path` を先頭から、各ディレクトリで `<名前>.py`・`tecslib/plugin/<名前>.py`。ファイルパスから読み（`sys.path` は触らない）、読んだクラスは実行回ごとのレジストリに持つ。例外は `print_exception` して P2003。`Host.resolve_plugin_file` を足し、`RecordedHost` が採取時の作業ディレクトリを `tests/user_plugins/<ケースID>/` に対応付ける。
- **`through` の差の解消**: P5b・P5c で原因未特定だった import 行の差は、P5j の見立てどおり `Plugin1` のクラス本体の `@@generated_celltype = {}` の副作用だった。`Plugin1.py` が本体で共有辞書を `clear()` し、実行ごとに読み直すので再現できた。
- **`generate` は組み込みの `ATK1TaskPlugin` で一致**: テスト同梱の `ATK1TaskPlugin.rb` は標準版と大きく違うが、移植しなくても 30/30 で一致した。組み込み優先の探索順と矛盾しない（Ruby 版が実際に標準版を読んだことの確証までは取れていない）。
- **`MyTracePlugin`**: Ruby 版は `TracePlugin.rb` の複製で `gen_ep_func_body` だけが違うので、`TracePlugin` の子クラスにして上書きした。
- **`class`**: 同梱の `MyClassPlugin`（クラスプラグイン、`__tool_info__( "MyClass_class_def" )` から定義を読む）の Python 版を足して 7/7 一致（P4 からの持ち越しは `__tool_info__` 未移植が原因と見ていたが、P5m で移植済みで、残りはこのプラグインだけだった）。
- **`ErrorCase/cell-err`（Ruby の例外メッセージ）**: ロードに失敗したプラグインクラスは nil で、Ruby はそれに `new` を送って `undefined method `new' for nil:NilClass` になる。`Cell.apply_plugin` で `None` なら同じ `no_method("new", None)` を送出するようにして一致。
- **`TECSInfoAccessor/*` の W1008（原因確定）**: Ruby 版は `Generator` の `initialize` で `@b_reuse` を設定しないので、`set_reuse` されないパーサでは nil のままで、`Generator.is_reuse?` が `false` ではなく nil を返す。`TECSInfoPlugin#new_cell` が同じ tmp ファイルを2回 `Import` すると、1回目は reuse が false、2回目は `false || nil` で nil となり、`false != nil` で W1008 が出る。Python は初期値が `False` だったので出なかった。`CdlParser._b_reuse` の初期値を `None` にして一致。原因は、WSL の Ruby に `Import#initialize` を差し替える計測コードを入れて、`Import` ごとの reuse の値とパーサスタックを実測して確定した。
- **残り（プラグインあり）**: なし。正解データの無いプラグイン（P5k の一覧）は入力が見つかるまで未移植のまま。

## Related

- [[tecsgen-python3移植計画]] — 本体（P5 節に索引）
- [[tecsgen-python3]]
- [[tecsgen-plugins]] — 移植元プラグインの仕様
