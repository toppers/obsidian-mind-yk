---
date: 2026-04-01
description: "YouTube「Claude Code ハーネスエンジニアリング完全解説」の要点 — 轡（方向制御・許可システム・制約条件）と鞍（安定化・コンテキスト管理・状態保持）の比喩"
tags:
  - reference
  - claude-code
  - youtube
---

[\(8\) 【知らないと損】Claude Code ハーネスエンジニアリング完全解説｜10倍生産性のAI開発術 \- YouTube](https://www.youtube.com/watch?v=W0RA5csT9H0)

轡　方向制御、許可システム、制約条件
鞍　安定化、コンテキスト管理、状態保持　
手綱　フィードバック、評価メカニズム、軌道修正

今のLLMの問題点
1.CONTEXT WINDOW
コンテキスト不安->モデルが早く終わらせないとコンテキストがあふれると学習してしまっている

コンテキストコンパクションより、コンテキストリセットのほうが効く場合が多い。
必要最小限の情報だけ残して、新鮮な状態で再開する->スプリント契約につながる
2.自己評価の限界->LLMが客観的に評価できない。自分の盲点に気づけない
Generator-Evaluatorパターンが重要
同じモデルでも文脈が違えば、別の視点で見れる（コンテキスト分離）

Evaluatorの評価基準
DESIGN QUALITY
ORIGINALITY
CRAFT(細部の作り込み)
FUNCTIONALITY（実用性）

PlayWriteで実際に操作して評価

ハーネスは３つのエージェントで構成

================
PLANNER ARCHITECTURE

簡単なプロンプトを包括的な仕様書に変換する
必要な機能一覧、技術スタック、UIフローを全部設計する

GENERATOR
実際に作る
PLANNERの仕様書に沿って実装する

EVALUATOR
バグを見つけてフィードバックを返す

*スプリント契約
Generatorは実装前に「これをつくります」とEvaluatorに宣言
期待値を事前に合意する

Collector/Executor権限マトリクス
　C    E
----------
R | 〇 | 〇
W | 〇 | X
E | 〇   |△

Knowledge Pool構造図
全ゴールから参照可能な共有知識
ImportantNextReadというフラグで、次回読込を指定できる

Goal 1                Goal2
        KP
Goal 2                 Goal4

KnowledgeとSummaryのスコープ分離

Summary(Goal固有)　コンテキストに依存し、実行結果を圧縮したもの
Knowledge(全体共有)　構造化され、再現可能なパターンとして抽出されたもの

![[Pasted image 20260401172958.png]]

AIアーキテクチャ・診断チェックリスト
1.制御層はあるか？
2.評価は分離されているか？
3.コンテキスト管理は？（長いコンテキストをどう管理しているか？）
4.フィードバックループは？

信頼と検証のバランス