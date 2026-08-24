---
date:
description: "Living document of goals, focus areas, and aspirations — read at session start, updated when direction shifts"
tags:
  - brain
  - north-star
aliases:
  - Goals
  - Focus
---

# North Star — Yasuo Kominami

A living document of goals, aspirations, and current focus areas. Both you and Claude write to this. Claude reads it at the start of meaningful work sessions and references it when making suggestions.

## Current Focus

_What am I working toward right now?_
### TOPPERSプロジェクトの[[TECS開発]]（TECS WG関連）

#### 🔴 最優先: TECSCDE JavaScript版の内部仕様・実装への移行

- [[TECSCDE外部仕様]]は全11章完成（2026-08-13）。第6章分割後も原文141,227 bytesとの完全一致、heading link、孤立ノート、oversized flagを検証済み。
- [[TECSCDE内部仕様]]の章構成（全12章）と責務境界（9モジュール：ファイルI/O・CDLパーサ/シリアライザ・モデル・編集コマンド・描画・表示制御・UIシェル・診断・tecsgen連携）を定義（2026-08-21）。依存方向図と境界設計判断まで記述済み。次の成果物は最初の実装単位への落とし込み。
- 外部仕様の追加整理やVault整備は、内部仕様・実装を直接前進させる場合だけ優先します。

#### [[tecsgen]]

- [[tecsgen|外部仕様]]と[[tecsgen-plugins|プラグイン仕様]]は、SVN trunk r3301の全85ファイルまで追随済み。[[work/active/tecsgen-plugins/PluginCoverageAudit|カバレッジ監査]]で既知対象を確認済みです。
- [[tecsgen内部仕様|内部仕様]]は、CType・MultiPluginディスパッチの統合（2026-08-15）に続き、4章クラス階層図の`MultiPlugin`欠落を修正し、9章に「既知の問題」節を新設して実装上の既知リスク3件（TransparentRPCSignaturePlugin参照切れ・FMPのRPC死コード・CppIfGenの二重無効化コード）を記録しました（2026-08-21）。2026-08-22、残っていた5・6・8・10〜12章をすべてソース照合し、set_require_joinの役割誤認（未結合エラー検出ではなくrequire節の自動結合生成）や存在しない変数`$KCODE_CDL`など複数の実質的な誤りを訂正。**2026-08-23、最後まで未検証だった1-3章も再照合**：1章の対象バージョン記載（1.9.0→実測1.9.1）、2章のファイル配置誤り3件（`tecs_lang.rb`の役割誤認・`namespacepath.rb`の配置先・`componentobj/generate.rb`の記載漏れ）、3章の処理フロー図の誤り（`set_require_join`の所属フェーズと役割・`check_join`のシグニチャ一致誤記・`optimize_and_generate`の条件付け誤り・`generate_post`の欠落）を訂正し、**全12章の個別検証パスが完了**しました。
- 次のステップは実装への着手——TECSCDE内部仕様の最初の実装単位への落とし込みが唯一の優先項目です。
- ソース更新または実装上の必要がない限り、新規プラグイン仕様の探索は最優先にしません。

### AIツールチェーンコスト最適化
- トークン削減（RTK — Rust Token Killer）
- コンテキスト圧縮（headroom MCP — compress/retrieve/status）
- セッション横断記憶（agentmemory — Docker + iii-engine + Node.js）
- Claude Code コスト運用（モデル選択・CLAUDE.md設計・作業プロセス最適化）
### obsidian-pluginの活用
#### Cobsidian-tagfolder + tag-wrangler を導入した目的のタグ整理をいつかやる

## Goals

### Short-term (This Quarter)

- [ ] [[TECSCDE外部仕様]]を入力として、JavaScript版内部仕様の章構成と主要コンポーネントの責務境界を決める
- [ ] 内部仕様の最初の1単位を作成し、対応する実装・テストの入口まで定義する
- [x] tecsgen内部仕様を継続し、CType・MultiPlugin・既知の参照切れを優先して整理する（2026-08-21完了）
- [ ] 週1回以上の執筆セッションをstandupの最優先タスクとして維持する

### Medium-term (This Half)

- TECSCDE JavaScript版（フレームワーク非依存）の内部仕様を完成させ、検証可能な縦切りの実装を1本成立させる
- tecsgen内部仕様へ外部仕様・プラグイン仕様の知見を統合する
- 個人開発システム群のうち2つ（候補: [[notebookmlclix]]・[[ghrepo]]）を「日常運用中」の状態にする

### Long-term (This Year+)

- コンポーネントモデルリファレンスマニュアルをTECS WGで公開状態に持っていく
- TECS向けLSPサーバを実用レベルにする
- vault + wiki + QMD のナレッジ基盤を、維持作業ほぼゼロで回る状態にする

## Aspirations

_What kind of engineer/person am I becoming?_
- TECS WGの主要ドキュメント整備者としての貢献を、公開された仕様書群という形に残す
- 自作ツールチェーン（RTK・スキル・フック構成）を他者が再利用できる形で公開する
## Anti-goals

_What am I explicitly NOT optimizing for?_

- 準備・方法論収集が執筆を押し出すこと — 執筆タスクが1本終わるまで新ツール導入・環境整備をしない（Shifts Log 6/22・6/29・7/20・7/27 で**4回検出**）
  - **ハードゲート（2026-07-27 設定・1週間の試行）→ ✅ 2026-07-29 クリア**: TECSCDE外部仕様 第2章（動作環境）が埋まるまで `/om-vault-audit` と新規ツール導入を行わない、という条件を設定。**2026-07-29 に第2章を執筆して解除**。`/om-vault-audit` を起動した時点でゲート抵触を指摘 → その場で第2章に着手する判断が取られ、監査より執筆を先に通した。ゲートが機能した初めての事例（07-27 深夜は指摘後に抵触作業を実行していた）。
  - **1週間後（2026-08-03）の判定 → 判定前に条件充足・継続**: 第2章が 07-29 に埋まったためゲートは保たれた。TECSCDE外部仕様は最優先のまま継続する。**第3章（画面構成）も同日 07-29 に完成**し、次のゲート条件とした**第4章（コンポーネント図の表現）は 07-31、第5章（ファイル操作）は 08-01 に完成**した。判定日を待たずに条件を2章分先行して満たしている。
  - **降格検討の根拠は失効した（2026-08-01）**: 「06-03 の着手から8週間で1章」という実績を根拠に降格を検討する条件を置いていたが、実績は**07-23 からの10日間で第1〜5章**に変わった。ゲートは4回検出しても止まらなかった再発ループを実際に断っており、目標が実際の意図を反映していないという仮説は否定されたと判断する。以後は降格判定ではなく、**執筆の継続そのものを既定**とする。**第6章（編集操作）は 2026-08-06 に完成**——現行版の未実装2機能（クリップボード操作・グループ操作）を新規要件として規定し、アンドゥのオフバイワン不具合と Redo 恒久無効化という2件の不具合を発見した。次のゲート条件は第7章（表示機能）。
- メモリ/タスクシステムの多重化 — 正は brain/ 一本（2026-07-06 の beads 廃止決定を維持する）
- 「いつかやる」項目を Current Focus に置き続けること — 動かさない項目はここ（Anti-goals の下の判断基準）で切る

## Shifts Log

Record when focus changes, with date and reason.

| Date | Shift | Reason |
|------|-------|--------|
|      | Created North Star | Initial setup |
