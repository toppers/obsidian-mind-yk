---
date: 2026-10-27
description: "tecsgen-python3移植計画のうち完了済みフェーズP5（プラグイン機構と標準プラグイン）の詳細と持ち越しをverbatim分離したアーカイブ。25KB閾値による分割"
project: tecsgen-python3
status: tracking
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3移植計画 Archive — P5

[[tecsgen-python3移植計画]]から、完了済みフェーズ P5 の節を逐語で分離した（2026-10-27、25KB閾値）。段階ごとの詳細は [[tecsgen-python3移植計画 — P5 進捗ログ]]。

### P5 プラグイン機構と標準プラグイン

- **最初に**: プラグインを使う35ケースも含めた一致一覧（`p4_progress.py` の拡張）と、1ケースの差分表示をリポジトリに用意する（常設ルール、[[Key Decisions]] 2026-09-27）
- `Plugin` 基底クラスと4種のサブクラス、`MultiPlugin`（`Node` の直下にある。内部仕様 9.5）、`PluginModule#load_plugin` → `importlib` による名前解決
- プラグイン引数の解析、`eval` の利用箇所（`tecslib` のうち24ファイル）の置き換え方を決める（**2026-10-03 訂正**: 24ファイルは `eval_const` などを含む部分文字列の一致数で、Ruby の `eval` の呼び出しは r3033 には無い。置き換えは不要）
- 移植の順序（`test/` での使用頻度で決める）: CelltypePlugin/SignaturePlugin の基本 → Through 系（Trace・RPC・opaqueRPC）→ TECSInfo 系 → Multi → カーネル依存（HRP/HRP2/FMP/HRMP/ATK1）→ mruby 系
- 既知の問題3件（内部仕様 9.7）は**そのまま移植しない**。1件ずつ直すか削除するかを決める
- 各プラグインの仕様は [[tecsgen-plugins]] を移植元として使う

**進捗**: 段階ごとの詳細は [[tecsgen-python3移植計画 — P5 進捗ログ]] に分離（2026-09-28、25KB閾値）。プラグイン使用ケースの一致は 20/35、不使用は 119/119（as of 2026-09-28、P5j 後）。

- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5a（2026-09-27）|P5a]]（2026-09-27）: プラグイン読み込み基盤・`Plugin` 基底・`MultiPlugin`／Celltype・Signature・Cell 各基底、一致一覧を `p4_progress.py` に実装
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5b（2026-09-27）|P5b]]（2026-09-27）: `ThroughPlugin` 基底（重複防止キャッシュの import 行の差は未解明の既知差異）
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5c（2026-09-27）|P5c]]（2026-09-27）: `TracePlugin`
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d#P5d（2026-09-27）|P5d]]（2026-09-27）: `RPCPlugin`＋`GenParamCopy`・`GenTransparentMarshaler`（一部）、`load_plugin` の2回目エラーコードのバグ修正
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5e（2026-09-28）|P5e]]（2026-09-28）: `OpaqueRPCPlugin`＋`GenOpaqueMarshaler`
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5f（2026-09-28）|P5f]]（2026-09-28）: `TECSInfoPlugin`・`TECSInfoCompoPlugin`・`CompositePlugin`・`tecsinfo.rb`（TECSInfo系4ケース）
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5g（2026-09-28）|P5g]]（2026-09-28）: Multi 系の `CIfGen`・`CppIfGen`（`cifplugin`・`cppifplugin`）
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5h（2026-09-28）|P5h]]（2026-09-28）: ATK1 の5本（`celltypePlugin`）、HRP・FMP・HRMP 系は正解データが無いため見送り
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i#P5i（2026-09-28）|P5i]]（2026-09-28）: MrubyBridge ファミリー7本（`multiplugin/1・2`）、`CdlParser.parse_file` の潜在バグ修正
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k#P5j（2026-09-28）|P5j]]（2026-09-28）: 正解データのある標準プラグインの残り全部（RPC 系3本＋`GenTransparentMarshaler` 全量、`C2TECSBridge`、`RepeatCell`/`RepeatJoin`、`Notifier`、`DataPumpHolder`）、mixin 順序のバグ修正、P5b の import 行の差の原因判明
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k#P5k（2026-09-30）|P5k]]（2026-09-30）: カーネル依存系（HRP・FMP・HRMP・HRP2・ATK1）の正解データを採取（`tests/golden/kernel/`、hrp3+tecs 2・fmp3+tecs 2・hrmp3+tecs 2・ev3rt+tecs 3・atk1+tecs 2の計11ケース、`arm-none-eabi-gcc`（ATK1 はホストの `gcc -E`）、2回の全件採取で同一）。HRP2 は hrp2+tecs 自体が構文エラーになるため ev3rt+tecs で採った。ATK1 の `ATK1EventPlugin` は入力にイベントのセルが無く、出力が空の経路だけ。正解データの無いプラグインは、計測で18件（プラグイン17＋補助モジュール1。as of 2026-10-01、2026-10-01 に採取された別セッションのパッケージ正解データ16ケース（`tests/golden/packages/`）を加えた再集計。09-30 は20件）: HRP2 のカーネルオブジェクト系7・ドメイン間通信系ほか5（補助モジュール `GenHRP2Marshaler` を含む）・`MrubyInfoBridge*` 3・`TransparentMarshalerPlugin`・`ATK1DelayTaskPlugin`。一覧と入力探索の結果は P5 進捗ログの P5k。移植は未着手
- [[tecsgen-python3移植計画 — P5 進捗ログ#P5l〜P5p（2026-10-01）|P5l〜P5p]]（2026-10-01）: カーネル依存系プラグイン（HRP・FMP・HRMP・HRP2、ATK1Event）を移植。カーネルの11ケースすべてで生成物・標準出力・終了コードが Ruby 版とバイト一致（プラグインありの一致 34/46、プラグインなし 119/119）。`__tool_info__`（`TOOL_INFO`）も移植。
- [[tecsgen-python3移植計画 — P5 進捗ログ#P5q（2026-10-01）|P5q]]（2026-10-01）: `-L` による利用者プラグインの探索（設計は [[tecsgen-python3 -L ユーザプラグイン探索設計]]）と、同梱プラグインの Python 版（`tests/user_plugins/`）。`-L` 待ちの8ケースと、持ち越しの4件（`class`・`ErrorCase/cell-err`・`TECSInfoAccessor/*` 2件）がすべて一致し、**プラグインありの全46ケースが一致**（プラグインなし 119/119。as of 2026-10-02）。

**持ち越し（as of 2026-10-02、P5q 後）**: 正解データのあるケースは全件一致。カーネル依存系（HRP・FMP・HRMP・HRP2・ATK1Event）は P5l〜P5p で移植済み（[[tecsgen-python3移植計画 — P5 進捗ログ#P5l〜P5p（2026-10-01）|P5l〜P5p]]）。正解データの無いもの（`ATK1DelayTaskPlugin` ほか）は未移植。**HRP2 の個別カーネルオブジェクト系・SVC・RPC は 2026-10-03 に正解データを採取し、P3 記録も採って移植済み**（合成入力 CDL、5ケース `hrp2/objects`・`hrp2/rpc`・`hrp2/cyclic`・`hrp2/alarm`・`hrp2/rpc_ptr`、`tests/golden/kernel/cases/hrp2/`・`tests/golden/kernel/p3/hrp2/`。再採取でバイト一致。**プラグインありの全 51 ケース一致**）。周期・アラームハンドラとRPCのポインタ引数は Ruby 版が例外で止まる経路で、その例外・終了コードまで一致。`HRP2Cache`・`HRP2PostHook` は動かす経路が無く対象外。**残りの `HRPRPCPlugin`・`ATK1DelayTaskPlugin`・`MrubyInfoBridge*`・`TransparentMarshalerPlugin`・`TECS2CBridgePlugin`・`Mruby2CBridgePlugin` も同日に正解データ（実プロジェクトの `make tecs`・`test/mruby`・合成入力）と P3 記録を採って移植済み。プラグインありの全 63 ケース一致、pytest 995 件通過**。未移植は 85 本中 2 本のみ（ファイル数を実数で突き合わせ。2026-10-02 の「18 本」は数え間違い）。パッケージ由来のケースも P3 記録で再生できるようにした（`packages/` 接頭辞、`collect_packages.py --p3-oracle`）。

## Related

- [[tecsgen-python3移植計画]] — 親の計画ノート
- [[tecsgen-python3移植計画 — P5 進捗ログ]]
- [[tecsgen-python3]]
