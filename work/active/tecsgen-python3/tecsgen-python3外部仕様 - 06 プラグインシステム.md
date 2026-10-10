---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第6章（プラグイン）— CDLでの呼び出し規約はRuby版と同じ、記述言語はPython。標準付属プラグインの移植状況（85ファイル中83ファイル移植。残る2ファイルは動かす経路が無く対象外。プラグインを使う85ケースが一致。as of 2026-10-09）と利用者プラグインの書き方（`CMake` API を呼ぶ時期の注意を含む）。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第6章（全10章）。CDL 上の `generate`・`through`・`domain`・`class` の書き方と、付与位置ごとの種別は [[work/active/tecsgen/tecsgen外部仕様 - 06 プラグインシステム|Ruby版 第6章]]と同じです。各プラグインの機能は [[tecsgen-plugins]] を参照してください。

## 6. プラグインシステム

### 6.1 呼び出し規約

CDL の記述（`[generate(PluginName, "param=val, ...")]`、`generate(PluginName, sSignature, "...")`、`through`、`domain(...)`、`class(...)`）、プラグイン引数の文法（`param=value` のカンマ区切り）、`MultiPlugin` による位置ごとの具象クラスの選択は Ruby 版と同じです。

### 6.2 標準付属プラグインの移植状況（as of 2026-10-03）

標準付属プラグインのうち、Ruby 版のファイル（85 本）で **83 本を移植**しました。残る 2 本（`HRP2Cache`・`HRP2PostHook`）は、動かす経路が無いので移植しません。正解データのあるテストケースでは、プラグインを使う 85 ケースが Ruby 版（tecsgen-rb）とバイト一致します（2026-10-09。`TransparentRPCSignaturePlugin` を含む）。（2026-10-02 の「67 本移植・18 本未移植」は数え間違いで、実際のファイル数との突き合わせで直しました。）

| 区分 | 状況 |
|---|---|
| トレース（`TracePlugin`）、RPC（`RPCPlugin`・`OpaqueRPCPlugin`・`SharedRPCPlugin`・`SharedOpaqueRPCPlugin`）、`C2TECSBridgePlugin`、`CIfGen`・`CppIfGen`、`TECSInfoPlugin`・`TECSInfoCompoPlugin`、`RepeatCellPlugin`・`RepeatJoinPlugin`、`NotifierPlugin`、`DataPumpHolderPlugin`、`MrubyBridgePlugin` ファミリー | 移植済み・一致確認済み |
| カーネル依存（ATK1 の Kernel・Task・Alarm・ISR・Resource・Event、HRP、HRP2 のオブジェクト基盤・Task・Handler・Object、FMP、HRMP） | 移植済み。カーネルの 11 ケースで一致 |
| HRP2 の個別カーネルオブジェクト（`HRP2SemaphorePlugin`・`HRP2EventflagPlugin`・`HRP2DataqueuePlugin`・`HRP2PriorityDataqueuePlugin`・`HRP2FixedSizeMemoryPoolPlugin`・`HRP2AlarmHandlerPlugin`・`HRP2CyclicHandlerPlugin`）、`HRP2SVCPlugin`・`HRP2RPCPlugin`・`GenHRP2Marshaler` | 移植済み（2026-10-03）。合成入力の 5 ケース（`kernel/hrp2/*`）で一致。`HRP2AlarmHandlerPlugin`・`HRP2CyclicHandlerPlugin`・ポインタ引数の `HRP2RPCPlugin` は、Ruby 版が例外で止まる経路で、その例外・終了コードまで一致する |
| `HRP2Cache`（コメントだけのファイル）、`HRP2PostHook`（tecslib のどこからも参照されない） | **移植しない**（動かす経路が無い） |
| `HRPRPCPlugin`（hrp3+tecs の sample2）、`ATK1DelayTaskPlugin`（et_robcon の nxt_sample 4本）、`MrubyInfoBridgePlugin`・`MrubyInfoBridgeCellPlugin`・`MrubyInfoBridgeSignaturePlugin`（`test/mruby` の2本）、`TransparentMarshalerPlugin`（合成入力）、`TECS2CBridgePlugin`・`Mruby2CBridgePlugin`（`Mruby2C`・`Mruby2C-File`） | 移植済み（2026-10-03）。上のすべてのケースで一致 |

`HRP2Cache`・`HRP2PostHook` を CDL で指定すると、そのプラグイン名は解決できず、Ruby 版とは違うエラーになります（ファイルが無いときのエラー P2001）。ただし、どちらも Ruby 版の標準付属の CDL から参照されません。

### 6.3 利用者プラグイン

Python 版では、利用者が書くプラグインは Python のモジュールです。

- 置き場所: `-L` で指したディレクトリ（複数指定可）。`<クラス名>.py`、または `tecslib/plugin/<クラス名>.py` の名前で探す
- 探す順序: 標準付属（組み込み）プラグインを先に探し、その後に `-L` のディレクトリを探す。**組み込みと同名のプラグインは `-L` で上書きできない**
- 基底クラス: `tecsgen.plugin.*`（`CelltypePlugin`・`CellPlugin`・`SignaturePlugin`・`ThroughPlugin` ほか）を明示的に import して継承する
- `MultiPlugin` の子クラス: `get_plugin` が返すクラスは、`MultiPlugin` の子クラスと**同じファイルに書いてよい**（ファイル名と違う名前のクラスでも、Ruby 版と同じく動く）。以前は、同じファイルに書いたクラスの post_code ファイル（`tmp_<クラス名>_post_code.cdl`）が出なかったが、修正した（2026-10-09、Python 版 PR #12 で `main` にマージ済み）
- 失敗時: ロードに失敗すると P2003、ファイルが無いと P2001（Ruby 版と同じ番号）
- 信頼モデル: `-L` で指したディレクトリのコードをそのまま実行する（Ruby 版と同じ。信頼できるディレクトリだけを指定すること）
- `CMake` API（2026-10-05 追加。tecsgen-rb の `TECSGEN::CMake` に対応）: `from tecsgen.core.tecsgen import CMake` で取り込み、`CMake.add_source(path)`・`add_include(path)`・`add_define(define)`・`add_link_option(opt)`・`add_custom_command(cmd)`・`add_line(line)` を呼ぶと、`gen/CMakeLists.tecsgen.cmake` の対応する一覧（`TECS_PLUGIN_EXTRA_SOURCES`・`TECS_INCLUDE_DIRS`・`TECS_COMPILE_DEFINITIONS`・`TECS_LINK_OPTIONS`・`TECS_CUSTOM_COMMANDS`・プラグインの追加行）に出力される（重複は除く）。標準付属プラグインでこの API を使うものは無い。次の点に注意すること（いずれも Ruby 版 tecsgen-rb と同じ挙動。2026-10-09 に、セルタイププラグインから呼ぶ合成ケースで、`gen/` の 13 ファイルが Ruby 版とバイト一致することを確認した。signature・cell・composite・multi・through・domain・class の各プラグインのコンストラクタから呼ぶ場合も、同日に Ruby 版との一致を確認した）
  - **呼ぶ時期**: `gen/CMakeLists.tecsgen.cmake` は生成の最初（`Makefile.tecsgen` の次）に書かれる。そのため、プラグインの**コンストラクタや `new_cell` など、生成より前に呼ばれる場所**から呼んだものだけが出力に反映される。`gen_factory` など**生成段階のフックから呼んだものは、反映されない**（エラーにも警告にもならず、黙って無視される）
  - **値の扱い**: 引数は文字列にして保持される（Symbol・整数も可）。同じ値を複数回渡しても出力は 1 回で、最初に渡した順に並ぶ。`add_include` に渡したパスは `\` が `/` に変わるだけで、`$(BASE_DIR)` などの変数は展開されずそのまま出る

### 6.4 Ruby版との差異

| 項目 | Ruby 版 | Python 版 |
|---|---|---|
| 利用者プラグインの言語 | Ruby（`.rb`） | Python（`.py`）。**Ruby で書いたプラグインは動かない**（2026-10-01 決定） |
| 探索パス | `-L`・`RUBYLIB` | `-L` のみ |
| 標準付属プラグイン | 全部 | 移植済みの範囲（6.2） |
| プラグイン内の `eval` | 使わない（r3033 の `tecslib` に Ruby の `eval`・`instance_eval`・`class_eval` の呼び出しは無い。以前の「24ファイル」は `eval_const`・racc 生成コードの `module_eval`・メッセージ中の `evaluate` を数えた誤り。2026-10-03 訂正） | 使わない。Python 版にも `eval`・`exec` は無い。プラグインは `importlib` で読み込む（[[tecsgen-python3内部仕様 - 09 プラグイン機構\|内部仕様 9章]]）。標準付属プラグインの出力は、正解データの全ケースで Ruby 版と一致している |

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3 -L ユーザプラグイン探索設計]] — `-L` の設計
- [[tecsgen-python3内部仕様 - 09 プラグイン機構]] — ロードの実装
- [[tecsgen-plugins]] — プラグインごとの機能仕様
