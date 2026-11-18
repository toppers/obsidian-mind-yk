---
date: 2026-11-16
description: "V0.2.5 三者相違一覧の分野5（開く（読み込み））のうち、表以外の節（参考・未確認・解消済み・集計）。25KB閾値で表と分けた。原文のまま。"
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

# TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16 — 分野5 補足

[[TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16]]の分割ノート（分野5 開く（読み込み）の補足）。原文のまま。相違の表は[[TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16 — 分野5]]。

### 未確認（相違として断定しないもの）

- **`_CDL_FILES.txt`に載っていない候補の扱いと読込不能**: `src/main/cdl-file-list.ts:70-73`は一覧の読込失敗（アクセス拒否を含む）をすべて「一覧なし」として通常探索へ戻す。外部05Aの「一覧が無いとき、読めないとき」と一致する。一覧が非UTF-8の場合に`buf.toString("utf8")`で読む（`:71`）ことは、05Aの「UTF-8（BOM可）」の範囲外の入力であり、相違とはしない。
- **`baseDir`が相対値の場合の基点**: `src/main/file-service.ts:261-265,287`は`__tool_info__`の`base_dir`をそのまま探索の起点にし、相対値ならmainプロセスのcwd基点で解決される。7D 7.5.2は「永続化された単一値」とだけ述べ、相対値の基点を定めていないため相違とはしない。
- **optsの値が次のオプションのとき**: `src/main/file-service.ts:365-370`等は`-I -S dir`のように値の位置に別のオプションが来ても値として取り込む。外部05A・7C 7.7.4は「末尾に値の無い`-I`・`-c`」だけを定めるため相違とはしない。
- **`import`未解決の警告の重複**: 同じ指定を複数のファイルがimportして解決できないと、`src/renderer/app/import-resolution.ts:190`は同じ警告を件数分出す。仕様は重複の扱いを定めていない。
- **起動時の`open-file`の到着時機（macOS）**: `ready`より後・`did-finish-load`より後に届いた`open-file`は#1のとおり消費されないが、起動直後の受信順は実機（macOS）で確認していない。
- **Plugin生成型の取り込みの時機**: 外部08 8.1「主ファイルを開くたび」。`src/renderer/app/file-actions.ts:118-122`は主ファイルのパスが空（主なしのセッション復元）だと取り込まない。「主ファイルを開く」に当たらないとも読めるため相違とはしない（tecsgen連携の詳細はdiff-01の範囲）。
- **リージョン所属の復元**: `src/renderer/cdl/document-builder.ts:299-321,666-679`は、定義元の`tecscde`ブロック→最後のブロックの順に所属を読み、編集可能ソースのセルは編集可能ファイルのリージョン、それ以外は全ファイルのリージョンへ復元し、食い違えば`W-REGION-MISMATCH`を出す。05A 5.3の規定と読み比べて相違は見つけていないが、「CDLのルート直下に書かれている場合に限り」の条件（`decl.regionPath !== "::"`のとき復元しない）以外の境界は試していない。

### 過去の監査で指摘され、V0.2.5で解消済みと確認できた項目（表に含めない）

計8件: 三者監査 #6（読込要求の世代・文書世代・revisionの照合。`src/renderer/app/store.ts:266-278`、`file-actions.ts`の各await後の`canApplyLoad`）、#10（拡張子判定の大小文字非区別を共有関数へ集約。`src/shared/file-kind.ts:2-6`を`src/main/index.ts:54-56,142`、`src/main/file-service.ts:27`、`src/renderer/app/file-browser-panel.ts:52`が使う）、#11（`-S`配下の`_CDL_FILES.txt`探索。`src/main/cdl-file-list.ts:52-91`、`src/main/file-service.ts:266-302`）、#12（絶対の`-I`・`-S`を基点へ連結しない。`src/main/file-service.ts:287`。ただし追加時の相対値は表#5）、#13（basenameだけの既読判定の廃止。`src/renderer/app/import-resolution.ts:153-171`）、#17（主ファイル未確定時のCtrl+クリック追加の許可。`src/renderer/app/file-actions.ts:319-421`。ただし未解決import時の中止は表#4）、#18（CDLファイル一覧生成の計画・確認・適用。`src/main/cdl-file-list.ts:166-269`、`src/main/ipc.ts:64-72`、`src/renderer/app/cdl-file-list-view.ts`）、差分一覧（2026-10-21）#11（`.tecsgen-opts`の拡張子の大小文字の不統一。現行仕様の非区別に統一）。三者監査#5は結果の役割・順序は一致するが、API形の残差があるため表#2に残した。

