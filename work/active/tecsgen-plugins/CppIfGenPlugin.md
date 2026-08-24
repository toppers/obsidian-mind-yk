---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン CppIfGenPlugin・CppIfGenCelltypePlugin・CppIfGenCellPluginの仕様書。CIfGenPluginのC++版だが、実装はマクロでなく本物のC++クラス生成——コピー元は共通テンプレートでなくCIfGenPlugin自身という証拠も発見"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# CppIfGenPlugin / CppIfGenCelltypePlugin / CppIfGenCellPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]（2026-08-15）に続き、[[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]]で発見した2つ目の完全未追跡`MultiPlugin`ファミリーに着手。一次資料は`tecslib/plugin/CppIfGenPlugin.rb`（60行）・`CppIfGenCelltypePlugin.rb`（459行）・`CppIfGenCellPlugin.rb`（75行）の計3ファイル。これでカバレッジ監査の4候補（CIfGen・CppIfGen・TECSInfo・RepeatCell/Join）のうち2つが完了。

## 1. CIfGenPluginとの対称性・非対称性

`MultiPlugin`ディスパッチ構造・`CellPlugin`側の実装は[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]とほぼ同一だが、**中核の`CelltypePlugin`側の実装がまったくの別物**。

| 観点 | CIfGenPlugin | CppIfGenPlugin |
|---|---|---|
| `MultiPlugin`ディスパッチ構造 | celltype/cellのみ対応、signature/through/domainは`nil` | 完全に同一構造 |
| `CelltypePlugin`側の生成物 | `<celltype>_cif.h`——フラットなCプリプロセッサマクロ | `<celltype>_cppif.hpp`——**本物のC++クラス** |
| セルタイプ単位での実装量 | 152行（`CIfGenCelltypePlugin.rb`） | 459行（`CppIfGenCelltypePlugin.rb`）——3倍以上 |
| copyright最終年 | 2011〜2017年（3ファイルとも古い） | **2023年（3ファイルとも新しい）** |
| `CellPlugin`側の実装・著者コメント | 「現状実装では、すべてのセルに対してセルプラグインを適用するのと同じ」 | **一字一句同じ文言** |

copyright年の食い違い（CIfGen: 2011〜2017年 vs CppIfGen: 2023年）は、[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]で使った「copyright年で実装順序を推定する」手法をここでも適用できる——**C版が先に作られ、C++版は近年（2023年）まで能動的に保守され続けている**、対称に見える2ファミリーの実際の開発強度は非対称だった。

## 2. CppIfGenCelltypePlugin: マクロでなく本物のC++クラスを生成する

生成される`<celltype>_cppif.hpp`は、CIfGenの「フラットなCマクロ」とはまったく異なる、**celltypeごとに1つのC++クラスを、entry portごとにネストしたインタフェースクラスとして生成する**設計。

```cpp
class MyCelltype {
    /* class for entry eMyEntry */
    class eMyEntry_ : public sMySignature {
        public:
        eMyEntry_( ... );          // internal use only
        RetType func1( ... );
        RetType func2( ... );
        private:
        CPP_MyCelltype_IDX cpp_idx;
    };
    public:
    MyCelltype( ... );             // constructor
    eMyEntry_ eMyEntry;            // メンバとして持つ
};
```

**使い方はセルを直接C++オブジェクトとして扱い、`cellName.entryName.FunctionName(params)`という素直なメンバ関数呼び出し構文で受け口を呼べる**——生成コード自身がこの使用例をコメントとして自動的に埋め込む（`/*-------------- begin: use sample ------------ ... */`ブロック、206〜216行）。CIfGenのフラットマクロが「セル名＋ポート名＋関数名」を1つのマクロ名にエンコードしていたのに対し、CppIfGenは**C++のドット記法そのものでセル・ポート・関数の階層を表現する**——同じ「非TECSコードからセルの受け口を直接呼ぶ」目的を、C版は名前空間のないプリプロセッサマクロで、C++版は言語ネイティブのクラス階層で実現する、という対比になっている。

### 2.1 シグニチャ単位のC++抽象クラスをグローバルに1回だけ生成

`gen_namespace_signature_header`（418〜457行）——ネームスペースツリー全体を再帰走査し、見つかった全シグニチャについて`純粋仮想関数のみを持つC++抽象クラス`（`<signature>_cppif.hpp`）を生成する。

```cpp
class sMySignature {
    public:
    virtual RetType func1( ... ) = 0;
    virtual RetType func2( ... ) = 0;
};
```

celltype側の`eMyEntry_`クラスがこの抽象クラスを継承する（`class eMyEntry_ : public sMySignature`）——**TECSシグニチャがC++の抽象基底クラス（インタフェース）へ1対1で対応付けられる**設計。生成は`@@b_signature_header_generated`というクラス変数フラグで**最初の呼び出し時に1回だけ**行われる——[[work/active/tecsgen-plugins/HRMPPlugin|HRMPDomainPlugin]]の`@@include_extsvc_fncd`と同じ「プロセス全体で1回だけ」制御パターンがここにも現れている。[[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgeCellPlugin]]の「ネームスペース全体を再帰走査する一括適用トリガー」とも同種の実装パターン。

### 2.2 発見: 二重に無効化された死コード——CIfGenの「CB型のみインクルード」トリックが未完成のまま残る

[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenCelltypePlugin]]は`TOPPERS_CB_TYPE_ONLY`という一時マクロで`_tecsgen.h`をインクルードし、CELLCB型定義だけを取り込む工夫をしていた。CppIfGenCelltypePluginにも同じトリックのコードが**存在するが、二重に無効化されている**：

```ruby
dummy = <<EOT
#if 0   ///////// MACROs are undef later /////////
#ifndef TOPPERS_CB_TYPE_ONLY
#define TOPPERS_CB_TYPE_ONLY
...
EOT
```

`file.print`ではなく**未使用のローカル変数`dummy`へのヒアドキュメント代入**（Rubyコード側で無効化）に加え、そのヒアドキュメントの中身自体が**Cプリプロセッサの`#if 0`で囲われている**（生成される側でも無効化）——**二重の無効化**。実際に生成されるコードは単純な`#include "<celltype>_tecsgen.h"`のみで、CB型限定インクルードは行われない。つまり**CppIfGenが生成するC++ヘッダは、CIfGenのCヘッダと違い、TECSの内部インライン関数を含む完全なtecsgen生成ヘッダをそのまま非TECSのC++コードに晒す**——CIfGenで確立されていた「TECS内部APIを隠す」設計方針が、C++版では実装されないまま(おそらく意図的に無効化されたまま)残っている。C++の場合クラス経由での呼び出しになるため型安全性は保たれるが、コンパイル時に見える公開面はCIfGenより広い。

## 3. CppIfGenCellPlugin: CIfGenCellPluginと一字一句同じ委譲コード

`CppIfGenCellPlugin < CellPlugin`。`gen_cdl_file`の実装は[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenCellPlugin]]と構造だけでなく**コメント文言まで完全に同一**：

```ruby
# 現状実装では、すべてのセルに対してセルプラグインを適用するのと同じ
#  (IDX マクロを特定セルに対してのみ出力するか、どうかの違い)
def gen_cdl_file file
  file.print <<EOT
generate( CppIfGenCelltypePlugin, #{@cell.get_celltype.get_namespace_path.get_path_str}, "" );
EOT
end
```

同じ日本語コメントが一字一句そのまま存在する——[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]でも指摘した「セル単位のつもりがセルタイプ単位になる」という未完成の粒度制御の限界も、C++版にそのまま引き継がれている。

## 4. 発見: `$Id`不一致がCIfGenPluginと完全に同一の文字列

3ファイルすべての`$Id`キーワードが、[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]で見つけたものと**一字一句同じ文字列**（`MultiPlugin.rb`/`CelltypePlugin.rb`/`CellPlugin.rb`、リビジョン番号・日付・作者名まで完全一致）で残っている。これは単に「同じ基底クラステンプレートから複製した」だけでは説明がつかない一致度——**CppIfGenPluginファミリーは、共通の基底クラスから独立に複製されたのではなく、既に出来上がっていた[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]ファミリー自体をコピーして作られた**、と考えるのが最も自然な説明になる。3節のCellPlugin側コメントの完全一致もこの仮説を補強する。**「C版が先にあり、C++版はC版を複製して作られた」**——[[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]]がHRP2Pluginから複製されたのと同型の関係が、ここでも確認できた。

## 5. 制約・注意点

- CDL実例はリポジトリ内に見つからず、`[generate(CppIfGenPlugin, ...)]`の具体的な記述例はソースからの逆算・未検証。
- singleton・配列受け口（entry array、`_EA`クラス＋`operator[]`）まわりの生成分岐は複雑で、本ノートでは構造の要点のみ記述し、全パターンの動作確認はしていない。
- 2.2節の「二重に無効化された死コード」は、意図的な設計変更（TECS内部APIをC++側では隠さない方針転換）なのか、単なる実装未完了なのか、コメントからは判断できない。
- [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|TECSInfoPlugin]]・`RepeatCellPlugin`/`RepeatJoinPlugin`は引き続き未着手。

## Related

- [[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]] — C版の対、本ノート全体で対比の基準にした。複製元と推測される
- [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] — 「複製元の存在をcopyright年・コード痕跡から推定する」手法の初出
- [[work/active/tecsgen-plugins/HRMPPlugin|HRMPPlugin]] — 「プロセス全体で1回だけ生成」パターンの対比元
- [[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]] — 本ファミリー発見の経緯
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理
