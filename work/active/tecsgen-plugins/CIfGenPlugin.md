---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン CIfGenPlugin・CIfGenCelltypePlugin・CIfGenCellPluginの仕様書。非TECS C言語コードからTECSセルの受け口を直接呼び出せる*_cif.hヘッダを生成する、C2TECSBridgePluginとは別系統のC連携機構と判明"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# CIfGenPlugin / CIfGenCelltypePlugin / CIfGenCellPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]]（2026-08-15）で発見した、完全未追跡だった`MultiPlugin`ファミリーの1つ目に着手。一次資料は`tecslib/plugin/CIfGenPlugin.rb`（60行）・`CIfGenCelltypePlugin.rb`（152行）・`CIfGenCellPlugin.rb`（75行）の計3ファイル。ソース位置は他ノートと同じく`E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。対になる`CppIfGenPlugin`ファミリーは未着手のまま残る。

## 1. 用途: 非TECS C言語コードからTECSセルの受け口を直接呼び出す

`CIfGenCelltypePlugin#gen_factory`が生成する`<celltype名>_cif.h`ヘッダの内容から、このファミリーの目的が確定できる——**TECS外の、通常のC言語で書かれたコードから、特定のTECSセルの受け口関数を直接呼び出せるようにする、フラットなCマクロ群を生成する**プラグイン。「CIfGen」＝「C Interface Generation」という名前どおりの機能だった。

```c
/* 生成される <celltype>_cif.h の骨格 */
#ifndef #{celltype}_H
#define #{celltype}_H
/*
 * This header file is intended to be included in non-TECS celltype code.
 * Multiple *_cif.h files can be included in non-TECS celltype code.
 */
#ifndef TOPPERS_CB_TYPE_ONLY
#define TOPPERS_CB_TYPE_ONLY
#include "#{celltype}_tecsgen.h"   /* CELLCB型定義だけを取り込む */
#undef TOPPERS_CB_TYPE_ONLY
#endif

/* セル単位・受け口関数単位でフラットなマクロを生成 */
#define #{cell}_#{port}_#{function}( args... ) \
        #{celltype}_#{port}_#{function}( cell_IDX, args... )
#endif
```

`TOPPERS_CB_TYPE_ONLY`という一時的なマクロで`<celltype>_tecsgen.h`をインクルードすることで、**CELLCB型定義だけを取り込み、TECS固有のインライン関数本体は取り込まない**——非TECSコードに対してTECSの内部API全体を晒さず、型情報だけを渡す狙いが読み取れる。そのうえで、セルタイプが持つ全ENTRY系ポートの全関数について、`<cell名>_<ポート名>_<関数名>(引数...)`という具体的なセル名を含んだCマクロを1つずつ定義し、そのマクロ経由で本来の`<celltype>_<ポート名>_<関数名>(IDX, 引数...)`呼び出しへ展開する。**呼び出し元は`IDX`（セルインデックス）を意識する必要がなく、セル名で直接呼べる**——TECSのセル・IDX機構を隠蔽した薄いCマクロ層。

## 2. C2TECSBridgePluginとの違い: CDLグラフ内蔵 vs 外部ヘッダ生成

同じ「C言語との連携」を扱う[[work/active/tecsgen-plugins/CInterfaceBridgePlugin|C2TECSBridgePlugin]]とは、名前の響きが似ているが仕組みが根本的に異なる。

| 観点 | C2TECSBridgePlugin | CIfGenPlugin |
|---|---|---|
| 基底クラス | `SignaturePlugin` | `MultiPlugin`（`CelltypePlugin`/`CellPlugin`にディスパッチ） |
| 動作の場 | CDLの結合グラフの中に「Cコードから呼べるTECSセル」を組み込む | CDLグラフの外——非TECS Cコードから直接includeするヘッダファイルを生成するだけ |
| 生成物 | CDLコード上のセル定義（`generate(C2TECSBridgePlugin, sSignature, ...)`） | `<celltype>_cif.h`という独立したCヘッダファイル |
| 呼び出し側 | TECSの結合機構を経由（呼び口・受け口） | TECS結合を経由せず、Cのプリプロセッサマクロで直接関数呼び出しへ展開 |

C2TECSBridgePluginは「Cコードの1関数ポインタをTECSシグニチャの受け口として結合可能にする」変換機、CIfGenPluginは「特定セルの受け口関数を、TECSの外にいるCコードから直接呼べる名前で公開する」露出機——**双方とも「C↔TECS境界」を扱うが、片方はTECS結合グラフの内側へCを持ち込み、もう片方はTECSセルをグラフの外へ持ち出す**、方向が逆の設計だった。

## 3. MultiPluginディスパッチ: SignaturePlugin/ThroughPlugin/DomainPluginでは無効

`CIfGenPlugin < MultiPlugin`（この調査シリーズ4件目の`MultiPlugin`実例、[[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]]・[[work/active/tecsgen-plugins/HRMPPlugin|HRMPPlugin]]に続く）。

```ruby
def self.get_plugin superClass
  if superClass == SignaturePlugin then return nil
  elsif superClass == CelltypePlugin then return CIfGenCelltypePlugin
  elsif superClass == CellPlugin then return CIfGenCellPlugin
  elsif superClass == ThroughPlugin then return nil
  elsif superClass == DomainPlugin then return nil
  else return nil
  end
end
```

celltype／cellへの付与のみ対応し、signature・through・domainへの付与は`nil`——**MrubyBridgePluginが4種類の位置すべてに対応していたのと異なり、CIfGenPluginは2種類の位置にしか実体を持たない**、MultiPluginディスパッチの中でも狭い適用範囲を持つ実例。

## 4. 発見: 3ファイルすべてに、コピー元を示す`$Id`の食い違い

[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で見つけた「`GenAttMod.rb`の`$Id`が`HRMPDomainPlugin.rb`を指す」という痕跡と同種の証拠が、CIfGenPluginファミリーでは**3ファイルすべて**に見つかった。

| ファイル | 実際のファイル名 | `$Id`が指す名前 |
|---|---|---|
| `CIfGenPlugin.rb` | CIfGenPlugin.rb | `MultiPlugin.rb` |
| `CIfGenCelltypePlugin.rb` | CIfGenCelltypePlugin.rb | `CelltypePlugin.rb` |
| `CIfGenCellPlugin.rb` | CIfGenCellPlugin.rb | `CellPlugin.rb` |

いずれも**自分がディスパッチされる先の基底クラス（`MultiPlugin`/`CelltypePlugin`/`CellPlugin`）そのもののファイル名**が`$Id`に残っている——このファミリーは「基底クラスのテンプレートファイルをそのままコピーしてクラス名だけ書き換える」という、これまでの調査で見た個別の複製痕跡（HRPPlugin←HRP2Plugin等）よりもさらに直接的な、**基底クラスからの複製という制作過程そのもの**を示す一次証拠。3ファイルすべてで一貫して再現している点が、単発の書き換えミスではなく制作手順そのものだったことを裏付ける。

## 5. CIfGenCellPlugin: セル単位の付与はセルタイプ単位への委譲に過ぎない

`CIfGenCellPlugin < CellPlugin`。個々のセルへの付与（`[generate(CIfGenPlugin, "")]`をcellに付与）に対応するが、自身ではヘッダを生成しない——`gen_cdl_file`が生成するのは**CDLコードそのもの**：

```ruby
def gen_cdl_file file
  file.print <<EOT
/* apply CIfGenCelltypePlugin to celltype '#{@cell.get_celltype.get_name}' ... */
generate( CIfGenCelltypePlugin, #{@cell.get_celltype.get_namespace_path.get_path_str}, "" );
EOT
end
```

つまり「セルへの付与」は実質的に「そのセルの属するセルタイプへ`CIfGenCelltypePlugin`をstatement形式で再付与する」という間接呼び出しに過ぎない。**このセルタイプに属する他のすべてのセルにも同じ`_cif.h`が生成されてしまう**——これは実装上の制約であり、著者自身のコメントが明記している：

> 現状実装では、すべてのセルに対してセルプラグインを適用するのと同じ（IDX マクロを特定セルに対してのみ出力するか、どうかの違い）

——「セル単位で選択的に適用しているつもりでも、実際にはセルタイプ単位で丸ごと適用されてしまう」という、[[work/active/tecsgen-plugins/HRP2Plugin|HRP2SVCPlugin/HRP2RPCPlugin]]の「mikan（未完成）」コメントと同種の、著者自身が把握して明記した未完成の粒度制御。

## 6. 制約・注意点

- CDL実例はリポジトリ内に見つからず、`[generate(CIfGenPlugin, ...)]`の具体的な記述例・オプション文字列の意味（`@plugin_arg_str`は取得されるが本体では未使用）はソースからの逆算・未検証。
- 5節の「セル単位のつもりがセルタイプ単位になる」制約は、実際にCDLで複数セルに異なる設定をしようとした場合の挙動として要注意——本ノートでは著者コメントの存在のみ確認し、実際の生成結果の検証はしていない。
- 対になる[[work/active/tecsgen-plugins/PluginCoverageAudit|CppIfGenPlugin]]ファミリー（C++版、実体3ファイル）は未着手。名前の対称性から同じ設計を想定しがちだが、[[work/active/tecsgen-plugins/CInterfaceBridgePlugin|C2TECSBridgePlugin/TECS2CBridgePlugin]]で学んだとおり対称な名前が対称な実態を保証しないため、実際に読むまで前提を置かない。
- [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|TECSInfoPlugin]]・`RepeatCellPlugin`/`RepeatJoinPlugin`も引き続き未着手。

## Related

- [[work/active/tecsgen-plugins/CInterfaceBridgePlugin|CInterfaceBridgePlugin]] — 「C↔TECS境界」を扱う別系統プラグイン、方向性の対比元
- [[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]] — `MultiPlugin`ディスパッチ機構の初出
- [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] — `$Id`不一致という同種の複製痕跡の初出
- [[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]] — 本ファミリー発見の経緯
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理
