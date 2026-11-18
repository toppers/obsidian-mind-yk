---
date: 2026-11-16
description: "V0.2.5 三者相違一覧の分野8（CDL連携・tecsgen）のうち、表以外の節（参考・未確認・解消済み・集計）。25KB閾値で表と分けた。原文のまま。"
project: TECS
quarter: Q4-2026
status: active
verbatim: true
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

# TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16 — 分野8 補足

[[TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16]]の分割ノート（分野8 CDL連携・tecsgenの補足）。原文のまま。相違の表は[[TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16 — 分野8]]。

### 未確認（相違として断定しないもの）

- **`.tecsgen-opts` の `-c` の値の引用符**: `src/main/file-service.ts:350-355,391-400` は opts を空白だけで分割する（引用符を解釈しない）ため、`-c "gcc -E -DTECSGEN"` のような値は Generate では `"gcc` と `-DTECSGEN"`（`-D` の値として）に割れる。一方 Plugin生成型の取り込みは `src/main/tecsgen-runner.ts:264-268` の `splitCommand`（引用符を解釈する）で opts を読む。opts の字句規則は 05A 5.3（diff-05 の範囲）で、同梱サンプルに `-c` が無いため、相違かどうかを判断していない。
- **アプリ自身のCプリプロセスに `-D` を渡さない**: `src/main/tecsgen-runner.ts:340-342` は、基本コマンド（`cppArgs` 等）と `-I` だけを渡し、`__tool_info__` の `define_macro`・opts の `-D` は渡さない。外部 V0.2.1 2.3 は「基本コマンドラインに `-I` を末尾に追加」とだけ述べ、`-D` を定めない。外部 08 8.1 の「現行版と同じ経路」が tecsgen 本体の cpp 起動（`-D` を渡すか）まで含むかは確かめていない。
- **opts を経由しない Generate の作業ディレクトリ**: `src/renderer/app/tecsgen-actions.ts:42` は opts が無いと `cwd` を渡さず、`src/main/tecsgen-runner.ts:182` はアプリの起動ディレクトリで tecsgen を起動する。tecsgen の既定の出力先（`gen`）がそこに作られる見込み（inferred）だが、外部 08 8.4.2 は出力先・作業ディレクトリを定めていない（opts のときだけ 05A 5.3 が定める）。
- **stderr の抜粋の作り方**: 外部 V0.2.1 2.1「先頭の有効行を中心に最大 200 文字程度」に対し、`src/main/tecsgen-runner.ts:138-147` は空行を除く全行を空白で連結して先頭 200 文字にする。「中心に」の解釈の範囲内とも読めるため判断を保留する。
- **内部処理の Worker の文法アセット**: `src/renderer/app/file-actions.ts:125-130` で `loadGrammarAssets` が失敗すると、Worker（`src/renderer/tecsgen/internal/worker.ts:102-104`）は既定の `/wasm/...` URL で初期化を試みる。内部仕様の索引 #7（`file://` の fetch は CORS で塞がれる）から失敗すると見込まれる（inferred）が、失敗は `W-PLUGIN-TYPE-LOAD` になり仕様の範囲内のため、相違とはしない。
- **Generate の上限（30秒・既定 `maxBuffer`）**: 差分一覧 #3 の残り。内部 09 9.7 の警告欄 2 で「変更しない」と決定済みで、外部仕様は数値を定めない。実測は未了のまま。

### 過去の監査で指摘され、V0.2.5 で解消を確認した項目（表に含めない）

計4件（diff-01 が数えた差分一覧 A#3・A#7・C、三者監査 #60〜#62 は除く）: 外部仕様と内部仕様・実装の差分一覧 #9（`.tecsgen-opts` の `-c`・`-D` の tecsgen への引き継ぎ。`src/renderer/app/tecsgen-actions.ts:45-47`）、同ノート「残る差」の `-I`／`-S` の記述順の引き継ぎと Generate の `cwd`（`tecsgen-actions.ts:42-45`、`src/main/file-service.ts:375-390`）、同 Plugin生成型の取り込みと `W-PLUGIN-TYPE-LOAD` の外部仕様化（外部 08 8.1・09 9.4）、同 opts 経由の取り込みで `-k utf8` が付かない経路（`src/main/tecsgen-runner.ts:114-117,270-275`）。ほかに 09B差分 #14（`CdeclExtractor.extract` の `tree.delete()`、`src/renderer/cdecl/extractor.ts:52-54`）と 4H 4B.10 の6件は、内部仕様自身が解消済みと記し、ソースでも確認した（過去監査の番号体系の外のため件数に含めない）。

### 集計

- 表の件数: 20件
- 種別（重複計上）: A 8件（#3・#6・#8・#9・#11・#13・#14・#20）、B 12件（#2〜#7・#10〜#14・#20）、C 13件（#1〜#5・#10〜#12・#15〜#19）
- 状態: 新規 19件、既知・未解消 1件（#12＝三者監査#50）、仕様が未実装・延期と明記 0件

