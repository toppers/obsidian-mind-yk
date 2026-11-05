---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第11章（未決事項と実装単位案）— 外部仕様由来の未決事項に加え、Rust/Tauri固有の未決事項（wasm-bindgenのバインディング整備状況・im crateの採否等）と本書の採否を整理。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 11 of 11（本書の最終章）。

## 11. 未決事項と実装単位案

### 11.1 未決事項（外部仕様由来、既存内部仕様と共通）

複合セルタイプの表現方法・OSクリップボード連携の詳細仕様・図全体の自動レイアウトは、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 11 未決事項と実装単位案|TECSCDE-TS内部仕様11.1節]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様11.1節]]と同一であり、実装言語・フレームワークとは無関係に残る。

### 11.2 Rust/Tauri固有の未決事項

| # | 事項 | 現状 |
|---|---|---|
| 1 | フロントエンドを完全にRustにする決定の妥当性 | [[TECSCDE-DT-TA内部仕様]]（本書）は`web-sys`によるDOM/SVG直接操作を採用したが、これは筆者（本書執筆時点）の判断であり、HTML/JS/TSフロントエンド＋Rustバックエンドという、より一般的なTauriの構成も選択肢として残る。採否は未決（第1章1.3節参照） |
| 2 | `tauri-sys`クレートの成熟度 | `invoke`のRustラッパーとして`tauri-sys`を用いる設計としたが、これは非公式のコミュニティクレートであり、Tauri本体のバージョンアップへの追随状況は実装時に確認が必要（unverified） |
| 3 | `im`クレート（永続データ構造）の採否 | 第3章3.2節で言及したとおり、`TecscdeDocument`の内部表現に`im::HashMap`を使うか、素朴な`std::collections::HashMap`のクローンで済ませるかは、性能検証を経てから決定する |
| 4 | `wasm32-unknown-unknown`ターゲットでのデバッグ体験 | Rust/WASMのデバッグ（ブレークポイント・ステップ実行）はTypeScript/Electronほど成熟していない（`console_error_panic_hook`・`wasm-bindgen`のソースマップ対応に依存）。実装時の生産性への影響は未検証 |
| 6 | tree-sitterバインディングの選択 | **2026-09-13追加**（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計\|TECSCDE内部仕様第4章]]の改訂に伴う本書固有の選択）。tree-sitterはRustが第一級の言語であり、**本書は他の3書と異なり公式の`tree-sitter`クレートを直接使える**。選択肢は①frontend（`wasm32-unknown-unknown`）で文法をWASMとして読む②backendで`tree-sitter`クレートを使い、解析結果をinvoke経由でfrontendへ渡す。②はモジュールBの配置（第2章2.2節「frontend」）を変えることになるが、**A・I以外はbackend不要という本書の配置原則に対する唯一の反例候補**であり、Rust版に固有の判断として残す。文法パッケージ側は`bindings/`にRustバインディングを同梱しているか未確認(TBC) |
| 5 | 配布・自動更新・コード署名 | [[TECSCDE-DT外部仕様]]同様、範囲外とする。Tauri固有の実現手段（`tauri-plugin-updater`等）の選定は実装時の課題として残る。コード署名自体の仕組み（Authenticode・OV/EV証明書等、Electron版と共通）は[[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]]、Electron版で比較したパッケージング・自動更新ツールは[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]参照（Tauriのエコシステムは別、`tauri-plugin-updater`等） |

### 11.3 Electron版との対比（参考）

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様11.3節]]がElectronの利点（WebViewバンドルによるOS差異の不在）とトレードオフ（配布サイズ）を記していたのに対し、Tauri（本書）は逆のトレードオフを持つ——**OSネイティブWebViewを利用するため配布サイズは小さく抑えられる**が、**WebView実装がOSごとに異なる**（第1章、[[TECSCDE-DT外部仕様]]第2章2.4節）という、本書がまだ解消していないリスクを抱える。どちらを選ぶかは本仕様群の範囲外の判断であり、両文書は判断材料としてのみ機能する。

### 11.4 最初の実装単位の提案

[[TECSCDE-TS内部仕様]]11.3節・[[TECSCDE-DT-EL内部仕様]]11.4節の提案（モデル＋CDLパーサ／シリアライザのround trip）を土台としつつ、本書固有の検証観点を追加する。

1. **モデル＋CDLパーサのround trip**（frontendのみで完結、backendへの依存なし）——外部との唯一の契約点を最初に固める。
2. **`wasm32-unknown-unknown`ターゲットでのビルド・実行を最初に確認する。** 標準的なRustのテスト（`cargo test`）はネイティブターゲットで実行されるため、モデル層のロジック自体は通常のRustプロジェクトと同じ手順で検証できるが、`web-sys`を使う描画層（第5章）は実際にWASMとしてビルドし、WebView上での動作を確認する必要がある。これは[[TECSCDE-TS内部仕様]]にはなかった検証観点である。
3. **`invoke`の疎通確認を、UIの実装より先に行う。** `FileGateway::open()`→`file_open` command→`invoke`→frontendでの受信、という一往復が正しく動作することを確認する（[[TECSCDE-DT-EL内部仕様]]11.4節#2と同じ位置付けの検証、Tauri版としての実現）。
4. 次点として`History`のUndo/Redoをヘッドレスでテストする単位（[[TECSCDE-TS内部仕様]]11.3節と同一の優先順位、これはネイティブターゲットの`cargo test`で完結できる）。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 11 未決事項と実装単位案|TECSCDE-TS内部仕様 第11章（外部仕様由来の未決事項の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（Electron版、対比対象）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]
