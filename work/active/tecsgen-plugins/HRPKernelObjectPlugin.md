---
date: 2026-08-15
description: "HRPKernelObjectPlugin の具象サブクラス3種（HRPTaskPlugin・HRPObjectPlugin・HRPHandlerPlugin）仕様。単機能1種＋テーブル/分岐駆動の汎用2種という二層構造がHRP2と同型と判明、HRPファミリー10/10ファイル完走"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# HRPKernelObjectPlugin 具象サブクラス群（HRPTaskPlugin・HRPObjectPlugin・HRPHandlerPlugin）

[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPDomainBoundaryPlugin]] §2 で扱った抽象基底 `HRPKernelObjectPlugin` の具象サブクラス3種を執筆。この3種の完成で **`HRP`（無印）ファミリーは10/10ファイル完走**。

## 1. 全体構造 — HRP2との二層構造の一致

[[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin 具象サブクラス群]]で見つけた「単機能プラグイン＋テーブル/分岐駆動の汎用プラグイン」という二層構造が、HRPでも**同型**であることが確認できた。ただし規模が違う。

| 観点 | HRP2 | HRP（無印） |
|---|---|---|
| 単機能プラグイン数 | 8（Task/Semaphore/Eventflag/Dataqueue/PriorityDataqueue/FixedSizeMemoryPool/AlarmHandler/CyclicHandler） | **1（Task のみ）** |
| 汎用プラグイン数 | 2（オブジェクト系・ハンドラ系） | 2（同じ切り分け） |
| 汎用プラグインの実装方式 | `HRP2ObjectPlugin`: `@@api` ハッシュ / `HRP2HandlerPlugin`: `elsif` 分岐 | `HRPObjectPlugin`: `@@api` ハッシュ（同じ変数名）/ `HRPHandlerPlugin`: `elsif` 分岐（同じ方式） |
| ファイル総数 | 10（8+2） | 3（1+2） |

HRP2では「単機能プラグインが存在しないオブジェクト種別」を汎用プラグインが補完する構造だったが、HRPでは**単機能プラグインがTaskしかなく**、Semaphore/Eventflag/Dataqueue/PriorityDataqueue/FixedSizeMemoryPool/Mutex/Kernel/MessageBufferの全てが最初から`HRPObjectPlugin`の`@@api`テーブル一本に統合されている。単機能プラグインをHRP2と同数だけ複製せず、テーブル駆動側に最初から寄せた設計 — HRP2からの複製元であることは[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で確認済みだが、この3ファイルは複製というより「HRP2の二層構造を踏襲しつつ、単機能側を大幅に間引いた」形になっている。

## 2. HRPTaskPlugin（336行中108行、単機能）

`< HRPKernelObjectPlugin`。`CRE_TSK`/`SAC_TSK` を1組だけ生成する、HRP2TaskPluginと同型の単機能プラグイン。

- `new_cell`: `cell.get_region.get_domain_root.get_domain_type.get_option` が `"OutOfDomain"` ならエラー（`HRP9999`固定コード）。タスクは無所属であってはならないが、**kernel/userどちらのドメインでも許容**——後述のHRPHandlerPluginが`"kernel"`ドメインのみに限定するのと対照的。
- `print_cfg_cre`: `systemStackSize` が `"0"` かどうかで2種類の `CRE_TSK` マクロ形（システムスタック定義の省略あり/なし）を出し分け。
- `print_cfg_sac`: `SAC_TSK` を4本の `accessPattern` 付きで出力。

## 3. HRPObjectPlugin（テーブル駆動、汎用）

`< HRPKernelObjectPlugin`。`@@api` ハッシュで `@plugin_arg_str` → `[マクロ接尾辞, :id, :attribute, ...]` の対応表を持つ、HRP2ObjectPluginと同じ設計。

```ruby
@@api = {
    "SEMAPHORE"          => ["SEM", :id, :attribute, :initialCount, :maxCount],
    "EVENTFLAG"          => ["FLG", :id, :attribute, :flagPattern],
    "DATAQUEUE"          => ["DTQ", :id, :attribute, :dataCount, :dataqueueManagementBuffer],
    "PRIORITY_DATAQUEUE" => ["PDQ", :id, :attribute, :dataCount, :maxDataPriority, :priorityDataqueueManagementBuffer],
    "FIXED_SIZE_MEMORYPOOL" => ["MPF", :id, :attribute, :blockCount, :blockSize, :memoryPool, :memoryPoolManagementBuffer],
    "KERNEL"             => ["SYS"],
    "MESSAGE_BUFFER"     => ["MBF", :id, :attribute, :maxMessageSize, :bufferSize, :mbfmb],
    "MUTEX"              => ["MTX", :id, :attribute, :ceilingPriority]
}
```

- `KERNEL` は特別扱い：`CRE_SYS`/`SAC_SYS` はそもそも生成しない（`print_cfg_cre`/`print_cfg_sac` とも `@plugin_arg_str != "KERNEL"` の分岐を通らず何もしない）。ただし `print_cfg_sac` の `else` 節では `SAC_SYS` を id なしの形で出力するコードが存在する — `print_cfg_cre` 側に対応する `else` 節がなく非対称。KERNELセルのSACが実際に生成されるパスがあるのかは未確認。
- `MUTEX` のみ可変長引数：`val[:attribute]` に `TA_CEILING` 属性が含まれるかどうかで `:ceilingPriority` を引数リストから外す (`slice_end = -2` vs `-1`)。天井優先度が指定されていない排他制御には天井優先度引数を省略する、という条件付き引数生成——他の7エントリにはない唯一の可変長パターン。
- **注意**: この `@@api` テーブルの内容（特に `MUTEX` の存在）が [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2ObjectPlugin]] の等価テーブルと完全一致するかは本セッションで再検証していない。HRP2側のサマリでは Mutex への言及がなく、HRP固有の追加である可能性がある——確認は今後の課題。

## 4. HRPHandlerPlugin（分岐駆動、汎用）

`< HRPKernelObjectPlugin`。`elsif @plugin_arg_str == "..."` 分岐でハンドラ系6種（`CONFIG_INT`/`ISR`/`DEF_INH`/`DEF_EXC`/`INIT_ROUTINE`/`TERM_ROUTINE`）を1ファイルにまとめる、HRP2HandlerPluginと同じ設計。

- `new_cell`: ドメインオプションが `"kernel"` **以外**（`OutOfDomain` はもちろん `"user"` も含む）ならエラー。HRPTaskPluginより厳格——ハンドラ／割込み関連セルはkernelドメイン限定。
- 6分岐それぞれが対応するマクロ（`CFG_INT`/`CRE_ISR`/`DEF_INH`/`DEF_EXC`/`ATT_INI`/`ATT_TER`）を生成。[[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2HandlerPlugin]] のカバー範囲（KERNEL/SYS, MESSAGE_BUFFER, CONFIG_INT, ISR, INIT_ROUTINE, TERM_ROUTINE）と比べると、HRPHandlerPluginは `KERNEL`/`MESSAGE_BUFFER` を持たない代わりに `DEF_INH`（割込みハンドラ定義）・`DEF_EXC`（CPU例外ハンドラ定義）を独自に持つ——ISRとは別に低レベル割込み/例外ハンドラの型が用意されている、HRP2側では確認していない分岐。
- `print_cfg_sac` の `ISR` 分岐に**著者コメント付きの意図的な死コード**が残る：

  ```ruby
  # kernel.cdl の tISR で accessPattern1 ～ accessPattern4 が定義されているときの名残。
  # accessPattern1 が定義されていない場合、ここへは来ない．復活したときに備えて残しておく．
  # file.puts "SAC_ISR(...)"
  puts "*** Unsupported *** SAC_ISR(...)"
  ```

  [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]や[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPDomainBoundaryPlugin]]で見てきた「消し忘れで理由不明な死コード」群とは性質が異なり、**なぜ残しているかを著者自身が明記した死コード**——「将来accessPattern1がkernel.cdlのtISRに復活したら使う」という設計意図が読み取れる、この一連の調査で初めて見つかった「説明付き死コード」の例。

## 5. HRP9999プレースホルダコードの再確認

HRPTaskPluginの `new_cell` とHRPHandlerPluginの `new_cell` はどちらもエラーコードとして汎用の `HRP9999` を使う（HRPHandlerPluginは実際にはコード番号を出力せず文字列のみ）。[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPDomainBoundaryPlugin]] §7で指摘した「HRP9999が生成系コードで多用され、HRPSVCSignaturePlugin/HRPSVCBodyCellPluginのような専用コード体系（HSV/HSW/HSI）が整備されていない」傾向は、このカーネルオブジェクト生成系にも同様に当てはまる。

## 6. 制約・未確認事項

- `HRPObjectPlugin`の`@@api`テーブルとHRP2ObjectPluginの対応テーブルとの厳密な差分比較（特にMUTEXエントリの有無）は未実施。
- `KERNEL`エントリの`print_cfg_sac`の`else`節が実際に到達可能か（`print_cfg_cre`側に対応する処理がない非対称性）は未検証。
- これでHRPファミリーは10/10ファイル完了。`FMP`・`HRMP`の2ファミリーは引き続き未着手・未サイジング。

## Related

- [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin・HRPKernelObjectManager]]
- [[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPKernelObjectPlugin・HRPRPCPlugin・HRPSVCThroughPlugin・HRPSVCSignaturePlugin・HRPSVCBodyCellPlugin]]
- [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin 具象サブクラス群]]
- [[tecsgen外部仕様]]
