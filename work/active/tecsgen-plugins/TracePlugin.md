---
date: 2026-08-14
description: "tecsgen 標準付属プラグイン TracePlugin の仕様書。ThroughPlugin（呼び口結合の間に透過的なセルを挿入する仕組み）の参照実装で、受け口呼び出しの前後を引数値付きでsyslogへ記録するトレースプローブを挿入する"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
  - plugin
---

# TracePlugin 仕様書

> [!info] 文書状態
> [[North Star]] のトレースカテゴリの1件目。もう1件として挙がっていた「TLVTracePlugin」は、リポジトリ全体を検索しても `tecslib/plugin/` にファイルが存在せず、CDL・コメント・ドキュメントのいずれにも1件もヒットしない（`TLVTrace` で全文検索してゼロ件、確認済み）——ATK1Plugin のような「実体が複数ファイル」ではなく、**このリポジトリには実体そのものが存在しない**という別種の食い違いであり、要確認事項として5章に記載する。一次資料は `tecslib/plugin/TracePlugin.rb`（`< ThroughPlugin`）・`tecslib/plugin/ThroughPlugin.rb`（親クラス）・`tecslib/core/bnf.y.rb`（`through` 系5構文の文法定義）・`tecslib/core/componentobj/region.rb`（region境界指定子の登録処理）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 概要

**TracePlugin は、`ThroughPlugin`（呼び口結合の間に透過的なセルを挿入する仕組み）の参照実装であり、挿入したセルを通じて受け口呼び出しの前後を、渡された引数・戻り値・マイクロ秒単位の実行時刻とともに `syslog` へ記録する。** [[work/active/tecsgen-plugins/MrubyBridgePlugin#2. 発見: MultiPlugin ディスパッチ機構|MrubyBridgePlugin 執筆時に整理した `MultiPlugin` ディスパッチ対応表]]の `ThroughPlugin` 行（`join.rb:744`）に対応する、初めて確認できた具体例。

## 2. `ThroughPlugin` の仕組み

`through` 系の指定子で参照されたプラグインは、呼び口の結合先（callee）との間に「透過的なセル」を1つ挿入する。挿入されるセルの構造は `ThroughPlugin#initialize`（`ThroughPlugin.rb` 81〜98行）で固定される。

- 受け口名: `eThroughEntry`（固定）
- 呼び口名: `cCall`（固定）
- 生成されるセルタイプ名: `t<プラグインクラス名>_<シグニチャのグローバル名>`
- `@through_type` は `:THROUGH`／`:TO_THROUGH`／`:FROM_THROUGH`／`:IN_THROUGH`／`:OUT_THROUGH` のいずれか（3章参照）
- `@caller_cell`／`@next_cell`（callee）を保持——`ThroughPlugin` が連接する場合、`@caller_cell` は最も呼び元のセルになる

**`ThroughPlugin` 自身は何もせず素通しするデフォルト実装であり、`TracePlugin` のようなサブクラスが `gen_through_cell_code`・`gen_ep_func_body` 等をオーバーライドすることで実際の処理（ここではログ出力）を追加する。**

## 3. CDL構文（`bnf.y.rb` より、5形式）

`through` 系の指定子は、単一の結合（join）に対するものと、region の境界を横断するすべての結合に一括適用するものの、大きく2系統・5形式がある。**リポジトリ内にこれらいずれの使用例も CDL ファイルとして存在しない**（全文検索でゼロ件）——文法定義から導出した構文であり、実働サンプルによる検証はできていない。

### 3.1 単一の結合に対する指定（`:THROUGH`）

```tecs-cdl
// join specifier 形式（bnf.y.rb 1197〜1198行）
[through(TracePlugin, "probeName=myProbe")]
cCall = TargetCell.eEntry;

// cell 内で受け口名を明示する形式（bnf.y.rb 773〜774行、"# cell" コメントあり）
through( cCall, TracePlugin, "probeName=myProbe" );
```

### 3.2 region 境界を横断する結合への一括適用（`bnf.y.rb` 1414〜1429行）

```tecs-cdl
region MyRegion {
    in_through( TracePlugin, "" );                    // このregionに"入る"すべての結合
    out_through( TracePlugin, "" );                    // このregionから"出る"すべての結合
    to_through( OtherRegion, TracePlugin, "" );        // OtherRegionへ向かうすべての結合
    from_through( OtherRegion, TracePlugin, "" );      // OtherRegionから来るすべての結合
    // 引数なしの形式（許可指定のみ、プラグインなし）も文法上可能
    // in_through(); out_through(); to_through(OtherRegion); from_through(OtherRegion);
};
```

`Region.new_in_through`/`new_out_through`/`new_to_through`/`new_from_through`（`region.rb` 201〜217行）は `(plugin_name, plugin_arg)` の組をリストへ登録するのみで、実際の挿入はコード生成段階で該当する結合すべてに対して行われる——**1回の指定で、その region に出入りする全結合へ自動的にトレースプローブを仕込める**ということであり、[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]・[[work/active/tecsgen-plugins/NotifierPlugin|NotifierPlugin]]で見た region/domain 境界の仕組みと同系統の「境界をまたぐ結合への自動介入」パターンがここにも現れている。

## 4. プラグイン引数

| 引数 | 意味 |
|---|---|
| `maxArrayDisplay` | 配列・ポインタ列を出力する際の最大要素数（デフォルト16） |
| `cellEntry` | `"Cell.eEntry"` 形式のカンマ区切りリスト。指定した受け口への結合のみトレース対象にする（未指定時は全結合が対象） |
| `probeName` | ログの接頭辞として出力される識別名 |
| `displayTime` | true/false（現状コードは `@b_diplayTime` という綴りミス変数に代入しており、実際に参照される `@b_displayTime` へは反映されない——4.1参照） |
| `kernelCelltype` | ログに使うカーネルセルタイプ名（デフォルト `tKernel`）。指定時は celltype/composite celltype として実在するか検証される |
| `syslogCelltype` | ログに使う syslog セルタイプ名（デフォルト `tSysLog`）。同上検証あり |

### 4.1 発見: `displayTime` オプションは実質無効

`set_displayTime`（`TracePlugin.rb` 462〜470行）は `@b_diplayTime`（`display` の `s` が抜けたタイポ）に代入するが、実際にログ出力コードが参照するインスタンス変数は `@b_displayTime`（`initialize` で `false` に初期化されるのみで、以後どこからも更新されない）。**`displayTime=true` を指定しても、意図した効果（ログにフラグを反映する等）は発生しない**——もっとも `getMicroTime`/`utime` によるタイムスタンプ自体は `@b_displayTime` の値に関わらず常にログへ出力されている（3.1節相当のコード、197〜199行・224〜226行）ため、実害の範囲は限定的と見られる。

## 5. 動作

1. **`gen_plugin_decl_code`**（81〜134行）: プローブ用セルタイプ（`t<TracePlugin>_<シグニチャ>`）を動的に CDL として書き出し `import`。send/receive パラメータがある場合は `allocator(...)` 指定子も付与。`require tKernel.eKernel`／`require tSysLog.eSysLog` に依存。
2. **`gen_through_cell_code`**（136〜169行）: `cellEntry` オプションで絞り込まれた場合のみ、実際にプローブセルを region 内へ配置し、呼び口を本来の callee（`@next_cell`）へ結合する。
3. **`gen_ep_func_body`**（171〜235行）: プローブセルの受け口関数本体を生成——`syslog(LOG_INFO, "Enter: ...")` の後、`print_params` で IN 方向の引数を型ごとに整形してログ出力し、実際の呼び出し（`cCall_<関数名>(...)`）を行い、`syslog(LOG_INFO, "Leave: ...")` の後 OUT 方向の引数・戻り値をログ出力する。
4. **`print_param`**（259〜430行）: スカラー型（bool/int/float）はそのまま、構造体は再帰的にメンバ展開、ポインタ・配列は `size_is`/`count_is` に応じて要素数を評価し `maxArrayDisplay` を上限にループ出力、`nullable` 指定のポインタは NULL チェックを分岐——tecsgen が扱う型システムのほぼ全パターンに対応した、かなり作り込まれたログ整形ロジック。

## 6. 制約・注意点

- **TLVTracePlugin はこのリポジトリに実体が存在しない**（文書冒頭参照）。North Star の記載が別リポジトリ・別バージョンを指しているのか、単純に未実装のまま項目名だけが残っているのか、現状では判別できない。
- `displayTime` オプションが実質無効（4.1節）。
- CDL 実例が一件もなく、5形式の構文はいずれも文法定義からの導出であり未検証（3章）。
- `kernelCelltype`/`syslogCelltype` を指定する場合、対象が celltype として実在している必要がある（存在しない名前を指定するとエラー）。

## Related

- [[tecsgen外部仕様]] — 6.2 `MultiPlugin` ディスパッチ対応表（`ThroughPlugin` 行の実例がこのノート）
- [[work/active/tecsgen-plugins/HRP2Plugin]]・[[work/active/tecsgen-plugins/NotifierPlugin]] — region/domain 境界をまたぐ自動介入という同系統のパターン
- [[North Star]] — カーネル対応プラグイン仕様書化の進捗管理
