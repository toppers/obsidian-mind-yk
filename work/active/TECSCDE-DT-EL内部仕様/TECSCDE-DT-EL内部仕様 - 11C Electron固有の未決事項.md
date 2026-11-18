---
date: 2026-11-11
description: "TECSCDE-DT-EL内部仕様 第11章11.2節 — Electron固有の未決事項（決定済みを含む）の表。第11章が25KB閾値を超えたため、11.2節の本文を逐語で分離した。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

Domain note split from [[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]] (2026-11-11). 第11章11.2節の本文を逐語で移したもの。配布方式とWindowsコード署名の候補は[[TECSCDE-DT-EL内部仕様 - 11B 配布方式と署名]]、目次は[[TECSCDE-DT-EL内部仕様]]。

### 11.2 Electron固有の未決事項

| # | 事項 | 現状 |
|---|---|---|
| 1 | ~~`sandbox: true`の採否~~ → **決定済み（2026-09-08）: `sandbox: false`** | preloadをESM（`.mjs`）で書く方針を採ったため`sandbox: false`（Electronのサンドボックス化preloadはESM importを使えない）。`contextIsolation: true`・`nodeIntegration: false`は維持。経緯・トレードオフ: [[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定\|preload ESM・sandbox決定]]。第2章2.4節のコードも`.mjs`に更新済み（`createRequire`によるclipboard取得は、2026-10-21の実機確認でpreloadから使えないと分かり、ipcMain経由に変更。第2章2.4節） |
| 2 | ~~配布ツールの選定~~ → **決定済み（2026-09-12パッケージング／2026-09-23自動更新）**: パッケージング(package/make)はElectron Forge（`@electron-forge/maker-squirrel`）。自動更新(publish)は`update-electron-app` + GitHub Actions（Node 22固定でpublish）で自動化する構成に確定。origin（`toppers/tecscde-dt-el`）が当初非公開で`update.electronjs.org`が使えないと判明し、いったん配布専用の公開ミラーリポジトリ案を採ったが、同日中にユーザーがoriginをpublicへ変更したため撤回——**originへ直接publishする**構成で確定した。**配布方式の決定・設定登録・実機検証を別の段階として扱い、macOS/Linuxを一括して「未実装」とは表記しない。設定の基準チェックアウトと検証状況は[[TECSCDE-DT-EL内部仕様 - 11B 配布方式と署名\|11B]]冒頭の表を正とする（2026-11-08、監査#20）。コード署名は当面見送り（未署名、2026-09-23決定）で、署名方式は未決（候補は11.2.1節）**。決定の経緯・却下した代替案は[[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|TECSCDE-DT-EL 配布アーキテクチャ決定]]参照。パッケージング導入時に見つかった3件の環境要因（gitフェッチ禁止によるoverrides、electron-winstallerの上流バグ、`@electron/packager`のNode 26非対応）は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]Action Items参照。コード署名の背景知識・設定箇所は[[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]]、選定時に比較したパッケージング・自動更新ツールの一覧は[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]参照 |
| 3 | `tecsgen`・Cプリプロセッサの検出方法 | **tecsgenの設定はV0.2.0で決定**（2026-11-05外部仕様、内部設計は[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理\|9D]]）。「情報」に設定欄を同居させ、環境変数`TECSGEN_COMMAND`、保存パス、実在する`TECSPATH`、`PATH`の順で解決します。Windows探索候補は2026-11-10に.bat/.ps1へ確定（09D.2）。TECSPATHがディレクトリのときは採用せずPATH探索へ進む（2026-11-17決定・実装済み）。ディレクトリ内の実行ファイルへの変換等はTBC。**Cプリプロセッサの検出・設定は V0.2.1 で決定**（2026-11-17 に反映。設計は[[TECSCDE-DT-EL内部仕様 - 09E V0.2.1 Cプリプロセッサ設定と失敗詳細|09E]]）。`.tecsgen-opts` の `-c`／`--cpp`、CDL の `__tool_info__` の `cpp`、設定の `cppPath`、`PATH` 上の末尾が `gcc` の実行ファイル、`gcc` の順に解決します（`.tecsgen-opts` の `-c` を `import_C` に使う実装は、v0.2.6 段2で実装済み、2026-11-17、コミット `b4fa6e1`、ブランチ `v0.2.6-stage2`・未マージ、三者相違一覧 8-4） |
| 5 | tree-sitterバインディングの選択 | **2026-09-13追加**（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計\|TECSCDE内部仕様第4章]]の改訂に伴う本書固有の選択）。ブラウザ版と異なりElectronはネイティブバインディング（`node-tree-sitter`）を選べるが、**モジュールBはrendererに置かれ`nodeIntegration: false`・`contextIsolation: true`（第2章2.4節）のためrendererからは読み込めない**。したがって選択肢は①rendererで`web-tree-sitter`（WASM）を使う（プロセス配置を変えずに済む・ブラウザ版と同一コード）②CDL解析をmainへ移し`node-tree-sitter`を使う（速いがBの配置を第2章2.2節から変更することになり、解析結果をIPCで渡す設計が増える）。**①を既定とする**——**2026-09-21、大規模CDLでの実測により決着**（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]の`tests/perf/cdl-parse.bench.test.ts`、`RUN_CDL_BENCH=1`で実行）: 150〜6000セル（100〜4000結合）で計測したところ、6000セル・4000結合という現実のtecsgen CDL図では想定しづらい規模でも`CdlDocumentLoader.loadSources()`（パース＋CST走査＋モデル構築のフルパイプライン）の中央値は約75ms、スケーリングもほぼ線形で崖（急激な劣化点）は観測されなかった。②へ切り替える性能上の根拠は無いと判断し、①のまま確定する |
| 4 | ~~ファイルブラウザの再検討~~ → **決定済み（2026-09-21）: 採用。** [[TECSCDE-DT外部仕様]]第3章3.5.1節・第10章10.4節を改訂し、階層ツリー表示のファイルブラウザを採用した。訂正: 本表は以前「mainプロセスに`fs.readdir`（`FileService`の拡張）が既にある」と記載していたが誤りだった——2026-09-21時点の[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装\|TECSCDE-DT-EL実装]]の`FileService`にディレクトリ列挙機能は存在せず（`openDialog`/`openPath`/`openPaths`/`save`/`saveAsDialog`/`exportFile`のみ）、新規実装が必要。設計は第7章7.6節に追加した |
| 6 | ~~`TecsgenCommandBuilder`に`-k`（CDLファイルの文字コード指定）を追加するか~~ → **決定済み（2026-09-24）: 追加した。** [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース\|tecsgen外部仕様第5章]]の`-k, --kcode`（既定`euc`）に対し、CDLファイルはUTF-8前提（[[TECSCDE外部仕様]]5.1.2節）のため`buildArgs`の先頭で常に`-k utf8`を付与するよう`command-builder.ts`を変更（コミット`6425b25`、テスト更新込みで279テスト全pass）。実際に文字化け・構文エラーが発生するかどうかは未確認のまま(inferred)だが、外部仕様が定める前提と一致させる安全側の対応として実施。**Plugin型取り込みの文字コード指定の欠落は2026-10-22に解消済み**。`.tecsgen-opts`に`-k`／`--kcode`が無い場合は、`-g <dir>`の直後に`-k utf8`を追加し、明示指定があればその値を尊重する（2026-11-08、監査#17で旧記述を整理）（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章冒頭の注記]]） |
| 7 | 起動時、固定のsamples/コマンドライン引数ではなく**前回終了時に開いていたファイルを復元する** | **決定済み（2026-09-22）、2026-11-07に監査#9の保存契約を具体化**: `lastSession`は`editablePath`・`referencePaths`・`optionsFilePath`・`extraImportPaths`を都度保存し、明示入力（CLI／関連付け確定要求） > `lastSession` > `samples`の優先順位で復元する。詳細は[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元\|7H]]。4項目の契約更新に対する実装適合は未確認 |
| 8 | ファイルブラウザで選択したファイルを既存の主ファイルを置き換えずに追加する | **実装済み**: Ctrl+クリックで`references`へ追加する。この名称は読み込み元の区別であり、ユーザ定義CDL由来のセルは主ファイルと同様に編集可能とする（システム定義CDL由来のセルは既定で編集不可、第3章3.2節）。重複パスは無視する。詳細は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章7.7.2節]]。 |
| 9 | ツールバーに**「消去」ボタンを追加**（現在の図をクリアし、CDLファイルを何も読み込んでいない状態にする） | **決定済み（2026-09-22、ユーザー確認）**: [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作\|TECSCDE-DT外部仕様5.2節「新規作成」]]の別名として設計。未保存確認は第7B章7.6.4節の`confirmDiscardChanges()`を再利用。設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合\|第7C章7.7.3節]]参照 |
| 10 | ファイルブラウザでtecsgenのオプション形式ファイルを選んだ場合、探索パスを使って列挙CDLを読み込む | **実装済み**: 最後のCDLを主ファイル、残りを`references`へ追加する。システム定義CDLを除くすべてのユーザ定義CDL由来セルは編集可能で、変更は各元パスへ保存する。詳細は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07L tecsgenオプション形式ファイルの一括読み込み|第7C章7.7.4節]]。 |
| 11 | `import`自動追跡先をファイルブラウザで追加したCDLと統一して扱う | **実装済み**: 読み込み経路を共通化し、2026-10-19に編集可否の規定も現行実装へ合わせて改訂した。主ファイル以外の通常CDLも編集可能で、Plugin生成CDLのみ読み取り専用とする。詳細は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章7.7.5節]]。 |

11.2.1〜11.2.3（Windowsのコード署名の候補比較、macOS／Linuxのパッケージング方式の決定）は、25KB閾値のため [[TECSCDE-DT-EL内部仕様 - 11B 配布方式と署名]] へ分離した（2026-10-10、本文は逐語移動）。

## Related

- [[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]] — 第11章（11.1・11.3〜11.7）
- [[TECSCDE-DT-EL内部仕様 - 11B 配布方式と署名]] — 11.2.1〜11.2.3
- [[TECSCDE-DT-EL内部仕様]] — 目次
