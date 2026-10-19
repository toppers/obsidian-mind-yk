---
date: 2026-09-21
description: "tecsgen（Ruby実装）のPython3移植版の作業ノート。構文解析はRuby版のracc表を移植（2026-09-27にtree-sitterから変更）。P0〜P7まで実装・検証済み（プラグイン不使用119/119・プラグイン使用85/85ケースで生成物がRuby版（tecsgen-rb）とバイト一致、2026-10-09時点）。cmake対応とAsp3Tecs.cmakeからの呼び出しも完了（2026-10-06）"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
---

# tecsgen-python3
tecsgenをPython3で実装する

`work/active/tecsgen-python3/` と `work/active/tecsgen-plugins-python3` 配下の仕様書群への入口。

## 計画

- [[tecsgen-python3移植計画]] — フェーズ分割・差分テスト方針・リスク（2026-09-26）。完了済みの P0〜P2 の詳細は [[tecsgen-python3移植計画 Archive — P0–P2]]
- [[tecsgen-python3 P0基本方針決定]] — CLI完全互換・mixinは多重継承・グローバル変数は設定オブジェクトへ集約（2026-09-26）
- P1 基盤（Node・エラー処理・入出力）を実装・検証（2026-09-27）→ [[tecsgen-python3移植計画]]・[[tecsgen-python3内部仕様 - 11 エラー・警告処理|内部仕様11章]]
- [[tecsgen-python3 tecsflow・Marshal調査]] — Ruby版のMarshal使用箇所と`tecsflow.rb:452`の不要な呼び出し（WSLで削除前後の出力一致を確認、2026-10-09）。tecsflow移植時の前提資料
- [[tecsgen-python3 パッケージ構成決定]] — Rubyと1ファイル対1モジュール、プラグインはRubyと同名（2026-09-26）
- [[tecsgen-python3 tree-sitter読み込み方式決定]] — 文法のCソースを同梱しC拡張としてビルド（2026-09-26、**2026-09-27 superseded**）
- P2 構文解析のフロントエンドを実装・検証（2026-09-27）→ [[tecsgen-python3 構文解析方式決定]]（tree-sitterをやめracc表駆動へ）・[[tecsgen-python3内部仕様 - 05 字句解析・構文解析|内部仕様5章]]
- P3 型・値・式・コンポーネントモデルと意味解析を実装・検証（2026-09-27）→ [[tecsgen-python3内部仕様 - 06 意味解析|内部仕様6章]]
- P4 最適化とコード生成を実装・検証（2026-09-27）。プラグインを使わない119ケースすべてで生成物・標準出力・終了コードが Ruby 版と一致 → [[tecsgen-python3内部仕様 - 07 最適化|内部仕様7章]]・[[tecsgen-python3内部仕様 - 08 コード生成|8章]]
- P5 プラグイン機構と標準プラグインを P5a〜P5p まで実装・検証（2026-09-27〜10-01）。正解データのあるプラグインは移植済みで、`-L` による利用者プラグインの探索も P5q で実装済み。プラグインありの全46ケースが一致（as of 2026-10-02、詳細は進捗ログの P5q。2026-10-03 に 63 ケースへ増え、85 本中 83 本を移植済み。[[tecsgen-python3移植計画#P5 プラグイン機構と標準プラグイン|移植計画のP5]]）。カーネル依存系（HRP・FMP・HRMP・HRP2・ATK1Event）は11ケースすべて一致 → [[tecsgen-python3移植計画 — P5 進捗ログ]]・[[tecsgen-python3移植計画#P5 プラグイン機構と標準プラグイン|移植計画のP5]]

## 仕様書

- [[tecsgen-python3外部仕様]] — 外部仕様（CDL入力・生成コード出力・CLI・プラグイン・エラー処理）
- [[tecsgen-python3内部仕様]] — 内部仕様（処理フロー・クラス設計・意味解析・最適化・コード生成の実装）
- [[tecsgen-plugins-python3|tecsgen プラグイン-python3仕様書]]
## Context
- [[reference/03-Resources/my-topic/CLAUDE|TECS Wiki]]
- [[TECS開発]] — 開発進捗全体
- [[tecsgen]]
- [[tecsgen外部仕様]]
- [[tecsgen内部仕様]]
- [[tecsgen-plugins]]
- Python3版最新コード "E:/Ccur/python3/tecsgen-python3-yk"
- Python3版リモートリポジトリ（`origin`、**public**）git@github.com:ykominami/tecsgen-python3-yk.git（2026-10-10 ユーザー決定: 今後はこちらを使う。`upstream` は public の git@github.com:toppers/tecsgen-python3-yk）。旧 `ykominami/tecsgen-python3`（**private**。2026-09-21 作成、2026-09-28 に `ykominami/tecsgen-python` から改名）は、`toppers/tecsgen-python3-yk` が public なのに合わせて public の `-yk` を作ったため退く。**将来削除する予定**（時期未定）。2026-10-10 13:36 JST の PR #15 まではこちらにマージしていた。`-yk` は 2026-10-04 作成の別リポジトリ（id が異なる）で、`origin` の向け直しは 2026-10-10 14:23 JST ごろ。両者の `main` の先頭は 2026-10-10 時点で同じ（`f33713a`）。決定の記録: [[Key Decisions]] 2026-10-10
- [[tecsgen 参照リポジトリ・配布パッケージ一覧]] — Ruby版の最新コード・旧版、WSL上のSVNリポジトリ、展開済み配布パッケージ21件の場所（2026-10-12 に共通部分を切り出し）

## Notes

- 2026-10-01: [[tecsgen 参照リポジトリ・配布パッケージ一覧]]の WSL 展開済み21パッケージは全件 `.cdl` を含むと確認。移植元 Ruby tecsgen r3304 を使い、`E:/Ccur/python3/tecsgen-python3/tests/golden/packages/` に Plugin 正解データ16ケースを採集（ASP3系13・ATK1・Mruby2C・EV3各1）。4系統の再採集で生成物・ログ・Plugin trace がバイト一致し、WSL 検証は903 pass・77 skip。RX 用 `ccrx.exe` 不在と旧 `MrubyBridge-test` の T1007 は `diagnostics/` に分離。全21件の選定理由は `package_inventory.json`、採集手順は同リポジトリの `tools/golden/README.md`。

## Action Items
- [x] [[tecsgen-python3外部仕様]]作成（全10章、2026-10-02）
- [x] [[tecsgen-python3内部仕様]]作成（全12章、2026-10-02）
- [x] tecsgen-python3実装作成（P0〜P6 完了、2026-10-02。プラグインなし119/119・あり77/77 が Ruby 版とバイト一致、as of 2026-10-05）
- [x] Ruby版tecsgenのcmake対応をPython版に反映する（2026-10-05 追加、同日 PR #9 でマージ。C5 は 2026-10-06 に完了。調査と計画: [[tecsgen-python3 cmake対応計画]]）
- [x] `CMake.add_*` を呼ぶプラグインでの一致確認（2026-10-09、合成した利用者プラグインで `gen/` 13ファイルがバイト一致。[[tecsgen-python3 cmake対応計画]] の C3 の結果）
- [x] `CMake.add_*` を、セルタイプ以外の7種類（signature・cell・composite・multi・through・domain・class）のプラグインから呼んで Ruby 版と比べた（2026-10-09）。multi で移植のずれ（`get_plugin` が返すクラスを同じファイルに書くと post_code が出ない）を見つけ、修正し、golden ケース `cmake_add_<種類>` 7件を追加（Python 版 PR #12。[[tecsgen-python3 cmake対応計画]] の「種類ごとの確認」）
- [x] Python 版 PR #12 をマージ（2026-10-09、マージコミット `9c3d635`）。外部仕様 4・6・8章のケース数を 78 から 85 に更新した。SonarCloud の品質ゲートは「新規コードの重複 33.2%（基準 3% 以下）」で失敗のまま（既存のテスト用プラグインを複製した変種ケースが原因）
- [x] SonarCloud の重複の品質ゲート対策として、`.sonarcloud.properties`（`sonar.cpd.exclusions=tests/**,tools/golden/inputs/**`）を追加（2026-10-09、Python 版 PR #13 で `main` にマージ済み、`3c19c86`）
- [x] PR #13 の効果を確認（2026-10-09）。検証用のドラフト PR #14（`tests/user_plugins/` に既存プラグインの完全な複製 168 行だけを追加。マージせずに閉じ、ブランチは削除）で、SonarCloud の「新規コードの重複」は **0.0%**、品質ゲートは通過した（PR #12 は 33.2% で失敗）。公式ドキュメントは「ワイルドカードは使えない」とするが、`sonar.cpd.exclusions=tests/**,tools/golden/inputs/**` は自動解析で効く。SonarCloud の API は非公開設定で認証が要るため、PR のコメントで確認した
- [x] `Asp3Tecs.cmake` の configure 以降（コンパイル・リンク）を確認した（2026-10-09）。NUCLEO-H563ZI の `sample1` を、CubeMX の代わりに ST の公開テンプレートで、tecsgen を Ruby 版・Python 版にして configure からリンクまで通し、最終イメージが SHA-256 まで一致（[[tecsgen-python3 cmake対応計画 — C6 ビルド検証]]）
- [x] ほかの 3 ボードを確認した（2026-10-09）。TECS を使うのは H563ZI と N6570-DK だけで、H533・C562 のサンプルは TECS を使わない（`asp3_add_syssvc`）ため対象外。N6570-DK（FSBL）は CubeMX の代わりに ST の公開テンプレートで、H563ZI と同様に Ruby 版・Python 版で configure からリンクまで通し、最終イメージが SHA-256 まで一致（[[tecsgen-python3 cmake対応計画 — C6 ビルド検証]]）
- [ ] 残り（[[tecsgen-python3移植計画]] P7）: 実機（書込み・起動）の確認、実際の CubeMX 生成物でのビルド、H533・C562 への TECS 展開後の確認（現状は TECS 不使用で対象外のため保留。展開されたら実施。2026-10-19 に表現を整理）（as of 2026-10-09）。（`transparent_marshaler` ケースの扱いは 2026-10-05 に決定済み。[[tecsgen-python3 cmake対応計画#決定事項（2026-10-05、ユーザー決定）|決定6]]、2026-10-19 に表現を整理）
- [ ] 旧 private リポジトリ `ykominami/tecsgen-python3` の削除（2026-10-10 決定、時期未定）。削除前に確認すること: (1) `-yk` の `main`・全ブランチ・タグが旧側と同等かを `git ls-remote` で比べる（`main` の先頭は 2026-10-10 時点で同じ `f33713a`）、(2) 旧側にだけある PR・Issue・Actions のシークレット・SonarCloud 連携・branch protection が無いか、(3) vault・`asp3_stm32cube_TECS`・他リポジトリの文書やスクリプトに旧 URL（`ykominami/tecsgen-python3`）が残っていないか。削除は取り消せないのでユーザーの明示的な指示で行う
- [x] `add_*` の合成ケースを golden ケース `cmake_add` としてリポジトリに固定（2026-10-09、Python 版 PR #11 で `main` にマージ済み、`11f38ef`。プラグインあり 78/78 一致）

## Related
- [[TECS開発]] — TECS WG開発進捗全体
- [[tecsgen]] — Ruby実装版（移植元）
- [[work/active/tecsgen-python3/tecsgen-python3 Mixin粒度決定|tecsgen-python3 Mixin粒度決定]] — Ruby版のクラス再オープンをPython Mixinへ変換する粒度の決定（2026-09-26、proposed）
- [[reference/Ruby動的ロードとPython対応|Ruby動的ロードとPython対応]] — Rubyのrequire/load/evalに対応するPythonの動的ロード手段リファレンス（プラグイン機構実装時に参照）
- [[reference/Racc代替のPythonパーサジェネレータ比較|Racc代替のPythonパーサジェネレータ比較]] — tree-sitterのPython利用がDLL運用前提で複雑になりうるため、DLL不要な代替（Lark/SLY等）を調査中
- [[reference/Ruby Mixinとpython多重継承対応|Ruby Mixinとpython多重継承対応]] — Ruby版`module`/`include`をPython多重継承＋MROへ移植する際のリファレンス
- [[reference/Pythonのグローバル変数の使い方|Pythonのグローバル変数の使い方]] — Ruby版の`$`グローバル変数（[[reference/tecsgen_ruby_global_variables.csv|実測CSV]]）をPython側でどう扱うかの検討材料
- [[reference/tecsgen動的typedef判定とPythonパーサ選定|tecsgen動的typedef判定とPythonパーサ選定]] — Ruby版字句解析の動的typedef判定機構がtree-sitter/Lark/SLYで再現できるかの検討（DLL回避との論点衝突あり）
- [[reference/Rubyとpythonのカレントディレクトリ変更の影響|Rubyとpythonのカレントディレクトリ変更の影響]] — chdirの影響比較。相対パス解決の設計原則
- [[reference/Rubyトップレベルメソッドとpython対応|Rubyトップレベルメソッドとpython対応]] — Ruby版の23トップレベルメソッド（実測CSV）をPythonのモジュール関数として移植する際の対応
- [[reference/Rubyネストクラスとpython対応|Rubyネストクラスとpython対応]] — Rubyのネストクラス（レキシカル定数探索）とPythonの名前空間化の違い
- [[reference/Rubyクラス再オープンとpython対応|Rubyクラス再オープンとpython対応]] — 複数ファイルにまたがるclass定義（再オープン）の挙動差とPython側のMixin代替。実測により`Namespace`（7ファイル）等コアクラス全般で広範に使用されていることを確認（[[reference/tecsgen_ruby_class_reopen.csv|CSV]]）——移植時にMixin設計への変換が必須になる可能性が高い
