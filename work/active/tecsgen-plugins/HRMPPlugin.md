---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン HRMPPlugin・HRMPDomainPlugin・HRMPClassPlugin・HRMPKernelObjectPlugin（TOPPERS/HRMP3対応）の仕様書。北極星未追跡3ファミリーの最後の1つで、HRPの信頼ドメイン軸とFMPのクラス（プロセッサ配置）軸を1つのカーネルに統合する設計と判明、全4ファイルで完走"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# HRMPPlugin / HRMPDomainPlugin / HRMPClassPlugin / HRMPKernelObjectPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/FMPPlugin|FMPファミリー完走]]（2026-08-15）を受けて、北極星に一度も載っていなかった3ファミリー（HRP・FMP・HRMP）のうち最後の1つ、HRMP（TOPPERS/HRMP3）に着手。`Glob`で`tecslib/plugin/HRMP*.rb`を確認した結果、**`HRMPPlugin.rb`（57行）・`HRMPDomainPlugin.rb`（207行）・`HRMPClassPlugin.rb`（166行）・`HRMPKernelObjectPlugin.rb`（254行）の計4ファイルのみ**——FMPと同程度に小さいが、内容はこれまでで最も密度が高い。本ノート1本で完走し、**これで北極星未追跡3ファミリーすべてが完了する**。ソース位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 最大の発見: HRMPPluginはHRPとFMP、両方の軸を1つのカーネルに統合する

`HRMPPlugin < MultiPlugin`（41行）——[[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]]執筆時に発見した`MultiPlugin`ディスパッチ機構のこの調査シリーズ2件目の実例。ただし分岐軸がMrubyBridgePluginとは異なる。

```ruby
def self.get_plugin superClass
  if superClass == DomainPlugin then
    require_tecsgen_lib 'tecslib/plugin/HRMPDomainPlugin.rb'
    return HRMPDomainPlugin
  elsif superClass == ClassPlugin
    require_tecsgen_lib 'tecslib/plugin/HRMPClassPlugin.rb'
    return HRMPClassPlugin
  else
    return nil
  end
end
```

MrubyBridgePluginは「CDL上の付与位置（celltype/cell/signature等）」で分岐したが、HRMPPluginは**「CDL指定子の種類（`domain(...)`か`class(...)`か）」**で分岐する。つまり同じCDL上で：

```tecs-cdl
[domain(HRMP, "kernel")]
region <ドメインリージョン> {
    [class(HRMP, CLS_PRC1)]
    region <クラスリージョン> {
        ...
    };
};
```

のように**同じ「HRMP」という名前を`domain(...)`と`class(...)`の両方の指定子で書け**、それぞれ`HRMPDomainPlugin`（信頼ドメイン境界、[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]と同系統）・`HRMPClassPlugin`（プロセッサ配置境界、[[work/active/tecsgen-plugins/FMPPlugin|FMPPlugin]]と同系統）に自動的にディスパッチされる。**HRMPは名前が示すとおり「HR(P) + MP（マルチプロセッサ）」——HRPの信頼ドメイン機構とFMPのマルチプロセッサ配置機構を、1つのカーネルの中でネストしたリージョンとして両立させる**ファミリーだと、この構造そのものから確認できた。

## 2. HRMPJoinManager: ドメイン軸とクラス軸をつなぐ共有モジュール

`HRMPPlugin.rb`内には`HRMPPlugin`クラスとは別に`module HRMPJoinManager`（59〜164行）が定義されており、`HRMPDomainPlugin`・`HRMPClassPlugin`の**両方から`include`される**（HRP2Plugin/HRPPlugin/FMPPluginはそれぞれ自分自身に`add_through_plugin`を直接実装していたのと対照的）。これは、リージョン結合の`add_through_plugin`判定がドメイン側・クラス側のどちらから呼ばれても同じロジックを通す必要があるためで、HRMPだけに現れる設計。

`HRMPJoinManager#add_through_plugin`は[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]の判定ロジックとほぼ同型（カーネルオブジェクトセルか／`OutOfDomain`か／ユーザ→カーネルか／ユーザ→ユーザか）だが、**カーネルオブジェクトセル判定とOutOfDomain判定の場合、ドメインをまたがないと分かった時点で`add_through_plugin_class`（クラス軸の判定）に処理を委譲する**——ドメイン軸のチェックをパスしたら、続けてクラス軸のチェックが必要かどうかを2段階で判定する構造。

```ruby
elsif current_domain.get_option.to_s != "kernel" && next_domain.get_option.to_s == "kernel"
    return [ :HRPSVCThroughPlugin, "" ] + add_through_plugin_class( join, current_region, next_region, through_type )
else
    return [ :HRPRPCPlugin, "noClientSemaphore=false,PPAllocatorSize=256" ]
```

**HRMPは自分専用のSVC/RPC仲介プラグインを一切持たない**（`HRMPSVCPlugin`・`HRMPRPCPlugin`のようなファイルは存在しない）——ユーザ→カーネルドメインの結合には[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPSVCThroughPlugin]]を、ユーザ間結合には`HRPRPCPlugin`を**そのまま呼び出す**。HRPファミリーのドメイン境界仲介機構を丸ごと再利用することで、HRMP独自のファイルはわずか4本で済んでいる——[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で発見した「`GenAttMod`/`GenDefSvc`をHRPとHRMPで共有」という関係が、SVC/RPCプラグイン本体のレベルでも成立していたと確認できた。

死コードも残っている：`# return [ :HRPRPCPlugin, "channelCelltype=tMessagebufferChannel,noClientSemaphore=true" ]`——これは[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]が使っていた引数文字列そのものであり（[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]の対比表参照）、HRMPPluginもHRP2由来のコードを経由して作られた可能性を示す一貫した痕跡。

`add_through_plugin_class`（クラス軸の判定、120〜163行）は[[work/active/tecsgen-plugins/FMPPlugin|FMPPlugin#add_through_plugin]]と似た構造（PU/NPUのプロセッサID・ロカリティ取得）を持つが、**FMPPluginが持っていた「クロスプロセッサならRPCを挿入すべき」という死コード（`:FMPRPCPlugin`参照）すら無く**、カーネルオブジェクトセルなら`[]`、それ以外は常に`[]`（Direct Call）——クラス軸単独でのクロスプロセッサRPC挿入はHRMPでは最初から試みられていない。ドメイン軸の判定が先に走って必要なSVC/RPCを挿入済みのため、クラス軸の判定はカーネルオブジェクト検出以外はほぼ形式的な通過処理になっている、と読める。

## 3. HRMPDomainPlugin: HRPと同じ語彙、より完成度の高いSACベクタ計算

`HRMPDomainPlugin < DomainPlugin`。`include HRMPJoinManager`・`include GenAttMod`・`include GenDefSvc`（47〜49行）——[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で発見した「GenAttMod/GenDefSvcはHRPとHRMPで共有、FMPは除外」という記述が、ここで実際の`include`文として直接確認できた。

- ドメイン種別オプションの語彙は`"kernel"`/`"user"`/`"OutOfDomain"`（56〜63行）——[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]の`"trusted"/"nontrusted"`ではなく[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]と完全に同じ語彙。HRMPがHRP系統（HRP2ではなく無印HRP）の直接の派生であることを裏付ける。
- `gen_factory`（89〜112行）は`gen_include`/`gen_att_mod`/`gen_def_svc`をnode_root単位で1回だけ呼ぶ（HRPPluginと同じ設計）のに加え、**`@@include_extsvc_fncd`という別のクラス変数フラグでプログラム全体1回だけ`#include "extsvc_fncode.h"`を出力する**——node_root単位ではなくプロセス全体で1回、という2種類の「一度だけ」制御が同じメソッド内に混在している。
- `get_sac_str`（147〜206行）——**ドメイン境界をまたぐすべての結合を`@@inter_domain_join_set`に記録し（`add_inter_domain_join_set`）、あるカーネルオブジェクトセルに対して実際に結合してきた全ドメインの集合を`TACP_KERNEL`/`TACP(domain_name)`/`TACP_SHARED`のOR結合として組み立てる**、完成度の高いアクセスベクタ計算。[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPSVCSignaturePlugin]]の`restrict_acptn_<func>`が関数単位でありながら計算経路が弱く配線されていた（未検証）のと対照的に、こちらは**呼び出し元は`HRMPKernelObjectPlugin#print_cfg_sac`から`HRMPDomainPlugin.get_sac_str`への単一の呼び出し経路のみ**——[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で指摘していた「`HRPKernelObjectPlugin#gen_factory`と`HRPPlugin.get_sac_str`のどちらが正か」という二重実装のあいまいさが、HRMPでは存在しない（一本化されている）。

## 4. HRMPClassPlugin: FMPPluginと同じJSON宣言方式、生成処理は持たない

`HRMPClassPlugin < ClassPlugin`。`include HRMPJoinManager`。クラス定義の取得方式は[[work/active/tecsgen-plugins/FMPPlugin|FMPPlugin]]と同じ——CDLオプション文字列ではなく`__tool_info__( "HRMP_class_def" )`というJSONブロックを`TOOL_INFO::VALIDATOR`でスキーマ検証して`@@class_info`に格納する。スキーマの`:locality`値は`"only"`/`"all"`/**`"root"`**（63行）——FMPPluginの対応するスキーマが`"only"`/`"all"`/**`"global"`**だったのと、第3の値の呼び名が食い違っている。同じ「クラス定義JSON」という仕組みを共有していながら語彙が統一されていない、[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で見た「HRP2の"trusted/nontrusted"とHRPの"kernel/user"」の不統一と同種の食い違いがここにも見つかった。

`gen_factory`は**空実装**（`def gen_factory node_root; end`、163〜164行）——FMPObjectPlugin/FMPHandlerPluginがそれぞれ独自に`@cell_list`をループしてコード生成していたのとは異なり、HRMPではクラス側のコード生成を一切行わない。生成処理はすべて後述の`HRMPKernelObjectPlugin`に一本化されている。

## 5. HRMPKernelObjectPlugin: オブジェクト系とハンドラ系を1つのテーブルに統合

`HRMPKernelObjectPlugin < CelltypePlugin`。ここがHRMPファミリー最大の構造的特徴——[[work/active/tecsgen-plugins/FMPPlugin|FMPObjectPlugin]]（カーネルオブジェクト）と[[work/active/tecsgen-plugins/FMPPlugin|FMPHandlerPlugin]]（ハンドラ）に分かれていた責務を、HRMPでは**`@@api`という1つのテーブルに統合**している。

```ruby
@@api = {
    "TASK"     => [ :InClass, :InDomain, "TSK", "CRE_TSK( {{id}}, ... )" ],
    "SEMAPHORE"=> [ :InClass, :Any,      "SEM", "CRE_SEM( {{id}}, ... )" ],
    ...
    "KERNEL"   => [ :InClass, :Any,      "SYS", "CRE_SYS"],
    ########## Handlers #########
    "INT_REQUEST"           => [:InClass, :kernel, "INT", "CFG_INT( ... )"],
    "INT_SERVICE_ROUTINE"   => [:InClass, :kernel, "ISR", "CRE_ISR( ... )"],
    ...
    "INIT_ROUTINE" => [:any, :kernel, "INI", "ATT_INI( ... )"],
    "TERM_ROUTINE" => [:any, :kernel, "TER", "ATT_TER( ... )"],
}
```

各エントリは`[クラス配置制約, ドメイン配置制約, マクロ略称, テンプレート文字列]`の4要素——**クラス軸の制約（`:InClass`、FMPHandlerPluginの`:InClass`/`:Any`と同じ発想）とドメイン軸の制約（`:InDomain`/`:kernel`/`:Any`、HRPKernelObjectPluginの`new_cell`と同じ発想）を同じテーブルの同じ行に同居させている**——これはHRP（ドメイン軸のみ）・FMP（クラス軸のみ）どちらの対応テーブルにも無かった、両軸を統合した初めてのテーブル構造であり、「HRMP=HRPの信頼ドメイン＋FMPのクラス配置」という1節の仮説を最も直接的に裏付ける証拠になっている。プレースホルダ置換によるテンプレート文字列生成方式は[[work/active/tecsgen-plugins/FMPPlugin|FMPHandlerPlugin]]と同じ。

**発見（配置制約チェックの大文字小文字不一致バグ）**: `new_cell`（112〜151行）のドメインチェックは`elsif @@api[@plugin_arg_str][1] == :InDomain`（TASKのみ該当）と`elsif @@api[@plugin_arg_str][1] == :Kernel`（大文字K）の2分岐しか実装されていない。しかしハンドラ系のテーブルエントリ（INT_REQUEST/INT_SERVICE_ROUTINE/INT_HANDLER/CPU_EXCEPTION_HANDLER）が指定しているドメイン制約は`:kernel`（小文字k、75〜93行）——**大文字小文字が一致しないため、これらのハンドラに対する「kernelドメインに置かれていること」という配置チェックは実装意図に反して一度も発火しない**。[[work/active/tecsgen-plugins/TracePlugin|TracePlugin]]の`@b_diplayTime`綴りミスや[[TECSCDE外部仕様]]第6章のRedo無効化と同種の、シンボルの表記ゆれによる検証漏れ。

`print_cfg_sac`（182〜199行）は`HRMPDomainPlugin.get_sac_str`（3節）を呼ぶ単一経路——[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で未解決のまま残していた二重実装問題がHRMPには存在しないことを裏付ける。

`gen_factory`（207〜252行）は各セルに対し`KERNEL_DOMAIN{...}`/`DOMAIN(<name>){...}`（ドメイン軸の外側ラップ）の内側にさらに`CLASS(<class>){...}`（クラス軸の内側ラップ、`"root"`なら省略）をネストする——**[[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin]]・[[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPKernelObjectPlugin]]で「死コードとして残っていた」`KERNEL_DOMAIN{}`/`DOMAIN(){}`ラップ処理と全く同じロジックが、HRMPでは生きたコードとして存在する**——HRP/HRP2ではこの責務が`GenAttMod`側へ移譲されて元のコードが死んだのに対し、HRMPは「ドメインラップ＋クラスラップ」という`GenAttMod`が単独では担えない2階層のネストが必要なため、`HRMPKernelObjectPlugin`自身が両方のラップを直接実装し続けている、と解釈できる——これまでのセッションで繰り返し見てきた死コードの謎への、最後のピースとなる説明。

## 6. エラーコードの傾向

`HRMP9999`という汎用プレースホルダのみ——HRP・HRP2・FMPいずれのカーネルオブジェクト生成系にも共通する「専用コード体系が無いまま」という傾向がHRMPでも再現している。

## 7. 制約・注意点

- CDL実例はリポジトリ内に見つからず、`domain(HRMP, ...)`と`class(HRMP, ...)`のネスト構文はソースからの逆算・未検証。
- 5節で指摘した`:kernel`/`:Kernel`の大文字小文字不一致は、実際にCDL上で誤配置したハンドラがエラーにならずすり抜けるバグである可能性が高いが、tecsgen本体のテストコードや実行での確認はしていない。
- これで北極星に一度も載っていなかった3ファミリー（HRP・FMP・HRMP）すべてが完走。次にtecsgenプラグイン仕様書に着手する際は、TLVTracePlugin（実体不明）を除き、名前の付いたカテゴリを含む全ファミリーが完了した状態からの再スコープが必要になる。

## Related

- [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] — ドメイン語彙・GenAttMod/GenDefSvc共有・SVC/RPCプラグイン本体の再利用元
- [[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPDomainBoundaryPlugin]] — HRMPが直接呼び出すHRPSVCThroughPlugin/HRPRPCPluginの実装
- [[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPKernelObjectPlugin]] — カーネルオブジェクト生成テーブルの対比元、死コードの謎を解く鍵
- [[work/active/tecsgen-plugins/FMPPlugin|FMPPlugin]] — クラス定義JSON方式・PU/NPU判定ロジックの対比元
- [[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]] — `MultiPlugin`ディスパッチ機構の初出
- [[tecsgen外部仕様]] — 6.2 プラグイン呼び出し規約（`DomainPlugin`/`ClassPlugin`両行）・6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理。北極星未追跡3ファミリー（HRP・FMP・HRMP）が本ノートで完走
