---
date: 2026-09-15
description: "TECSCDEの外部仕様・内部仕様・実装が言語/フレームワーク別（JS-TS, TS, DT-EL, DT-TA）に枝分かれした関係を一覧するワークストリーム索引ノート"
project: TECSCDE
status: active
quarter: Q3-2026
tags:
  - work-note
---

# TECSCDE-仕様関係

## Context
- [[TECSCDE外部仕様]]
- [[TECSCDE内部仕様]]

- [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|TECSCDE共通ロジック]]

- [[work/active/tecs/TECSCDE-実装アーキテクチャ案|TECSCDE-実装アーキテクチャ案]]
- [[TECSCDE-JS-TS実装]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]
- [[work/active/tecs/TECSCDE-TS-実装アーキテクチャ案|TECSCDE-TS-実装アーキテクチャ案]]
- [[TECSCDE-TS実装]]

- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT-EL実装]]

- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]]
- [[TECSCDE-DT-TA実装]]

## 依存関係

各ノートの `## Related` の記述から起こした実態ベースの依存関係。

```mermaid
graph TD
    TECSCDE外部仕様 --> TECSCDE内部仕様
    TECSCDE外部仕様 --> TECSCDE-TS内部仕様
    TECSCDE外部仕様 --> TECSCDE-DT外部仕様
    TECSCDE外部仕様 -->|制約の一次情報源| TECSCDE-実装アーキテクチャ案
    TECSCDE外部仕様 -->|制約の一次情報源| TECSCDE-TS-実装アーキテクチャ案

    TECSCDE内部仕様 --> TECSCDE-実装アーキテクチャ案
    TECSCDE-実装アーキテクチャ案 --> TECSCDE-JS-TS実装
    TECSCDE-TS内部仕様 --> TECSCDE-TS-実装アーキテクチャ案
    TECSCDE-TS-実装アーキテクチャ案 --> TECSCDE-TS実装

    TECSCDE-DT外部仕様 --> TECSCDE-DT-EL内部仕様
    TECSCDE-DT外部仕様 --> TECSCDE-DT-TA内部仕様
    TECSCDE-TS内部仕様 -->|クラス設計の一次情報源| TECSCDE-DT-EL内部仕様
    TECSCDE-TS内部仕様 -->|クラス設計の一次情報源| TECSCDE-DT-TA内部仕様

    TECSCDE-DT-EL内部仕様 --> TECSCDE-DT-EL実装
    TECSCDE-DT-TA内部仕様 --> TECSCDE-DT-TA実装

    TECSCDE-TS実装 -.->|model/cdl/diagnostics 移植| TECSCDE-DT-EL実装
    TECSCDE-TS実装 -.->|model/cdl/diagnostics 移植| TECSCDE-DT-TA実装

    TECSCDE内部仕様 -.-|1層目 挙動の正典| TECSCDE共通ロジック
    TECSCDE-TS内部仕様 -.-|3層目 クラス表現の正典| TECSCDE共通ロジック
    TECSCDE共通ロジック -.- TECSCDE-JS-TS実装
    TECSCDE共通ロジック -.- TECSCDE-TS実装
    TECSCDE共通ロジック -.- TECSCDE-DT-EL実装

    class TECSCDE外部仕様,TECSCDE内部仕様,TECSCDE-TS内部仕様,TECSCDE-DT外部仕様,TECSCDE-実装アーキテクチャ案,TECSCDE-TS-実装アーキテクチャ案,TECSCDE-JS-TS実装,TECSCDE-TS実装,TECSCDE-DT-EL内部仕様,TECSCDE-DT-EL実装,TECSCDE-DT-TA内部仕様,TECSCDE-DT-TA実装,TECSCDE共通ロジック internal-link;
```

凡例

- 実線 — 仕様・設計の派生／実装対象
- 点線矢印 — コードの移植
- 無向点線 — [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|TECSCDE共通ロジック]] が正典・実装として参照する関係

外部仕様から3系統に分岐する。[[TECSCDE内部仕様]]（関数ベース・ブラウザ）、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]（クラスベース・ブラウザ）、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（デスクトップ）。DT 系の内部仕様は挙動を DT 外部仕様から、クラス設計を TS 内部仕様から受け取る二重の上流を持つ。

[[work/active/tecs/TECSCDE-実装アーキテクチャ案|TECSCDE-実装アーキテクチャ案]] は [[TECSCDE内部仕様]] と [[TECSCDE-JS-TS実装]] の間に位置する中間ノート。[[work/active/tecs/TECSCDE-TS-実装アーキテクチャ案|TECSCDE-TS-実装アーキテクチャ案]] は [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] と [[TECSCDE-TS実装]] の間に位置する中間ノート。


## Notes

## Action Items
- [ ]

## Related
- [[work/active/tecs/TECS開発|TECS開発]]
- [[work/Index]]
- [[brain/North Star|North Star]]
