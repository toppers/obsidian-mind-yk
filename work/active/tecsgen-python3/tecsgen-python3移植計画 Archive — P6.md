---
date: 2026-10-05
description: "tecsgen-python3移植計画のうち完了済みフェーズP6（仕上げ: 配布・CLI・tecsmerge・実プロジェクトの差分テスト・仕様書の完成）の詳細をverbatim分離したアーカイブ。25KB閾値による分割"
project: tecsgen-python3
status: tracking
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3移植計画 Archive — P6

[[tecsgen-python3移植計画]] の P6 の節を、25KB 閾値のため verbatim で分離したもの（2026-10-05）。P0〜P2 は [[tecsgen-python3移植計画 Archive — P0–P2]]、P3・P4 は [[tecsgen-python3移植計画 Archive — P3–P4]]。

### P6 仕上げ

- CLI 全オプション、`tecsmerge`、ドキュメント、配布（`uv tool install` 等）
- 実プロジェクト（ASP3/HRP3 の MANIFEST）で差分テストを行う
- [[tecsgen-python3外部仕様]]・[[tecsgen-python3内部仕様]] を完成させる

**進捗（as of 2026-10-02）**: Python リポジトリの PR #4（ブランチ `p6a-bundle-tecs-library`、3コミット）を `main` にマージ済み（マージコミット `cf0931b`、2026-10-02）。Windows 983 passed / 72 skipped、WSL 978 passed / 77 skipped、`ruff`・`ty` とも通過。
- **P6a 配布**（`e25531f`）: `cli.py` が参照する `{PACKAGE_DIR}/tecs`（標準 CDL ライブラリ）が `src/tecsgen/` に無く、wheel に入っていなかった。記録再生のテストでは検出できない欠落だった。Ruby 版の `tecs/`（102ファイル）を `src/tecsgen/tecs/` に同梱（`.gitattributes` で改行変換なし）。wheel を別の仮想環境へ入れて `tecsgen` を実行し、Ruby 版と出力が一致することを確認。README に利用者向けインストール、`CHANGELOG.md` を追加
- **P6b CLI**（`4156508`）: `--help`（標準出力）・`--version`（標準エラー出力）は Ruby 版とバイト一致と判明。差は `-v` の Ruby バージョン行と「`sMalloc.cdl is found in`」のインストール先パスだけで、意図した差。`tests/golden/cases/cli/` に正解を置いてテスト化
- **P6d tecsmerge**（`34bb681`）: `src/tecsgen/tecsmerge.py` と `tecsmerge` コマンド。正解データは `tools/golden/collect_tecsmerge.py`（`wsl_check.ps1 -TecsmergeGolden`）で WSL の Ruby 版から採取（73シナリオ: マージ・old mode・新規コピー・`-e`・受け口／関数の改名・削除・キーワード欠落・引数エラー）。標準出力・終了コード・実行後のファイル一式が一致。Ruby 版が例外で落ちる場面（`-f` を `-p` より前に書く、キーワード欠落時の `nil[0]`）も、メッセージ先頭の行と終了コード 1 まで再現
- **P6c 実プロジェクトの差分テスト（2026-10-02 閉じた）**: `tests/golden/kernel/`（HRP3・FMP3 ほか11ケース）は生成物・標準出力・終了コードが一致済み、`tests/golden/packages/`（ASP3 sample1 13件ほか16ケース）は正解データを採取済み。`MANIFEST_for_asp3`・`MANIFEST_for_hrp3` は配布ファイルの一覧（tecsgen の入力ではない）で、これを単位にした通し実行は新しい検証にならないため行わない。配布パッケージの再生比較（P3 記録の採取）は、必要になったときに別途判断する
- **P6e 仕様書の完成（2026-10-02）**: 外部仕様の全10章を章別ノートとして執筆（[[tecsgen-python3外部仕様]]）。内部仕様の1〜3章を執筆し、全12章がそろった（[[tecsgen-python3内部仕様]]）。TBC のうち、`--help`・`-v`・`TOOL_INFO`（4章）、非 ASCII のバイト単位字句解析（10章）、`celltypePlugin` の終了コード（11章）、`sprintf`（12章）を解消。残りの TBC は `-k euc`・`cp932` と Ruby の Shift_JIS の差（10章）、macOS の動作（外部仕様 2章）（**2026-10-03 訂正**: 残りはこの2件だけではない。全体は P6 完了の項を参照）。外部仕様には Python 版固有の事実（未移植プラグイン18本、`RUBYLIB` 非対応、`tecsgen.rbdmp` を書かない）を明記した（**2026-10-03 訂正**: 「18本」は数え間違いで、未移植は 85 本中 2 本。外部仕様は訂正済み）
- **P6 完了（2026-10-02）**: P6a〜P6e をすべて完了し、`main` にマージ済み。残る作業は、未移植プラグイン（2026-10-03 に 85 本中 83 本を移植済み。残る `HRP2Cache`・`HRP2PostHook` は動かす経路が無く対象外）が無くなったので、未解消の TBC の解消（as of 2026-10-03、`work/active/tecsgen-python3/` を `TBC` で全文検索した結果）。主なもの:
  - 残っている TBC（2026-10-04 の時点で、`work/active/tecsgen-python3/` を `TBC` で全文検索して確認）: なし。最後に残っていた macOS の動作は、2026-10-04 に GitHub Actions（`macos-latest`、macOS 26.6.2・arm64）で、`uv sync`・`tecsgen --version`・pytest（1020 件成功・83 件スキップ）が通ることを確認して解消した（使い捨てブランチで1回だけ実行し、ブランチは削除した。CI としては残していない）
  - **`-k` の差異をなくした（2026-10-04）**: 2026-10-03 に Ruby 3.2.3 との比較で見つけた3つの差異（`-k euc` で標準付属プラグインの日本語コメントが UTF-8 のまま混ざる、`-k sjis` で Shift_JIS に無い文字が `H1001`、`-k sjis` で Windows-31J として不正なバイト列が `G1014`／`B1002`）を、Python 版リポジトリのブランチ `ykominami/fix-kcode-differences`（コミット `d062f91`、未プッシュ。**2026-10-05 注記**: その後 PR #8 で `main` へ取り込み済み）で直した。最小の CDL（`-k none`・`utf8`・`euc`・`sjis`）、`test/opaqueRPC`（`-k euc`・`utf8`）、`ThroughPlugin` 経由の日本語リテラル（4通り）、不正バイト列4種を Ruby 版とバイト比較して一致を確認した。詳細は [[tecsgen-python3内部仕様 - 10 ファイル入出力]]
  - 解消済み（2026-10-03）: `-k euc`・`cp932` と Ruby の Shift_JIS の差（差異を確認して上の項のとおり解消）、`-k sjis` のときのプラグインの日本語リテラルの出力、Windows-31J の `\w`（Ruby 3.2.3・4.0.6 とも全角に当たらない。`re.ASCII` と一致）、読み込み失敗時の例外メッセージの書式、`$library_path` 先頭との一致と組み込み優先の探索順、`gen_plugin_decl_code` のキャッシュの不一致（`Plugin1.rb` が原因で P5q で一致）、プラグイン内 `eval`（Ruby 版に呼び出しが無かった。「24ファイル」は誤り）、「差異が出る見込み」の節、グローバル変数の数（110種・808箇所、特殊変数なし）、mixin 内の `@@`・モジュールメソッド、合成クラスの組み立て箇所と MRO、`Token` の Symbol と String、`--help`・`-v`、`HRP2KernelObjectPlugin` の再オープン（Ruby 版でも無効なコード）、プラグインからの設定オブジェクトの参照方法、`celltypePlugin` の終了コード、`RUBYLIB`


## Related

- [[tecsgen-python3移植計画]] — 本体
- [[tecsgen-python3移植計画 Archive — P3–P4]] — 完了済みフェーズ P3・P4
- [[tecsgen-python3移植計画 Archive — P0–P2]] — 完了済みフェーズ P0〜P2
- [[tecsgen-python3]]
