---
date: 2026-05-04
description: "書籍「マンガで分かる自立型AIエージェント」の読書メモ — PowerShell による停止コマンド（taskkill /F /IM openclaw.exe 等）"
tags:
  - reference
  - kindle
  - book
  - agent
---

# PowerShellによる停止コマンド
taskkill /F /IM openclaw.exe 
taskkill /F /IM python.exe 

# icacls コマンドによるフォルダの要塞化
icacls "C:\ImpotysntData" /deny "AI_User_Account":(OI)(CI)(F)

# macOS : 
## AI専用ユーザ
- AI_Agent という標準ユーザを新規作成
- このアカウント内だけでOpenClawを実行
## プロセス一層
- pkill -9 -f openclaw
## ファイルとフォルダのプライバシー制限
- システム設定>プライバシーとセキュリティ>ファイルとフォルダ
- - デスクトップや書類フォルダへのアクセス権を個別にオフにする
# OpenClawの設定ファイル
## .env, config.yaml
- MAX_STEPS_PRE_RUN 20-30 無限ループに陥っても、一定回数で自動停止させるため
- MAX_MONTHLY_BUDGET$50.00(任意)　API利用料が想定を超えたときに強制的にエラー
- CONFIRM_BEFORE_PURCHASE True 決済画面の認識時に必ず人間へ通知を送るため
# OpenClaw最適化ワークフロー
## ミッション設計術
### Objects(目的)　何をすべきか
### Onstraints(制約条件)　何をしてはいけないか、何を守るべきか
### Definition of Done(完了の定義)　どのような状態になれば終了か

数値化、具体化することが第一歩

## マルチエージェント連携：役割分担の最適化
### 応用例：Kindle出版の完全サポート・ワークフロー
- 市場分析(OpenClaw + Genspark) 「現在Kindleストアで「AI」カテゴリのベストセラーを調査し、共通する不満点をレビューから抽出せよ」と指示
- 構成案の作成　抽出された「読者の悩み」を解決するための章立てをエージェントに考案させる
- 執筆と構成　各章の内容を執筆させつつ、別のエージェント（またはステップ）で「エンジニア視点で論理的か？」を検証させます
- KDP登録準備　OpenClawにKDPの管理計画（テスト環境を推奨）を開かせ、タイトル、説明文、キーワードを自動入力し、下書きとして保存させる。
### エラーハンドリング
- ステップ・バイ・ステップで思考せよ：現在の状況をスクリーンショットから分析し、何が問題化をテキストで出力させてから次の行動を選ばせる
- リトライの回数制限：同じ操作を３回失敗したら、作業を中断して人間に通知を送る

![[Pasted image 20260504183012.png]]

![[スクショ-付録：OpenwClaw導入・運用チェックリスト.png]]