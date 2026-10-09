---
date: 2026-09-15
description: "tecsgen内部仕様12章のうち、ソースとの突き合わせが未了・未確証のまま残っている箇所を横断的に列挙した一覧ノート。2026-09-15、第8章8.1/8.3/8.4/8.5・第9章9.7既知の問題3件（表裏一体の第3章項目含む）を検証・解消、残り2件（MultiPlugin設計理由・エラーコード由来）は未検証のまま。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen内部仕様 - 要再検証項目一覧

[[work/active/tecsgen/tecsgen内部仕様|tecsgen内部仕様]]の各章本文中に「未検証」「未確認」「推測」等のマーカー付きで残っている箇所を横断的に集約した一覧。2026-08-22〜23の全12章検証パスの副産物で、そのとき手が回らなかった／確証が得られなかった項目。

## Context

2026-08-22〜23、[[work/active/tecs/TECS開発|TECS開発]]セッションで tecsgen ソース（`E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen`）を直接読んで全12章を検証・訂正した。大半は訂正して確定させたが、以下6件は根拠不足・時間切れ・実行時確認手段の欠如により未確定のまま `(未検証)` 等のマーカーを残した。2026-09-15時点でソース側に新規コミットは無い（SVN r3302のまま変更なし）ため、この一覧は現在も有効。**2026-09-15、項目1・3・4・5を解消**（下記参照、残り2件）。

## 解消済み項目

### ~~1. 第3章 処理フロー — `generate_post`の8章側との整合~~（2026-09-15解消）
項目3（8.1/8.3/8.5）の検証完了に伴い解消。[[work/active/tecsgen/tecsgen内部仕様 - 03 処理フロー|第3章]]の`root_namespace.generate_post`の記述を検証済みとして更新済み。

### ~~3. 第8章 コード生成 — 8.1/8.3/8.5節が旧内容のまま~~（2026-09-15解消）
`generate.rb`の`Namespace#generate`・`Celltype#generate_private_header`/`generate_private_header_post`・`generate_celltype_factory_code`/`generate_cell_factory_code`、および`DomainPlugin.rb`・`HRPPlugin.rb`・`HRMPDomainPlugin.rb`・`tTINETChannel.cdl`を直接読んで検証・訂正。

- **8.1**: 実態と一致、訂正なし
- **8.3**: 旧版は単一フェーズ9ステップとしていたが、実際は「本体（`generate_private_header`）」と「後処理（`generate_private_header_post`）」の二段階構成。省略されていた中間ステップ（INIB代替マクロ・IDX型定義・呼び口/受け口数マクロ・オプション呼び口未結合テスト・受け口スケルトンプロトタイプ・ディスクリプタ参照/設定関数・CB初期化マクロ・dealloc用コード）を補完し、「属性・変数アクセスマクロの短縮形・通常形」が実際には隣接せず離れた位置にあることを訂正
- **8.5**: 「`tecsgen.cfg`の生成」という単一機構ではなく、CDLの`FACTORY{}`/`factory{}`宣言による**宣言的生成**（`Celltype#generate`から呼ばれる、ファイル名はCDL側が自由指定——慣習で`tecsgen.cfg`という名前を選んでいるだけ）と、プラグイン自身のRubyコード（`HRPPlugin`等の`gen_factory`override）による**命令的生成**（`Namespace#generate`末尾のプラグインディスパッチから呼ばれる）という、呼び出し元も設計思想も異なる2つの独立経路が同名慣習ファイルに収束していただけと判明

これで8章全節の検証パスが一巡した。詳細: [[work/active/tecsgen/tecsgen内部仕様 - 08 コード生成|第8章]]

### ~~4. 第8章 コード生成 — プレースホルダの詳細な対応関係~~（2026-09-15解消）
`generate.rb`の`subst_name`（5234-5276行）・`get_name_array`（3866-3922行）を直接読んで確定。11種類のプレースホルダ（`$ct$`/`$ct_global$`/`$cell$`/`$cell_global$`/`$cb$`/`$cbp$`/`$cb_proto$`/`$id$`/`$ID$`/`$idx$`/`$$`）の展開内容を表にまとめ、旧版の`$id$`＝「セル名」という説明が誤り（正しくは`"<ct>_<cell_global>"`の合成文字列）だったことを訂正。さらに`FACTORY{}`（セルタイプ単位）と`factory{}`（セル単位）で使えるプレースホルダの種類が異なる（前者は`$ct$`/`$ct_global$`/`$$`の3種のみ）ことも判明。詳細: [[work/active/tecsgen/tecsgen内部仕様 - 08 コード生成#8.4 `_factory.h` の生成|8.4節]]

### ~~5. 第9章 プラグイン機構 — 9.7 既知の問題（3件、実行時未再現）~~（2026-09-15解消）
`pluginModule.rb`・`signature.rb`・`join.rb`・`FMPPlugin.rb`・`CppIfGenCelltypePlugin.rb`を直接読んで、3件それぞれの呼び出し元・エラー処理経路まで追跡（実際にtecsgenを実行してのブラックボックス再現ではないが、コードパスを最後まで辿ったことで結果は一意に定まる）:

- **9.7.1** `TransparentRPCSignaturePlugin`参照切れ: `load_plugin`が`require_tecsgen_lib`失敗→`cdl_error("P2001 ...")`→`nil`を返し、呼び出し元`Signature#apply_plugin`が`return if plClass == nil`で安全に処理。**クラッシュではなく、コード生成ゲート（11章）に引っかかる「クリーンだが確実な失敗」**と判明。**2026-09-26、実行して確認済み**（`test/` の `class`・`rpc`・`DataPumpHolder` が P2001 で終了コード1。詳細は [[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構|9章 9.7.1]]）
- **9.7.2** FMPのRPC死コード: 呼び出し元（`join.rb`）は戻り値が`nil`なら結合を拒否するが`[]`（空配列）は「結合許可・追加プラグイン不要」と解釈される。`FMPPlugin#add_through_plugin`は全分岐で`[]`を返しており`nil`を返す分岐が無い——**RPC仲介が必要な条件でもエラー無く直接呼出しとして黙って結合を許可する、9.7.1より深刻なサイレント欠陥**と判明
- **9.7.3** CppIfGenの二重無効化コード: 定義側・undef側の対（110-118行・124-130行）が同じ二重無効化パターン（Ruby`dummy`代入＋C`#if 0`）で揃っている構造を確認。単発の消し忘れでは説明しにくく、意図的無効化説を補強（ただし明示的記録は無く「なぜ」は依然未確定）

加えて同章9.5節、[[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]]のCDL付与位置（celltype/cellの2種類のみ）は`CIfGenPlugin.get_plugin`とコメント文言・分岐構造が一字一句同一（`$Id: MultiPlugin.rb...`という複製元由来の文字列まで残存）と直接比較で確認——「推測」から確定情報に格上げ。

詳細: [[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構#9.7 既知の問題（プラグイン仕様書調査で発見）|第9章9.7節]]

## 未検証項目

### 2. [[work/active/tecsgen/tecsgen内部仕様 - 04 クラス設計|第4章 クラス設計]] — `MultiPlugin`が`Plugin`を継承しない理由
`MultiPlugin < Node`であり`Plugin`の子ではない設計になっている。素直に`Plugin`の下に置いてディスパッチメソッドを1つ追加する設計も可能だったはずだが、実際には別系統の基底クラスとして実装されている。**理由がソースから読み取れず未検証**（設計判断の経緯・コミットログ等の追加調査が必要）。

### 6. [[work/active/tecsgen/tecsgen内部仕様 - 11 エラー・警告処理|第11章 エラー・警告処理]] — エラーコードプレフィックスの発生源対応表
プレフィックス文字（S/G/W/T/E/I/P/B/H/C/V）と発生源モジュールの対応表は、全`.rb`ファイルへの出現頻度からの推定に基づく。**文字の由来自体（なぜその文字が選ばれたか）は未確認**。

## 優先度メモ

- **低**: 項目2・6 — 設計意図・命名由来の調査で、実装の正しさそのものには影響しない。
- 項目5の9.7.2（FMPのサイレント欠陥）は実装バグとして修正候補になりうるが、それは「再検証」の範囲外（本一覧はドキュメント精度の追跡が目的）。

## Action Items
- [x] 8.1/8.3/8.5節を`generate.rb`で再検証（2026-09-15）
- [x] プレースホルダ（`$ct$`/`$cb$`/`$idx$`等）の展開ルールを`generate.rb`で確認（2026-09-15）
- [x] 9.7の3件を呼び出し元・エラー処理経路まで追跡（2026-09-15、実機実行によるブラックボックス再現ではなくコードパス追跡）

## Related
- [[work/active/tecsgen/tecsgen内部仕様|tecsgen内部仕様]]
- [[work/active/tecsgen/tecsgen内部仕様 - 03 処理フロー|3. 処理フロー]]
- [[work/active/tecsgen/tecsgen内部仕様 - 04 クラス設計|4. クラス設計]]
- [[work/active/tecsgen/tecsgen内部仕様 - 08 コード生成|8. コード生成]]
- [[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構|9. プラグイン機構]]
- [[work/active/tecsgen/tecsgen内部仕様 - 11 エラー・警告処理|11. エラー・警告処理]]
- [[work/active/tecs/TECS開発|TECS開発]]
