---
date: 2026-08-14
description: "tecsgen 標準付属ドメインプラグイン HRP2Plugin の仕様書。region の domain 指定子でTOPPERS/HRP2カーネルの信頼ドメイン境界を宣言し、ドメインをまたぐ結合へSVC/RPCプラグインを自動挿入する"
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

# HRP2Plugin 仕様書

> [!info] 文書状態
> [[North Star]] が「16/17種が未記載」と挙げていたプラグイン仕様書のうち、カーネル対応系から最初の1件として執筆（2026-08-14）。一次資料は `tecslib/plugin/HRP2Plugin.rb`・`tecslib/plugin/DomainPlugin.rb`（親クラス）・`tecslib/core/componentobj/domaintype.rb`・`tecslib/core/componentobj/region.rb`・`tecslib/core/bnf.y.rb`（CDL 文法定義）。ソースの実際の位置は [[TECSCDE外部仕様]] と同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。CDL 使用例の構文パターンは同リポジトリの `test/domainPlugin/domainPlugin.cdl`（テスト用ドメイン `MyDomain` を使用）から採り、HRP2 固有の意味論はソースコードから確定した——テストファイルでは `MyDomain`、本仕様書では `HRP2` に置き換えて例示している。

## 1. 概要

**HRP2Plugin は、TOPPERS/HRP2 カーネル（保護機能付き ITRON 仕様カーネル）向けの信頼ドメイン境界を region に宣言するための「ドメインプラグイン」である。** CDL の `[generate(PluginName, ...)]` で呼び出す通常のプラグイン（tecsgen外部仕様 6.2 参照）とは異なる系統で、`region` の `domain(...)` 指定子から呼び出される。

役割は2つある。

1. **リージョンの信頼レベル（trusted / nontrusted / OutOfDomain）を宣言する。** HRP2 カーネルの保護ドメイン機構（カーネルドメイン／ユーザドメイン）に対応する。
2. **ドメインをまたぐ結合（呼び口↔受け口）に対し、SVC 呼び出しまたは RPC のどちらを自動的に仲介プラグインとして挿入するかを、両端のドメイン種別から判定する。** 利用者は結合を通常どおり記述するだけでよく、ドメイン境界を横切る際に必要な仲介コードの生成は HRP2Plugin が判断する。

## 2. CDL 構文

### 2.1 region への domain 指定子

`domain` は region の specifier（`region` キーワードの前、`[` `]` で囲む位置）として記述する（`bnf.y.rb` 1434〜1435行）。

```
[domain(HRP2, "trusted")]
region <リージョン名> {
    ...
};
```

| 引数 | 位置 | 型 | 内容 |
|---|---|---|---|
| 第1引数（domain_type） | `domain(` の直後 | IDENTIFIER | ドメインプラグインの種別名。**`Plugin` を付けない**（後述） |
| 第2引数（option） | `,` の後 | STRING_LITERAL | `"trusted"` / `"nontrusted"` / `"OutOfDomain"` のいずれか |

region は入れ子にでき、`domain` 指定は各階層で独立に行える（`test/domainPlugin/domainPlugin.cdl` 33・48・61行、ネストした `region rSample { … region rSample1 { [domain(...)] … } }` の例）。

### 2.2 命名規則の落とし穴（`Plugin` を書かない）

**`domain(HRP2Plugin, "trusted")` ではなく `domain(HRP2, "trusted")` と書く。** `DomainType#initialize` が `@plugin_name = (name.to_s + "Plugin").to_sym` として自動的に `Plugin` を末尾に付加し、その名前でクラスをロードする（`domaintype.rb` 58〜62行）。domain_type に `HRP2Plugin` と書いてしまうと、tecsgen は `HRP2PluginPlugin.rb` を探しにいって存在せず読み込みエラーになる。同じ命名規則は `class(...)` 指定子（`ClassType`）にも共通する。

## 3. 動作

### 3.1 生成タイミング

`domain(...)` を持つ region がパースされると、`Region.set_domain` がクラス変数へ一時保存し（`region.rb` 227〜235行）、`Region.new` が実際の `DomainType` インスタンスを生成する（`region.rb` 115〜120行）。プラグイン本体（`HRP2Plugin` インスタンス）が実際に `new` されるのは構文解析完了後の `Region.end_of_parse` → `Namespace#create_domain_plugin` → `DomainType#create_domain_plugin` の経路で、`@pluginClass.new( @region, @name, @option )` として呼び出される（`domaintype.rb` 80〜89行）。

### 3.2 オプション検証（initialize）

`HRP2Plugin#initialize` は第3引数 `option` を検証し、`"trusted"` `"nontrusted"` `"OutOfDomain"` 以外を指定すると **`cdl_error`（"is unacceptable domain kind"）を出し、`"trusted"` にフォールバックして処理を続行する**（`HRP2Plugin.rb` 51〜58行）。エラーにしても解析を中断せず、暫定値で継続する設計である。

### 3.3 ドメイン種別の判定（`get_kind`）

`option` 文字列をシンボルへ写像するだけの単純な変換である（`HRP2Plugin.rb` 124〜133行）。

| `option` | `get_kind` の戻り値 |
|---|---|
| `"trusted"` | `:kernel` |
| `"nontrusted"` | `:user` |
| `"OutOfDomain"` | `:OutOfDomain` |

### 3.4 結合可否（`joinable?`）

`HRP2Plugin#joinable?` は**常に `true` を返す**（`HRP2Plugin.rb` 135〜138行）。すなわち HRP2Plugin 自体はドメインをまたぐ結合そのものを禁止しない——結合の可否ではなく、次節の「どの仲介プラグインを挿入するか」が実質的な制御点になっている。

### 3.5 スルー・プラグインの自動挿入（`add_through_plugin`）

結合の両端が別リージョンに属し、そのリージョンにそれぞれドメインが設定されている場合、`add_through_plugin` が呼ばれて仲介プラグインを決定する（`HRP2Plugin.rb` 61〜120行）。判定は次の順で行われる。

| # | 条件 | 挿入するプラグイン |
|---|---|---|
| 1 | 結合先セルがカーネルオブジェクトセル（`HRP2KernelObjectPlugin.include_celltype?` が真） | なし（`[]`、素通し） |
| 2 | 結合先ドメインの `option` が `"OutOfDomain"` | なし（`[]`） |
| 3 | 結合元が非trusted かつ結合先が trusted（ユーザドメイン → カーネルドメイン） | `HRP2SVCPlugin`（引数なし） |
| 4 | 結合元と結合先のドメインインスタンスが異なる（ユーザドメイン → 別のユーザドメイン） | `HRP2RPCPlugin`（`channelCelltype=tMessagebufferChannel,noClientSemaphore=true`） |
| 5 | 上記いずれにも該当しない | `nil` を返し、`"warning: at HRP2 Join Check"` を出力（意図的な設計というより、想定外ケースの検出に近い） |

**#3・#4 で挿入されるプラグインは、いずれも本ノートの対象範囲外**（`HRP2SVCPlugin`・`HRP2RPCPlugin` は北極星の「RPC」カテゴリが挙げる `TransparentRPCPlugin` 等の汎用 RPC 系プラグインとは別ファイル・別実装であり、HRP2 専用の仲介プラグイン）。両者の詳細は別途の仕様書に委ねる。

## 4. 使用例

```
// syntax pattern: test/domainPlugin/domainPlugin.cdl（MyDomain → HRP2 に置換して例示）

[domain(HRP2, "trusted")]
region rKernel {
    cell tKernelObj Sem {};   // HRP2KernelObjectPlugin が扱うカーネルオブジェクトセル
};

[domain(HRP2, "nontrusted")]
region rTaskA {
    cell tTask Task {
        cBody = Worker.eMain;
        priority  = 17;
        stackSize = 2016;
        taskAttribute = C_EXP("TA_ACT");
    };
    cell tWorker Worker {
        cKernel = rKernel::Sem.eWait;   // trusted への結合 → HRP2SVCPlugin が自動挿入される（3.5 #3）
    };
};

[domain(HRP2, "nontrusted")]
region rTaskB {
    cell tOther Other {
        cToA = rTaskA::Worker.eSomething;  // 別ユーザドメインへの結合 → HRP2RPCPlugin が自動挿入される（3.5 #4）
    };
};
```

利用者が記述するのは通常の結合（`cKernel = rKernel::Sem.eWait;` 等）だけであり、`HRP2SVCPlugin` / `HRP2RPCPlugin` を明示的に `generate` 指定する必要はない。ドメイン境界をまたぐかどうかを HRP2Plugin が判定し、必要な仲介コードを自動的に選ぶ。

## 5. 関連プラグイン

| プラグイン | 関係 |
|---|---|
| `DomainPlugin` | HRP2Plugin の親クラス（`tecslib/plugin/DomainPlugin.rb`）。ドメインプラグイン共通の契約（`initialize`・`add_through_plugin`・`joinable?`・`get_kind`・`gen_factory`）を定義する |
| `HRP2SVCPlugin` | 3.5 #3 で自動挿入される、ユーザドメイン→カーネルドメインの SVC 呼び出し仲介プラグイン（詳細は [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin\|HRP2DomainBoundaryPlugin 仕様書]] 参照、2026-08-15完成） |
| `HRP2RPCPlugin` | 3.5 #4 で自動挿入される、ユーザドメイン間の RPC 仲介プラグイン（詳細は [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin\|HRP2DomainBoundaryPlugin 仕様書]] 参照、2026-08-15完成） |
| `HRP2KernelObjectPlugin` | 3.5 #1 の判定（結合先がカーネルオブジェクトセルか）に使われる、カーネルオブジェクトセル生成プラグインの抽象基底クラス（詳細は [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin\|HRP2DomainBoundaryPlugin 仕様書]] 参照、2026-08-15完成。具象サブクラス群は未着手） |
| `ClassType` / `class(...)` 指定子 | `domain(...)` と文法上並列の region specifier（`bnf.y.rb` 1436〜1437行）。命名規則（`Plugin` 自動付加）も共通 |

## 6. 制約・注意点

- **`Plugin` を付けずに書く命名規則は他の `[generate(...)]` プラグイン呼び出しと非対称**（tecsgen外部仕様 6.2 の `generate(PluginName, ...)` はフルクラス名を書く）であり、混同しやすい（2.2 参照）。
- **不正な `option` はエラーを出しつつ `"trusted"` へフォールバックする**（3.2）ため、タイプミスに気づかないまま解析が進む可能性がある。
- **`joinable?` は常に `true`**（3.4）であり、ドメイン間結合そのものを禁止する仕組みは HRP2Plugin にはない。禁止したい場合は `region` の `out_through()`（許可なし）等、region specifier 側で制御する必要がある（別途 region 仕様の確認を要する、本仕様書の範囲外）。
- 3.5 の判定条件5（該当なし）は警告のみで処理が止まらないため、意図しない組み合わせのドメイン設定が黙って通過する可能性がある。

## Related

- [[work/active/tecsgen/tecsgen外部仕様 - 06 プラグインシステム|tecsgen外部仕様 第6章]] — プラグイン呼び出し規約（`[generate(...)]`）と標準付属プラグイン一覧。HRP2Plugin は同章の表に一覧はあるが詳細は本ノートで初めて記載
- [[TECS開発]] — 開発進捗全体、プラグイン仕様書のトラッキング
- [[North Star]] — 「プラグイン仕様書（16/17種が未記載）」ゲート
- [[perf/competencies/技術文書化|技術文書化]] — ソースコードからの一次資料調査によるプラグイン仕様確定の competency 証拠
