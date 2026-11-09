---
date: 2026-04-24
tags: [tecs, toppers, documentation]
type: source-summary
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\tecs\MrubyInfoBridgePlugin.html
description: "TECS ドキュメント source-summary: MrubyInfoBridgePlugin プラグインリファレンス"
---

# MrubyInfoBridgePlugin プラグインリファレンス

（内容は raw article を参照）

## Key Points

- # MrubyInfoBridgePlugin プラグインリファレンス
- ## 名前
- ## 概要
- ## プラグイン種別
- ## 使用方法
- ### 1) TECS CDL(.cdl) の記述
- ### 2) mruby コード (.rb) の記述
- ### 2-1) 追加コード
- ## -------- MrubyInfoBridgePlugin: Bridge Joiner --------- ##moduleTECSmoduleBridge@@accessor=TECS::TnTECSInfo_sAccessor.new('TECSInfoeAccessorBridge')@@cp=TECS::CharPointer.new(256);defself.join(cell_ent_name)# このメソッドでは、ネームスペース下のシグニチャに対応しないcell_ent_chararray=TECS::CharPointer.new(cell_ent_name.length+1);cell_ent_chararray.from_scell_ent_nameif(@@accessor.getSignatureNameOfCellEntry(cell_ent_chararray,@@cp,@@cp.length)!=0)raise"'#{cell_ent_name}' not found"endsignature_name=@@cp.to_sself.join2(cell_ent_name,signature_name)enddefself.join2(cell_ent_name,signature_global_name)# このメソッドでは、ネームスペース下のシグニチャに対応できる# signature_global_name は '_' つなぎ、'::' ではないbridgeClass=Object.const_get('TECS::Info'+signature_global_name.to_s)# this can cause Ruby exception for non-existing signature namebridgeClass.new(cell_ent_name)endendend
- ### 2-2) ブリッジの生成と結合
- ### 2-3) ネームスペース下にシグニチャがある場合
- ## 備考、制限事項
- ### マルチ VM に未対応
- ### ・MrubyBridgePlugin との併用
- ### MrubyBridgePlugin の呼出しは必須ではない

## Entities Mentioned

- [[mruby-tecs]]
- [[plugin-mruby-bridge]]
- [[plugin-mruby-info-bridge]]
- [[tecs-cdl]]
- [[tecs-cell]]
- [[tecs-celltype]]
- [[tecs-composite-celltype]]
- [[tecs-namespace]]
- [[tecs-overview]]
- [[tecs-plugin]]
- [[tecs-port]]
- [[tecs-signature]]

## See Also

- [[index]]
