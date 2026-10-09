---
date: 2026-08-16
description: "tecsgen内部仕様書 第9章（プラグイン機構、plugin.rb/pluginModule.rb）— プラグインの種類・ロード、PluginModule、MultiPluginディスパッチ機構、既知の問題3件（TransparentRPCSignaturePlugin参照切れ・FMPのRPC死コード・CppIfGenの二重無効化コード）。2026-09-15、3件とも呼び出し元・エラー処理経路を追跡——9.7.1はP2001のクリーンな失敗、9.7.2はサイレントな誤生成（nilとの違いが鍵）、9.7.3は定義/undef対の構造から意図性を補強。CppIfGenPluginの複製も直接比較で確認済みに格上げ。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 9 of 12. **2026-09-15、9.7の既知の問題3件を`pluginModule.rb`・`signature.rb`・`join.rb`・`FMPPlugin.rb`・`CppIfGenCelltypePlugin.rb`まで遡って追跡し、実行時挙動を確定**（[[work/active/tecsgen/tecsgen内部仕様 - 要再検証項目一覧#5. 第9章 プラグイン機構 — 9.7 既知の問題（3件、実行時未再現）|要再検証項目一覧]]項目5）。

## 9. プラグイン機構（plugin.rb / pluginModule.rb）

### 9.1 プラグインの種類

| 基底クラス | 用途 | CDL での指定位置 |
|-----------|------|----------------|
| `CelltypePlugin` | セルタイプ全体へのコード生成 | `[generate(Name, ...)]` を celltype の前 |
| `SignaturePlugin` | シグニチャへの処理 | `[generate(Name, ...)]` を signature の前 |
| `ThroughPlugin` | through 結合の透過的挿入 | セルタイプの through 指定 |
| `CellPlugin` | セル単位の処理 | セルの `[generate(Name, ...)]` |
| `MultiPlugin` | 上記4種＋domain/classへの動的振り分け | 詳細は 9.5 参照 |

### 9.2 プラグインのロード

`require_tecsgen_lib` が `-L` オプション→ `$RUBYLIB` → システムパスの順にサーチ。プラグインは `tecslib/plugin/` にも自動サーチされる。見つからなければ警告のみ（`b_fatal = false`）。

### 9.3 PluginModule

`PluginModule` モジュールは `Signature`, `Celltype`, `Cell` に include される。

- `@generate` / `@generate_list`：CDL の `[generate(...)]` で登録されたプラグイン情報
- `gen_plugin_post_code(file)`: 全プラグインの `gen_cdl_file` を呼んでポストコードを出力

### 9.4 プラグイン引数パース（Plugin#parse_plugin_arg）

`"key1=val1, key2=val2"` 形式をパース。値は `"..."`, `%...%`, `!...!`, `'...'` 等の複数の囲み記法に対応。`PluginArgProc` ハッシュで識別子ごとの処理を登録。

### 9.5 MultiPlugin ディスパッチ機構

`MultiPlugin < Node`（`tecslib/plugin/MultiPlugin.rb`）は、`CelltypePlugin` / `SignaturePlugin` / `CellPlugin` / `ThroughPlugin` のどれか1つに固定されない、**CDL上の付与位置ごとに別の具象クラスへ振り分けられるプラグインファミリー**の基底となる仕組み。

`PluginModule#load_plugin(plugin_name, superClass)`（`pluginModule.rb`）が実際の分岐点:

```ruby
plClass = Object.const_get plugin_name
if ( plClass <= superClass ) then       # 通常のプラグイン: 期待する基底クラスをそのまま継承
  return plClass
elsif (plClass <= MultiPlugin) then     # MultiPlugin 経由: get_plugin に委譲
  plugin_object = plClass.get_plugin superClass
  # nil ならその付与位置は未対応（P9999 エラー）
  return plugin_object
else
  cdl_error( "P2002 ..." )              # 期待する基底クラスの継承でも MultiPlugin でもない
end
```

`superClass` は呼び出し元（`Cell#load_plugin` 等）が「今どの種類の CDL 要素に `[generate(...)]` が付与されたか」（celltype / cell / signature / through）に応じて渡す。プラグイン名のクラス（例: `CIfGenPlugin`）が `MultiPlugin` を継承していれば、そのクラス自身が override した `self.get_plugin(superClass)` が呼ばれ、家系固有の具象クラス（`CIfGenCelltypePlugin` / `CIfGenCellPlugin` 等）を返す。基底の `MultiPlugin.get_plugin` はデフォルト実装として汎用4基底クラス（`SignaturePlugin`/`CelltypePlugin`/`CellPlugin`/`ThroughPlugin`）をそのまま返すのみで、`DomainPlugin` は明示的に非対応（`nil`）。

既知の `MultiPlugin` 派生ファミリー（tecsgen プラグイン仕様書調査で確認済み。詳細は [[work/active/tecsgen-plugins/PluginCoverageAudit|カバレッジ監査]]参照）:

| ファミリー | 分岐軸 | 対応する付与位置 |
|-----------|--------|----------------|
| [[work/active/tecsgen-plugins/MrubyBridgePlugin\|MrubyBridgePlugin]] | CDL上の付与位置（celltype/cell/signature/through） | 4種類すべて |
| [[work/active/tecsgen-plugins/HRMPPlugin\|HRMPPlugin]] | CDL指定子の種類（`domain(...)` か `class(...)` か） | HRMPDomainPlugin / HRMPClassPlugin |
| [[work/active/tecsgen-plugins/CIfGenPlugin\|CIfGenPlugin]] | CDL上の付与位置 | celltype/cell の2種類のみ（signature・through・domainは非対応） |
| [[work/active/tecsgen-plugins/CppIfGenPlugin\|CppIfGenPlugin]] | CDL上の付与位置 | celltype/cell の2種類のみ（2026-09-15確認: `CIfGenPlugin.get_plugin`と`CppIfGenPlugin.get_plugin`はコメント文言・分岐構造とも一字一句同一で、`$Id: MultiPlugin.rb...`という複製元由来のヘッダ文字列まで残る——「推測」ではなく直接比較で確認済みの複製） |

> [!note] 発見: 基底クラステンプレートの複製痕跡
> `CIfGenPlugin`・`HRPPlugin` など複数のプラグインファミリーで、ファイル内の `$Id` キーワードが実際のファイル名ではなく複製元の基底クラスファイル（`MultiPlugin.rb`・`CelltypePlugin.rb`・`CellPlugin.rb` 等）を指したまま残っている（[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin 仕様書]] 4節）。単発の書き換え忘れではなく、「基底クラスファイルをコピーして新しいプラグインファミリーを作る」という標準付属プラグインの制作過程そのものを示す一次証拠。新規プラグイン開発者が既存ファミリーを雛形にする際に踏襲されている慣行と見られる。

### 9.6 ポストコード生成の優先順位

`PluginModule` はプラグイン種別ごとに固定の優先順位定数を持つ（数字が小さいほど優先度が高い＝先に生成される）:

| 定数 | 値 | 対象 |
|------|-----|------|
| `MULTI_PLUGIN_POST_CODE_PRIORITY` | 0 | MultiPlugin 経由の全プラグイン |
| `DOMAIN_PLUGIN_POST_CODE_PRIORITY` | 10000 | DomainPlugin |
| `CLASS_PLUGIN_POST_CODE_PRIORITY` | 10000 | ClassPlugin |
| `THROUGH_PLUGIN_POST_CODE_PRIORITY` | 20000 | ThroughPlugin |
| `CELLTYPE_PLUGIN_POST_CODE_PRIORITY` | 30000 | CelltypePlugin |
| `COMPOSITE_PLUGIN_POST_CODE_PRIORITY` | 40000 | CompositeCelltype 関連 |
| `CELL_PLUGIN_POST_CODE_PRIORITY` | 50000 | CellPlugin |
| `SIGNATURE_PLUGIN_POST_CODE_PRIORITY` | 60000 | SignaturePlugin |

`MultiPlugin` 経由のプラグインが常に最優先（0）で生成される点に注意。DomainPlugin と ClassPlugin は同順位（10000）で並ぶ——[[work/active/tecsgen-plugins/HRMPPlugin|HRMPPlugin]] のように両方にディスパッチしうるファミリーがあっても、生成順序としては区別されない設計。

### 9.7 既知の問題（プラグイン仕様書調査で発見）

標準付属プラグイン群の仕様書化（[[work/active/tecsgen-plugins/PluginCoverageAudit|カバレッジ監査]]、2026-08-15完了）で見つかった、実装上のリスクとなりうる3件。**2026-09-15、3件とも実際の呼び出し元・エラー処理経路まで遡って追跡し、「静的な文字列の不一致」から「トレース済みの具体的な実行時挙動」へ格上げした**（実際にtecsgenを実行してのブラックボックス再現ではないが、コードパスを最後まで辿ったことで結果は一意に定まる）。

#### 9.7.1 `TransparentRPCSignaturePlugin` 参照切れ — 挙動を追跡: クラッシュではなく「クリーンな失敗」

[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]（`gen_marshaler_celltype_`、195〜201行）と [[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]] が生成するCDLが、どちらも独立に `generate(TransparentRPCSignaturePlugin, ...)` というクラス名を呼び出す。しかし `tecslib/plugin/` 全85ファイルおよびリポジトリ全体を検索しても、この名前のクラス定義・エイリアスは一切存在しない（実在するのは `TransparentMarshalerPlugin`）。`TransparentMarshalerPlugin` が過去に `TransparentRPCSignaturePlugin` という名前だった時期にリネームされ、生成コード側の文字列リテラルだけ追随できなかった、という説明が最も自然だが確証はない。

**追跡した実行時挙動**: `PluginModule.load_plugin`（`pluginModule.rb:75`）は`require_tecsgen_lib("TransparentRPCSignaturePlugin.rb", false)`でファイルを探すが、`$library_path`/`$LOAD_PATH`のどこにもそのファイル名は存在しないため`false`を返す→`cdl_error("P2001 $1.rb : fail to load plugin", ...)`を発行して`nil`を返す。呼び出し元の`Signature#apply_plugin`（`signature.rb:315`）は`return if plClass == nil`で**nilを安全に処理**しており、Rubyの未捕捉例外やクラッシュにはならない。つまり実際に起きるのは、**`P2001`という明確なエラーメッセージが出て、コード生成フェーズへ進むゲート（11章、`Generator.get_n_error != 0`）に引っかかりtecsgenが正常終了コードでは終わらない**という「クリーンだが確実な失敗」である——未定義動作や不可解なクラッシュではない。

**実行による確認（2026-09-26）**: [[tecsgen-python3移植計画]]の正解データ採取で、移植元 `test/` のケースを実際に実行し、上の追跡どおりの挙動を確認した（WSL Ubuntu、Ruby 3.2.3、gcc 13.3、SVN r3304）。`class`・`rpc`・`DataPumpHolder` の3ケースが `P2001 TransparentRPCSignaturePlugin.rb : fail to load plugin` を出し、終了コード1で止まる。Ruby の例外は出ない。続けて、ロードに失敗したプラグインが作るはずだった CDL（`gen/tMarshaler_*.cdl` など）が見つからないという `S1148`、またはセルタイプが見つからないという `S1027` が連鎖して出る。つまり**移植元の標準テストのうち、RPC を使う3ケースは現行版では通らない**。

#### 9.7.2 FMP の RPC 死コード — 追跡の結果、「未完成」より深刻な**サイレントな誤生成**と判明

`FMPPlugin#add_through_plugin`（87〜140行）は [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]・[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] と同じ役割（結合先のクラス境界をまたぐ場合の仲介プラグイン自動選択）を持つが、「呼び先クラスが特定プロセッサ限定（`locality=="only"`）かつ呼び元が別プロセッサまたは非限定」という、本来RPC仲介が必要なはずの条件で `[]`（挿入なし）を返す。分岐には次のコメントアウト済みコードが残る。

```ruby
# return [ :FMPRPCPlugin, "noClientSemaphore=false,PPAllocatorSize=256" ]
# return [ :SelectiveJoinPlugin, "processorID=#{callee_prc_NPU_cell}" ]
return []
```

`FMPRPCPlugin` というクラスは `tecslib/plugin/` のどこにも存在しない（FMP関連3ファイルのみで確認済み）。

**追跡した実行時挙動**: 呼び出し元（`join.rb`、複数箇所）は`add_through_plugin`の戻り値が**`nil`なら`cdl_error`で結合を拒否**するが、**`[]`（空配列）は「結合は許可、追加のthroughプラグインは不要」として扱われる**——`FMPPlugin#add_through_plugin`は全分岐（カーネルオブジェクト宛て・RPC必要・直接呼出し可）で一貫して`[]`を返しており、`nil`を返す分岐が存在しない。つまりRPC仲介が必要と判定した条件でも**エラーも警告も一切出さず、プロセッサ境界をまたぐ直接呼出しとして黙って結合を許可する**——「未実装のため止まる」のではなく「未実装のまま気づかれずに通る」という、9.7.1より一段階深刻なサイレント欠陥。マルチプロセッサ間RPC仲介機構は設計段階で構想されたが実装されないまま終わったことを示す直接証拠でもある。

#### 9.7.3 CppIfGen の二重無効化コード — 構造から「意図的」の裏付けを追加

`CppIfGenCelltypePlugin`（100〜130行）には、[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenCelltypePlugin]] と同じ「`TOPPERS_CB_TYPE_ONLY` マクロで `_tecsgen.h` をインクルードし CELLCB 型定義だけを取り込む」トリックのコードが存在するが、`dummy = <<EOT` ... `#if 0` という**二重の無効化**（到達不能なヒアドキュメント代入の中に、さらに `#if 0` で囲まれたコード）がかかっている。**同じ構造の無効化が定義側・undef側の2箇所（110〜118行・124〜130行）に対で存在し**、間に挟まる`file.print "#include \"...\_tecsgen.h\""`（120〜122行）だけがガード無しでそのまま出力される——結果としてC++用インタフェースヘッダは`_tecsgen.h`の全内容を素通しでincludeする形になり、CIfGenPlugin（C版）が意図するCB型限定includeとは異なる。

これが「TECS内部APIをC++側では隠さない」という意図的な設計方針転換なのか、単なる実装未完了なのかは、コメントからは判断できない（[[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin 仕様書]] 5節）。**ただし、定義側・undef側という対になる2箇所が両方とも同じ二重無効化パターン（Rubyのdummy代入＋C側`#if 0`）で揃っている**という構造は、単発の消し忘れでは起こりにくく、9.5で確認した「CIfGenPluginからの複製」慣行の延長として——C言語版のコードをC++版へ複製した際に、C++側では丸ごと不要と判断して意図的に無効化した可能性を補強する（が、明示的な記録が無い以上「未検証」のまま残す）。

---

