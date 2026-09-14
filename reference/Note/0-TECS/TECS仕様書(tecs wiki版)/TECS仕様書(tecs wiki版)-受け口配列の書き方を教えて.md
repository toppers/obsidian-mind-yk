---
date: 2026-06-09
description: "受け口配列のCDL宣言（entry sSignature eArray[N]）・TCD表記・C実装（subscript第2引数）。サイズN必須、呼び元識別可能（tecs wiki版）"
tags:
  - tecs
  - reference
  - tecs-wiki
  - cdl
---

# 受け口配列の書き方（tecs wiki版）

> **ソース**: tecs wiki（ReadTheDocs版）— `wiki/concepts/implementation-model.md`, `wiki/topics/tcd-notation.md`

## 1. セルタイプでの宣言（CDL）

**このwiki（tecs ReadTheDocs版）には受け口配列のCDL宣言構文の明示的な例がありません。**

呼び口については「配列形式で複数セルへの結合が可能」と `cdl-language.md` に明記されていますが、受け口配列の宣言構文は記載なし。

> 参考: tecs-0 wiki の `cdl-language-spec.md` BNF より: `entry sSignature eArray[N];`（サイズ N 必須）

## 2. TCD（コンポーネント図）での表記

`tcd-notation.md` より：

> **配列インデックスをポート名に付加して表記。** 呼び口配列と受け口配列のインデックスを対応させると、複数の呼び元にわたるコールバック機能を実現できる。

```
CallerA --cArray[0]--> Provider.eCallback[0]
CallerB --cArray[1]--> Provider.eCallback[1]
CallerC --cArray[2]--> Provider.eCallback[2]
```

## 3. C実装側の受け口関数の形式

`implementation-model.md` より：

受け口配列の受け口関数は CELLIDX idx の次（第2引数）に `int_t subscript` が追加される:

```c
/* 非配列の場合 */
ER eEntry_func1(CELLIDX idx, int32_t inval, int32_t *outval)

/* 配列の場合 */
ER eEntry_func1(CELLIDX idx, int_t subscript, int32_t inval, int32_t *outval)
```

`subscript` は呼び元のインデックス番号。受け口配列はこれにより呼び元セルを識別できる。

シングルトンの場合:

```c
ER eEntry_func1(int_t subscript, int32_t inval, int32_t *outval)
```

## 知識ギャップ

- CDL宣言構文が未収録 → [[TECS仕様書-受け口配列の書き方を教えて]]（tecs-0 wiki版に BNF あり）
- subscript の値が何を表すか（呼び元セルの番号）の詳細説明が不足

## See Also

- [[TECS仕様書(tecs wiki版)-受け口配列とは何か]]
- [[TECS仕様書(tecs wiki版)-呼び口配列の書き方を教えて]]
- [[TECS仕様書-受け口配列の書き方を教えて]]