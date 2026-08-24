---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン FMPPlugin・FMPObjectPlugin・FMPHandlerPlugin（TOPPERS/FMP3マルチプロセッサカーネル対応）の仕様書。北極星未追跡3ファミリーの2つ目で、HRP/HRP2とは異なりドメインでなくクラス境界を使う設計と判明、全3ファイルで完走"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# FMPPlugin / FMPObjectPlugin / FMPHandlerPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPファミリー完走]]（2026-08-15）を受けて、北極星に一度も載っていなかった残る2ファミリー（FMP・HRMP）のうちFMPに着手。`Glob`で`tecslib/plugin/FMP*.rb`を確認した結果、**`FMPPlugin.rb`（226行）・`FMPObjectPlugin.rb`（211行）・`FMPHandlerPlugin.rb`（185行）の計3ファイルのみ**——HRP（10ファイル）・HRP2（15ファイル以上）よりはるかに小さいファミリーで、本ノート1本で完走する。ソース位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。TOPPERS/FMP3（マルチプロセッサ対応カーネル）向け。

## 1. 最大の発見: HRP/HRP2とは別系統の境界機構

`FMPPlugin < ClassPlugin`——**`DomainPlugin`ではなく`ClassPlugin`を継承する**。[[work/active/tecsgen-plugins/NotifierPlugin|NotifierPlugin]]執筆時（2026-08-14）に発見した「FMP/HRMPクラス境界」の`class(...)`指定子が、まさにこのFMPPluginの入口だったと確認できた。

```tecs-cdl
[class(FMP, CLS_PRC1)]
region <リージョン名> {
    ...
};
```

HRP2Plugin/HRPPluginが`domain(...)`指定子（信頼ドメイン境界、`DomainPlugin`）を使うのに対し、FMPPluginは`class(...)`指定子（`ClassPlugin`、[[tecsgen外部仕様]] 6.2表の3行目）を使う——**「ドメイン」と「クラス」は tecsgen 上で別のCDL構文・別の基底クラス**であり、FMPは信頼境界ではなくマルチプロセッサの**処理単位（プロセッサ配置）境界**を表現する仕組みだと判明した。

## 2. FMPPlugin: クラス定義はCDL属性ではなくJSON（`__tool_info__`）

`FMPPlugin#initialize`はCDLのオプション文字列（例: `"kernel"`）を受け取る代わりに、クラス定義本体を`__tool_info__( "FMP_class_def" )`というJSON形式のツール情報ブロックから取得する。`CLASS_DEF_schema`（51〜65行）で定義されるスキーマは:

```ruby
:class => {
    :type         => "class",
    :class_name   => :string,    # TECS上のクラス名（"CLS_PRC1"等）
    :processorID  => :integer,   # 1, 2, 3...
    :locality     => :string,    # "only" / "all" / "global"
},
:__class => {                    # optional
    :class_name_in_kernel => :string   # HRMP3/FMP3側の別名（オプション）
}
```

`TOOL_INFO::VALIDATOR`でこのJSONを検証してから`@@class_info`（クラス変数、全インスタンス共有）に格納する——HRP2Plugin/HRPPluginの`initialize`がCDLのオプション文字列だけで完結していたのとは異なり、**外部のツール情報ブロックとJSONスキーマ検証を組み合わせる**という、この一連の調査で初めて見る宣言方式。`locality`が`"only"`（特定プロセッサ専用）・`"all"`（全プロセッサ）・`"global"`（プロセッサ非依存）の3値を取ることが、後述のRPC要否判定・ハンドラ配置制約の基礎になっている。

## 3. add_through_plugin: RPC挿入は実装未完（死コードのみ）

`FMPPlugin#add_through_plugin`（87〜140行）はHRP2Plugin/HRPPluginと同じ役割（結合先のクラス境界をまたぐ場合の仲介プラグイン自動選択）を持つが、判定結果が大きく異なる。

| # | 条件 | 挿入されるプラグイン |
|---|---|---|
| 1 | 結合先がカーネルオブジェクトセル（`HRPKernelObjectManager.include_celltype?`） | なし（`[]`） |
| 2 | 呼び先クラスが特定プロセッサ限定（`locality=="only"`）かつ呼び元が別プロセッサまたは非限定 | **なし（`[]`）——本来RPCが必要な場面のはずが実装されていない** |
| 3 | それ以外（同一プロセッサ内の直接呼び出し） | なし（`[]`、`Direct Call`） |

条件2の分岐には、実行されないコメントアウト済みのコードが残っている：

```ruby
# return [ :FMPRPCPlugin, "noClientSemaphore=false,PPAllocatorSize=256" ]
# return [ :SelectiveJoinPlugin, "processorID=#{callee_prc_NPU_cell}" ]
return []
```

`FMPRPCPlugin`という名前のクラスは`tecslib/plugin/`のどこにも存在しない（3ファイルのみと確認済み）——**マルチプロセッサ間のRPC仲介機構は設計段階で構想されたが実装されないまま終わった**ことを示す直接証拠。[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で見つけた「死コードがHRP2からの複製元を示す」パターンとは異なり、こちらは**存在しないクラスへの参照**であり、複製の痕跡ではなく未完成機能の痕跡。同じ`return []`でも、条件1・3は「意図的に何もしない」、条件2は「本来何かすべきだが実装されていない」という質的に異なる`[]`である点をノートとして明記しておく。

**カーネルオブジェクト判定にHRP系の`HRPKernelObjectManager`をそのまま流用**している点も注目に値する——FMP専用のマネージャクラスを作らず、`require_tecsgen_lib "HRPKernelObjectManager.rb"`（40行）で無印HRPファミリーの静的セルタイプ名リストをそのまま再利用している。カーネルオブジェクトの集合（tTask・tSemaphore等18種）はカーネル非依存の共通概念として扱われている、という設計判断が読み取れる。

## 4. GenAttModとの関係——「含むが実質no-op」という第3のパターン

`FMPPlugin`も`include GenAttMod`（48行）し`gen_factory`で`gen_att_mod`を呼ぶ（205〜208行）。しかし[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]執筆時に発見した`GenAttMod#gen_att_mod`の分岐条件——`ct.get_domain_roots[ :HRMP ] == nil && ct.get_domain_roots[ :HRP ] == nil`の場合は処理をスキップし「FMP3 は、対象外となる」とコメントされている——を踏まえると、FMPはそもそも`domain(...)`指定子を使わない（`class(...)`のみ）ため`get_domain_roots`に`:FMP`キーが登録されようがなく、**`gen_att_mod`を呼んでいても実質的に何もしないコードパスを通るだけ**になる。HRPPluginでは「HRPとHRMPの2ファミリーで共有、FMPは明示除外」という記述だけで確認していた仮説が、今回FMPPlugin自身のコードから「呼んではいるが到達しない」という形で裏付けられた——**FMPはGenAttModを`include`する義理は果たしつつ、実際にはHRP/HRMPの機能を利用していない**、意図的な整合性維持のためのno-op呼び出しと解釈できる。

## 5. FMPObjectPlugin: 単一ファイルの汎用テーブル駆動（HRP2/HRPの二層構造なし）

`FMPObjectPlugin < CelltypePlugin`——`HRPKernelObjectPlugin`/`HRP2KernelObjectPlugin`のような専用の抽象基底クラスを持たず、`CelltypePlugin`を直接継承する1ファイル完結型。単機能プラグイン群は存在せず、最初からテーブル駆動の汎用プラグイン1本のみ。

```ruby
@@api = {
    "TASK"                  => [ cre_params_task_proc,   "TSK", :id, :attribute, :priority, :stackSize ],
    "SEMAPHORE"             => [ cre_params_proc,        "SEM", ... ],
    "EVENTFLAG"             => [ cre_params_proc,        "FLG", ... ],
    "DATAQUEUE"             => [ cre_params_proc,        "DTQ", ... ],
    "PRIORITY_DATAQUEUE"    => [ cre_params_proc,        "PDQ", ... ],
    "FIXED_SIZE_MEMORYPOOL" => [ cre_params_proc,        "MPF", ... ],
    "MESSAGE_BUFFER"        => [ cre_params_proc,        "MBF", ... ],
    "SPINLOCK"              => [ cre_params_proc,        "SPN", :id, :attribute],
    "MUTEX"                 => [ cre_params_mutex_proc,  "MTX", ... ],
    "KERNEL"                => [ cre_params_kernel_proc, "SYS"],
}
```

- HRP/HRP2の対応テーブルにない**`SPINLOCK`**（`CRE_SPN`）が新規に存在する——マルチプロセッサ間の排他制御プリミティブで、単一プロセッサ前提のHRP/HRP2には無い概念。FMPがマルチプロセッサカーネル向けであることを裏付ける最も直接的な差分。
- 各エントリの第1要素が生成関数（`Proc`）そのもの——HRPObjectPluginが`slice`呼び出しをメソッド本体に直接書いていたのに対し、FMPObjectPluginは`cre_params_task_proc`/`cre_params_mutex_proc`/`cre_params_kernel_proc`/`cre_params_proc`（共通）の4種類の`Proc`をテーブルの値として持たせ、`print_cfg_cre`から`proc.call self, cell, params`で呼び出す——関数分岐をテーブルの外に出さずテーブル自体に埋め込む、より関数型寄りの実装。
- `gen_factory`は`cell.get_owner.get_class_root.get_class_type`からセルの所属クラスを取得し、**`is_active?`（タスク的セルタイプかどうか）で「処理単位（PU）」か「非処理単位（NPU）」かを判定**し、`class_type.get_plugin.get_PU_kernel_class`/`get_NPU_kernel_class`のいずれかでカーネル側のクラス名を解決してから`CLASS(<kernel_class_name>){...}`ブロックで各セルの`CRE_XXX`を包む。同じCDL上のクラス指定でも、アクティブセル（タスク等）かどうかで生成先のカーネルクラスが変わりうる、という設計——単一プロセッサのHRP/HRP2には存在しない区別。

## 6. FMPHandlerPlugin: テンプレート文字列駆動（HRP/HRP2のheredoc分岐と異なる実装技法）

`FMPHandlerPlugin < CelltypePlugin`。ハンドラ系6種（`INT_REQUEST`/`INT_SERVICE_ROUTINE`/`INT_HANDLER`/`CPU_EXCEPTION_HANDLER`/`INIT_ROUTINE`/`TERM_ROUTINE`）をカバーする点は[[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPHandlerPlugin]]/HRP2HandlerPluginと同じだが、実装技法が異なる。

```ruby
@@handler_list = {
    "INT_REQUEST" =>
        [:InClass, "CFG_INT( {{interruptNumber}}, { {{attribute}}, {{interruptPriority}} })"],
    "INT_SERVICE_ROUTINE" =>
        [:InClass, "CRE_ISR( {{id}}, { {{attribute}}, $cbp$, {{interruptNumber}}, tISR_start, {{isrPriority}} })"],
    ...
    "INIT_ROUTINE" => [:Any, "ATT_INI({ {{attribute}}, $cbp$, tInitializeRoutine_start })"],
    "TERM_ROUTINE" => [:Any, "ATT_TER({ {{attribute}}, $cbp$, tTerminateRoutine_start })"],
}
```

HRP/HRP2HandlerPluginがRubyの`elsif`分岐＋heredocでマクロごとに専用コードを書いていたのに対し、FMPHandlerPluginは**マクロ文字列自体をテーブルの値として持たせ、`{{attribute}}`のようなプレースホルダを`gsub`で置換する**——生成コードをデータとして表現するテンプレートエンジン方式。HRP/HRP2系より後発（copyright開始年2019年）であることを踏まえると、後発ファミリーでよりデータ駆動な実装に寄せていった、という実装スタイルの世代差とも読める。

- 各エントリの第1要素`:InClass`/`:Any`は配置制約——`:InClass`のハンドラ（INT_REQUEST/ISR/INT_HANDLER/CPU_EXCEPTION_HANDLER）は`class(...)`で明示的にクラス指定されたリージョン内に置く必要があり、`global`ロカリティのクラス（≒プロセッサ非依存）に置くとエラー（`FMH9999`）になる。`:Any`（INIT_ROUTINE/TERM_ROUTINE）はクラス種別を問わない——HRP系の「kernelドメイン限定」という単純な二値制約より細かい、ロカリティ単位の配置ルール。
- `gen_factory`はFMPObjectPluginと同様、セルの所属クラスの`locality`が`"only"`かどうかで出力先の`CLASS(...)`ブロックを決定するが、`"only"`でない場合は`FMPPlugin.get_prc_only`でそのプロセッサIDに対応する`"only"`クラスを検索し直す——ハンドラは元のクラス指定がプロセッサ非限定でも、実際には特定プロセッサに割り当て直される、という間接的なクラス解決ロジックが存在する。

## 7. エラーコードの傾向

`FMP9999`（FMPPlugin/FMPObjectPlugin）・`FMH9999`（FMPHandlerPlugin）という汎用プレースホルダコードのみで、[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPSVCSignaturePlugin]]のような専用コード体系は存在しない——[[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPKernelObjectPlugin]]で確認した「カーネルオブジェクト生成系はどのファミリーでも汎用コードのまま」という傾向がFMPでも再現している。

## 8. 制約・注意点

- CDL実例はリポジトリ内に見つからず、`class(FMP, ...)`構文・`__tool_info__( "FMP_class_def" )`の具体的な記述例はソースからの逆算・未検証。
- 条件2（クロスプロセッサ呼び出し）のRPC仲介が未実装のため、実際のマルチプロセッサ間呼び出しがどう扱われるか（コンパイルエラーになるのか、単に直接呼び出しとして生成されて動作時に問題を起こすのか）はソースからは断定できない。
- HRMPは未着手・未サイジングのまま。

## Related

- [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] — GenAttMod/GenDefSvc共有・HRPKernelObjectManager流用の対比元
- [[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPKernelObjectPlugin 具象サブクラス群]] — カーネルオブジェクト生成テーブル駆動方式の対比元
- [[work/active/tecsgen-plugins/NotifierPlugin|NotifierPlugin]] — `class(...)`指定子・`ClassPlugin`基盤の初出
- [[tecsgen外部仕様]] — 6.2 プラグイン呼び出し規約（`ClassPlugin`行）・6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理。北極星未追跡3ファミリーのうちFMPが完走、残るHRMPが最後の1つ
