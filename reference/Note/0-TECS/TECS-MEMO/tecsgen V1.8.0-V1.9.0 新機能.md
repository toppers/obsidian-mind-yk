---
date: 2026-10-19
description: "Ruby版tecsgen V1.8.0→V1.9.0 の新機能・仕様変更・不具合修正の一覧。出典はSVN tags/tecsgen-1.9.1 の doc/changes.txt（V1.9.1の追加も参考記載）"
tags:
  - reference
  - tecs
  - tecsgen
---

# tecsgen V1.8.0 → V1.9.0 新機能

- 出典: `https://dev.toppers.jp/svn/tecs/toppers/tecsgen/tags/tecsgen-1.9.1/doc/changes.txt`（1.9.0RC1〜RC6 の範囲、取得 2026-10-19）。SVN のタグ一覧に 1.9.0 はなく、1.9.1 のタグのみ
- リビジョンの対応は [[tecsgen-VCS]]（1.8.0 = r3252、1.9.0 = r3280、1.9.1 = r3303）
- 前の版の差分は [[tecsgen V1.7.0-V1.8.0 新機能]]
- `#` は公式の変更管理番号
- `changes.txt` の記述に基づく一覧で、ソース差分での検証は未実施 (unverified)

## 新機能・追加

- **C++ 向けインタフェース生成プラグインを新設**（#1221）
  - `CppIfGenPlugin`（マルチプラグイン）、`CppIfGenCelltypePlugin`、`CppIfGenCellPlugin`
  - テストコード `cppifplugin` も追加
- **C 向けインタフェース生成プラグインを新設**（#1225）
  - `CIfGenPlugin`（マルチプラグイン）、`CIfGenCelltypePlugin`、`CIfGenCellPlugin`
  - テストコード `cifplugin` も追加
- `CppIfGenCelltypePlugin` の強化
  - `public` キーワードを2か所追加。受け口の参照を取り出し、シグニチャ型のポインタ変数に代入できる（#1226）
  - シングルトンに対応（#1227）
  - 受け口配列に対応（#1237）
- `CIfGenCelltypePlugin` が受け口配列に対応（#1233）
- テンプレートコードに未編集の警告を出す（"'受け口関数名' needs to be edited."、#1234）
- **ポインタのポインタ**を使うと警告やエラーになる問題への対応。`deviate` を指定すると警告・エラーを抑制できる（#1183）
- C パーサに `__int64` と `_Bool` 型を追加（MS の C 言語拡張への対応、#1228）
- `-DNO_TECSGEN_VA_LIST` で、`import_C` 時の `va_list` の強制定義をやめられる（#1229）

## 仕様変更

- テンプレートコードに `idx` をチェックするコードを挿入しなくなった（#1224）
- `CB` も `INIB` もないときの `CBP` のダミー値を `NULL` から `0` に変更（C++ では int 変数に `NULL` を代入するとエラーになるため、#1223）

## 主な不具合修正

- `generate` 文で指定したセルタイププラグインに対し、`gen_factory` が呼ばれない問題（#1222）
- `FMPHandlerPlugin` が生成する静的 API の行末に `;` が出力されない問題（#1219）
- `FMPHandlerPlugin`・`FMPObjectPlugin` で、ルートに置いたカーネルオブジェクトが正しく扱われない問題（#1220）
- `*_tecsgen.h` に定義される受け口配列サイズのマクロが `undef` されない問題（#1235）
- `CIfGenCelltypePlugin`・`CppIfGenCelltypePlugin` の `TOPPERS_MACRO_ONLY` ガードコードを改良（#1231）
- cygwin 上で `test/cygwin` を `-I` で指定しないと Ruby 例外になる問題（#1202）
- Windows 版 Ruby での例外（#1232）

## 内部変更（抜粋）

- `componentobj.rb` と `syntaxobj.rb` を、クラスごとに `.rb` ファイルへ分割（#1230）
- Ruby 3.0 では `$KCODE` への代入時に警告も出ないため、KCODE 関連処理を見直し（#1203）
- マクロの `undef` 生成を `gen_ph_undef` に分離（#1236）
- `Makefile` と `test/Makefile` を変更（#1238）

## 参考: 1.9.0 の後の V1.9.1（2026-06-07）

- `.h` の `typeof` エラーを回避。GCC 1.5.2 で tecsgen がエラーになる問題への対応（#1239）
- `DataPumpHolder` プラグインに対応（#1240）
- `TransparentRPCSignaturePlugin` に対応（#1241）

## Related

- [[tecsgen V1.9.0-V1.9.1 新機能]] — 次の版の差分
- [[tecsgen V1.7.0-V1.8.0 新機能]] — 1つ前の版の差分
- [[tecsgen-VCS]] — バージョンとリビジョンの対応
- [[svn-diff]] — タグ間のログ取得コマンド控え
- [[tecsgen-inner-spec]] — tecsgen 内部仕様
