---
date: 2026-08-22
description: "tecsgen内部仕様書 第10章（ファイル入出力）— Import/import_C（即時パース・reuse指定・二段探索）、TECSIO（行単位の文字コード変換）。「キューに積む」という誤記を訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 10 of 12. 2026-08-22、`componentobj/import.rb`・`componentobj/import_c.rb`・`componentobj/importable.rb`・`bnf.y.rb`（`TECSIO`）を直接読んで全面検証・訂正。

## 10. ファイル入出力

> [!warning] Import はキューに積まない — その場で同期的にパースする
> 旧版は「CDL ファイルをキューに積んでパース」としていたが誤り。`Import.new`（`componentobj/import.rb`）はコンストラクタの中で直ちに `Generator.new` → `parser.parse([@cdl_path])` を呼び出し、同期的にパースを完了させる（`Import_C` と同じ構造）。「キュー」に相当するのは 5.1 の字句解析器が使う `@q`（1ファイル分のトークン配列）であり、複数ファイルを跨ぐインポート待ち行列は存在しない。ネストは `Import.push`/`Import.pop` によるスタック（`@@nest_stack`）で管理される。

### 10.1 Import / import_C

- `Import.new(cdl, b_reuse = false, b_imported = true)`：CDL ファイルをその場で解決・パースする。`b_reuse` が真、または `Generator.is_reuse?` が真なら `@b_reuse_real = true` となり、対応する Celltype の template コード生成が抑制される（8.2 参照）
- `Import_C.new(header, define = nil)`：C ヘッダを `cpp` でプリプロセスして `C_parser` で解析（詳細は 5.3）
- インポート済みファイルは `@@import_list`（絶対パスをキーとするハッシュ）で重複チェックされ、2回目以降は再パースされない。ただし reuse 指定が前回と食い違う場合は `W1008` 警告
- ファイル探索は `Importable#find_file`（`import.rb`/`import_c.rb` 共通、`componentobj/importable.rb`）が担う二段探索：まず `$import_path` の各パスをそのまま試し、見つからなければ、過去に import が見つかった基点ディレクトリ（`$base_dir` に蓄積）ごとに `$import_path` を再度当てる。後者はインポート元ファイルからの相対パス解決を支える

### 10.2 文字コード変換（TECSIO）

`TECSIO`（`bnf.y.rb` 2158行目、`Generator`/`Import` 等と同じ `---- inner` セクション内 — 独立ファイルではない）:

- `TECSIO.foreach(file) { |line| ... }`：CDL ファイルを1行ずつ読み込みながら `str_code_convert` でエンコーディングを揃えて yield する。5.1 の字句解析はこの正規化済みの行を受け取る。SJIS 指定時は Ruby の `File.open` を `Windows-31J` として開いてから変換することで、SJIS として不正な文字が例外を起こさず `?`（UTF-8 では U+FFFD）に置換されるようにしている（コメント中の混在文字コードを許容するための実装上の工夫）
- `TECSIO.str_code_convert(msg, str)`：`str` のエンコーディングが `msg` と異なる場合のみ `str.encode(msg.encoding)` を試み、変換不能なら元の `str` をそのまま返す（例外を握りつぶす形の縮退）。エラーメッセージへの文字列埋め込み（`Generator.error2` 等）でも同じメソッドが使われる

---

