---
date: 2026-04-24
tags: [tecs, toppers, documentation]
type: source-summary
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\tecs\tecsflow.html
description: "TECS ドキュメント source-summary: tecsflow コマンドリファレンス"
---

# tecsflow コマンドリファレンス

（内容は raw article を参照）

## Key Points

- # tecsflow コマンドリファレンス
- ## 名前
- ## 使用方法
- ## 説明
- ## Makefile 記述例
- # TECS_TARGET = tecsgen            # 古い TECS ジェネレータのターゲット# TECS_TARGET = tecsgen.timestamp  # カーネルパッケージなどに見られる# GEN_DIR     = gen                # もし GEN_DIR が定義されていなければtecsflow :$(GEN_DIR)/tecsgen.rbdmptcflowtecsflow-g$(GEN_DIR)tecsflow_u :$(GEN_DIR)/tecsgen.rbdmptcflowtecsflow-g$(GEN_DIR)-U
- ## 出力例
- ### (1) 「アクティブセルを起点とするフロー」の出力例
- ### (2) 「未使用の受け口関数を起点とするフロー」の出力例
- ### (3) 「未使用の非受け口関数を起点とするフロー」の出力例

## Entities Mentioned

- [[atk2-tkernel]]
- [[tecs-cell]]
- [[tecs-celltype]]
- [[tecs-overview]]
- [[tecs-port]]
- [[tecsflow]]
- [[wiki-tecsgen]]

## See Also

- [[index]]
