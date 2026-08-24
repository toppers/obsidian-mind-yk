---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン TECSInfoPlugin・TECSInfoCompoPluginの仕様書。CDLモデル全体（セルタイプ・セル・シグニチャ・呼び口/受け口）を実行時イントロスペクションできるCデータ構造を生成する機構。MrubyInfoBridgePluginが使うTECSInfo APIの供給元と確認"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# TECSInfoPlugin / TECSInfoCompoPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]]（2026-08-15）に続き、[[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]]で発見した3つ目の未追跡対象に着手。一次資料は`tecslib/plugin/TECSInfoPlugin.rb`（290行）・`TECSInfoCompoPlugin.rb`（96行）の計2ファイル。これでカバレッジ監査の4候補のうち3つが完了、残るは`RepeatCellPlugin`/`RepeatJoinPlugin`のみ。

## 1. 確認: MrubyInfoBridgePluginが使うTECSInfo APIの供給元だった

[[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin]]執筆時（2026-08-14）に発見した「`TECSInfo`という実行時イントロスペクションAPI——`cTECSInfo_findRawEntryDescriptor`等で文字列パスから対象を検索する仕組み」の**供給元がTECSInfoPluginだった**と確認できた。`TECSInfoPlugin < CelltypePlugin`は、CDLで宣言された`tTECSInfo`セルタイプに付与され、**コンパイル対象のCDLモデル全体（すべてのセルタイプ・セル・シグニチャ・受け口・呼び口・属性・変数）を実行時に参照できるCデータ構造一式**を生成する。

## 2. gen_factory: 6種類の`nTECSInfo_t*Info_factory.h`を生成する

`gen_factory`（96〜264行）は、モデルの構成要素ごとに専用のヘッダファイルを1つずつ生成する。

| 生成ファイル | 内容 |
|---|---|
| `include_all_signature_header.h` | プロジェクト全シグニチャの`_tecsgen.h`を一括インクルードする集約ヘッダ |
| `nTECSInfo_tVarDeclInfo_factory.h` | 変数宣言情報（属性/変数のオフセット・型） |
| `nTECSInfo_tCelltypeInfo_factory.h` | セルタイプ情報（属性数・変数数・呼び口数・受け口数、シングルトンか等） |
| `nTECSInfo_tCallInfo_factory.h` | 呼び口情報（シグニチャ・配列サイズ・optional/dynamic/ref_desc等の指定子） |
| `nTECSInfo_tEntryInfo_factory.h` | 受け口情報 |
| `nTECSInfo_tCellInfo_factory.h` | セル情報 |
| `nTECSInfo_tRawEntryDescriptorInfo_factory.h` | 生の受け口ディスクリプタ情報——動的結合（`[dynamic]`）が使う低レベル記述子 |

各ファイルの生成には[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]/[[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]]で見た`TOPPERS_CB_TYPE_ONLY`トリック（CELLCB型定義だけを取り込む）が本格的に使われているうえ、**取り込んだ定義が意図せず再定義エラーを起こさないよう、数十個のマクロ名を明示的に`#undef`する長大なリストを都度組み立てている**（119〜177行・157〜177行・192〜206行・249行）——多数の異なるセルタイプ（tVarDeclInfo/tCelltypeInfo/tCallInfo等）の生成マクロが同じ生成基盤（`print_celltype_define`等）を使い回すことで生じる名前衝突を、リテラルな`#undef`列挙で手動回避している、既存プラグインには見られなかった大規模なマクロ衝突対策。

## 3. new_cell: セル生成時にCDLフラグメントを動的に生成・インポートする新パターン

`new_cell`（58〜94行）は、この調査シリーズで初めて見る手法を使う——**一時CDLファイルをその場で書き出し、`Import.new`でコンパイル中のモデルへ動的に取り込む**：

```ruby
fn = "#{$gen}/tmp_#{cell.get_region.get_global_name}_TECSInfoSub.cdl"
File.open( fn, "w" ){ |f|
  f.print <<EOT
#{indent}[in_through()]
#{indent}region rTECSInfo {
#{indent}    cell nTECSInfo::tTECSInfoSub TECSInfoSub;
#{indent}};
EOT
}
Import.new fn
```

これまでのプラグイン（例: [[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenCellPlugin]]）は`generate(...)`という**CDL文そのものをテキストとして出力先ファイルに書く**やり方だったのに対し、TECSInfoPluginは**一時ファイルにCDL断片を書き出し、`Import`クラスを直接呼んでコンパイル中のモデルへその場で取り込ませる**——[[work/active/tecsgen-plugins/TracePlugin|TracePlugin]]で見つけた`in_through()`指定子（region境界をまたぐすべての結合へ一括適用する形式の1つ）をここでも使い、`tTECSInfo`セルの近くに専用のサブリージョン`rTECSInfo`と補助セル`TECSInfoSub`を自動的に作り込む。

続けて、そのセルに`cTECSInfo`という呼び口の結合が無ければ、`rTECSInfo::TECSInfoSub.eTECSInfo`への結合を**自動的に追加する**——ユーザーがCDLで明示的に書かなくても、`tTECSInfo`セルは常に自分専用のイントロスペクション補助セルへの経路を持つ、という暗黙の配線。

### 3.1 副作用: `--unoptimize-entry`をプラグイン自身が強制する

`initialize`（50〜56行）は、`$unopt_entry`（[[tecsgen外部仕様]] 5.2の`--unoptimize-entry`オプションに対応するグローバル変数）が`false`の場合、**プラグインの初期化時点で勝手に`true`へ書き換え**、その旨を`TIF0001`という情報メッセージで通知する：

```ruby
if $unopt_entry == false then
  cdl_info( "TIF0001 forcely set --unoptimize-entry by TECSInfoPlugin (by importing TECSInfo.cdl)" )
  $unopt_entry = true
end
```

——`TECSInfo.cdl`をインポートするだけで、**プロジェクト全体のコマンドラインオプション相当の最適化設定がコンパイラ全体レベルで強制的に上書きされる**。[[tecsgen外部仕様]] 4.4で説明した「受け口最適化（optimize_entry）」——スケルトン関数を省略する最適化——が無効化される。イントロスペクション目的でランタイムから任意の受け口を検索・呼び出す以上、スケルトン関数が省略されていては困る、という機能要件から来る強制であり、ユーザーが意識しないまま最適化方針が変わる、実質的なグローバル副作用。

## 4. get_post_code_priority: 全モデル確定後に実行されることを保証する

`self.get_post_code_priority`（284〜288行）は`PluginModule::SIGNATURE_PLUGIN_POST_CODE_PRIORITY + 1000`を返す——**他のシグニチャプラグインのpost_codeがすべて生成し終わったあとに、意図的に最後に実行されるよう優先度をずらしている**。TECSInfoPluginの生成物（各種`*Info_factory.h`）はプロジェクト全体のセルタイプ・シグニチャを横断的に参照するため、他プラグインの生成結果が出そろってから走る必要がある——この調査シリーズで初めて明示的に確認できた、プラグイン間の実行順序制御の仕組み。

`gen_post_code`（266〜282行）自体も`Generator.get_n_error > 0`なら`I9999`情報メッセージを出して即座に処理を打ち切る——[[TECSCDE外部仕様]] 第9章で見た「tecsgen本体はコード生成前にエラー件数を確認して`exit`するが、TECSCDEが呼ぶ`run1`にはこのチェックが無い」という記述と対をなす、**tecsgen本体側での早期エラー打ち切りの実例**をここで直接確認できた。

## 5. TECSInfoCompoPlugin: `$Id`が指すのは基底クラスでなく「TECSInfoPlugin自身の古いリビジョン」

`TECSInfoCompoPlugin < CompositePlugin`。複合セルタイプ版の`tTECSInfo`に対応する。`new_cell`は3節で見た`TECSInfoPlugin#new_cell`と**一字一句同一のコード**（一時CDLファイル生成・`Import.new`・`cTECSInfo`自動結合・`$unopt_entry`強制のすべてが同じ）——ただし`gen_factory`・`gen_post_code`・`get_post_code_priority`は一切持たない（`CompositePlugin`側では2〜4節の生成処理が不要、または`TECSInfoPlugin`側の生成が複合セルタイプの構成要素にも及ぶため重複させていないと考えられる）。

**発見**: `TECSInfoCompoPlugin.rb`の`$Id`は

```
$Id: TECSInfoPlugin.rb 2952 2018-05-07 10:19:07Z okuma-top $
```

——[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]・[[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]]で見た「基底クラスのファイル名を指す」パターンとは異なり、**自分自身が属する（はずの）ファミリーの相方——`TECSInfoPlugin.rb`——を、しかも古いリビジョン番号（2952、2018年）で**指している。一方`TECSInfoPlugin.rb`自身の`$Id`はリビジョン3159（2020年）と、より新しい。つまり**`TECSInfoCompoPlugin.rb`は、`TECSInfoPlugin.rb`がまだ`new_cell`だけを持ち`gen_factory`を持たなかった（あるいは現在と異なる）古い時点からフォークして作られ、その後`TECSInfoPlugin.rb`だけが2020年まで拡張され続けた**、という系譜が`$Id`の数値差から直接読み取れる——CIfGen/CppIfGenの「基底クラステンプレートからの複製」とは異なる、「同じファミリーの兄弟ファイルからの分岐」という、この調査で初めて見る`$Id`不一致のバリエーション。

## 6. 制約・注意点

- CDL実例（`tTECSInfo`セルタイプの具体的な宣言・`TECSInfo.cdl`の中身）はリポジトリ内で直接確認しておらず、`new_cell`が動的生成するCDL断片から逆算した理解にとどまる。
- `TECSInfo.print_info`（`gen_post_code`が呼ぶ、実際のイントロスペクションデータ出力を担うクラス）自体は未読——本ノートは`TECSInfoPlugin`/`TECSInfoCompoPlugin`という「呼び出し元」の挙動のみを扱う。
- 残る[[work/active/tecsgen-plugins/PluginCoverageAudit|カバレッジ監査]]の候補は`RepeatCellPlugin`・`RepeatJoinPlugin`のみ。

## Related

- [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin]] — `TECSInfo`APIの消費者側、本ファミリーの発見動機
- [[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]・[[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]] — `TOPPERS_CB_TYPE_ONLY`トリック・`$Id`不一致パターンの対比元
- [[work/active/tecsgen-plugins/TracePlugin|TracePlugin]] — `in_through()`等through系指定子の初出
- [[TECSCDE外部仕様]] 第9章 — tecsgen本体の早期エラー打ち切り（`Generator.get_n_error`チェック）との対比元
- [[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]] — 本ファミリー発見の経緯
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理
