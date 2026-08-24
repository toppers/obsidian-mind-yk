[[TECS開発 — Progress Log#Action Items 履歴（完了分）|Action Items 履歴（完了分）へ戻る]]

## Entries

- [x] ユーザー指示「tecsgenのtrunkの最新の状態を元に、tecsgen プラグイン仕様書を更新して」に応じ、trunkの現在状態を確認する → **[[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin・TransparentMarshalerPlugin]] 完成（2026-08-15）**。`E:\Crepo\ykominami-svn-2\tecsgen\`が生きたSVN作業コピーだったと判明し、`svn info`でリビジョン3301（2026-01-13）へ更新済み・ファイル数が83→85に増加していると確認した。新規2ファイルは`DataPumpHolderPlugin.rb`（この調査シリーズで最も新しい、2026-01-04コミット、ソース自身に唯一長大な設計ドキュメントを持つ）・`TransparentMarshalerPlugin.rb`（2018年の古いファイルだが今回初めて存在を確認、RPCPluginのTransparent方式マーシャラ生成の実装本体）。**最大の発見**: DataPumpHolderPluginが生成するCDLと、既存ノート済みの[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]自身の生成コードの両方が、`TransparentRPCSignaturePlugin`という**リポジトリのどこにも定義されていないクラス名**を参照している——単発の見落としでなく2箇所で共有される参照切れ。既存の[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin.md]]にもこの発見を追記し、両ノートから相互参照させた
