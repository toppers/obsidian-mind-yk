---
date: 2026-08-22
description: "tecsgen内部仕様書 第5章（字句解析・構文解析）— bnf.y.rb内蔵の手書きスキャナ、RESERVED/RESERVED2キーワード表、Import_C経由のC言語パーサ連携。tecs_lang.rbの役割誤認を訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 5 of 12. 2026-08-22、`tecslib/core/bnf.y.rb`・`C_parser.y.rb`・`componentobj/import_c.rb`・`tecs_lang.rb` を直接読んで全面検証・訂正。

## 5. 字句解析・構文解析

> [!warning] tecs_lang.rb は字句解析器ではない
> 旧版はキーワード表・リテラル処理を `tecs_lang.rb` の役割としていたが、誤り。`tecs_lang.rb` が扱うのは `LANG` / `TECSGEN_LANG` / `TECSGEN_FILE_LANG` / `-k` オプションからの**言語・文字コード解決**（メッセージファイル `messages_console_*.rb` / `messages_file_*.rb` の選択、`Kconv` 用の `$KCONV_CDL` / `$KCONV_CONSOLE` / `$KCONV_TECSGEN` 設定）のみで、CDL の字句解析には関与しない。実際の字句解析は 5.1 の通り `bnf.y.rb` の `Generator#parse` に手書きで内蔵されている。

### 5.1 字句解析（bnf.y.rb 内蔵スキャナ）

CDL には独立した字句解析ファイルは存在しない。`racc` の `---- inner` セクション（`bnf.y.rb` 1516行目以降）に定義された `Generator#parse` が、`TECSIO.foreach` で1行ずつ読みながら正規表現の `case/when` チェーンでトークン化し、`@q`（トークン配列）に積む一括先読み方式（generator ではなく配列キュー）。`next_token` が `@q.shift` で1トークンずつ racc の `do_parse` に渡す。

- 識別子は `/\A[a-zA-Z_]\w*/` にマッチ後、`RESERVED[word] || :IDENTIFIER` でキーワード判定（1518行目の `RESERVED` ハッシュ：`namespace`/`signature`/`celltype`/`cell`/`attr`/`call`/`entry`/`import_C`/`generate`/`__tool_info__` 等の予約語、および `int`/`char`/`enum` 等の型名）
- `[` `]` 内でのみ有効な指定子キーワード（`singleton`/`optional`/`in`/`out`/`through` 等）は別テーブル `RESERVED2`（1599行目）に分離されており、`next_token` 内で `@in_specifier` フラグが立っているときだけ `IDENTIFIER` → 対応トークンへ置き換える（`set_in_specifier` / 対応する解除メソッドで管理）。同じ単語が `[...]` の外では通常の識別子として扱える設計
- `IDENTIFIER` はさらに `Namespace.is_typename?` で既知の型名なら `TYPE_NAME` トークンへ再置換される（typedef 済み型を後続の構文規則が区別するため）
- リテラルは 16進（`0x...`）・8進（`0[0-7]+`）・浮動小数・整数・文字（`'...'`）・文字列（`"..."`、改行を含む文字列は複数行にまたがる `b_in_string` 状態で継続結合）をそれぞれ専用トークンへ
- コメントは `/* ... */`（`b_in_comment`）と TECS 独自の `---+` ブロックコメント（`b_in_comment2`）の2種を状態フラグで処理
- 文字コード変換（`kconv`／`TECSIO`）は 5.1 のスキャナが `TECSIO.foreach` を経由して行単位で受け取る時点で完了しており、上記の正規表現マッチ自体は文字コードに関知しない

### 5.2 構文解析（bnf.y.rb / bnf.tab.rb）

- `racc` で生成されたパーサ（LALR(1)）。文法規則は `bnf.y.rb` の `---- inner` より前の部分に記述
- `bnf.tab.rb`（生成済みパーサ本体）はリポジトリに同梱済み（`racc` インストール不要で実行可）
- パース中にコンポーネントオブジェクト（`Namespace`/`Celltype`/`Cell`/`Join` 等）を各文法規則のアクションから直接インスタンス化する（中間 AST を経由しない）
- `on_error(t, v, vstack)` が構文エラー時のフックで、`token_to_str(t) == "$end"` なら `G1015 Unexpected EOF`、それ以外は `G1016 syntax error near '$1'` を報告
- エラー・警告・情報メッセージは `Generator.error`/`warning`/`info`（クラスメソッド）に一元化されており、`@@import_C` フラグが立っている間は現在位置の取得元を `C_parser.current_locale` に切り替える（5.3 の C パーサ呼び出し中でも正しい locale で報告するため）

### 5.3 C 言語パーサ（Import_C + C_parser.y.rb）

`import_C` ディレクティブで取り込む C ヘッダを解析する経路。`bnf.y.rb` の文法規則 `import_C` アクションが `Import_C.new(header, define)`（`componentobj/import_c.rb`）を呼び出し、以下を行う。

1. 取り込み対象ヘッダを `#include` する一時 C ソース（`$gen/tmp_C_src.c`）を生成し、GCC 拡張の互換 typedef（`__attribute__`/`__extension__`/`va_list` 等の空定義）を先頭に注入
2. `$cpp`（`-c` オプションまたは `TECS_CPP` 環境変数、`__tool_info__` の `cpp` フィールドで指定）を `IO.popen` で子プロセス実行し、プリプロセス済みテキストを取得。`#` で始まる行（cpp が出力するラインマーカー等のディレクティブ残骸）は `/* ... */` コメントへ置換してから一時ファイル（`tmp_<header>`）へ書き出す
3. **この時点でマクロは cpp によってすでに展開済み** — `C_parser` 自身はマクロ定義を扱わない。`C_parser.new.parse([tmp_header])` が cpp 出力を読み込む
4. `C_parser` は `bnf.y.rb` とほぼ同型の手書きスキャナを内蔵（独自の `RESERVED` テーブル、16進/8進/浮動小数/整数/文字/文字列リテラルの正規表現）が、構文解析の対象は **typedef と struct の宣言文のみ**（`next_token` 内の `@in`/`@count`/`@prev_block_end` という簡易ステートマシンで、typedef/struct の開始から対応する `;` までの間だけトークンを racc へ渡し、それ以外の関数プロトタイプ等はブロックの対応を数えて読み飛ばす）
5. 変換結果（型宣言・typedef）を Namespace に登録
6. 変換後の型オブジェクト（`CIntType` 等）は `types.rb` の型クラスに `ctypes.rb` の `CType` モジュールを include したもの。`const` / `unsigned` / `long` など複数の型指定子が並ぶ C 宣言は `CType#merge` で1つの型オブジェクトへ畳み込まれる（例: `unsigned long` → 1回目の `merge` で `unsigned`、2回目で `long` を反映）

---

