---
date: 2026-09-13
description: "仕様書作成と実装のパターン — コードベース直読みでの仕様書作成、ghrepo型Python CLI、実装言語別分類、多分岐仕様書ツリーの派生、実装セッション区切りでのこまめなコミット、WindowsのPythonでの一括編集はnewline=""で改行を保つ（2026-09-27）、実プロジェクトが使わない機能の正解データは使用例の探索→最小パッチ→合成入力の順に採り、Ruby と Python の食い違いは直さず再現する（2026-10-03）。Patternsから分割（verbatim）。"
tags:
  - brain
---

Domain note split from [[Patterns]] (2026-09-13, 25KB threshold). 内容は verbatim、物理順を保持。

## コードベース直読み仕様書作成パターン

- **採用文脈**: NotebookLM・RST変換ツール等の中間ツールなし。Claude Code がソースコードを直接読み、仕様書を生成する
- **適用例**: tecsgen 外部仕様（17KB・420行超）・内部仕様（25KB・530行超）を1日でスクラッチ作成（2026-05-19）
- **利点**: ツール設定コストゼロ・コードと仕様の乖離なし・反復修正が高速
- **適用条件**: コードベースが Claude のコンテキストウィンドウに収まる規模、または対象モジュールを絞れる場合
- **出典**: [[work/active/tecs/TECS開発]], [[tecsgen外部仕様]], [[tecsgen内部仕様]], git `8b5ebd7`

## ghrepo 型 Python CLI パターン（仕様書駆動）

**ghrepo のプログラム構造**を、サブコマンドを持つ Python CLI の canonical パターンとして使う。

```
エントリーポイント層  ghrepo.py / main() — Clix で引数パース → ディスパッチ
CLI定義層           Clix (clix.py)      — argparse 定義のみ、ロジックなし
コマンド実行層      CommandXxx          — yklibpy.command.Command 継承
設定・ストレージ層  AppConfigx + yklibpy.AppStore/Storex
```

**スキル連携（仕様書駆動フロー）**:

```
docs/req/idea/*.md  (アイデアレベルの要件)
    ↓ python-cli-req-to-external-spec スキル
docs/req/detail/*.md (詳細要件)
    ↓ python-cli-external-spec スキル  (ghrepo-external-spec)
外部仕様書 (docs/spec/external.md)
    ↓ python-cli-internal-spec スキル
内部仕様書 (docs/spec/internal.md)
```

- **採用文脈**: [[ghrepo]]・[[gistx]]・[[gitreporemote]]・[[calibrex]]・[[filelist]] 等、Python CLI プロジェクト全般
- **適用条件**: サブコマンドを持つ CLI、yklibpy を共通基盤として使うプロジェクト
- **出典**: [[ghrepo]], [[gistx]], [[gitreporemote]], `reference/Inbox/仕様書駆動の取り組み.md`（2026-06-04）

## プロジェクト実装言語別分類（2026-04-11 時点）

### Ruby 実装
- [[bookinfor]], [[bookmarkr]], [[cpiconfiles]]

### Python 実装
| 状態 | プロジェクト |
|------|-------------|
| 済 | [[ghrepo]], [[gistx]], [[calibrex]] |
| 未済 | [[filelist]], [[gitreporemote]], [[notebooklmclix]] |

## 多分岐仕様書ツリーの派生パターン（2026-09-05）

1つの外部仕様から、実装方式ごとに複数の代替内部仕様を分岐させて執筆するワークフロー。

- **系譜**: [[TECSCDE外部仕様]]（ブラウザ版） → [[TECSCDE内部仕様]]（関数/interfaceベース、実装済み）／[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]（クラスベース代替案）。さらに[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（デスクトップ版、Electron/Tauri言語非依存） → [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]（Electron/TS）／[[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]]（Tauri/Rust）と枝分かれ。1セッションで4文書・計49ファイルを執筆。
- **執筆手順（毎回同じ形）**: ①既存の姉妹文書群を全章読み込み、差分が生じる章と生じない章を仕分ける ②新文書の目次冒頭に「文書状態」callout で位置づけ・採用方針・姉妹文書との対応表を明記 ③差分が小さい章は全文複製せず「姉妹文書と同一、変更なし」+ 一次情報源へのリンクのみで済ませる（単一情報源の原則を保つ） ④差分が大きい章のみ実装コード例つきで詳述する。
- **章番号ずれの罠**: 元文書の章を1つ統合・省略すると（例: TECSCDE-TS内部仕様でCDLパーサ章をモジュール構成章に統合）、それ以降の章番号が1つずれる。目次・各章の相互参照・前方参照（「本書第N章で扱う」）を**同じ編集パスで全て直さないと、後から章を書き足すときに矛盾が露呈する**（本セッションで実際に発生し、第4章執筆時に気づいて目次・第1章を修正した）。
- **言語・フレームワークによる設計転換は機械的な置換で済まない**: TypeScriptの`class`ベース設計をRustへ「移植」する際、Rustに継承がないため単純な文法変換ではなく、コンポジション（別structへの分離）や所有権システムによる不変性の言い換えが必要だった。「同じ設計思想を別言語のイディオムで表現し直す」という作業自体を明示的な章（第1章）で扱うと、読み手が「単なる翻訳」と誤解しない。
- **各文書は「対応する実装は存在しない、採否は未決定」と明記**——複数の代替設計を書くことは実装への昇格を意味しない。North Starには追加せず、検討中の設計案として`work/active/`に留め置く。
- **出典**: 2026-09-05セッション、[[Memories]]同日エントリ

## 実装セッションの区切りごとに`npm run check`通過を確認した時点でこまめにコミットする（2026-09-23）

- **発見の経緯**: [[work/active/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]でファイルブラウザ機能を実装したセッション（2026-09-21、`E:\Ccur\typescript\TECSCDE-DT-EL`）が、テストpass・実機確認まで済ませたにもかかわらず一度もコミットしなかった。作業ツリーは未コミットのまま翌日（2026-09-22）の別セッションへ引き継がれ、そのセッションが続きの機能（第7C章#7〜#11）を実装してまとめてコミット（`829efc7`）した結果、**前日分の実装がその日のコミットメッセージに現れず、Brag Docの記録からも漏れた**（`/om-wrap-up`で発覚、[[perf/brag/Q3 2026 — Impact — 2026-09-21|補完エントリ]]参照）。vault側の記録（Key Decisions・内部仕様）は都度書いていたため知識自体は失われなかったが、コード側の履歴と実際の作業単位がずれた。
- **教訓**: 実装セッションの区切り（機能1つ・バグ修正1つ等のまとまり）ごとに、`npm run check`（型チェック＋テスト＋依存関係検証）が通過した時点で、その場でコミットする。「後でまとめてコミットすればよい」という先延ばしは、次のセッション（自分か他人か問わず）が作業ツリーをそのまま引き継いだ場合に、コミット境界と実際の作業境界の対応が失われるリスクを持つ。
- **適用条件**: 複数セッションにまたがる可能性がある実装作業全般。1セッション内で完結し即座にレビュー・破棄する使い捨てコードには適用しない。
- **出典**: [[work/active/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]、[[perf/brag/Q3 2026 — Impact — 2026-09-21|Brag Doc補完エントリ]]

## Windows の Python でテキストを一括編集するときは改行を保つ書き方に固定する（2026-09-27）

スクリプトでファイルを書き換えるときは、次の形だけを使う。

```python
s = open(p, encoding="utf-8", newline="").read()
# 置換（見つからなければ assert で止める）
open(p, "w", encoding="utf-8", newline="").write(s)
```

`newline=""` を付けないと、Windows では読み込み時に改行が `
` に揃えられ、書き出し時に CRLF になる。`core.autocrlf=input` のリポジトリではコミット内容が LF に戻るので差分に出ず、作業ツリーだけが CRLF になって WSL のシェルスクリプトが壊れる（[[tecsgen-python3移植計画|tecsgen-python3]] P3 で発生、[[Gotchas - CLI Build Tooling]]）。シェルスクリプトを変えたら WSL で `sh -n` を実行して確かめる。ユーザー採用の常設ルール（[[Key Decisions]] 2026-09-27）。

## 実プロジェクトが使わない機能の正解データは、使用例の探索 → 合成入力の順に採る（2026-10-03）

移植元の機能（[[tecsgen-python3移植計画|tecsgen-python3]] では標準付属プラグイン）に、実プロジェクトの使用例が無いと、正解データが採れず移植できない。次の順で進めた。

1. **使用例を探し尽くす**: 実プロジェクトの CDL → 移植元のテストツリー → 別ブランチ・別リポジトリ・パッケージ。見つかったら、その Makefile が呼ぶ `make tecs` やテストの引数をそのまま再現する（`ATK1DelayTaskPlugin` は et_robcon の nxt_sample 4本、`MrubyInfoBridge*` は `test/mruby`、`HRPRPCPlugin` は hrp3 の sample2 だった）。
2. **そのままでは通らないなら、元ファイルに最小のパッチ**: 派生ファイルを丸ごとコピーせず、置換元が1か所でなければ失敗する文字列置換で、直した理由と一緒に記録する（`collect_kernel.py` の `patch`）。
3. **使用例が全く無いなら合成入力**: 実プロジェクトのカーネル定義を import し、現行の文法で最小の CDL を書く。tecsgen を `-k euc` で呼ぶなら CDL のコメントは ASCII だけにし、説明は同じディレクトリの README に書く。
4. **Ruby 版が例外で止まる経路も正解データ**: 例外メッセージ・終了コード・例外までに作られたファイルまで一致させる。例外で止まるので、1ケースに1種類しか置けない。
5. **狙ったクラスが本当に動いたか** は、出力の文字列検索でなく実行の計測（`plugin_trace.rb`）で確かめる（[[Patterns - 検証と調査]] 2026-09-30）。

Ruby と Python の食い違いで繰り返し出たもの（どれも「直さず再現」が方針。[[Patterns - 検証と調査]] 2026-10-01）:

- **無いキーの参照**: Ruby の `Hash#[]` は nil、文字列にすると空。Python の `d[k]` は `KeyError` になる。`to_s(d.get(k))` にする（`HRPObjectPlugin`）。
- **重複排除の登録漏れ**: Ruby 版が「見た」と記録しないために重複して出る出力は、Python 版で直さない（`core/tecsinfo` の `#include`）。
- **日本語リテラル**: Ruby は `-k euc` でも、プラグインの UTF-8 ソースの文字列リテラルを UTF-8 のバイト列のまま書く。`ruby_compat.utf8_literal` で同じバイトにする。
- **同名モジュールの再オープン**: `GenHRP2Marshaler.rb` は `GenTransparentMarshaler` を再オープンして差し替える。派生クラスで上書きし、同じ実行での併用による影響は再現しない（docstring に書く）。
- **make 経由のケースの終了コード**: make が失敗すると 2 になる。tecsgen の終了コードは stderr の `Error N` から取る。

## Related

- [[Patterns]] — 索引

## 記録を再生するテストだけでは、配布物の欠落を検出できない（2026-10-02）

tecsgen-python3 は差分テストを `RecordedHost`（Ruby 版の入出力の記録を再生する）で動かすため、実ファイルシステムを読む処理は一度も試されない。その結果、`cli.py` が `{PACKAGE_DIR}/tecs`（標準 CDL ライブラリ）を参照するのに、`src/tecsgen/` に `tecs/` が無く、wheel にも入っていないことに、P5 まで気づかなかった。P6a で、**wheel を作って別の仮想環境へ入れ、実際にコマンドを実行して Ruby 版と出力を比べる**ことで見つけた。配布する成果物は、記録再生のテストが全部通っていても、インストールした状態で1回は動かす（回帰防止には、同梱ファイルの存在を調べる小さなテスト `tests/test_p6_packaging.py` を置く）。関連: [[tecsgen-python3移植計画]]（P6a）。
