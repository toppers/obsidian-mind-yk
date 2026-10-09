---
date: 2026-10-01
description: "tecsgen-python3移植計画のP5のうち、P5j（-L 以外の標準プラグインの一致状況、2026-09-28）と P5k（カーネル依存系の正解データ採取・プラグインの網羅状況、2026-09-30〜10-01）の進捗記録。P5 進捗ログから25KB閾値で verbatim 分離したイベントログ"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
---

# tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k

[[tecsgen-python3移植計画 — P5 進捗ログ]] から、P5j（2026-09-28）と P5k（2026-09-30〜10-01）の段落を verbatim で移した（2026-10-01、25KB閾値による分離）。P5l 以降は元のログに、P5e〜P5i は [[tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i]]、P5a〜P5d は [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d]] にある。

## P5j（2026-09-28）

**進捗（as of 2026-09-28、P5j）**: 正解データのある標準プラグインの残りをすべて移植（ユーザー決定: `-L` ユーザプラグインより標準プラグインを先に）。外部リポジトリのブランチ `ykominami/tecsgen-python3-P5x` に3コミット（`3b1832e`・`ebd18b2`・`74268e7`、プッシュなし）。プラグイン使用ケースの一致は 11/35 → **20/35**、不使用は 119/119 のまま。pytest 908 passed / 72 skipped（Windows）・903 passed / 77 skipped（WSL、`wsl_check.ps1`）、`ruff`・`ty` とも両環境で通過。
- RPC 系: `OpaqueMarshalerPlugin`（`opaqueMarshaler` 115/115）、`SharedRPCPlugin`（`sharedRPC` 85/85）、`SharedOpaqueRPCPlugin`（`sharedOpaqueRPC` 224/224）。`sharedRPC` は Ruby 版で成功するケースなので、P5d でスタブにした `GenTransparentMarshaler` のコード生成部分（`gen_ep_func_body*`・`print_params`・`print_param_nc`・`gen_preamble`・`gen_postamble`）を全量移植した。Ruby 版の癖（アロケータ指定の `'[#{subsc}]'` が単一引用符で式展開されない、`gen_post_code` が各インスタンスでなく代表の `@cell_name` を並べる、サーバ側でも開始リージョンのインデントを使い回す）を再現。Ruby ではクラスメソッドとインスタンスメソッドの `gen_post_code` が同名で共存するので、インスタンス側は `gen_post_code_channel` に改名。
- `C2TECSBridgePlugin`（`signaturePlugin` 39/39）: プロトタイプのヘッダは Ruby 版が `CFile` でなく `Kernel#open` で書くので、`RubyIO(..., "utf-8")` で書く。
- `RepeatCellPlugin`・`RepeatJoinPlugin`（`cellPlugin` 24/24）: `set_count` は Ruby 版どおり各クラスに持たせた（片方から他方を import すると、Ruby では読み込まれないクラスまで読み込まれるため）。
- `NotifierPlugin`（`NotificationPlugin` 46/46、Ruby 1,231行）: 11種のハンドラタイプの判別、factory テンプレートの `{{attr}}` 置換、`tTimeEventHandler` のアダプタ関数生成。HRP/HRMP ドメイン・FMP/HRMP クラスの分岐は移植したが到達しない（カーネル依存プラグインは未移植）。`gen_sac` はドメインプラグインの `get_sac_str` を呼ぶため `PluginNotPorted`。
- `DataPumpHolderPlugin`（`DataPumpHolder` 5/5）: Ruby 版もコード生成の前に失敗する（9.7.1）ので、CDL 生成まで移植し `gen_ep_func_body` はスタブ。約260行のヒアドキュメントは Ruby ソースから機械的に写した（Windows の SVN 作業コピーは CRLF なので `\r` を除いた。[[Gotchas - Tooling & Config]] 2026-09-26 の既知の罠）。Ruby 版のタイポ `@datholder_celltype`（nil で空文字列になる）も再現。
- **見つけて直した既存コードのバグ**:
  - **mixin の順序**: Ruby の `include` はモジュールを親クラスより前に入れるので、`GenOpaqueMarshaler#gen_ep_func_body` などが `ThroughPlugin` のものに勝つ。`RPCPlugin`・`OpaqueRPCPlugin` は Python の基底クラスを `(ThroughPlugin, Gen...Marshaler, GenParamCopy)` と親クラスから書いていたため、マーシャラの受け口関数が `ThroughPlugin` の実装で生成されていた。これが P5e・P5f で「未調査」としていた `opaqueRPC` の残り2ファイルの原因（`(GenParamCopy, Gen...Marshaler, ThroughPlugin)` に直して 306/306）。
  - その陰に隠れていた `GenOpaqueMarshaler.gen_preamble` のプロトタイプ宣言の書き誤り（P5e の移植。これまで呼ばれていなかった）。
  - `ThroughPlugin` の `@@generated_celltype` がケース間でリセットされておらず、`rpc` が他の through 系ケースの後に実行されると失敗していた（`state.py` に登録）。
- **P5b 以来の未解明差異の原因が判明**: `through` ケースの import 行の差（P5b・P5c で「原因未特定」）は、テストケース同梱の `Plugin1.rb` がクラス本体で `@@generated_celltype = {}` を実行し、ロード時に `ThroughPlugin` 系で共有する辞書を空にするため。`ThroughPlugin` の問題ではなく、`-L` ユーザプラグインを移植すれば解消する。
- 道具: `tools/port/p4_progress.py` に `-d`（中身が違う生成物の unified diff 表示）を追加。`signature.py` の format 違反（P5f 以来 `ruff format --check` が落ちていた）を修正。
- **残り15件の内訳（as of 2026-09-28）**: `-L` ユーザプラグイン待ち8件（CPPBridge・SWIGBridge・domainPlugin・ErrorCase/domainPlugin-err・generate・region・restrict・through）、標準出力のデバッグ文言の差4件（`optimize/*` 3件は `-v` 系の `Class.new`/`plClass.name}` の表記、`ErrorCase/cell-err` は Ruby の例外メッセージ `undefined method 'new' for nil:NilClass`）、`TECSInfoAccessor/*` 2件の W1008、`class` の `__tool_info__`（P4 からの持ち越し）。

## P5k（2026-09-30）

**進捗（as of 2026-09-30、P5k）**: カーネル依存系プラグイン（HRP・FMP、続けて HRMP・HRP2・ATK1）の**正解データを採取**した。移植はしていない。P5h で見送った判断（2026-09-28、「着手するなら先に ASP3/HRP3 などの CDL で WSL の Ruby 版からオラクルケースを採取する」）の前半にあたる。外部リポジトリの `main` にコミット `9850ad0`（HRP・FMP の4ケース）と `91715a7`（HRMP・HRP2 の5ケース追加）と `312ad28`（ATK1 の2ケース追加）（いずれもプッシュなし）。以下の最初の4項目は `9850ad0` の分、「HRMP・HRP2 の追加」が `91715a7` の分、「ATK1 の追加」が `312ad28` の分。「プラグインの網羅状況」の計測ツールが `2214d49`。
- **採取したもの**: `tests/golden/kernel/`（約2.4MB）の4ケース、すべて終了コード0。`hrp3/blueninja_gcc/sample1`（生成物142ファイル）・`hrp3/ct11mpcore_gcc/sample1`（148）・`fmp3/zybo_gcc/sample1`（121）・`fmp3/zybo_gcc/tSample2`（162）。出力に `HRPPlugin`・`HRPHandlerPlugin`・`HRPObjectPlugin`・`HRPTaskPlugin`・`HRPSVCThroughPlugin`・`HRPSVCSignaturePlugin`・`HRPSVCBodyCellPlugin`、`FMPPlugin`・`FMPHandlerPlugin`・`FMPObjectPlugin` の痕跡があることを確認した。各ケースの `meta.json` の `tecsgen_args` に、`make -n tecs` で得た tecsgen の呼び出しを記録している。
- **方法**: `tools/golden/collect_kernel.py` と `cases_kernel.toml`。カーネルの SVN 作業コピー（`~/repo/svn-toppers-TECS-2/svn/toppers/<名前>/trunk`）を `svn export --native-eol LF` し、`configure.rb`（Ruby の `shell` gem が要る。WSL の `~/.gem` に導入）→ `make tecs` を再現する。`tecsgen` ディレクトリは移植元 r3304 に差し替える。同梱の r3306 は Ruby 3.2 で `tried to create Proc object without a block` になり、移植元とも版が違うため。カーネルのリポジトリ自体は r3306 のまま。WSL からの実行は `wsl_check.ps1 -KernelGolden <移植元の作業コピー>`（オプションとして追加）。
- **C プリプロセッサ**: 最初は交差コンパイラが無くホストの `gcc`（`make CC=gcc`）で採ったが、ユーザー指示で `gcc-arm-none-eabi`（13.2.1、apt の 15:13.2.rel1-2）を入れ、ターゲット本来の `arm-none-eabi-gcc` で採り直した。ホスト `gcc` 版との差は、tecsgen の呼び出し行（`--cpp "…"`）と、保存しない `tmp_*.h` のハッシュだけ。生成された `.c`・`.h`・`.cdl` の本体は4ケースとも同一だった。
- **再現性**: `arm-none-eabi-gcc` 版を2回続けて採り、`diff -r` で完全に同一（`environment.json` の `target_gcc` を含む）。ホスト `gcc` 版も2回で同一だった。
- **採取に約10分かかる**（`/mnt/e` への書き込みが遅い。プロセスは `v9fs_evict_inode` で待っていた）。原因の切り分けはしていない。
- **HRMP・HRP2 の追加（2026-09-30、`91715a7`）**: 合計9ケースになった。すべて終了コード0で、9ケースを2回続けて採り `diff -r` で完全に同一だった。
  - **HRMP**: `hrmp3+tecs` の `zybo_z7_gcc` の `sample1`（生成物155ファイル）・`tSample2`（200）。`HRMPKernelObjectPlugin`・`HRMPPlugin` の痕跡を確認した。`target/zybo_gcc` は `Makefile.target` が無く、`configure.rb` は通るが `make` が失敗するので一覧から外した（`dummy_gcc` は `GCC_TARGET` がコメントアウトされているので使っていない）。
  - **HRP2**: `ev3rt+tecs`（HRP2 ベースの `hr-tecs`）の `workspace/sample1`（347）・`sd`（276）・`bluetooth`（286）。`HRP2Plugin`・`HRP2TaskPlugin`・`HRP2HandlerPlugin`・`HRP2ObjectPlugin` の痕跡を確認した。アプリケーション CDL は `MrubyBridgePlugin` も使うので、mruby 系の使用例にもなる。`configure` は使わず（Perl 版で、古い構成）、ケースに `workdir` を指定して `make tecs` を実行する。同梱 tecsgen の置き換え先は `hr-tecs/tecsgen/tecsgen/`（`tecsgen_dest`）。`workspace/mruby_app` は `tecs` ターゲットが無く、`common` は Makefile が別物なので使っていない。
  - **`hrp2+tecs` 自体は使えない**: `obj_lm3sxxxx/sample1`・`obj_stm32p207/sample1` を移植元 r3304 の tecsgen で動かすと、`tSample1.cdl:138:16: G1016 syntax error near ')'` で止まり、HRP2 プラグインまで進まない。行は region の古い文法 `[domain(DOMAIN1), out_through(), in_through()]`。入力は変更していない。原因（文法が後の版で変わったのか、`-k euc` などの指定の問題か）は切り分けていない。
  - **道具**: `collect_kernel.py` が `configure` なしのケース（`workdir`）と `tecsgen_dest` に対応した。`make -n tecs` の出力から tecsgen の行を探す処理は、バックスラッシュで続く行もつなぐようにした。
- **ATK1 の追加（2026-09-30、`312ad28`）**: 合計11ケースになった。11ケースを2回続けて全件採り、`diff -r` で完全に同一だった（ATK1 の2ケースは絞り込み実行でも同一）。
  - **入力**: `atk1+tecs` の `tools/m16c-renesas/oaks16_mini_ecc2/sample.cdl`。`include/kernel.cdl` が `generate(ATK1EventPlugin, "")` ほか ATK1 のプラグインを使う。`sample`（生成物101ファイル）と `sample-U`（`-U` で最適化なし、101。両者で24ファイルの内容が違う）の2ケース。`ATK1KernelPlugin`・`ATK1TaskPlugin`・`ATK1ISRPlugin`・`ATK1AlarmPlugin`・`ATK1ResourcePlugin`・`ATK1EventPlugin` の実行を確認した。
  - **呼び出しの再構成**: Makefile が無く、tecsgen は Renesas の ProjectEditor（`.tmk` の tecsgen ターゲット）が呼ぶ（`tecsgen.exe -v -L -U -D TECS -c "$(CPP) -D NC30" -I… sample.c`）。NC30 が無く Windows のパスでもないので、r3304 向けに次のとおり置き換えた: 末尾の `sample.c` は `sample.cdl`（`.tmk` の誤記と判断、inferred）、プリプロセッサはホストの `gcc -E -D NC30`、`-L` は外す（r3304 では `-L` が引数を取り、`-L -U` を写すと `-U` が効かなくなる）、syslib の import に必要な `-I` を足す、`.tmk` の `-I…\r16c-renesas…` は存在しないパスなので使わない。コミット済みの古い `gen/` は消してから実行する。ケースには `make` を使わず `tecsgen_args` を直接書く形式を追加した。
  - **`ATK1EventPlugin` の限界**: プラグインは読み込まれ実行されるが、`tmp_ATK1EventPlugin_0.cdl`・`tmp_ATK1EventPlugin_post_code.cdl`・`EVENT_tecsgen.oil` は0バイト。`sample.cdl` にイベントを使うセルが無いため（inferred。`tEvent` 系のセルの有無だけで判断）。記録されているのは「イベントが無いとき何も出さない」経路だけで、生成ロジックの本体は検証できない。`ATK1DelayTaskPlugin` は atk1+tecs の CDL に使用箇所が無く、対象外（2026-10-01 に21パッケージ・カーネル5リポジトリ・hrp2+tecs の CDL を全検索しても、使う CDL は見つからなかった）。イベントを使う派生 CDL を作る案は、入力がリポジトリのものでなくなるため見送った（ユーザー判断、案1）。
  - **P5h で移植済みの ATK1 5本の追加の検証材料**になり得る（`sample` で Python 版と比べる）。未実施。
  - **道具（ほか）**: `--case` は `wsl_check.ps1 -KernelGolden … -PytestArgs '--case','atk1/*'` の形でしか届かない。`-KernelGolden` の後ろに直接書くと全ケースが再採取される。HRMP・HRP2 の採取（`91715a7`）の頃の「hrmp3 だけ」「ev3rt だけ」の実行も、実際は全件の再採取だった（結果は同一）。
- **プラグインの網羅状況（計測、2026-09-30、ツールは外部リポジトリ `2214d49`、プッシュなし）**: 正解データ（`test/` の155ケース＋カーネル11ケース）が、`tecslib/plugin/` のどのプラグインを実際に実行したかを、Ruby 版に差し込む計測フック（`tools/golden/plugin_trace.rb`）で数えた。実行は `wsl_check.ps1 -PluginCoverage <作業コピー>`（20〜40分）。プラグイン名を出力から検索する最初の方法は、`OpaqueMarshalerPlugin`・`CompositePlugin`・`MultiPlugin` など名前が出力に現れない経路を見落として39個を「痕跡なし」としたので捨てた。全件実行を2回行い、報告は51行すべて同一だった。2026-10-01 に、別セッションが採ったパッケージの正解データ16ケース（外部リポジトリ `87f772d`、Vault `a0886ab`。WSL の `~/Ccur/TECS-WG-DL` の21パッケージから。ケースごとに同じ計測フックの記録 `plugin_trace.txt` を保存している）を加えて再集計した。以下は**この再集計後（as of 2026-10-01）**の数と一覧。
  - **内訳**（プラグイン78個＋補助モジュール `lib/` 7個、正解データは `test/` 155ケース＋カーネル11ケース＋パッケージ16ケースの計182ケース）: 1回以上インスタンス化された48（09-30 の46から +2）、ロードされたが生成されていない13、一度もロードされなかった17（＋補助モジュール1）。
  - **正解データが無い（一度もロードされなかった）18件**（09-30 の20件から、`Mruby2CBridgePlugin`・`TECS2CBridgePlugin` が Mruby2C のケースで各6回生成されて外れた）:
    - HRP2 のカーネルオブジェクト系7: `HRP2AlarmHandlerPlugin`・`HRP2CyclicHandlerPlugin`・`HRP2DataqueuePlugin`・`HRP2EventflagPlugin`・`HRP2FixedSizeMemoryPoolPlugin`・`HRP2PriorityDataqueuePlugin`・`HRP2SemaphorePlugin`。使う CDL は hrp2+tecs の `include/kernel.cdl` で、その sample1 が古い文法（G1016）で止まるため届いていない。ev3rt+tecs は `HRP2Plugin`・`HRP2TaskPlugin`・`HRP2HandlerPlugin`・`HRP2ObjectPlugin` を使う。
    - HRP2・HRP のドメイン間通信系: `HRP2RPCPlugin`・`HRP2SVCPlugin`・`HRPRPCPlugin`、補助 `HRP2Cache`・`HRP2PostHook`、補助モジュール `lib/GenHRP2Marshaler`。
    - mruby 情報ブリッジ系3: `MrubyInfoBridgePlugin`・`MrubyInfoBridgeCellPlugin`・`MrubyInfoBridgeSignaturePlugin`（P5i で「対象ケースなし」としたものの残り）。**入力の手がかり**: Context の21パッケージとは別に `~/Ccur/TECS-WG-DL/tecsgen-1.9.1/tecsgen-1.9.1/test/mruby/` の `MrubyInfoBridge-test/test.cdl`（178〜180行）と `MrubyInfoBridge-SimpleSample/SimpleSample.cdl`（61行）が `generate(MrubyInfoBridgePlugin, TECSInfo, "exclude_port=eTECSInfo")` を使っている。実行できるかは未検証（`test/mruby` は、`mruby` ケースとして MRUBYPATH・ASP のソースツリーが無く採取を見送った経緯がある）。`MrubyInfoBridgeCellPlugin`・`MrubyInfoBridgeSignaturePlugin` は `MrubyInfoBridgePlugin`（振り分け）から呼ばれるので、同じ入力で同時に埋まる可能性がある（inferred）。
    - その他2: `TransparentMarshalerPlugin`（単体のマーシャラ。補助モジュール `GenTransparentMarshaler` はロード済み）・`ATK1DelayTaskPlugin`（使う CDL が未発見）。
  - **ロードされたが生成されていない13**: 基底クラス `CellPlugin`・`CelltypePlugin`・`ClassPlugin`・`CompositePlugin`・`DomainPlugin`・`MultiPlugin`（毎回ロードされる抽象クラス）、振り分け用 `CIfGenPlugin`・`CppIfGenPlugin`・`MrubyBridgePlugin`、カーネル系の基底・管理用 `HRMPPlugin`・`HRP2KernelObjectPlugin`・`HRPKernelObjectPlugin`・`HRPKernelObjectManager`。抜けとは判断していない（inferred。個別には検証していない）。
  - **薄いもの（生成が3回以下。as of 2026-10-01）**: `CIfGenCellPlugin`・`DataPumpHolderPlugin`・`MrubyBridgeCompositePlugin`・`OpaqueMarshalerPlugin`・`OpaqueRPCPlugin`・`RepeatJoinPlugin`（各3回）、`SignaturePlugin`（2回）。`C2TECSBridgePlugin` は Mruby2C のケースで増えて外れた。`ATK1EventPlugin` は生成されているが出力が空（前述。パッケージ版の atk1+tecs_1.0.0 でも `EVENT_tecsgen.oil` ほか3ファイルが0バイトで、変化なし）。
  - **残り18件の入力の探索（2026-10-01）**: Context の21パッケージ、カーネル5リポジトリ、hrp2+tecs の CDL・CDF を名前で全検索した（`generate(` 以外の書き方も拾う）。HRP2 のカーネルオブジェクト系7は hrp2+tecs の `include/kernel.cdl` だけ（古い文法で構文エラー、前述）。`ATK1DelayTaskPlugin`・`HRP2RPCPlugin`・`HRP2SVCPlugin`（hrp2+tecs の1件を除く）・`HRPRPCPlugin`・`TransparentMarshalerPlugin`・`HRP2Cache`・`HRP2PostHook`・`GenHRP2Marshaler` は、どの CDL にも名前が無い。`MrubyInfoBridge*` だけ上の手がかりがある。パッケージ側の選定記録（`tests/golden/packages/package_inventory.json`）も、残りのパッケージ5件（rx_ccrx は `ccrx.exe` が無く診断のみ、ほかは既に採ったプラグインの重複か参照なし）に新しいプラグインは無いとしている。
  - **正解データの無いプラグインの仕様書（移植元の仕様の読み先）**: HRP2 のカーネルオブジェクト系7（`HRP2SemaphorePlugin` ほか）は [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin]]、`HRP2RPCPlugin`・`HRP2SVCPlugin` は [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2DomainBoundaryPlugin]]、`HRPRPCPlugin` は [[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPDomainBoundaryPlugin]]、`MrubyInfoBridge*` 3件は [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin]]、`TransparentMarshalerPlugin` は [[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]]、`ATK1DelayTaskPlugin` は [[work/active/tecsgen-plugins/ATK1Plugin|ATK1Plugin]]。`HRP2Cache`・`HRP2PostHook`・`GenHRP2Marshaler` は専用の仕様書が無く、[[work/active/tecsgen-plugins/PluginCoverageAudit|PluginCoverageAudit]] に名前があるだけ。
  - **限界**: 判定はロードと生成の有無だけで、プラグイン内の全メソッド・全分岐を実行したかは見ていない。対象は今の182ケースだけ。この再集計は、パッケージ16ケースの `plugin_trace.txt` を手元で連結して `plugin_coverage.py` に渡したもので、`run_plugin_coverage.sh`（`wsl_check.ps1 -PluginCoverage`）はまだパッケージを含めていない（未対応）。
- **範囲外（次に採るなら）**: `ATK1EventPlugin` の生成ロジック（イベントのセルを使う入力が要る）、`ATK1DelayTaskPlugin`（使う CDL が未発見）、hrp3 の `sample2`、`hrp2+tecs` の sample1（文法エラーの原因調査が先）。Context に書いた `hr-tecs3`・`ssp+tecs` は、WSL に `trunk` が無かった（`~/repo/svn-toppers-TECS-2/svn/toppers/` 配下）。

## Related

- [[tecsgen-python3移植計画 — P5 進捗ログ]]
- [[tecsgen-python3移植計画]]
- [[tecsgen-python3]]
