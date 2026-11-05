---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン HRPKernelObjectPlugin（抽象基底）・HRPRPCPlugin・HRPSVCThroughPlugin・HRPSVCSignaturePlugin・HRPSVCBodyCellPluginの仕様書。HRPファミリーのドメイン境界仲介機構で、対応するHRP2側より大幅に高度な関数単位アクセス制御を実装する"
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

# HRPKernelObjectPlugin / HRPRPCPlugin / HRPSVCThroughPlugin / HRPSVCSignaturePlugin / HRPSVCBodyCellPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]（2026-08-15）が残していたHRPファミリー7ファイルのうち5ファイルを執筆。残る3ファイル（`HRPTaskPlugin`・`HRPObjectPlugin`・`HRPHandlerPlugin`——`HRPKernelObjectPlugin`の具象サブクラス）は未着手（6節）。一次資料は `tecslib/plugin/HRPKernelObjectPlugin.rb`（336行）・`HRPRPCPlugin.rb`（531行）・`HRPSVCThroughPlugin.rb`（352行）・`HRPSVCSignaturePlugin.rb`（542行）・`HRPSVCBodyCellPlugin.rb`（284行）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。CDL実例はリポジトリ内に見つからず未検証。

## 1. 概要

**5ファイルは [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] の `add_through_plugin` が自動挿入する仲介機構一式である。** [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2側の対応する2ファイル（HRP2SVCPlugin・HRP2RPCPlugin）]]と比べ、**HRP側は同じ役割を3ファイルに分割したうえで、関数単位のドメインアクセス制御という、HRP2側には存在しない機能を実装している**。

| 役割 | HRP2 | HRP |
|---|---|---|
| ユーザ→カーネルドメインの SVC 仲介（through） | `HRP2SVCPlugin`（1ファイルで完結） | `HRPSVCThroughPlugin`（`generate`文で以下2つに処理を委譲するオーケストレータ） |
| SVC セルタイプ宣言＋関数本体生成 | 同上に同居 | `HRPSVCSignaturePlugin`（`< SignaturePlugin`） |
| 呼び出し元ドメインの許可制御 | なし | `HRPSVCBodyCellPlugin`（`< CellPlugin`、`gen_post_code`フックで結線） |
| ユーザドメイン間の RPC 仲介 | `HRP2RPCPlugin`（Transparent マーシャリング、`GenTransparentMarshaler`） | `HRPRPCPlugin`（**Opaque マーシャリング**、`GenOpaqueMarshaler`＋`GenParamCopy`） |
| カーネルオブジェクトセル判定基盤 | `HRP2KernelObjectPlugin`（`< CelltypePlugin`） | `HRPKernelObjectPlugin`（`< CelltypePlugin`、ほぼ同型） |

## 2. HRPKernelObjectPlugin: HRP2版とほぼ同型だが、責務の一部がGenAttModへ移譲済み

構造は [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin]] とほぼ同一（`print_cfg_cre`/`print_cfg_sac` を純粋仮想メソッドとして持つ `CelltypePlugin` 直系の抽象基底クラス、`gen_factory` が対象セルを走査して `CRE_XXX`/`SAC_XXX` を生成）。

**発見**: `gen_factory`（154〜162行、178〜182行）には、HRP2 版でまだ生きているコード（`KERNEL_DOMAIN{ INCLUDE(...) }`/`DOMAIN(...){ INCLUDE(...) }` の出力）と同一のコードが**コメントアウトされた状態で残っている**。[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] 6節で確認した `GenAttMod#gen_include` が同じ処理を一括して肩代わりするようになったため、`HRPKernelObjectPlugin` 側の重複コードが無効化された、という削り跡だと判断できる——[[work/active/tecsgen-plugins/HRPPlugin]]で見つけた「HRP2からの複製→後から整理」という流れの、もう一つの裏付け。

アクセス許可ベクタ（`SAC_XXX`）の生成は HRP2 版より作り込まれており、`HRPPlugin.get_inter_domain_join_roots`（実際にそのセルへドメインをまたいで結合しているセルの集合、[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] 5節参照）を参照して呼び出し元ドメインごとのアクセスパターンを算出し、複数ユーザドメインからカーネルオブジェクトへ直接結合された場合はエラー（`HRP9999`）にする——`HRPPlugin.get_sac_str`（HRPPlugin.rb 215〜260行）にも酷似したロジックが存在しており、**2箇所で類似のアクセスベクタ計算が行われている**（どちらが実際に使われる経路か、あるいは両方使われるのかは未検証）。

## 3. HRPSVCThroughPlugin: 実装をシグニチャ側・セル側の2プラグインへ委譲するオーケストレータ

`< ThroughPlugin`。[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2SVCPlugin]] のように自分でセルタイプ CDL を heredoc 生成するのではなく、`gen_plugin_decl_code`/`gen_through_cell_code` から以下2つの `generate(...)` 文を発行するだけの薄い層になっている。

```tecs-cdl
generate( HRPSVCSignaturePlugin, <シグニチャ>, "" );
generate( HRPSVCBodyCellPlugin, <結合先セル>, "exportEntryPort=<受け口>:<呼び出し元リージョン>" );
```

`initialize` で呼び出し元・呼び出し先の両方のドメイン種別が `:HRP` または `:HRMP` であることを検証する（`HSV0011`/`HSV0013`）——**`HRPSVCThroughPlugin` は HRP と HRMP の両方で共用される設計であることがコードから直接確認できる**（[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] 6節で見つけた `GenAttMod`/`GenDefSvc` 共有の傍証を、今回はプラグイン本体側から裏付けた）。旧実装（クライアント/サーバーセルを自前 heredoc で生成していたと思われるコード）が `=begin`〜`=end` で丸ごとコメントアウトされて残っており（156〜199行）、委譲方式への移行の跡と読める。

私有メソッド `gen_caller_check_code`（214〜351行、4節で詳述する仕組みの中核）もこのファイル内にあるが、実際に呼び出している形跡はコード内に見当たらず（`HRPSVCSignaturePlugin#gen_postamble` 側では呼び出しがコメントアウトされている、4.2節参照）、**未結線のまま残っている可能性がある**。

## 4. HRPSVCSignaturePlugin: 関数単位のドメインアクセス制御——HRP2にない機能

### 4.1 概要

`< SignaturePlugin`。シグニチャから2つのセルタイプ（呼び出し元 `tHRPSVCCaller_<シグニチャ>`・呼び出し先 `tHRPSVCBody_<シグニチャ>`）を生成し、拡張サービスコール（`cal_svc`）経由の呼び出しコードを組み立てる点は [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2SVCPlugin]] と同じだが、**`tHRPSVCBody_...` セルタイプが関数ごとに `ACPTN restrict_acptn_<関数名>` という属性を持つ**（83〜99行）。

### 4.2 発見: `TACP(cdmid) & ATTR_restrict_acptn_<func>` によるビットマスク許可チェック

`gen_postamble`（215〜419行）が生成する SVC 本体関数には、呼び出し元ドメイン ID（`cdmid`）と `restrict_acptn_<関数名>` 属性値のビット論理積を取り、非ゼロでなければ `E_OACV`（アクセス違反）を返すチェックコードが埋め込まれる（387〜395行）。

```c
if (cdmid != TDOM_KERNEL) {
  /* ... ポインタ引数の prb_mem/prb_str チェックがここに入る ... */
  if( (TACP(cdmid) & ATTR_restrict_acptn_<func>) == 0 ){
    return E_OACV;
  }
}
```

さらにポインタ引数については `[in]` なら `prb_mem`/`prb_str` で読み取り可能性（`TPM_READ`）、`[out]`/`[inout]` なら書き込み可能性（`TPM_WRITE`）を検証するコードも自動生成される——[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2SVCPlugin]] にも `prb_mem` チェックはあったが（受け口関数全体で一律）、**HRP側は「この関数はどのドメインから呼べるか」を関数単位で制御できる**点が質的に異なる。ただし、この許可値 `restrict_acptn_<func>` を実際に埋める処理（3節で触れた `gen_caller_check_code`）は呼び出されている形跡が薄く（`check_code = ""` に固定、296行）、**関数単位アクセス制御の"配線"自体は用意されているが、実際に有効化されているか未検証**。

### 4.3 シグニチャの型制約チェック（`check_signature`）

拡張サービスコールは最大5引数まで（`NUM_SVC_ARG_MAX = 5`、HRP2SVCPlugin と同じ制約）、戻り値は `ER`/`ER_UINT` が推奨（それ以外は警告）、引数はポインタなら整数・real・構造体（メンバも整数系のみ）に限る、多重ポインタは不可——といった制約を、シグニチャ登録時に静的にチェックするコード（424〜540行）を持つ。エラーコード体系は `HSV0001`〜`HSV0009`・`HSW0001`・`HSI0001`。**HRP2SVCPlugin にはこの種の事前検証コードは存在しない**——HRP側のみの追加安全機構。

## 5. HRPSVCBodyCellPlugin: ドメイン外へ受け口を明示的にエクスポートする仕組み

`< CellPlugin`（HRP2ファミリーに対応物なし）。CDL の `generate(HRPSVCBodyCellPlugin, <セル>, "exportEntryPort=<受け口>:<呼び出し元リージョン,...>")` で、そのセルの指定受け口を、指定したリージョン（ドメイン）から拡張サービスコール経由で呼び出せるように「輸出（export）」する。`gen_post_code`（クラスメソッド、全プラグインインスタンス生成後にまとめて実行）で、輸出登録された受け口ごとに `tHRPSVCBody_<シグニチャ>` セルを生成し、`restrict_acptn_<関数名>` へアクセス許可ベクタ（`regions_to_tacp`、153〜184行）を埋め込む。

もう1つのオプション `substRegion='<domain外リージョン>:<domain内リージョン>'` は、ドメイン外リージョンをドメイン内リージョンへ置き換える機構だが、コード内では検証（存在チェック・ドメイン所属チェック）のみが実装されており、**実際に置換処理が行われている箇所はソース上に見当たらない**（未完成の可能性）。

## 6. HRPRPCPlugin: Opaqueマーシャリング＋MessageBufferベースの双方向チャンネル

`< ThroughPlugin`、`include GenOpaqueMarshaler`・`include GenParamCopy`。[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2RPCPlugin]] が [[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] と同じ `GenTransparentMarshaler`（固定型シリアライズ）を使うのに対し、**HRPRPCPlugin は Opaque マーシャリング（`OpaqueMarshalerPlugin`、汎用シリアライズ）を使う**——HRP2 と HRP で RPC のマーシャリング方式そのものが異なる。

チャンネル実装も異なり、HRP2RPCPlugin の3ポート構成（`sEventflag`/`sSemaphore`/`sMessageBuffer`）ではなく、`tMessageBuffer` を双方向（client→server・server→client）に2つ生成し `tMessageBufferCEP` でラップする構成（199〜227行）。各メッセージバッファには `accessPattern1`〜`4` に呼び出し元・呼び出し先両ドメインの `TACP` を OR で埋め込む（175〜191行）——ここでも HRP 系はドメインベースのアクセス許可を随所で明示的に埋め込む設計思想が一貫している。

`class(...)` 指定子（region の別系統の specifier、[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] 2.2節参照）を扱う `print_class_region_str_pre`/`post` という独自メソッドを持ち、クラス（`class_type`）が `:root` の場合にデフォルトのクラスリージョン（`CLS_PRC1`/`__CLS_P1_GLOBAL`）へチャンネルセルを自動配置する——HRP2RPCPlugin にはない、クラス機構との統合コード。

## 7. 制約・注意点

- 残る3ファイル（`HRPTaskPlugin`・`HRPObjectPlugin`・`HRPHandlerPlugin`）は [[work/active/tecsgen-plugins/HRPKernelObjectPlugin|別ノート]]（2026-08-15完成）で執筆完了。[[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin]] と同型の単機能/汎用の二層構造だったが、単機能側はTaskのみでHRP2の8種より大幅に少ないと判明——HRPファミリー全10ファイルを完走した。
- 4.2節の関数単位アクセス制御（`restrict_acptn_<func>`）は、許可値を実際に計算する `gen_caller_check_code` の呼び出し経路が弱く、機構が完全に配線されているか未検証。
- 5節の `substRegion` オプションは検証コードのみで、実際の置換処理の実装箇所が見当たらない。
- 2節で指摘したとおり、アクセスベクタ計算が `HRPKernelObjectPlugin#gen_factory` と `HRPPlugin.get_sac_str` の2箇所に類似ロジックとして存在し、どちらが実際の経路か未整理。
- 多くのエラーメッセージが `HRP9999` という汎用プレースホルダコードのままで、正式なコード番号が割り当てられていない（`HRPPlugin.rb`・`HRPKernelObjectPlugin.rb`・`HRPRPCPlugin.rb` に共通）——`HRPSVCSignaturePlugin`（HSV/HSW/HSI）・`HRPSVCBodyCellPlugin`（HRPSB/HSW0002）は独自のコード体系を持ち対照的。

## Related

- [[work/active/tecsgen-plugins/HRPPlugin]] — 本ファミリーのエントリポイント（ドメイン宣言・仲介プラグイン自動選択）
- [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin]] — HRP2側の対応する仲介プラグイン。本ノート全体で対比の基準にした
- [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin]] — HRP2KernelObjectPluginとの対比元（2節）
- [[work/active/tecsgen-plugins/RPCPlugin]] — GenTransparentMarshaler/GenOpaqueMarshalerの一般版
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理。HRPファミリー7ファイル中5ファイルが完了
