---
date: 2026-08-22
description: "tecsgen内部仕様書 第10章（ファイル入出力）— Import/import_C（即時パース・reuse指定・二段探索）、TECSIO（行単位の文字コード変換）。2026-09-23、Importable#find_fileの実ソースコードと二段階解決アルゴリズム・$import_path既定値・典型挙動を詳細化。"
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
- ファイル探索は `Importable#find_file`（`import.rb`/`import_c.rb` 共通、`componentobj/importable.rb`）が担う二段探索：
  - **実ソース実装（`componentobj/importable.rb`）**:
    ```ruby
    def find_file file
      $import_path.each{ |path|
        if path == "."
          pt = file
        else
          pt = "#{path}/#{file}"
        end
        if File.exist?( pt )
          $base_dir[ Dir.pwd ] = true unless $base_dir[ Dir.pwd ]
          return pt
        end
      }
      $base_dir.each_key{ |bd|
        $import_path.each{ |path|
          pt = "#{path}/#{file}"
          Dir.chdir $run_dir
          Dir.chdir bd
          if File.exist?( pt )
            $base_dir[ bd ] = true
            return pt
          end
        }
      }
      return nil
    end
    ```
  - **解決アルゴリズム詳細（実ソース検証）**:
    - `$import_path` は `tecsgen.rb:293` で `$import_path = [ "." ]`（カレントディレクトリ）に初期化され、`-I` オプションや `__tool_info__("tecsgen")` の `import_path` 指定（`tool_info.rb`）が末尾に追加される。
    - **第1段階**: `$import_path` の各エントリを順に試す。`path == "."` なら指定文字列 `file` をプロセスの現在の作業ディレクトリ基準でそのまま `File.exist?` チェック（それ以外は `"#{path}/#{file}"`）。見つかった場合、**見つかったファイル自体のディレクトリではなく `Dir.pwd`（プロセスの起動ディレクトリ）** を `$base_dir` へ登録する。
    - **第2段階（第1段階で見つからなければ）**: これまで `$base_dir` に蓄積された各ディレクトリ `bd` へ実際に `Dir.chdir` し、その状態で再度 `$import_path` の各エントリと組み合わせて探索する。見つかればその `bd` を改めて `$base_dir` へ登録する。
  - **解釈と実務上の帰結（典型例）**:
    - `/project/main.cdl` をカレントディレクトリ `/project/` で `tecsgen main.cdl` 実行した場合:
      1. `main.cdl` 自体は `$import_path=["."]` により `Dir.pwd`（`/project/`）基準で見つかり、`$base_dir["/project/"] = true` が登録される。
      2. `main.cdl` 内の `import("sub/types.cdl")` は、まず第1段階を `Dir.pwd` 基準で試し、同ディレクトリで実行していれば `./sub/types.cdl` がそのまま見つかる。
      3. 異なる作業ディレクトリから実行していた場合は第1段階で見つからず、第2段階で `$base_dir`（`/project/`）へ `chdir` して再探索することで見つかる。
    - 「importを書いたファイルからの相対パス」に近い結果になるのは、`.` が既定で `$import_path` に含まれることと `$base_dir` が蓄積される副次効果によるものであり、「importしたファイル自身のディレクトリ」を直接記録・参照する専用の仕組みではない。CDLファイル群が別々のディレクトリに散らばり、tecsgenの実行ディレクトリが一致しない場合、`-I` で明示的にサーチパスを渡さないと解決に失敗しうる。
  - **TECSCDE-DT-ELとの対比**:
    - TECSCDE-DT-EL側の自動追跡実装（「編集対象ファイルのディレクトリ → `base_dir` → `import_path` の順」）は、tecsgen本体のこの挙動を簡略化・独自解釈したものである。

### 10.2 文字コード変換（TECSIO）

`TECSIO`（`bnf.y.rb` 2158行目、`Generator`/`Import` 等と同じ `---- inner` セクション内 — 独立ファイルではない）:

- `TECSIO.foreach(file) { |line| ... }`：CDL ファイルを1行ずつ読み込みながら `str_code_convert` でエンコーディングを揃えて yield する。5.1 の字句解析はこの正規化済みの行を受け取る。SJIS 指定時は Ruby の `File.open` を `Windows-31J` として開いてから変換することで、SJIS として不正な文字が例外を起こさず `?`（UTF-8 では U+FFFD）に置換されるようにしている（コメント中の混在文字コードを許容するための実装上の工夫）
- `TECSIO.str_code_convert(msg, str)`：`str` のエンコーディングが `msg` と異なる場合のみ `str.encode(msg.encoding)` を試み、変換不能なら元の `str` をそのまま返す（例外を握りつぶす形の縮退）。エラーメッセージへの文字列埋め込み（`Generator.error2` 等）でも同じメソッドが使われる

---

