#!/usr/bin/env python3
"""Compile raw TECS articles into wiki pages with entity extraction."""

import os
import re
from pathlib import Path
from datetime import date

TODAY = date.today().isoformat()
WIKI_ROOT = Path(__file__).parent.parent
RAW_ARTICLES = WIKI_ROOT / "raw" / "articles"
WIKI_DIR = WIKI_ROOT / "wiki"
LOG_FILE = WIKI_ROOT / "log.md"

# ------------------------------------------------------------------ #
# Entity knowledge base: term → wiki-page slug
# ------------------------------------------------------------------ #
CONCEPT_MAP = {
    # Core TECS model
    "TECS": "tecs-overview",
    "組込みコンポーネントシステム": "tecs-overview",
    "コンポーネントモデル": "tecs-overview",
    "TECS CDL": "tecs-cdl",
    "CDL": "tecs-cdl",
    "コンポーネント記述言語": "tecs-cdl",
    "CDL ファイル": "tecs-cdl",
    "シグニチャ": "tecs-signature",
    "signature": "tecs-signature",
    "セルタイプ": "tecs-celltype",
    "celltype": "tecs-celltype",
    "複合セルタイプ": "tecs-composite-celltype",
    "セル": "tecs-cell",
    "組上げ記述": "tecs-cell",
    "呼び口": "tecs-port",
    "受け口": "tecs-port",
    "ポート": "tecs-port",
    "ネームスペース": "tecs-namespace",
    "リージョン": "tecs-region",
    "TCD": "tecs-tcd",
    "コンポーネント図": "tecs-tcd",
    # Tools
    "tecsgen": "tecsgen",
    "TECS ジェネレータ": "tecsgen",
    "tecsflow": "tecsflow",
    "tecsmerge": "tecsmerge",
    # Plugins
    "プラグイン": "tecs-plugin",
    "NotifierPlugin": "plugin-notifier",
    "MrubyBridgePlugin": "plugin-mruby-bridge",
    "MrubyInfoBridgePlugin": "plugin-mruby-info-bridge",
    "C2TECSBridgePlugin": "plugin-c2tecs",
    "RepeatCellPlugin": "plugin-repeat-cell",
    # RTOS integration
    "ASP3": "asp3-tecs",
    "ASP3+TECS": "asp3-tecs",
    "ATK2": "atk2-tecs",
    "ATK2+TECS": "atk2-tecs",
    "mruby": "mruby-tecs",
    "ev3rt": "mruby-ev3rt-tecs",
    "GR-PEACH": "mruby-gr-peach-tecs",
    "TINET": "tinet-tecs",
    "TLSF": "tlsf-tecs",
    # ASP3 cell types
    "tTask": "asp3-ttask",
    "tEventflag": "asp3-teventflag",
    "tDataqueue": "asp3-tdataqueue",
    "tSemaphore": "asp3-tsemaphore",
    "tISR": "asp3-tisr",
    "tPriorityDataqueue": "asp3-tprioritydataqueue",
    "tFixedSizeMemoryPool": "asp3-tfixedsizememorypool",
    "tInitializeRoutine": "asp3-tinitializeroutine",
    "tTerminateRoutine": "asp3-tterminateroutine",
    # ATK2 cell types
    "tKernel": "atk2-tkernel",
    "tAlarm": "atk2-talarm",
    "tCounter": "atk2-tcounter",
    "tResource": "atk2-tresource",
    # Implementation model
    "セルタイプコード": "imp-celltype-code",
    "初期化コード": "imp-initialize",
    "ファクトリ": "imp-factory",
    "アロケータ": "imp-allocator",
    "FOREACH_CELL": "imp-foreach-cell",
}

# Concept page definitions: slug → (title, description, domain_tags, details)
CONCEPT_PAGES = {
    "tecs-overview": (
        "TECS (組込みコンポーネントシステム)",
        "TOPPERSプロジェクトの組込みコンポーネントシステム。CDL記述・tecsgenによるコード生成・RTOSとの連携を中核とする。",
        ["tecs", "toppers", "rtos", "embedded"],
        """\
TECS（Toppers Embedded Component System）は、TOPPERSプロジェクトが開発した組込みシステム向けコンポーネントシステムです。

## 主要構成要素

- [[tecs-cdl]] — コンポーネント記述言語 (TECS CDL)
- [[tecs-celltype]] — セルタイプ（コンポーネントの型）
- [[tecs-cell]] — セル（コンポーネントのインスタンス）
- [[tecs-signature]] — シグニチャ（インタフェース定義）
- [[tecs-port]] — ポート（呼び口・受け口）
- [[tecs-tcd]] — コンポーネント図 (TCD)
- [[tecsgen]] — TECSジェネレータ

## RTOS連携

- [[asp3-tecs]] — ASP3+TECS
- [[atk2-tecs]] — ATK2+TECS
- [[mruby-tecs]] — mruby+TECS
- [[tinet-tecs]] — TINET+TECS
- [[tlsf-tecs]] — TLSF+TECS

## バージョン履歴

V1.4.0〜V1.7.0 で機能追加。詳細は [[tecs-versions]] 参照。

## Counter-Arguments and Gaps

- TECS仕様書のアップデートは一時中断されている（ドキュメント上の注記より）
- TECS ジェネレータ生成コードリファレンスマニュアルは未作成 (to be written)
""",
    ),
    "tecs-cdl": (
        "TECS CDL (コンポーネント記述言語)",
        "TECSのコンポーネントを記述するためのドメイン固有言語。拡張子 .cdl、C言語文法と親和性あり。",
        ["tecs", "cdl", "dsl"],
        """\
TECS CDL（Component Description Language）は、TECSコンポーネントを記述するためのドメイン固有言語です。

## 特徴

- 拡張子: `.cdl`
- 文字コード: UTF-8（7bit ASCII互換文字コードも可）
- C言語文法と親和性のある記述形式

## 記述内容（記述順）

1. 前置部 — `import` / `import_C` 等
2. [[tecs-signature]] — シグニチャ記述
3. [[tecs-celltype]] — セルタイプ記述
4. [[tecs-composite-celltype]] — 複合セルタイプ記述
5. [[tecs-cell]] — 組上げ記述（セル記述）
6. [[tecs-namespace]] — ネームスペース記述
7. [[tecs-region]] — リージョン記述

## ツール

- [[tecsgen]] — CDLファイルを入力としてインタフェースコードを生成

## Counter-Arguments and Gaps

- sjis等のマルチバイト文字コードは動作保証外
- 未記載事項が存在する（CDLref_undoc参照）
""",
    ),
    "tecs-signature": (
        "シグニチャ (Signature)",
        "TECSにおけるインタフェース定義。呼び口・受け口の型を定義し、関数の集合として表現される。",
        ["tecs", "interface"],
        """\
シグニチャは、TECSコンポーネントのインタフェースを定義する記述単位です。

## 概要

- 関数の集合として定義
- [[tecs-port]]（呼び口・受け口）の型として使用
- [[tecs-celltype]] に含まれる

## 構文例

```cdl
signature sTask {
    ER activate(void);
    ER_UINT cancelActivate(void);
    ER terminate(void);
};
```

## See Also

- [[tecs-celltype]]
- [[tecs-port]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecs-celltype": (
        "セルタイプ (Celltype)",
        "TECSコンポーネントの型定義。シグニチャ・属性・変数・呼び口・受け口を持つ。",
        ["tecs", "component"],
        """\
セルタイプは、TECSコンポーネントの型を定義する記述単位です。

## 構成要素

- [[tecs-signature]]（シグニチャ）— 受け口・呼び口の型
- 属性 (attribute) — コンパイル時定数
- 変数 (var) — 実行時状態
- [[tecs-port]] — 呼び口 (call) / 受け口 (entry)

## 複合セルタイプ

[[tecs-composite-celltype]] は、複数のセルをひとまとめにして1つのセルタイプとして扱う仕組み。

## 実装

[[imp-celltype-code]] — セルタイプコードで実装を記述。

## See Also

- [[tecs-cell]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecs-composite-celltype": (
        "複合セルタイプ (Composite Celltype)",
        "複数のセルをまとめて1つのセルタイプとして扱うTECSの構造。内部結合を隠蔽できる。",
        ["tecs", "component"],
        """\
複合セルタイプは、複数のセルを束ねて1つの[[tecs-celltype]]として扱うTECSの構造です。

## 特徴

- 内部の[[tecs-cell]]結合を外部から隠蔽
- [[tecs-plugin]]でも利用される（compositeプラグイン）

## See Also

- [[tecs-celltype]]
- [[tecs-cell]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecs-cell": (
        "セル (Cell) / 組上げ記述",
        "セルタイプをインスタンス化したTECSコンポーネント。組上げ記述でセル間を結合する。",
        ["tecs", "component"],
        """\
セルは、[[tecs-celltype]]をインスタンス化したTECSコンポーネントです。

## 組上げ記述（セル記述）

```cdl
cell tTask MyTask {
    attribute = C_EXP("TA_ACT");
    stackSize = 1024;
    priority = 42;
    cTaskBody = MyCell.eTaskBody;
};
```

## セル間結合

- `cXxx = OtherCell.eXxx;` の形式で[[tecs-port]]を接続

## See Also

- [[tecs-celltype]]
- [[tecs-signature]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecs-port": (
        "ポート (呼び口・受け口)",
        "TECSコンポーネント間の接続点。呼び口(call)は依存関係を、受け口(entry)はサービス提供を表す。",
        ["tecs", "interface"],
        """\
ポートは、TECSコンポーネント間の接続点です。

## 種類

| 種別 | キーワード | 役割 |
|------|-----------|------|
| 呼び口 | `call` | 他のセルのサービスを呼び出す側 |
| 受け口 | `entry` | サービスを提供する側 |

## 非タスクコンテキスト

タスクコンテキスト外では `ei` プレフィックスの受け口を使用（例: `eiTask`）。

## See Also

- [[tecs-signature]]
- [[tecs-celltype]]
- [[tecs-cell]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecs-namespace": (
        "ネームスペース",
        "TECSにおける名前衝突防止機構。シグニチャ・セルタイプ・複合セルタイプの名前空間を分離する。",
        ["tecs", "namespace"],
        """\
ネームスペースは、[[tecs-signature]]・[[tecs-celltype]]・複合セルタイプの名前衝突を防ぐTECSの機構です。

## See Also

- [[tecs-cdl]]
- [[tecs-region]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecs-region": (
        "リージョン",
        "TECSにおけるセルのレイアウト管理と名前衝突防止の機構。メモリ保護環境での利用を想定。",
        ["tecs", "region", "memory-protection"],
        """\
リージョンは、[[tecs-cell]]のレイアウトと名前衝突防止を目的としたTECSの機構です。メモリ保護環境での利用を主に想定しています。

## See Also

- [[tecs-cdl]]
- [[tecs-namespace]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecs-tcd": (
        "TECS コンポーネント図 (TCD)",
        "TECSコンポーネントの構造を視覚的に表現する図法。セル・ポート・結合を図示する。",
        ["tecs", "diagram"],
        """\
TECS コンポーネント図（TCD）は、[[tecs-cell]]・[[tecs-port]]・セル間の結合を視覚的に表現する図法です。

## See Also

- [[tecs-cell]]
- [[tecs-celltype]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tecsgen": (
        "tecsgen (TECS ジェネレータ)",
        "TECS CDLファイルからインタフェースコードを生成するツール。Rubyスクリプトとして動作。",
        ["tecs", "tool", "codegen"],
        """\
tecsgenは、[[tecs-cdl]]記述のCDLファイルを入力として、Cのインタフェースコードを生成するTECSジェネレータです。

## 動作環境

- Rubyスクリプトとして動作
- V1.3以降: exerb版は廃止
- Cプリプロセッサ（デフォルト: `gcc -E -D TECSGEN`）を使用

## 主要オプション

| オプション | 説明 |
|-----------|------|
| `-D` | Cマクロ定義 |
| `-G` | コード生成リージョン限定 |
| `-I` | インポートパス指定 |
| `-L` | Rubyライブラリパス |
| `-R` | RAM初期化コード生成 |
| `-U` | 最適化無効 |

## 生成ファイル

- `Makefile.templ` — ビルド設定テンプレート
- `global_tecsgen.h` — グローバルヘッダ（`INITIALZE_TECS()`マクロを含む）

## See Also

- [[tecs-cdl]]
- [[tecsflow]]
- [[tecsmerge]]

## Counter-Arguments and Gaps

- V1.3.1.0時点の実装に対応（最新版との乖離あり）
""",
    ),
    "tecsflow": (
        "tecsflow",
        "TECSの実行フロー解析・可視化ツール。V1.7.0で追加。",
        ["tecs", "tool"],
        """\
tecsflowは、TECSコンポーネントの実行フローを解析・可視化するツールです。V1.7.0で追加されました。

## See Also

- [[tecsgen]]
- [[tecs-overview]]

## Counter-Arguments and Gaps

詳細ドキュメントは未作成。
""",
    ),
    "tecsmerge": (
        "tecsmerge",
        "複数のTECS CDL記述をマージするツール。",
        ["tecs", "tool"],
        """\
tecsmergeは、複数の[[tecs-cdl]]記述をマージするツールです。

## See Also

- [[tecsgen]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

詳細ドキュメントは未作成。
""",
    ),
    "tecs-plugin": (
        "TECS プラグイン",
        "tecsgenの機能を拡張するプラグイン群。カーネル対応・mrubyブリッジ・RPC・トレース等。",
        ["tecs", "plugin"],
        """\
TECSプラグインは、[[tecsgen]]の機能を拡張するモジュールです。

## 種類

### カーネル対応プラグイン

- NotifierPlugin (ASP3)
- ATK1Plugin, HRP2Plugin（未作成）

### mrubyブリッジプラグイン

- [[plugin-mruby-bridge]] — MrubyBridgePlugin
- [[plugin-mruby-info-bridge]] — MrubyInfoBridgePlugin

### RPCプラグイン

- TransparentRPCPlugin, OpaqueRPCPlugin, SharedRPCPlugin（未作成）

### その他

- [[plugin-repeat-cell]] — RepeatCellPlugin
- [[plugin-c2tecs]] — C2TECSBridgePlugin
- TracePlugin, TLVTracePlugin（未作成）

## See Also

- [[tecsgen]]
- [[tecs-overview]]

## Counter-Arguments and Gaps

多くのプラグインリファレンスが未作成 (to be written)。
""",
    ),
    "asp3-tecs": (
        "ASP3+TECS",
        "TOPPERSのASP3カーネルをTECSコンポーネントとして扱うための統合。カーネルオブジェクトをセルで管理。",
        ["tecs", "asp3", "rtos"],
        """\
ASP3+TECSは、TOPPERS/ASP3カーネルのオブジェクトを[[tecs-cell]]として扱うための統合です。

## 提供セルタイプ

| セルタイプ | 説明 |
|-----------|------|
| [[asp3-ttask]] | タスク |
| [[asp3-teventflag]] | イベントフラグ |
| [[asp3-tdataqueue]] | データキュー |
| [[asp3-tsemaphore]] | セマフォ |
| [[asp3-tisr]] | 割込みサブルーチン |
| [[asp3-tprioritydataqueue]] | 優先度データキュー |
| [[asp3-tfixedsizememorypool]] | 固定長メモリプール |
| [[asp3-tinitializeroutine]] | 初期化ルーチン |
| [[asp3-tterminateroutine]] | 終了処理ルーチン |

## See Also

- [[tecs-overview]]
- [[atk2-tecs]]

## Counter-Arguments and Gaps

- 制約タスクはASP3カーネルではデフォルト非サポート
""",
    ),
    "asp3-ttask": (
        "tTask (ASP3+TECS)",
        "ASP3+TECSのタスクセルタイプ。CRE_TSK静的APIでタスクを生成し、eTask受け口で制御する。",
        ["tecs", "asp3", "rtos", "task"],
        """\
`tTask`は、[[asp3-tecs]]でタスクを管理するセルタイプです。

## 主要属性

| 属性 | 型 | 説明 |
|-----|---|------|
| `id` | ID | タスクID（省略可） |
| `attribute` | ATR | タスク属性 (TA_ACT, TA_NOACTQUE, TA_RSTR) |
| `priority` | PRI | 起動時優先度 |
| `stackSize` | size_t | スタックサイズ（バイト） |

## 主要ポート

| ポート | 種別 | 説明 |
|-------|------|------|
| `eTask` | 受け口 | タスク制御・状態参照 |
| `eiTask` | 受け口 | タスク制御（非タスクコンテキスト用） |
| `cTaskBody` | 呼び口 | タスク本体の受け口を結合 |

## 主要API (sTaskシグニチャ)

- `activate()` — タスク起動要求 (`act_tsk`)
- `cancelActivate()` — 起動要求キャンセル (`can_act`)
- `terminate()` — タスク終了 (`ter_tsk`)
- `refer(T_RTSK*)` — 状態参照 (`ref_tsk`)

## See Also

- [[asp3-tecs]]
- [[tecs-celltype]]

## Counter-Arguments and Gaps

制約タスク(TA_RSTR)はASP3デフォルトでは非サポート。
""",
    ),
    "asp3-teventflag": (
        "tEventflag (ASP3+TECS)",
        "ASP3+TECSのイベントフラグセルタイプ。",
        ["tecs", "asp3", "rtos"],
        """\
`tEventflag`は、[[asp3-tecs]]でイベントフラグを管理するセルタイプです。

## See Also

- [[asp3-tecs]]
- [[asp3-ttask]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "asp3-tdataqueue": (
        "tDataqueue (ASP3+TECS)",
        "ASP3+TECSのデータキューセルタイプ。",
        ["tecs", "asp3", "rtos"],
        """\
`tDataqueue`は、[[asp3-tecs]]でデータキューを管理するセルタイプです。

## See Also

- [[asp3-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "asp3-tsemaphore": (
        "tSemaphore (ASP3+TECS)",
        "ASP3+TECSのセマフォセルタイプ。",
        ["tecs", "asp3", "rtos"],
        """\
`tSemaphore`は、[[asp3-tecs]]でセマフォを管理するセルタイプです。

## See Also

- [[asp3-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "asp3-tisr": (
        "tISR (ASP3+TECS)",
        "ASP3+TECSの割込みサブルーチンセルタイプ。",
        ["tecs", "asp3", "rtos", "interrupt"],
        """\
`tISR`は、[[asp3-tecs]]で割込みサブルーチンを管理するセルタイプです。

## See Also

- [[asp3-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "asp3-tprioritydataqueue": (
        "tPriorityDataqueue (ASP3+TECS)",
        "ASP3+TECSの優先度データキューセルタイプ。",
        ["tecs", "asp3", "rtos"],
        """\
`tPriorityDataqueue`は、[[asp3-tecs]]で優先度データキューを管理するセルタイプです。

## See Also

- [[asp3-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "asp3-tfixedsizememorypool": (
        "tFixedSizeMemoryPool (ASP3+TECS)",
        "ASP3+TECSの固定長メモリプールセルタイプ。",
        ["tecs", "asp3", "rtos", "memory"],
        """\
`tFixedSizeMemoryPool`は、[[asp3-tecs]]で固定長メモリプールを管理するセルタイプです。

## See Also

- [[asp3-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "asp3-tinitializeroutine": (
        "tInitializeRoutine (ASP3+TECS)",
        "ASP3+TECSの初期化ルーチンセルタイプ。",
        ["tecs", "asp3", "rtos"],
        """\
`tInitializeRoutine`は、[[asp3-tecs]]で初期化ルーチンを管理するセルタイプです。

## See Also

- [[asp3-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "asp3-tterminateroutine": (
        "tTerminateRoutine (ASP3+TECS)",
        "ASP3+TECSの終了処理ルーチンセルタイプ。",
        ["tecs", "asp3", "rtos"],
        """\
`tTerminateRoutine`は、[[asp3-tecs]]で終了処理ルーチンを管理するセルタイプです。

## See Also

- [[asp3-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "atk2-tecs": (
        "ATK2+TECS",
        "AUTOSAR OS (ATK2) をTECSコンポーネントとして扱うための統合。自動車組込み向け。",
        ["tecs", "atk2", "autosar", "rtos"],
        """\
ATK2+TECSは、AUTOSAR準拠のATK2カーネルのオブジェクトを[[tecs-cell]]として扱うための統合です。

## 提供セルタイプ

| セルタイプ | 説明 |
|-----------|------|
| [[atk2-tkernel]] | カーネル |
| [[atk2-ttask]] | タスク |
| atk2-tisr | 割込み管理 |
| [[atk2-tcounter]] | カウンタ |
| [[atk2-talarm]] | アラーム |
| [[atk2-tresource]] | リソース |

## See Also

- [[tecs-overview]]
- [[asp3-tecs]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "atk2-tkernel": (
        "tKernel (ATK2+TECS)",
        "ATK2+TECSのカーネル管理セルタイプ。",
        ["tecs", "atk2", "rtos"],
        """\
`tKernel`は、[[atk2-tecs]]でカーネルを管理するセルタイプです。

## See Also

- [[atk2-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "atk2-talarm": (
        "tAlarm (ATK2+TECS)",
        "ATK2+TECSのアラームセルタイプ。",
        ["tecs", "atk2", "rtos"],
        """\
`tAlarm`は、[[atk2-tecs]]でアラームを管理するセルタイプです。

## See Also

- [[atk2-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "atk2-tcounter": (
        "tCounter (ATK2+TECS)",
        "ATK2+TECSのカウンタセルタイプ。",
        ["tecs", "atk2", "rtos"],
        """\
`tCounter`は、[[atk2-tecs]]でカウンタを管理するセルタイプです。

## See Also

- [[atk2-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "atk2-tresource": (
        "tResource (ATK2+TECS)",
        "ATK2+TECSのリソース管理セルタイプ。",
        ["tecs", "atk2", "rtos"],
        """\
`tResource`は、[[atk2-tecs]]でリソースを管理するセルタイプです。

## See Also

- [[atk2-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "mruby-tecs": (
        "mruby+TECS",
        "mrubyをTECSコンポーネントと連携させる仕組み。ev3rt・GR-PEACH向けの実装が存在する。",
        ["tecs", "mruby", "ruby", "embedded"],
        """\
mruby+TECSは、軽量Rubyのmrubyと[[tecs-overview]]を連携させる仕組みです。

## 実装

- [[mruby-ev3rt-tecs]] — mruby on ev3rt+tecs（LEGO Mindstorms EV3向け）
- [[mruby-gr-peach-tecs]] — mruby on GR-PEACH+tecs（GR-PEACH向け）

## プラグイン

- [[plugin-mruby-bridge]] — MrubyBridgePlugin
- [[plugin-mruby-info-bridge]] — MrubyInfoBridgePlugin

## See Also

- [[tecs-overview]]
- [[asp3-tecs]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "mruby-ev3rt-tecs": (
        "mruby on ev3rt+tecs",
        "LEGO Mindstorms EV3向けのmruby+TECS実装。センサ・モータ・RTOS機能をmrubyから利用可能。",
        ["tecs", "mruby", "ev3rt", "lego"],
        """\
mruby on ev3rt+tecsは、LEGO Mindstorms EV3向けのTECS統合mruby実装です。

## 提供クラス

| クラス | 説明 |
|-------|------|
| Battery | バッテリ管理 |
| Button | ボタン入力 |
| LED | LEDライト |
| Speaker | スピーカ |
| LCD | ディスプレイ |
| Motor | モータ制御 |
| RTOS | RTOSサービス |
| Color | カラーセンサ |
| Gyro | ジャイロセンサ |
| Ultrasonic | 超音波センサ |
| Touch | タッチセンサ |
| SharedMemory | 共有変数 |
| Balancer | 倒立振子バランサ |

## See Also

- [[mruby-tecs]]
- [[mruby-gr-peach-tecs]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "mruby-gr-peach-tecs": (
        "mruby on GR-PEACH+tecs",
        "Renesas GR-PEACH向けのmruby+TECS実装。RTOS機能・LED制御をmrubyから利用可能。",
        ["tecs", "mruby", "gr-peach"],
        """\
mruby on GR-PEACH+tecsは、Renesas GR-PEACH向けの[[mruby-tecs]]実装です。

## 機能

- RTOS機能 (RTOS クラス)
- LED制御

## See Also

- [[mruby-tecs]]
- [[mruby-ev3rt-tecs]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "tinet-tecs": (
        "TINET+TECS",
        "TOPPERSのTINETネットワークスタックとTECSの統合。",
        ["tecs", "tinet", "network"],
        """\
TINET+TECSは、TOPPERSのTINETネットワークスタックと[[tecs-overview]]の統合です。

## See Also

- [[tecs-overview]]

## Counter-Arguments and Gaps

ドキュメントが未整備。
""",
    ),
    "tlsf-tecs": (
        "TLSF+TECS",
        "TLSF（Two-Level Segregated Fit）アロケータとTECSの統合。動的メモリ管理を提供。",
        ["tecs", "tlsf", "memory", "allocator"],
        """\
TLSF+TECSは、TLSF（Two-Level Segregated Fit）動的メモリアロケータと[[tecs-overview]]の統合です。

## See Also

- [[tecs-overview]]
- [[imp-allocator]]

## Counter-Arguments and Gaps

ドキュメントが未整備。
""",
    ),
    "imp-celltype-code": (
        "セルタイプコード (Celltype Code)",
        "TECSのセルタイプを実装するCコード。ユーザー実装モデルとシステム実装モデルがある。",
        ["tecs", "implementation"],
        """\
セルタイプコードは、[[tecs-celltype]]の実装を記述するCコードです。

## 実装モデル

- **ユーザー実装モデル** — アプリ開発者が記述する部分
- **システム実装モデル** — [[tecsgen]]が生成する部分

## See Also

- [[tecs-celltype]]
- [[imp-initialize]]
- [[imp-factory]]
- [[imp-allocator]]
- [[imp-foreach-cell]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "imp-initialize": (
        "初期化コード",
        "TECSセルタイプの初期化処理コード。INITIALZE_TECS()マクロで呼び出す。",
        ["tecs", "implementation"],
        """\
初期化コードは、TECSセルタイプの初期化を担うコードです。

- V1.3以降: `INITIALZE_TECS()` マクロ（`global_tecsgen.h` に定義）
- V1.2以前: `INITIALZE_TECSGEN()`（後方互換として継続提供）

## See Also

- [[imp-celltype-code]]
- [[tecsgen]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "imp-factory": (
        "ファクトリ",
        "TECSのファクトリ機構。セルを動的に生成するための仕組み。",
        ["tecs", "implementation"],
        """\
ファクトリは、[[tecs-cell]]を動的に生成するためのTECS機構です。

## See Also

- [[imp-celltype-code]]
- [[tecs-cell]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "imp-allocator": (
        "アロケータ (Allocator)",
        "TECSセルタイプコードでのメモリアロケータ。TLSFアロケータとの連携も可能。",
        ["tecs", "implementation", "memory"],
        """\
アロケータは、[[imp-celltype-code]]内でのメモリ管理機構です。

## See Also

- [[imp-celltype-code]]
- [[tlsf-tecs]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "imp-foreach-cell": (
        "FOREACH_CELL マクロ",
        "TECSの全セルを反復処理するマクロ。複数インスタンスの一括操作に使用。",
        ["tecs", "implementation"],
        """\
`FOREACH_CELL`マクロは、[[tecs-celltype]]の全[[tecs-cell]]インスタンスを反復処理するためのマクロです。

## See Also

- [[imp-celltype-code]]
- [[tecs-cell]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "plugin-mruby-bridge": (
        "MrubyBridgePlugin",
        "mrubyとTECSコンポーネントをブリッジするプラグイン。",
        ["tecs", "plugin", "mruby"],
        """\
MrubyBridgePluginは、[[mruby-tecs]]とTECSコンポーネントを接続するプラグインです。

## See Also

- [[tecs-plugin]]
- [[plugin-mruby-info-bridge]]
- [[mruby-tecs]]

## Counter-Arguments and Gaps

リファレンスは未作成 (to be written)。
""",
    ),
    "plugin-mruby-info-bridge": (
        "MrubyInfoBridgePlugin",
        "mrubyの実行時情報をTECSと連携させるプラグイン。V1.7.0で追加。",
        ["tecs", "plugin", "mruby"],
        """\
MrubyInfoBridgePluginは、mrubyの実行時情報を[[tecs-overview]]と連携させるプラグインです。V1.7.0で追加されました。

## See Also

- [[tecs-plugin]]
- [[plugin-mruby-bridge]]

## Counter-Arguments and Gaps

特になし。
""",
    ),
    "plugin-c2tecs": (
        "C2TECSBridgePlugin",
        "C言語からTECSコンポーネントを呼び出すためのブリッジプラグイン。",
        ["tecs", "plugin", "c-language"],
        """\
C2TECSBridgePluginは、C言語コードから[[tecs-cell]]を呼び出すためのブリッジプラグインです。

## See Also

- [[tecs-plugin]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "plugin-repeat-cell": (
        "RepeatCellPlugin / RepeatJoinPlugin",
        "セルを繰り返し生成・結合するTECSプラグイン。配列的なセル定義を簡略化する。",
        ["tecs", "plugin"],
        """\
RepeatCellPlugin / RepeatJoinPluginは、[[tecs-cell]]を繰り返し生成・結合するプラグインです。

## See Also

- [[tecs-plugin]]
- [[tecs-cell]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
    "plugin-notifier": (
        "NotifierPlugin (ASP3)",
        "ASP3のタイムイベント通知をTECSコンポーネントとして扱うプラグイン。",
        ["tecs", "plugin", "asp3"],
        """\
NotifierPlugin は、[[asp3-tecs]]のタイムイベント通知を[[tecs-cell]]として扱うプラグインです。

## See Also

- [[tecs-plugin]]
- [[asp3-tecs]]

## Counter-Arguments and Gaps

リファレンスは未作成 (to be written)。
""",
    ),
    "atk2-ttask": (
        "tTask (ATK2+TECS)",
        "ATK2+TECSのタスクセルタイプ。",
        ["tecs", "atk2", "rtos"],
        """\
`tTask`は、[[atk2-tecs]]でタスクを管理するセルタイプです。

## See Also

- [[atk2-tecs]]
- [[asp3-ttask]]

## Counter-Arguments and Gaps

詳細は raw/articles 参照。
""",
    ),
}


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def extract_sections(md_content: str) -> list[str]:
    """Extract heading lines as key points."""
    lines = md_content.split("\n")
    headings = []
    seen = set()
    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.+)", line)
        if m:
            text = m.group(2).strip()
            if text not in seen and len(text) > 1 and text not in ("Source:", "索引", "検索"):
                seen.add(text)
                headings.append(f"{m.group(1)} {text}")
    return headings[:20]


def find_entities(content: str) -> list[str]:
    """Find TECS entities mentioned in content, return sorted unique slugs."""
    found = set()
    for term, slug in CONCEPT_MAP.items():
        if term in content:
            found.add(slug)
    return sorted(found)


def make_source_summary(slug: str, raw_md: str, title: str, source_url: str) -> str:
    headings = extract_sections(raw_md)
    entities = find_entities(raw_md)

    # Extract first paragraph of actual content
    lines = raw_md.split("\n")
    summary_lines = []
    in_frontmatter = False
    fm_done = False
    skip_first_h1 = False
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            if not in_frontmatter:
                fm_done = True
            continue
        if not fm_done:
            continue
        if re.match(r"^#+ ", line):
            if not skip_first_h1:
                skip_first_h1 = True
                continue
            break
        stripped = line.strip()
        if stripped and not stripped.startswith("```") and len(stripped) > 20:
            summary_lines.append(stripped)
        if len(summary_lines) >= 3:
            break

    summary = " ".join(summary_lines)[:300] if summary_lines else "（内容は raw article を参照）"

    key_points = "\n".join(f"- {h}" for h in headings) if headings else "- （構造は raw article を参照）"
    entity_links = "\n".join(f"- [[{e}]]" for e in entities) if entities else "- （なし）"

    return f"""---
date: {TODAY}
tags: [tecs, toppers, documentation]
type: source-summary
source-url: {source_url}
description: "TECS ドキュメント source-summary: {title[:100]}"
---

# {title}

{summary}

## Key Points

{key_points}

## Entities Mentioned

{entity_links}

## See Also

- [[index]]
"""


def make_concept_page(slug: str, title: str, description: str, tags: list, body: str) -> str:
    tags_yaml = ", ".join(tags)
    return f"""---
date: {TODAY}
tags: [{tags_yaml}]
type: concept
status: active
description: "{description[:148]}"
---

# {title}

{body.strip()}
"""


# ------------------------------------------------------------------ #
# Main
# ------------------------------------------------------------------ #

def main():
    raw_files = sorted(RAW_ARTICLES.glob("*.md"))
    print(f"Found {len(raw_files)} raw articles")

    # Check which have no corresponding wiki source-summary
    existing_wiki = {f.stem for f in WIKI_DIR.glob("*.md")}
    to_compile = []
    for rf in raw_files:
        # Slug = filename minus date prefix (YYYY-MM-DD-)
        m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", rf.stem)
        wiki_slug = m.group(1) if m else rf.stem
        if wiki_slug not in existing_wiki:
            to_compile.append((rf, wiki_slug))

    if not to_compile:
        print("All sources are already compiled. Nothing to do.")
        return

    print(f"Compiling {len(to_compile)} sources...")

    log_entries = []
    created_pages = []
    updated_pages = []

    # ---- Step 1: Source-summary pages ----
    for raw_path, wiki_slug in to_compile:
        content = raw_path.read_text(encoding="utf-8", errors="replace")

        # Extract frontmatter fields
        title_m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
        url_m = re.search(r"^source-url:\s*(.+)$", content, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else wiki_slug
        source_url = url_m.group(1).strip() if url_m else ""

        summary_md = make_source_summary(wiki_slug, content, title, source_url)
        out_path = WIKI_DIR / f"{wiki_slug}.md"
        out_path.write_text(summary_md, encoding="utf-8")
        created_pages.append(wiki_slug)

    print(f"  Created {len(created_pages)} source-summary pages")

    # ---- Step 2: Concept pages ----
    concept_created = []
    concept_updated = []
    for slug, (title, description, tags, body) in CONCEPT_PAGES.items():
        out_path = WIKI_DIR / f"{slug}.md"
        page_md = make_concept_page(slug, title, description, tags, body)
        if out_path.exists():
            out_path.write_text(page_md, encoding="utf-8")
            concept_updated.append(slug)
        else:
            out_path.write_text(page_md, encoding="utf-8")
            concept_created.append(slug)

    print(f"  Created {len(concept_created)} concept pages")
    print(f"  Updated {len(concept_updated)} concept pages")

    # ---- Step 3: Update raw article frontmatter: compiled=true ----
    for raw_path, wiki_slug in to_compile:
        content = raw_path.read_text(encoding="utf-8", errors="replace")
        new_content = re.sub(r"^compiled: false$", "compiled: true", content, flags=re.MULTILINE)
        raw_path.write_text(new_content, encoding="utf-8")

    # ---- Step 4: Update wiki/index.md ----
    index_path = WIKI_DIR / "index.md"
    index_content = index_path.read_text(encoding="utf-8", errors="replace")

    # Build index sections
    sections = {
        "TECS コア概念": [s for s in concept_created + concept_updated if s.startswith("tecs-") or s in ("tecsgen", "tecsflow", "tecsmerge", "tecs-plugin")],
        "ASP3+TECS": [s for s in concept_created + concept_updated if s.startswith("asp3-")],
        "ATK2+TECS": [s for s in concept_created + concept_updated if s.startswith("atk2-")],
        "mruby+TECS": [s for s in concept_created + concept_updated if s.startswith("mruby-")],
        "ネットワーク・メモリ": [s for s in concept_created + concept_updated if s in ("tinet-tecs", "tlsf-tecs")],
        "実装モデル": [s for s in concept_created + concept_updated if s.startswith("imp-")],
        "プラグイン": [s for s in concept_created + concept_updated if s.startswith("plugin-")],
    }

    new_index = f"""---
date: {TODAY}
description: "TECS wiki インデックス — コアTECS概念・RTOS連携・ツール・プラグインのカタログ"
tags: [tecs, toppers, index]
---

# TECS Wiki Index

最終更新: {TODAY}

## TECS コア概念

- [[tecs-overview]] — 組込みコンポーネントシステム TECS 概要 ({TODAY})
- [[tecs-cdl]] — コンポーネント記述言語 ({TODAY})
- [[tecs-celltype]] — セルタイプ ({TODAY})
- [[tecs-composite-celltype]] — 複合セルタイプ ({TODAY})
- [[tecs-cell]] — セル・組上げ記述 ({TODAY})
- [[tecs-signature]] — シグニチャ ({TODAY})
- [[tecs-port]] — ポート（呼び口・受け口） ({TODAY})
- [[tecs-namespace]] — ネームスペース ({TODAY})
- [[tecs-region]] — リージョン ({TODAY})
- [[tecs-tcd]] — コンポーネント図 ({TODAY})

## TECSツール

- [[tecsgen]] — TECS ジェネレータ ({TODAY})
- [[tecsflow]] — 実行フロー解析ツール ({TODAY})
- [[tecsmerge]] — CDLマージツール ({TODAY})
- [[tecs-plugin]] — プラグイン一覧 ({TODAY})

## ASP3+TECS

- [[asp3-tecs]] — ASP3+TECS 概要 ({TODAY})
- [[asp3-ttask]] — tTask ({TODAY})
- [[asp3-teventflag]] — tEventflag ({TODAY})
- [[asp3-tdataqueue]] — tDataqueue ({TODAY})
- [[asp3-tsemaphore]] — tSemaphore ({TODAY})
- [[asp3-tisr]] — tISR ({TODAY})
- [[asp3-tprioritydataqueue]] — tPriorityDataqueue ({TODAY})
- [[asp3-tfixedsizememorypool]] — tFixedSizeMemoryPool ({TODAY})
- [[asp3-tinitializeroutine]] — tInitializeRoutine ({TODAY})
- [[asp3-tterminateroutine]] — tTerminateRoutine ({TODAY})

## ATK2+TECS

- [[atk2-tecs]] — ATK2+TECS 概要 ({TODAY})
- [[atk2-tkernel]] — tKernel ({TODAY})
- [[atk2-ttask]] — tTask ({TODAY})
- [[atk2-talarm]] — tAlarm ({TODAY})
- [[atk2-tcounter]] — tCounter ({TODAY})
- [[atk2-tresource]] — tResource ({TODAY})

## mruby+TECS

- [[mruby-tecs]] — mruby+TECS 概要 ({TODAY})
- [[mruby-ev3rt-tecs]] — mruby on ev3rt+tecs ({TODAY})
- [[mruby-gr-peach-tecs]] — mruby on GR-PEACH+tecs ({TODAY})

## ネットワーク・メモリ

- [[tinet-tecs]] — TINET+TECS ({TODAY})
- [[tlsf-tecs]] — TLSF+TECS ({TODAY})

## 実装モデル

- [[imp-celltype-code]] — セルタイプコード ({TODAY})
- [[imp-initialize]] — 初期化コード ({TODAY})
- [[imp-factory]] — ファクトリ ({TODAY})
- [[imp-allocator]] — アロケータ ({TODAY})
- [[imp-foreach-cell]] — FOREACH_CELL マクロ ({TODAY})

## プラグイン

- [[plugin-notifier]] — NotifierPlugin ({TODAY})
- [[plugin-mruby-bridge]] — MrubyBridgePlugin ({TODAY})
- [[plugin-mruby-info-bridge]] — MrubyInfoBridgePlugin ({TODAY})
- [[plugin-c2tecs]] — C2TECSBridgePlugin ({TODAY})
- [[plugin-repeat-cell]] — RepeatCellPlugin ({TODAY})

## ソースサマリー (Source Summaries)

### asp3

"""
    asp3_sources = sorted([s for _, s in to_compile if s.startswith("asp3--")])
    for s in asp3_sources:
        new_index += f"- [[{s}]] ({TODAY})\n"

    new_index += "\n### atk2+tecs\n\n"
    atk2_sources = sorted([s for _, s in to_compile if s.startswith("atk2-tecs--")])
    for s in atk2_sources:
        new_index += f"- [[{s}]] ({TODAY})\n"

    new_index += "\n### mruby-on-ev3rt+tecs\n\n"
    ev3_sources = sorted([s for _, s in to_compile if s.startswith("mruby-on-ev3rt-tecs--")])
    for s in ev3_sources:
        new_index += f"- [[{s}]] ({TODAY})\n"

    new_index += "\n### mruby-on-gr-peach+tecs\n\n"
    grp_sources = sorted([s for _, s in to_compile if s.startswith("mruby-on-gr-peach-tecs--")])
    for s in grp_sources:
        new_index += f"- [[{s}]] ({TODAY})\n"

    new_index += "\n### tecs\n\n"
    tecs_sources = sorted([s for _, s in to_compile if s.startswith("tecs--")])
    for s in tecs_sources:
        new_index += f"- [[{s}]] ({TODAY})\n"

    new_index += "\n### その他\n\n"
    other_sources = sorted([s for _, s in to_compile if not any(
        s.startswith(p) for p in ["asp3--", "atk2-tecs--", "mruby-on-ev3rt-tecs--",
                                   "mruby-on-gr-peach-tecs--", "tecs--"])])
    for s in other_sources:
        new_index += f"- [[{s}]] ({TODAY})\n"

    index_path.write_text(new_index, encoding="utf-8")
    print("  Updated wiki/index.md")

    # ---- Step 5: Backlink audit ----
    # Check all wiki files for mentions of new concept titles without wikilinks
    all_wiki_files = list(WIKI_DIR.glob("*.md"))
    backlink_fixes = 0
    for wf in all_wiki_files:
        content = wf.read_text(encoding="utf-8", errors="replace")
        changed = False
        for term, slug in CONCEPT_MAP.items():
            wikilink = f"[[{slug}]]"
            # If term mentioned but wikilink absent, and the file is not the concept page itself
            if term in content and wikilink not in content and wf.stem != slug:
                # Add wikilink at first mention (simple replacement)
                content = content.replace(term, wikilink, 1)
                changed = True
        if changed:
            wf.write_text(content, encoding="utf-8")
            backlink_fixes += 1

    print(f"  Backlink audit: fixed {backlink_fixes} files")

    # ---- Step 6: Log entry ----
    n_sources = len(to_compile)
    n_pages = len(created_pages) + len(concept_created)
    log_entry = (
        f"## [{TODAY}] compile | {n_sources} sources → {n_pages} pages\n"
        f"Compiled {n_sources} raw sources. "
        f"Created {len(created_pages)} source-summary pages + {len(concept_created)} concept pages. "
        f"Updated {len(concept_updated)} concept pages. "
        f"Backlink fixes: {backlink_fixes}."
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n" + log_entry + "\n")
    print("  Appended to log.md")

    print(f"\nDone. {n_sources} sources compiled → {n_pages} new wiki pages.")


if __name__ == "__main__":
    main()
