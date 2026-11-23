---
date: 2026-09-10
description: "TOPPERS の tecs-docs リポジトリ（E:\\Crepo\\github-toppers\\tecs-docs）の作業ノート。TECS 関連ドキュメントの管理・整備。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
---

# tecs-docs

## Context
- ローカルリポジトリ　E:/Crepo/github-toppers/tecs-docs
- リモートリポジトリ　git@github.com:toppers/tecs-docs.git
- TOPPERS の [[work/active/tecs/TECS開発|TECS開発]] 関連ドキュメント群のリポジトリ
- tecsgenのローカルリポジトリ E:\Crepo\ykominami-svn-2\tecsgen\branches\ykominami_r3033
- tecsgenのtrunkのリモートリポジトリ https://dev.topers.jp/svn/tecs/toppers/tecsgen/trunk

## Notes
- TECSマニュアルのライセンス
- 組み込みコンポーネントシステム
- TECS V1.9.1の新機能
- TECS V1.9.0の新機能
- TECS V1.8.0の新機能
- TECS V1.4.0～V1.7.0の新機能
- TECSコンポーネント図
- TECSコンポーネント記述言語(TECS CDL)
- TECSコンポーネント実装モデル
- ASP3+TECS
- ATK2+TECS
- mruby on ev3rt+tecs
- mruby on GR-PEACH+TECS
- TINET+TECS
- (TLSF+TECS)
- プラグインリファレンスマニュアル
	- 各種カーネル対応プラグイン
		- ATK1Plugin プラグインリファレンスマニュアル
		- HRP2Plugin プラグインリファレンスマニュアル
		- ASP3(NotifierPlugin)プラグインリファレンスマニュアル
	- mrubyブリッジプラグイン
		- MrubyBridgePlugin プラグインリファレンスマニュアル
		- Mruby2CBridgePlugin プラグインリファレンスマニュアル
		- MrubyInfoBridgePlugin プラグインリファレンスマニュアル
	- トレースプラグイン
		- TracePlugin プラグインリファレンスマニュアル
		- TLVTracePlugin プラグインリファレンスマニュアル
	- RPCプラグイン
		- TransparentRPCPlugin プラグインリファレンスマニュアル
		- OpaqueRPCPlugin プラグインリファレンスマニュアル
		- SharedRPCPlugin プラグインリファレンスマニュアル
		- SharedOpaqueRPCPlugin プラグインリファレンスマニュアル
	- C言語インタフェースプラグイン
		- C2TECSPluginプラグインリファレンスマニュアル
		- TECS2CPluginプラグインリファレンスマニュアル
- コマンドリファレンスマニュアル
	- tecsgenコマンドリファレンス
	- tecsmergeコマンドリファレンス
	- tecsflowコマンドリファレンスマニュアル
	- tecsgen_rcovコマンドリファレンス
- 参考リンク
- [[Prompts]]
	- work/active/tecs-document/tecs-docs/tecs-docs を参照し、tecsgenのローカルリポジトリを参照し、E:/Crepo/github-toppers/tecs-docs/docs/tecs/tecsgen.rst` に対して、最新のtecsflowのリファレンスマニュアルを　reStructuredText形式　で修正して
		作成したドキュメント自体には、絶対に、何をもとにドキュメントを作成したかに言及してはいけない
		そのような情報は、同じ階層に、メタ情報ファイル（ファイル名：<ドキュメントのファイル名のベース部分>.meta.txt）として出力する。

## Action Items
- [ ] .rst -> .md 変換スクリプト作成
- [ ] 図をテキスト

## Related
- [[work/active/tecs/TECS開発|TECS開発]]
- [[perf/competencies/ナレッジマネジメント|ナレッジマネジメント]] — TECS ドキュメント資産の ingest・整理
- [[work/Index.md|work/Index]]
