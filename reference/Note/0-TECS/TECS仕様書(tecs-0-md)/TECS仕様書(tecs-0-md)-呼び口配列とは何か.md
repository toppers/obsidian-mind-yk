---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 呼び口配列とは何か。添数で呼び先セルを切り替える配列化された呼び口。TECSで許されない分流の代替手段として使う"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-呼び口配列とは何か

呼び口配列は、**配列化された呼び口**である。添数で呼び先セルを切り替えることができ、分流（1つの呼び口から複数の受け口への接続）の代替手段として使用する。

---

## 定義

TECSでは分流（1つの呼び口から複数の受け口への結合）は不可だが、呼び口配列を使うことで同等の機能を実現できる。

| 種別 | 説明 |
|------|------|
| **呼び口配列** | 配列化された呼び口。添数で呼び先セルを切替え（分流の代替手段） |

## コンポーネント図での表現

コンポーネント図では、呼び口名に配列の添数を添えて記す（§3.2.3）。

## 呼び口配列と受け口配列の組み合わせ

呼び口配列と受け口配列を対にすることで、複数呼び元に対するコールバックを実現できる（§3.2.6）。

## セルタイプコードでの使い方

呼び口配列の場合は添数も指定して呼び出す：

```c
ER ret = cCallArray_func(idx, subscript, arg1);   // 添数 subscript を指定
```

---

**Sources used:**
- [呼び口・受け口（call/entry port）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-port.md) (confidence: high) — 呼び口配列の定義
- [TECSコンポーネントモデル](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-model.md) (confidence: high) — 一対多の結合モデル
- TECS仕様書 V1.3.0.1 raw — §3.2.3「呼び口配列」

**Knowledge gaps:**
- CDLでの呼び口配列の具体的な記述構文はwikiに詳細なし
