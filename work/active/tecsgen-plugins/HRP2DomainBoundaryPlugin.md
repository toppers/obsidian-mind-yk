---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン HRP2SVCPlugin・HRP2RPCPlugin・HRP2KernelObjectPlugin の仕様書。HRP2Plugin の add_through_plugin が自動挿入する2つのドメイン境界仲介プラグインと、その判定に使うカーネルオブジェクトセル判定基盤"
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

# HRP2SVCPlugin / HRP2RPCPlugin / HRP2KernelObjectPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] 仕様書（2026-08-14）の「5. 関連プラグイン」節で「別ファイル、未記載」と明記していた3件を執筆。着手のきっかけは、プラグイン仕様書シリーズの名前の付いたカテゴリ（カーネル対応・mrubyブリッジ・トレース・RPC・Cインタフェース）が完走した時点で [[North Star]] の「17件」カウント自体を `tecslib/plugin/` の実ファイル一覧（79ファイル）と突き合わせ直したところ、`HRP2*` だけで約15ファイルの未記載ファミリーが存在し、さらに `HRP*`（無印HRP）・`FMP*`・`HRMP*` という3つの独立したカーネルドメインファミリーが北極星の一覧に一度も登場していないと判明したこと。今回はその中で最も緊急度が高い——HRP2Plugin 自身の動作説明に必須な——3ファイルに範囲を絞った。一次資料は `tecslib/plugin/HRP2SVCPlugin.rb`（473行）・`tecslib/plugin/HRP2RPCPlugin.rb`（325行）・`tecslib/plugin/HRP2KernelObjectPlugin.rb`（374行）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 概要

**3プラグインは、[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] の `add_through_plugin`（3.5節）が保護ドメイン境界をまたぐ結合を検出したときに自動的に挿入する「仲介プラグイン」と、その判定に使う基盤クラスである。**

- **`HRP2KernelObjectPlugin`**（`< CelltypePlugin`）: 直接の仲介プラグインではなく、HRP2 カーネルオブジェクト（セマフォ・タスク等）を生成する具象プラグイン群の共通親クラス。`add_through_plugin` の条件1「結合先セルがカーネルオブジェクトセルか」を判定する `include_celltype?` を提供する。
- **`HRP2SVCPlugin`**（`< ThroughPlugin`）: ユーザドメイン→カーネルドメイン（条件3）で挿入される。TOPPERS/HRP2 の拡張サービスコール（SVC）機構を使い、保護レベルの低いドメインから高いドメインへの呼び出しを、カーネルが仲介する安全な経路に変換する。
- **`HRP2RPCPlugin`**（`< ThroughPlugin`）: 異なるユーザドメイン間（条件4）で挿入される。[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] と同じ `GenTransparentMarshaler` モジュールを使う、Transparent RPC の HRP2 専用版。

## 2. HRP2KernelObjectPlugin（`< CelltypePlugin`）

### 2.1 役割: カーネルオブジェクト生成プラグインの抽象基底クラス

`gen_factory`（167〜312行）は具象実装済みだが、`print_cfg_cre`・`print_cfg_sac`・`get_entry_ports_name_list`・`string_cfg_cre` の4メソッドは `raise "called virtual method ... in #{@celltype.get_name} plugin"` で純粋仮想メソッドとして定義されている（139〜165行）。ATK1Plugin ファミリー（[[work/active/tecsgen-plugins/ATK1Plugin]]）の `ATK1KernelPlugin` と同じ設計パターン——1つの抽象基底クラスの下に、カーネルオブジェクト種別ごとの具象サブクラスがぶら下がる構造。**具象サブクラス10種の詳細仕様は [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin 具象サブクラス群仕様書]]（2026-08-15完成）参照**——ATK1と異なり単機能8種＋テーブル駆動の汎用2種という二層構造で、汎用2種は単機能プラグインが存在しないオブジェクト種別（KERNEL・MESSAGE_BUFFER・割込み関連3種）にも対応する。

### 2.2 gen_factory の処理

各セルについて、①セルが属する `region` のドメイン種別（`get_domain_root.get_domain_type`）を調べ、②`trusted` なら `KERNEL_DOMAIN{ INCLUDE(...) }`、それ以外なら `DOMAIN(<region名>){ INCLUDE(...) }` という OS コンフィギュレーションファイル（`tecsgen.cfg`・`tecsgen_<region名>.cfg`）を生成し、③サブクラスが実装する `print_cfg_cre`/`print_cfg_sac`（`CRE_*`・`SAC_*` という TOPPERS/HRP2 のコンフィギュレータ生成物）へ委譲する。`accessPattern` 属性からアクセス許可ベクタ（`TACP_KERNEL`/`TACP(<domain>)`/`TACP_SHARED`）も生成する（260〜306行）。

### 2.3 include_celltype?（クラスメソッド、370〜372行）

```ruby
def self.include_celltype?( celltype )
  return @@celltype_list.include?(celltype)
end
```

`initialize` で `HRP2KernelObjectPlugin.set_celltype(celltype)`（134〜137行）が全インスタンス生成時にクラス変数へ自セルタイプを登録するため、**このプラグインを使う celltype すべてが自動的に「カーネルオブジェクトセルタイプ」として登録される**——サブクラス側で明示的な登録処理は不要。[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] 3.5節の条件1・[[#3.2 gen_ep_func_body の分岐|3.2節]]・HRP2RPCPlugin/HRP2SVCPlugin 双方の `gen_plugin_decl_code`/`gen_through_cell_code` からこのクラスメソッドが横断的に参照される。

## 3. HRP2SVCPlugin（`< ThroughPlugin`）

### 3.1 拡張サービスコール（SVC）の仕組み

`SVCManage`（内部クラス、48〜73行）が関数ごとに一意な SVC 番号を自動採番する（`@@id` を20から連番、`assign_id`）。生成される呼び出し元コードは `cal_svc( <svcid>, par1, par2, par3, par4, par5 )`（324行）——TOPPERS/HRP2 カーネルの拡張サービスコール API をそのまま使い、引数は最大5個の `intptr_t` にキャストして渡す（型情報は失われ、呼び出し先で元の型へキャストし直す）。

### 3.2 gen_ep_func_body の分岐（283〜471行）

`HRP2KernelObjectPlugin.include_celltype?(@next_cell.get_celltype)` で分岐する。

| 条件 | 生成されるコード |
|---|---|
| 結合先がカーネルオブジェクトセル**ではない** | `cal_svc(<svcid>, ...)` によるサービスコール発行コードと、カーネルドメイン側で実行される SVC ハンドラ関数（`#{@ct_name_body}_#{func_name}`、引数のメモリアクセス検証 `prb_mem` 付き）の両方を生成し、`DEF_SVC` としてカーネルドメインへ登録する |
| 結合先が**カーネルオブジェクトセルの場合** | 「カーネルドメインのセルは特別なことは何もせず，普通に呼び出す」（467〜469行のコメント）として `super`（`ThroughPlugin` のデフォルト処理）へ委譲する——[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] 3.5節の条件1（カーネルオブジェクトセルへの結合は仲介プラグインを挿入しない）と一貫した二重の判定になっている |

### 3.3 引数のメモリアクセス検証（`prb_mem`）

SVC ハンドラ側で、ポインタ引数（`get_ptr_level > 0`）について `IN` 方向なら読み取り検証（`TPM_READ`）、`OUT` 方向なら書き込み検証（`TPM_WRITE`）を `prb_mem` で行い、失敗時は `E_MACV`（メモリアクセス違反）を返す（406〜426行）。ユーザドメインが渡すポインタをカーネルドメインが盲目的に信用しない、保護ドメイン機構らしい設計。

## 4. HRP2RPCPlugin（`< ThroughPlugin`、`include GenTransparentMarshaler`）

### 4.1 RPCPlugin ファミリーとの関係

[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] と同じ共有モジュール `GenTransparentMarshaler`（`tecslib/plugin/lib/GenTransparentMarshaler.rb`）を `include` し、`RPCPluginArgProc` を複製して `noClientSemaphore`・`semaphoreCelltype` オプションを追加する（67〜69行）——**定数名 `TransparentRPCPluginArgProc` は `RPCPlugin.rb` の同名定数と同じ名前だが別クラスのスコープにある別の定数**であり、衝突しない（両クラスとも `RPCPluginArgProc.dup` から独立に複製している）。channel 生成のクライアント/サーバー composite 構造（`eEventflag`/`eSemaphore`/`eMessageBuffer` の3ポート）も [[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] の Transparent 版とほぼ同型——実体としては「RPCPlugin の HRP2 ドメイン間結合専用フォーク」に近い。

### 4.2 相違点

- サーバー側 composite が `[active]` 指定で専用タスク（`tRPCDedicatedTaskMain`）を生成する点は RPCPlugin の dedicated 版と同じだが、`taskPriority` 属性を通じて **HRP2Plugin から呼ばれる際は `@task_priority` が渡される**（281行）——RPCPlugin 側は呼び出し元がプラグイン引数で明示的に指定する
- `[[North Star]]`・[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin 仕様書]] で既に確認済みの通り、HRP2Plugin の `add_through_plugin` 条件4（別ユーザドメイン間の結合）で `channelCelltype=tMessagebufferChannel,noClientSemaphore=true` という固定引数で呼ばれる——利用者が `generate(HRP2RPCPlugin, ...)` を明示的に書くことは通常想定されていない

## 5. 発見: 両プラグイン共通の「mikan」コメント

`HRP2SVCPlugin.rb`（40〜46行）と `HRP2RPCPlugin.rb`（48〜54行）の冒頭に、一字一句同じ制限事項コメントが存在する。

```
# mikan through plugin: namespace が考慮されていない
# これを利用する場合、以下のように toppers_jsp.cdl sChannel.cdl を指定する必要がある
# tecsgen toppers_jsp.cdl sChannel.cdl your_description.cdl

# 以下を仮定（制限事項）
#  呼び元、呼び先のエンディアン、char, short, int_t, long_t, intptr_t のサイズが同じ
#  有符号、無符号でサイズが同じ
```

「mikan」は tecsgen ソース全体で使われる開発者用語で、未完成・既知の制限を示す接頭辞（[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] 仕様書でも同種の注記が別箇所にあった）。ここでは**名前空間（namespace）が正しく考慮されていない**という、HRP2 ドメイン境界仲介プラグイン共通の未解決の制限が、作者自身によって明記されている——同一文言が2ファイルにコピーされている点から、共通の設計上の弱点として認識されていたことがうかがえる。

## 6. 制約・注意点

- 2節の通り、`HRP2KernelObjectPlugin` は抽象基底クラスであり、実際にカーネルオブジェクトを生成する具象サブクラス10種は [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|別ノート]]（2026-08-15完成）で執筆済み。
- 5節の「mikan」コメントの通り、両プラグインとも名前空間の扱いに既知の制限がある（未検証・詳細不明）。
- `HRP2SVCPlugin` はデバッグ用 `puts`/`p` 呼び出しが多数残っており（92〜94行等）、開発中コードの色が強い。
- `HRP*`（無印、HRP2の前身カーネル向け）・`FMP*`・`HRMP*` という3つの独立したカーネルドメインプラグインファミリーが `tecslib/plugin/` に存在するが、[[North Star]] の17件リストに一度も登場しておらず、本ノートの範囲外——北極星のカウント自体の整理が必要という、以前から繰り越されていた課題の具体的な内訳の一部であると今回判明した。

## Related

- [[work/active/tecsgen-plugins/HRP2Plugin]] — 本ノートが補完する、ドメイン境界宣言プラグイン本体。「5. 関連プラグイン」節の3つの空欄をここで埋めた
- [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin]] — `HRP2KernelObjectPlugin` の具象サブクラス10種（本ノートでは抽象基底クラスのみ扱う）
- [[work/active/tecsgen-plugins/RPCPlugin]] — `HRP2RPCPlugin` が共有する `GenTransparentMarshaler` モジュールの一般版（`RPCPlugin`）
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧（HRP2 系は個別ノートへのリンクのみで詳細は未収録）
- [[North Star]] — プラグイン仕様書化の進捗管理。「17件」カウントの不整合の内訳を本ノートで一部具体化
