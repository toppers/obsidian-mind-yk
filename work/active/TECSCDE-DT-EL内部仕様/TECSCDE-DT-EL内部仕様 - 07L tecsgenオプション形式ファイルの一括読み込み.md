---
date: 2026-11-17
description: "TECSCDE-DT-EL内部仕様 第7C章7.7.4節（#10 tecsgenオプション形式ファイルの一括読み込み）。第7C章から25KB閾値で逐語分離（2026-11-17）。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note [[TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合]]（2026-11-17、25KB閾値で7.7.4節を逐語分離。見出しの番号は元のまま）。

### 7.7.4 tecsgenオプション形式ファイルの一括読み込み（#10）

> [!note] 位置づけ
> 本節は当初DT-EL固有の拡張として設計したが、**2026-10-21に[[TECSCDE-DT外部仕様]]（言語非依存の親仕様）の第5章5.3節へ昇格した**（ユーザー決定。規定は[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05A 開く（読み込み）|DT外部仕様5.3節]]）。想定利用シーン（tecsgenビルド用Makefile等の実引数列をそのまま流用する運用）自体は未検証(inferred)のまま。本節はその実装側の設計と実装済みの規則を持つ。

**①ファイル形式・拡張子**: 新拡張子`.tecsgen-opts`を定義する（**拡張子名は2026-10-21に確定**。当初は仮称）。内容はtecsgenのコマンドライン引数をそのまま記述したプレーンテキスト（`-I <path>` / `--import-path=<path>` / CDLファイルパスの列挙、空白・改行区切り、`#`始まりの行はコメント）。

```ts
// main/file-service.ts の listDirectory() フィルタを変更（第7B章7.6.1節）
.filter((e) => e.isDirectory() || /\.(cde|cdl|tecsgen-opts)$/i.test(e.name))
```

**クリック時の分岐**: `FileBrowserView`（7.6.3節）はクリックされたファイルの拡張子で処理を分ける——`.cde`/`.cdl`は既存の`openFromPath`（7.6.4節）、`.tecsgen-opts`は本節の`loadOptionsFile`へ。

**②編集対象の決定**: 新規メソッド`FileService.parseTecsgenOptionsFile(path)`がテキストを解析し、列挙されたCDLファイル群・`-I`/`--import-path`の値・`cpp`指定（あれば）を返す。CDLファイルが複数列挙されている場合は、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05A 開く（読み込み）|TECSCDE-DT外部仕様5.3節]]・[[TECSCDE外部仕様]]8.1.2節の「最後に列挙されたファイルを編集対象とする」規則をそのまま適用する。

```ts
// main/file-service.ts に追加
export interface TecsgenOptionsFile {
  readonly cdlFiles: readonly string[]; // 列挙順。最後の要素が編集対象候補
  readonly importPaths: readonly string[]; // -I/--import-path の値
  readonly cpp?: string;
  readonly defineMacros: readonly string[]; // -D/--define の値（記述順。2026-10-22追加）
  readonly systemDirs: readonly string[]; // -Sの絶対パス。一括要求へ同じ解析結果を渡す
}

async parseTecsgenOptionsFile(path: string): Promise<TecsgenOptionsFile> {
  const text = await fs.promises.readFile(path, 'utf-8');
  // 空白・改行区切りのトークン化、`-I`/`--import-path=`の値をimportPathsへ、
  // それ以外の非オプショントークン（`-`で始まらない）をcdlFilesへ分類する。
  // 引用符の扱い等パース規則の詳細は実装時に確定。
}
```

**パース規則（実装済み、2026-10-21 時点）**: 上のスケッチの「実装時に確定」とした詳細は、`main/file-service.ts` の `parseTecsgenOptionsFile`（結果の型 `TecsgenOptionsFile` は `shared/ipc-types.ts`）が次のとおり確定している。

1. **読み込み**: 文字コードは `decodeBuffer` で判定し、失敗したら UTF-8 とみなす（スケッチの「`utf-8` で読む」より広い）。
2. **トークン化**: `#` で始まる行（前後の空白を除いて判定）を除き、残りを空白・改行で区切る。引用符による空白の保護は扱わない（空白を含むパスは書けない）。
3. **分類**:

| トークン | 扱い |
|---|---|
| `-I <path>`、`--import-path <path>`、`--import-path=<path>`、`-I<path>` | `importPaths` へ |
| `-c <cmd>`、`--cpp <cmd>`、`--cpp=<cmd>`、`-c<cmd>` | `cpp` へ（複数あれば最後が残る） |
| `-D <macro>`、`--define <macro>`、`--define=<macro>`、`-D<macro>` | `defineMacros` へ（記述順。値が CDL ファイル名として `cdlFiles` に混入しない）。2026-10-22に、以前の「値ごと読み飛ばす」から変更 |
| 拡張子が `.cdl` または `.cde` のトークン | `cdlFiles` へ。列挙順を保つ |
| `-k <code>`、`--kcode <code>`、`--kcode=<code>`、`-k<code>` | **読み取らない（無視する）**。`-k`の値（`euc`／`sjis`／`utf8`など）は`.cdl`／`.cde`で終わらないため`cdlFiles`に混入しない。DT-ELのCDLの復号は`-k`に関係なく決まる（第7章7.8節）。tecsgenへ渡す`-k`は別の話で、`TecsgenCommandBuilder`の`-k utf8`と、オプションファイルの原文を渡す経路で異なる（第9章冒頭の`-k`の注記） |
| それ以外 | 無視する |

4. **パスの解決**: `cdlFiles` の相対パスは、**オプションファイルのあるディレクトリ**を基点に絶対パスへ解決する（`resolve(dirname(path), f)`）。tecsgen の実際の呼び出しがそのディレクトリから行われる想定のため。これを省くと、`fs.readFile` が main プロセスの起動ディレクトリで解決して、存在しないパスになる。`importPaths` は解決せずに値のまま返す（基点は `import-resolution.ts` が、オプションファイルのあるディレクトリと `baseDir` から決める）。
5. **値が欠けた末尾の `-I`・`-c`**: 何も追加せずに終わる（エラーにしない）。
6. **スケッチとの違い**: 「`-` で始まらない非オプショントークンを `cdlFiles` へ」ではなく、**拡張子が `.cdl`/`.cde` のものだけ**を `cdlFiles` に入れる。ほかの非オプショントークンは無視される。
7. **tecsgenの実行への引き継ぎ**（2026-10-22、外部仕様8.4.2）: 「実行(Generate)」と「コマンドをコピー」（`app/tecsgen-actions.ts`）は、コマンドを作るたびに`store.getOptionsFilePath()`のファイルを`parseTecsgenOptionsFile`で**再解析**して、`-I`・`-D`・`-c`を得る。復元した`extraImportPaths`をコマンド生成の固定値にしないのは、オプションファイルの現在の内容を使うため（7H.4節）。合成の規則は、`importPath = [__tool_info__の import_path, …, オプションファイルの -I]`、`defineMacro = [__tool_info__の define_macro, …, オプションファイルの -D]`（すべて渡す）、`cpp = オプションファイルの -c ?? __tool_info__の cpp`。オプションファイルが無い、または解析に失敗したときは、`__tool_info__`の値だけを使う（Generateは止めない）。このため`tecsgenCommandLine`は非同期（`Promise<string | undefined>`）になる。**作業ディレクトリ**（外部仕様5.3節）: `optionsFilePath`があるときは、そのディレクトリ（`shared/path-under.ts`の`dirnameOf`）を`cwd`として`generate()`に渡し、IPC `tecsgen:generate(args, cwd?)`から`TecsgenRunner.generate(args, cwd)`が`execFile`の`cwd`に指定する。相対パスの`-I`・`-S`の基点を変えないため。上限は従来どおり30秒・既定の`maxBuffer`のまま（Plugin型の取り込みの`run(args, cwd)`の120秒・16MiBとは別）。オプションファイルの解析に失敗しても`cwd`は指定する。`-S`の引き継ぎは下の「`-S`」の項（`importPaths`経由）。

呼び出しの経路（起動時、2026-11-07、監査#16で統一）: CLIの対象1件選択後、その1件が`.tecsgen-opts`なら解析する。[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I]]に従い、元のCDL列挙から主ファイルと参照の役割、重複排除した列挙順`sourceOrder`を別々に確定し、明示的な要求DTOで`FileService.openPaths(request)`へ渡す。順序を逆転させず、関連メタデータとともに起動時の一括結果を`app:bootstrap`へ送る。

**`-S`（システム定義ディレクトリ）の追加（設計、2026-10-21。2026-10-22に実装）**: 外部仕様（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05A 開く（読み込み）|DT外部仕様5.3節]]）の追加に合わせ、`parseTecsgenOptionsFile`の分類に次を加える。

| トークン | 扱い |
|---|---|
| `-S <dir>`、`--system-dir <dir>`、`--system-dir=<dir>`、`-S<dir>` | `systemDirs`（絶対パスに解決）へ入れ、**同時に`importPaths`にも、書かれた値のまま、`-I`との記述順を保って入れる**。`-I`と同じ4形。値が欠けた末尾の`-S`は何も追加しない |

- `TecsgenOptionsFile`に`readonly systemDirs: readonly string[]`を追加する。`cdlFiles`と同様、相対パスは**オプションファイルのあるディレクトリを基点に絶対パスへ解決**して返す（`importPaths`は解決しないのと異なる）。
- `systemDirs`は`OpenResult`に載せてrendererへ送り（`extraImportPaths`と同じ経路）、`AppStore`が保持する。`CdlDocumentLoader.loadSources()`は`systemDirs`で各ソースの`systemDefined`を決める（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章3.2節]]）。
- セッション復元時は7H.3.1を正とし、opts再解析成功なら同じ結果の探索パスと`systemDirs`を採用する。空配列も優先し、失敗時だけ保存済み探索パス＋`systemDirs`空へ戻す。現行コードは探索パスを旧値のままにするため未対応だった（三者監査#8、2026-11-09。段0で実装済み、as of 2026-11-12）。ファイルブラウザからの通常のクリックや、「消去」では、`extraImportPaths`と同じく`systemDirs`も空に戻る。
- **tecsgenの実行への引き継ぎ**（2026-10-22実装）: `-S`は`importPaths`に入った時点で`-I`相当になり、上の7.の合成で、他の`-I`と記述順のまま`-I <path>`として渡る（作業ディレクトリは7.のとおり`.tecsgen-opts`のあるディレクトリ）。並べ替え・重複除去はしない。`-S`の値は書かれたまま渡す（`systemDirs`のような絶対パスへの解決はしない）。

**③`-I`/`--import-path`の受け渡し**: 既存の`ImportResolutionOptions.importPaths`（第7章7.5節）へそのまま渡す。CDLファイル自身の`__tool_info__`が持つ`import_path`・`base_dir`は5.1節の方針どおり書き換えず、オプションファイル由来の`importPaths`は追加の探索候補として重ねる（既定順序: CDL自身の`import_path`を先に試し、見つからなければオプションファイル由来を試す——第7章7.5節の既存探索順序に追加ステップとして挿入する）。

**④#8との統合（2026-11-07、監査#16で契約更新）**: 主ファイルの役割と読み込み順を分離し、全ファイルの読み取り・参照解決・モデル構築が成功してから、図と関連状態を一度だけ適用する。主ファイルを`openFromPath`で開いて残りを`addAsReference`する方式や、その逆の逐次適用は使わない。

要求型`OpenPathsRequest`、main・preload・rendererの共通API、`loadOptionsFile`の正規コード例は[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I.2〜4]]に統一する。`primaryPath`・`referencePaths`・`sourceOrder`を明示し、`optionsFilePath`・`extraImportPaths`・`systemDirs`を同じ一括結果へ含める。未保存確認は1回だけ、キャンセル・失敗時は旧状態を保持し、成功後に7Hのセッションを1回保存する。これは確定契約で、現行`5cf2d85`は未対応だった（三者監査#5は段0で実装済み、as of 2026-11-12）。DTO・`primarySourceKey`・ストアとセッションの順序保持を7I.0に従って実装する必要がある（三者監査#5、2026-11-09）。

## Related

- [[TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合]] — 分離元（7.7節の全体）
- [[TECSCDE-DT外部仕様 - 05C tecsgenオプション形式ファイルとシステム定義CDL]] — 対応する外部仕様（5.3節から分離）
- [[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約]] — opts を含む複数ファイル読み込みの契約
- [[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元]] — opts のパスと探索パスのセッション復元
