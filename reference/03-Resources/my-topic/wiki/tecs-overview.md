---
date: 2026-05-31
tags: [tecs, toppers, rtos, embedded]
type: concept
status: active
description: "TOPPERSプロジェクトの組込みコンポーネントシステム。CDL記述・tecsgenによるコード生成・RTOSとの連携を中核とする。"
---

# TECS (組込みコンポーネントシステム)

TECS（Toppers Embedded Component System）は、TOPPERSプロジェクトが開発した組込みシステム向けコンポーネントシステムです。

## 主要構成要素

- [[tecs-cdl]] — コンポーネント記述言語 (TECS CDL)
- [[tecs-celltype]] — セルタイプ（コンポーネントの型）
- [[tecs-cell]] — セル（コンポーネントのインスタンス）
- [[tecs-signature]] — シグニチャ（インタフェース定義）
- [[tecs-port]] — ポート（呼び口・受け口）
- [[tecs-tcd]] — コンポーネント図 (TCD)
- [[wiki-tecsgen]] — TECSジェネレータ

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
