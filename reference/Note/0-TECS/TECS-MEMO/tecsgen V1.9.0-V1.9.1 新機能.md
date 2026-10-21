---
date: 2026-10-19
description: "Ruby版tecsgen V1.9.0→V1.9.1 の新機能・内部変更の一覧。出典はSVN tags/tecsgen-1.9.1 の doc/changes.txt とファイル差分"
tags:
  - reference
  - tecs
  - tecsgen
---

# tecsgen V1.9.0 → V1.9.1 新機能

- 出典: `https://dev.toppers.jp/svn/tecs/toppers/tecsgen/tags/tecsgen-1.9.1/doc/changes.txt`（V1.9.1 の節、取得 2026-10-19）。ファイル差分は `svn diff --summarize trunk@3280 tags/tecsgen-1.9.1` で確認
- リビジョンは 1.9.0 = r3280、1.9.1 = r3303（2026-06-07）。対応は [[tecsgen-VCS]]
- 前の版の差分は [[tecsgen V1.8.0-V1.9.0 新機能]]
- `#` は公式の変更管理番号
- 追加は3件で、V1.8.0→V1.9.0 より小規模。ソース内容の検証は未実施 (unverified)

## 新機能・追加

- **`.h` の `typeof` エラーを回避**（#1239）
  - GCC 1.5.2 で tecsgen がエラーになる問題への対応
  - 差分では `C_parser.y.rb`・`C_parser.tab.rb` が変更されている
- **`DataPumpHolder` プラグインに対応**（#1240）
  - 新規ファイルは `DataPumpHolderPlugin.rb`、`tecs/DataPumpHolder/DataPumpHolder.cdl`、`tPumpMainConverter_inline.h`
  - `RPCPlugin.rb`・`CelltypePlugin.rb` も変更されている
- **`TransparentRPCSignaturePlugin` に対応**（#1241）
  - 差分では新規ファイルが `TransparentMarshalerPlugin.rb`、変更が `lib/GenTransparentMarshaler.rb`
  - `TransparentRPCSignaturePlugin` という名前のファイルは差分に出ていない。対応するクラスの所在は未確認 (TBC)

## 内部変更

- CDL にネームスペースのないオブジェクトを宣言するための出力を追加
  - `NamespacePath#print_cdl_decl_path_pre`
  - `NamespacePath#print_cdl_decl_path_post`
  - `Namespace#get_NamespacePath`
  - 差分では `namespace.rb`・`namespacepath.rb`・`celltype.rb` が変更されている

## その他の差分

- 変更履歴の PDF `doc/changes_TECS_V1.9.pdf` が変更されている
- `MANIFEST`・`MANIFEST_tecsgen_body`・`version.rb` が変更されている
- `trunk` のコミットメッセージは `release 1.9.1` のみで、機能の説明はない

## Related

- [[tecsgen V1.8.0-V1.9.0 新機能]] — 1つ前の版の差分
- [[tecsgen-VCS]] — バージョンとリビジョンの対応
- [[svn-diff]] — タグ間のログ取得コマンド控え
- [[tecsgen-inner-spec]] — tecsgen 内部仕様
