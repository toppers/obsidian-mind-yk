---
date: 2026-06-18
description: "/wiki:query「シグニチャの引数方向」--wiki tecs_md の実行記録（整形前の生ログ）"
tags:
  - reference
  - tecs
  - wiki-query
---

❯  /wiki:query "シグニチャの引数方向" --wiki tecs_md — 記事への質問

● Skill(wiki:query)
Successfully loaded skill · 5 tools allowed
Allowed by auto mode classifier

HUBは既知。インデックスを確認して関連記事を特定します。

  Read 1 file

「シグニチャの引数方向」に関連する記事3件を並列で読みます。

  Read 3 files

十分な情報が揃いました。回答を合成します。

● Update(C:/Users/ykomi/wiki/topics/tecs_md/log.md)
Added 2 lines

## [2026-06-18] ingest | TECS Documentation (raw/articles/2026-06-18-tecs-documentation.md)

## [2026-06-18] query | "シグニチャの引数方向" → answered from 3 articles (standard)

## [2026-06-18] compile | 1 source → 17 new articles (concepts/tecs-overview, concepts/cdl-language, con
cepts/tecs-implementation-model, topics/cdl-reference, topics/implementation-reference, topics/tcd-refer
ence, topics/spc-reference, topics/asp3-tecs-reference, topics/atk2-tecs-reference, topics/mruby-ev3rt-t
ecs-reference, topics/mruby-gr-peach-tecs-reference, topics/tinet-tlsf-tecs, references/tecsgen-referenc
e, references/tecsmerge-reference, references/tecsflow-reference, references/plugin-reference, reference
s/mruby-bridge-reference)

シグニチャの引数方向

TECS CDL では、シグニチャの関数宣言において各引数に引数方向指定子を [...] で明示します。

基本指定子（3種）

┌──────────────────────────┬─────────────────────────────────────────────────┬─────────────────────────────┐
│          指定子          │                      意味                       │       Cコードでの形式       │
├──────────────────────────┼─────────────────────────────────────────────────┼─────────────────────────────┤
│ [in]                     │ 入力引数（呼び元→受け元）。値渡し。             │ int32_t val（ポインタなし） │
├──────────────────────────┼─────────────────────────────────────────────────┼─────────────────────────────┤
│ [out]                    │ 出力引数（受け元→呼び元）。ポインタ経由で返す。 │ int32_t *p_val              │
├──────────────────────────┼─────────────────────────────────────────────────┼─────────────────────────────┤
│ [in, out] または [inout] │ 入出力引数。双方向。                            │ int32_t *p_val              │
└──────────────────────────┴─────────────────────────────────────────────────┴─────────────────────────────┘

記述例

signature sInputOutput {
    ER setOutput( [in]int8_t val );    // 値渡し、ポインタ不要
    ER getInput( [out]int8_t *val );   // ポインタ経由で返す
    ER noParameter( void );            // 引数なし
};

メモリ転送系指定子

大きなデータを転送する場合は send/receive を使います：

┌──────────────────────┬──────────────────────────────────────────────────────────────┐
│        指定子        │                             意味                             │
├──────────────────────┼──────────────────────────────────────────────────────────────┤
│ [send(allocator)]    │ 送信引数（呼び元がアロケータでメモリ確保、受け元が使用）     │
├──────────────────────┼──────────────────────────────────────────────────────────────┤
│ [receive(allocator)] │ 受信引数（受け元がアロケータでメモリ確保、呼び元が受け取る） │
└──────────────────────┴──────────────────────────────────────────────────────────────┘

可変長配列の補助指定子

┌───────────────┬─────────────────────────────────────┐
│    指定子     │                意味                 │
├───────────────┼─────────────────────────────────────┤
│ [size_is(n)]  │ 配列のバイトサイズを別引数 n で指定 │
├───────────────┼─────────────────────────────────────┤
│ [count_is(n)] │ 配列の要素数を別引数 n で指定       │
├───────────────┼─────────────────────────────────────┤
│ [string]      │ ヌル終端文字列（size_is 不要）      │
└───────────────┴─────────────────────────────────────┘

Cコードへの対応（実装モデル）

引数方向は受け口関数のシグニチャに直接反映されます：

// CDL: ER func1([in] int32_t inval, [out] int32_t *outval);
ER eEntry_func1(CELLIDX idx, int32_t inval, int32_t *outval)
{
    CELLCB *p_cellcb = GET_CELLCB(idx);
    *outval = ATTR_someValue;   // [out] はポインタ経由で書き込む
    return E_OK;
}

ポイント: [in] は値渡しなのでCの引数は通常型、[out] / [inout] はポインタ型になります。tecsgen がシグニチャヘッダ（gen/SIGNATURE_tecsgen.h）を生成するため、型の一致はコンパイル時に保証されます。

---
Sources used:
- CDL言語リファレンス (wiki/topics/cdl-reference.md)（confidence: high） — 引数指定子テーブル（[in]/[out]/[inout]/[send]/[receive]/[size_is]/[count_is]/[string]）の全一覧
- CDL言語概要 (wiki/concepts/cdl-language.md)（confidence: high） — シグニチャ記述例（[in]/[out] の具体コード）
- 実装モデルリファレンス (wiki/topics/implementation-reference.md)（confidence: high） — [in]/[out] がCコードの引数型（値渡し vs ポインタ）にどう対応するかの実装例

Knowledge gaps:
- [send]/[receive] のアロケータ指定の詳細構文（wiki ではシグニチャ側の記述のみ。アロケータセル側の [allocator(...)] 指定との対応関係は raw ソースに詳細あり）
- [in,out] と [out] の違いの厳密な仕様（初期値を呼び元が渡すかどうか）
