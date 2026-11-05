---
date: 2026-08-14
description: "tecsgen 標準付属プラグイン群 ATK1*Plugin（7ファイル）の仕様書。OSEK/VDX 準拠 TOPPERS/ATK1 カーネルの OIL オブジェクト（OS/ALARM/TASK/ISR/RESOURCE/EVENT）を CDL セル属性から生成する celltype プラグイン群を横断的に扱う"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
  - plugin
---

# ATK1Plugin 仕様書（ATK1*Plugin ファミリー）

> [!info] 文書状態
> [[North Star]] の「未記載プラグイン」リストが1項目として挙げる「ATK1Plugin」は、実際には `tecslib/plugin/` 配下の独立した7ファイル（ATK1KernelPlugin・ATK1AlarmPlugin・ATK1TaskPlugin・ATK1ISRPlugin・ATK1ResourcePlugin・ATK1EventPlugin・ATK1DelayTaskPlugin）の集合である。[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] 執筆時点で「個別ノート化は要検討」と保留していた論点を、本ノートで決定する：**7ファイルとも `CelltypePlugin` を直接継承する同一アーキテクチャの派生（OSEK/VDX OIL オブジェクト1種を CDL セル属性から生成する）であり、[[reference/03-Resources/my-topic/wiki/tecs-plugin|my-topic wiki の既存カタログ]]も「ATK1Plugin」を単一項目として扱っている実績があるため、1本の横断ノートに統合する**（DRY — 7個の類似ファイルより、差分を表形式で見せる1ファイルの方が高凝集）。一次資料は `tecslib/plugin/ATK1*.rb`（7ファイル）・`tecslib/plugin/CelltypePlugin.rb`（親クラス）・`tecslib/core/componentobj/cell.rb`（`is_generate?`）・`tecslib/core/bnf.y.rb`（`attribute` 文法、989〜1076行）。ソースの実際の位置は [[TECSCDE外部仕様]] と同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。**このリポジトリには ATK1 プラグインを使った CDL の例・テストファイルが一件も存在しない**（`.cdl` 全文・リポジトリ全体を "ATK1" で検索していずれも0件、確認済み）ため、CDL 使用例は各プラグインの `gen_factory` 内 `get_join_list.get_item(:シンボル)` 呼び出しから逆算した推定であり、実動作するサンプルによる検証はできていない。

## 1. 概要

**ATK1*Plugin ファミリーは、OSEK/VDX 準拠の TOPPERS/ATK1（自動車用カーネル第1版）向けに、CDL セルの属性値から OIL（OSEK Implementation Language）オブジェクト定義と C言語アダプタコードを生成する celltype プラグイン群である。**

> [!warning] 訂正: 「AUTOSAR OS (ATK1) 対応」ではない
> [[tecsgen外部仕様]] 6.3 の既存の表記「AUTOSAR OS (ATK1) 対応」は誤り。ATK1*Plugin が生成する OIL オブジェクト種別（`OS` / `ALARM` / `TASK` / `ISR` / `RESOURCE` / `EVENT`）は OSEK/VDX OS 標準のオブジェクトモデルであり、AUTOSAR OS API 準拠ではない。TOPPERS プロジェクトにおいて AUTOSAR OS（AUTOSAR Classic Platform）準拠のカーネルは後継の **TOPPERS/ATK2** であり、TECS との統合は本ファミリーとは別の独立した取り組み（[[reference/03-Resources/my-topic/wiki/atk2-tecs|ATK2+TECS]] を参照。`atk2-tkernel`・`atk2-ttask` など別のセルタイプ群を使う、コード共有のない別系統）。本ノートでは 6.3 の表記もあわせて訂正する。

7ファイルはいずれも `CelltypePlugin` を直接継承し、対応する CDL セルタイプに `[generate(ATK1XxxPlugin, "options")]`（specifier 形式、[[tecsgen外部仕様]] 6.2 参照）で付与されることを前提とする。

## 2. 共通アーキテクチャ

### 2.1 継承関係と初期化

7ファイルすべてが `CelltypePlugin` を直接の親クラスとし、`initialize(celltype, option)` は `super` を呼ぶのみ（ATK1KernelPlugin と ATK1EventPlugin のみ、後述の理由でクラス変数を追加初期化する）。`option` 引数（プラグイン呼び出しの第2引数文字列）は `CelltypePlugin#initialize` が `@plugin_arg_str` に保存するが、**7ファイルのいずれも `@plugin_arg_str` を読み出すコードが存在しない**（grep で `option`/`plugin_arg_str` の使用箇所ゼロを確認）。つまり `[generate(ATK1AlarmPlugin, "任意の文字列")]` の第2引数は構文上受理されるが、現状は完全に無視される。

### 2.2 属性値の取得

CDL の `attribute { ... };` ブロック（`bnf.y.rb` 989〜1076行、[[TECSCDE外部仕様 - 11 用語集#11. 用語集|属性]]）で celltype 側が宣言した属性を、cell 本体で `属性名 = 値;` の形で代入する。プラグイン側は `cell.get_join_list.get_item(:属性名シンボル)` で値を取得する（結合と属性代入は内部的に同じ `Join` オブジェクトとして格納される — [[work/active/tecsgen-plugins/NotifierPlugin|NotifierPlugin]] の結合先解決と同じ仕組み）。

### 2.3 生成対象の判定 — `is_generate?`

6プラグイン（ATK1EventPlugin を除く）は `gen_factory` 内で `if cell.is_generate?` によって出力対象セルをフィルタする。`Cell#is_generate?` は「現在コード生成中の region の直下にセルが属するか」を判定する（`cell.rb` 862〜874行）。この機構は [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] のドメイン境界（region の `domain(...)` 指定子）と同じ region の仕組みに依拠しており、意味解析後・コード生成前でないと呼び出せない（呼ぶと例外）。

### 2.3b 呼び出し経路 — どこから `ATK1TaskPlugin.rb` が呼ばれるか（2026-10-12 確認、tecsgen-rb 基準）

`ATK1*Plugin.rb` はどこからも直接 `require` されない。`MANIFEST_tecsgen_body` に出てくるのは配布物の一覧で、呼び出しではない。CDL の `generate` 指定が起点で、実行時に動的にロードされる。

1. **指定**: `include/kernel.cdl` の `[active, generate(ATK1TaskPlugin,"")] celltype tTask`（ほかのセルタイプも同様）
2. **ロード**: CDL 解析中にセルタイプが `generate` を受けると、`componentobj/celltypeModule.rb:60` が `load_plugin(plugin_name, plugin_class)` を呼ぶ。`core/pluginModule.rb:65` の `load_plugin` が `require_tecsgen_lib("ATK1TaskPlugin.rb")` でファイルを読み、`Object.const_get` でクラスを得て `CelltypePlugin` の派生か確かめる。ロード済みは重複して読まず、失敗は `P2001`〜`P2003`。`-v` では `load 'ATK1TaskPlugin.rb'` と出る
3. **生成**: コード生成の最後に `core/generate.rb:3285` の `generate_factory_header_post` が `@generate_list` を回し、各プラグインの `gen_factory(f)` を呼ぶ。`TASK_tecsgen.oil` はここで書かれる
4. 他の種類のプラグインのロード元: Signature は `signature.rb:314`、Cell は `cell.rb:683`、Through は `join.rb:744`、Domain は `domaintype.rb:62`、Class は `classtype.rb:63`

Python 版の対応は `src/tecsgen/plugin/ATK1TaskPlugin.py`（`importlib` による名前解決。[[tecsgen-python3内部仕様 - 09 プラグイン機構]]）。

**既知の制約（2026-10-12 確認）**: `gen_factory` の `extended_task_count` は `++extended_task_count;`（`ATK1TaskPlugin.rb:156`）で増やすつもりだが、Ruby の `++x` は `+(+x)` で何もしない。イベント付きのタスクが 2 本以上あると、全部が id 1 になり `S3003`（id 衝突）になる。TOPPERS Automotive Kernel アプリケーションノートのサンプル（MainTask・Task2・Task3 の 3 本がイベント付き）は、Ruby 版・Python 版とも `S3003` で止まる。Python 版は Ruby 版の挙動をそのまま再現している。

### 2.4 出力の形

各プラグインは `gen_factory` で次の2種類を出力する：
1. **OIL ファイル**（`CFile.open` で新規書き出し、`#{$gen}/<SECTION>_tecsgen.oil`）— OSEK OIL 構文でオブジェクトを列挙
2. **C アダプタコード**（`AppFile.open` で追記、文字コード変換なし）— コールバック関数・宣言等

## 3. 7プラグイン一覧

| プラグイン | OIL オブジェクト | 生成ファイル | 主な属性（`get_join_list` で参照するシンボル） | 備考 |
|---|---|---|---|---|
| `ATK1KernelPlugin` | `OS` | `Kernel_tecsgen.oil` + `tKernel_tecsgen.c` 追記 | `status`・`useStartupHook`・`useErrorHook`・`useShutdownHook`・`usePreTaskHook`・`usePostTaskHook`・`useGetServiceId`・`useParameterAccess`・`useResourceScheduler` | 唯一 `self.gen_post_code` で `useResourceScheduler` が TRUE のセルに対し `RES_SCHEDULER` という `tResource` セルを CDL コードとして自動追記する（`@@cell_list` に全セルを蓄積） |
| `ATK1AlarmPlugin` | `ALARM` | `ALARM_tecsgen.oil` + `tAlarm_tecsgen.c` 追記 | `counter`・`action`（`SETEVENT`/`ACTIVATETASK`/`ALARMCALLBACK` の3種、値により `task`/`event`/`callbackName` を追加参照）・`autoStart`・`alarmTime`・`cycleTime`・`appMode` | `action` の値で分岐する唯一のプラグイン |
| `ATK1TaskPlugin` | `TASK` | `TASK_tecsgen.oil` + `tTask_tecsgen.c` 追記 | `autoStart`・`appMode`・`priority`・`activation`・`schedule`・`event`（配列）・`resource`（配列）・`message`（配列）・`stackSize` | `event` 配列に `OMISSIBLE` 以外の値があると `extended_task_count` を使い `set_specified_id` で拡張タスク番号を採番 |
| `ATK1ISRPlugin` | `ISR` | `ISR_tecsgen.oil` | `category`・`priority`・`entryNumber`（CDL 予約語 `entry` と衝突するため `Number` を付加）・`resource`（配列）・`message`（配列） | — |
| `ATK1ResourcePlugin` | `RESOURCE` | `RESOURCE_tecsgen.oil` + `<celltype名>_factory.h` | `property`（`LINKED` の場合 `linkedResource` を追加参照） | セル名が `RES_SCHEDULER` の場合は特別扱い（`set_specified_id(1)`、OIL 出力と `DeclareResource` をスキップ）— `ATK1KernelPlugin` が自動生成するセルとの結線点 |
| `ATK1EventPlugin` | `EVENT` | `EVENT_tecsgen.oil` | `mask`（`AUTO` 指定で自動ビット採番、未指定なら32固定値で `Join` を新規作成） | **他6種と構造が異なる唯一のクラス**。`new_cell` では何もせず、`initialize` で `@@instancies`（クラス変数の配列）に自分自身を登録し、`self.gen_post_code` で全インスタンスの `gen_oil_code` をまとめて呼ぶ（＝全セルタイプの意味解析完了後に一括出力）。かつ `is_generate?` によるフィルタがコメントアウトされており、有効化されていない（全セルが対象になっている可能性） |
| `ATK1DelayTaskPlugin` | なし（専用 OIL セクションを持たない） | `tDelayTaskBody_factory.h` 追記のみ | `event`（`&` プレフィクスがあれば除去） | 唯一 OIL ファイルを生成しない。`DeclareEvent(...)` の宣言だけを出力する — 遅延タスク（delay task）に紐づくイベントを `ATK1TaskPlugin`／`ATK1EventPlugin` が別途扱う `TASK`/`EVENT` オブジェクトと結びつけるための補助と推測されるが、`ATK1TaskPlugin` 側との直接の呼び出し関係はソース上に見当たらない（要確認事項として残す） |

## 4. 使用例（推定・未検証）

> [!warning] 未検証
> 本節はソースコードの `get_join_list` 呼び出しから逆算した CDL 記述例であり、実際に tecsgen へ通したことはない。実働サンプルが見つかり次第、置き換えること。

```tecs-cdl
celltype tAlarm {
    attribute {
        [omit] char *counter;
        [omit] char *action;      // "SETEVENT" | "ACTIVATETASK" | "ALARMCALLBACK"
        [omit] char *task;
        [omit] char *event;
        [omit] char *callbackName;
        [omit] bool  autoStart;
        [omit] int   alarmTime;
        [omit] int   cycleTime;
    };
};

[generate(ATK1AlarmPlugin, "")]
cell tAlarm MyAlarm {
    counter    = "SysTimerCnt";
    action     = "ACTIVATETASK";
    task       = "MyTask";
    autoStart  = TRUE;
    alarmTime  = 100;
    cycleTime  = 1000;
};
```

## 5. 制約・注意点

- **CDL 実例ゼロ**: リポジトリ内に ATK1 系プラグインを使う `.cdl` ファイル・テストが一件もない（HRP2Plugin/NotifierPlugin と異なり、参照できる実例がない）。属性名の綴り・型はソースの `get_join_list.get_item` 呼び出しから読める範囲でしか確認できていない。
- **`option` 引数は未使用**: 7ファイルとも `[generate(...)]` の第2引数文字列を読み出していない。将来の拡張余地として残っているだけの可能性がある。
- **ATK2 と混同しないこと**: 本ファミリーは OSEK/VDX 準拠 ATK1 向けであり、AUTOSAR OS 準拠の ATK2（[[reference/03-Resources/my-topic/wiki/atk2-tecs|ATK2+TECS]]）とは無関係な別系統。
- **ATK1EventPlugin の構造差異**: `self.gen_post_code` + `@@instancies` パターンは `ATK1KernelPlugin` の `@@cell_list` パターンと類似するが、目的が異なる（Kernel 側はセル自動追加、Event 側は全セルタイプ横断でのビットマスク採番）。
- **ATK1DelayTaskPlugin の位置づけ未確定**: 他プラグインとの結線関係がソースから読み取れず、5章の表に「要確認事項」として明記した。

## Related

- [[tecsgen外部仕様]] — 6.2 プラグイン呼び出し規約・6.3 標準付属プラグイン一覧
- [[work/active/tecsgen-plugins/HRP2Plugin]] — 同じ celltype プラグイン系統、region/`is_generate?` の参照元
- [[work/active/tecsgen-plugins/NotifierPlugin]] — 結合と属性代入が同じ `Join` 機構である点の参照元
- [[reference/03-Resources/my-topic/wiki/tecs-plugin]] — プラグイン一覧のカタログページ（ATK1Plugin を単一項目として扱う既存分類）
- [[reference/03-Resources/my-topic/wiki/atk2-tecs]] — 対比対象。AUTOSAR OS 準拠の別系統
- [[North Star]] — カーネル対応プラグイン仕様書化の進捗管理
