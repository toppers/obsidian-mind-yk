---
date: 2026-08-14
description: "tecsgen 標準付属プラグイン MrubyInfoBridgePlugin（実体3ファイル）の仕様書。MrubyBridgePluginの静的結合とは異なり、TECSInfo実行時イントロスペクションAPIを使い、mrubyスクリプト側が文字列パスを指定して実行時にセルの受け口を検索・バインドする動的版のmrubyブリッジ"
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

# MrubyInfoBridgePlugin 仕様書

> [!info] 文書状態
> [[North Star]] の mruby ブリッジ系3件目・最終項目。実体は `tecslib/plugin/` の3ファイル（`MrubyInfoBridgePlugin`・`MrubyInfoBridgeSignaturePlugin`・`MrubyInfoBridgeCellPlugin`）。[[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]] 執筆時点で「同じ `MultiPlugin` ディスパッチ構造と推定・要確認」としていた仮説を、本ノートでソースにより確認した。一次資料はこの3ファイルと、参照先の `tecs/TECSInfo/TECSInfoAccessor.cdl`（TECSInfo リフレクション API の定義）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 概要

**MrubyInfoBridgePlugin は、[[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]] と同じく mruby スクリプトから TECS の受け口を呼び出すブリッジを生成するプラグインだが、結合方式が根本的に異なる。** MrubyBridgePlugin はブリッジセルの呼び口 `cTECS` を CDL 記述時に対象セルへ**静的に結合**するのに対し、MrubyInfoBridgePlugin は `TECSInfo`（TECS の実行時イントロスペクション API、`tecs/TECSInfo/TECSInfoAccessor.cdl`）を使い、mruby 側が**文字列のセルパスを渡すことで実行時に対象を検索・検証してバインドする**（[[tecsgen外部仕様]] 6.3 の「TECSInfo を使った mruby ブリッジ（V1.7.0）」の実体）。

## 2. `MultiPlugin` ディスパッチ（仮説の確認）

`MrubyInfoBridgePlugin < MultiPlugin` の `get_plugin` は2分岐のみ実装（`CelltypePlugin`/`CompositePlugin` 分岐はコメントアウトで未実装——[[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]] の5ファイル構成に対し3ファイルしか存在しない理由はこれで確定した）。

| `superClass` | 返すクラス |
|---|---|
| `SignaturePlugin` | `MrubyInfoBridgeSignaturePlugin` |
| `CellPlugin` | `MrubyInfoBridgeCellPlugin` |
| `CelltypePlugin`／`CompositePlugin` | 未実装（コメントアウト） |

## 3. 発見: `MrubyInfoBridgeCellPlugin` は「そのセル」とは無関係な全体トリガー

`[generate(MrubyBridgePlugin, "...")]` を**どこか1つの cell に付与すると**（`MultiPlugin` 経由で `MrubyInfoBridgeCellPlugin` がロードされる）、`self.gen_post_code` が呼ばれ、`Namespace.get_root` から名前空間ツリー全体を再帰走査して、見つかった**すべてのシグニチャ**に対し `generate( MrubyInfoBridgeSignaturePlugin, <シグニチャ>, "auto_exclude=true" );` を自動生成する（`nMrubyInfo::` 名前空間配下のシグニチャは除外）。

```ruby
# MrubyInfoBridgeCellPlugin.rb 65〜79行
def self.gen_signature_cdl( file, namespace )
  namespace.get_signature_list.each{ |sig|
    if sig.get_namespace_path.to_s =~ /nMrubyInfo::/ then
      # ignore
    else
      file.print "generate( MrubyInfoBridgeSignaturePlugin, #{sig.get_namespace_path.to_s}, \"auto_exclude=true\" );\n"
    end
  }
  namespace.get_namespace_list.each{ |ns| gen_signature_cdl( file, ns ) }
end
```

つまり cell への付与は「**どのセルか**」に意味はなく、CDL 処理系にこの自動生成コードを1回走らせるための**トリガー**として機能しているに過ぎない——ATK1Plugin・MrubyBridgePlugin のような「セル単位で個別に処理する」パターンとは根本的に異なる、プログラム全体を対象にした一括適用の仕組み。

## 4. 動的結合の仕組み（`MrubyInfoBridgeSignaturePlugin`）

### 4.1 ブリッジセルタイプ

生成されるブリッジセルタイプ（`nMrubyInfo::tInfo<シグニチャ名>`）の呼び口 `cTECS` は `[dynamic,optional]` 指定——CDL 記述時に結合しない前提の呼び口である。かわりに TECSInfo 系の呼び口（`cTECSInfo`／`cEntryInfo`／`cSignatureInfo`／`cRawEntryDescriptorInfo`）を持つ。

```tecs-cdl
// 自動生成される（MrubyInfoBridgeSignaturePlugin.rb 369〜394行より）
namespace nMrubyInfo{
    [singleton, idx_is_id, active]
    celltype tInfo<Signature> {
        [dynamic,optional] call <Signature> cTECS;
        call nTECSInfo::sTECSInfo cTECSInfo;
        [dynamic,optional] call nTECSInfo::sEntryInfo cEntryInfo;
        [dynamic,optional] call nTECSInfo::sSignatureInfo cSignatureInfo;
        [dynamic,optional] call nTECSInfo::sRawEntryDescriptorInfo cRawEntryDescriptorInfo;
        attr {
            [omit] char_t *VMname = "VM";
            [omit] char_t *bridgeName = C_EXP( "$cell$" );
        };
    };
};
```

### 4.2 実行時の初期化フロー（`initialize`、593〜830行）

mruby スクリプトが `TECS::Info<Signature>.new("対象セルパス")` を実行すると、生成された `initialize` は次を行う（`gen_preamble_instance_initialize`）。

1. `cTECSInfo_findRawEntryDescriptor(name, &rawEntryDescDesc, &entryDesc)` — 渡された文字列パスからセルの受け口を検索。見つからなければ mruby 例外 `E_ARGUMENT_ERROR`。
2. `cEntryInfo_getSignatureInfo`／`cSignatureInfo_getName` — 見つかった受け口のシグニチャ名を取得し、**このブリッジが対象とするシグニチャ名と一致するか検証**。不一致なら例外。
3. `cRawEntryDescriptorInfo_getRawDescriptor` — 検証を通ったら実際の呼び出し用ディスクリプタを取得し、インスタンスに保持。

以降のメソッド呼び出しは、保持したディスクリプタを `cTECS_set_descriptor(...)` で都度セットしてから `cTECS_<関数名>(...)` を呼ぶ形で実行される（`gen_preamble_bridge_func`）——MrubyBridgePlugin の静的結合と異なり、対象セルの取り違えは実行時の文字列一致検証で防いでいる。

## 5. プラグイン引数と関数フィルタ

`MrubyBridgeSignaturePluginModule` の `MrubyBridgePluginArgProc` を共有（`@plugin_arg_check_proc_tab = MrubyBridgePluginArgProc`、61〜79行）。加えて、対象シグニチャの各関数を次のルールで検査し、条件を満たさない関数は自動的に除外対象へ回す（`check_name_and_return_type`／`check_parameter_type`）。

| 制約 | `auto_exclude=true`（デフォルト）時の挙動 | `auto_exclude=false`時の挙動 |
|---|---|---|
| 戻り値が `bool_t`/整数/浮動小数点/`void` 以外 | 自動除外（`cdl_info` で通知） | エラー |
| パラメータ指定子が `send`/`receive` | 自動除外 | エラー |
| パラメータの構造体がタグなし、またはメンバがスカラー型以外 | 自動除外 | エラー |
| `size_is`/`count_is`/`string` 指定の構造体ポインタ | 自動除外 | エラー |

`include`/`exclude`（含める／除外する関数名リスト）は同時指定不可（`MRB1011`）。除外の結果、対象関数が0件になると警告 `MRB1012`。

## 6. 除外されるシグニチャ

`sig_path` が次のいずれかに一致する場合、プラグインは何も生成しない（`@b_refused_signature = true`、92〜106行）。

- `::nTECSInfo::sAccessor` は許可（TECSInfo 自身へのブリッジは許可）
- `::nMruby::sInitializeBridge`／`::nMruby::sInitializeTECSBridge` は拒否
- `::nTECSInfo::` 配下（`sAccessor` 以外）は拒否

初期化用シグニチャや TECSInfo API 自身への再帰適用を防ぐ設計と見られる。

## 7. MrubyBridgePlugin との対比

| 観点 | [[work/active/tecsgen-plugins/MrubyBridgePlugin\|MrubyBridgePlugin]] | MrubyInfoBridgePlugin |
|---|---|---|
| 対象セルの決定時期 | CDL 記述時（静的） | 実行時、文字列パスから検索（動的） |
| `cTECS` 呼び口 | 通常の `call`、CDL で `=` 結合 | `[dynamic,optional]` |
| 誤結合の防止 | CDL 記述の正しさに依存 | 実行時のシグニチャ名一致検証 |
| celltype/composite celltype 単位の適用 | 対応（`MrubyBridgeCelltypePlugin`/`MrubyBridgeCompositePlugin`） | 未実装（2章） |
| cell 単位の適用の意味 | そのセルを bridge 対象に加える | 名前空間ツリー全体への一括トリガー（3章） |
| 追加の依存 | なし | `TECSInfo`（`nTECSInfo::sTECSInfo` 等） |

## 8. 制約・注意点

- CDL 上で `[generate(MrubyBridgePlugin, "...")]` を実際にどの cell に付与するのが慣例か、リポジトリ内に使用例が見当たらず未確認（3章のとおり付与対象のセル自体には意味がないため、どこでもよいはずだが確立された慣習は不明）。
- `MrubyInfoBridgeCellPlugin` は Celltype/Composite への適用が未実装（2章）——MrubyBridgePlugin の対応する4種のうち2種のみ。
- 実行時の文字列パス検索・シグニチャ名比較は追加のオーバーヘッドを伴う（静的結合の MrubyBridgePlugin にはないコスト）。

## Related

- [[tecsgen外部仕様]] — 6.2 `MultiPlugin` ディスパッチ対応表・6.3 標準付属プラグイン一覧
- [[work/active/tecsgen-plugins/MrubyBridgePlugin]] — 静的結合版。`MultiPlugin` ディスパッチ・型対応表の多くを共有
- [[reference/03-Resources/my-topic/wiki/plugin-mruby-info-bridge]] — 概念スタブページ
- [[North Star]] — カーネル対応プラグイン仕様書化の進捗管理
