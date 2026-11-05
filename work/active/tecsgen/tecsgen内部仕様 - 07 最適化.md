---
date: 2026-08-16
description: "tecsgen内部仕様書 第7章（最適化、optimize.rb）— 最適化フラグ、optimize_call、optimize_entry。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 7 of 12.

## 7. 最適化（optimize.rb）

> [!info] 検証済み（2026-08-15）
> `optimize.rb`（`Namespace`/`Celltype` にメソッドを追加）と `componentobj/port.rb`（フラグ実体・`reset_optimize`）を直接読んで、以下 7.1〜7.3 を実ソースと突き合わせた。

### 7.1 最適化フラグ

`@b_cp_optimized` は **Celltype 側**の属性であり、Port 側のフラグではない（`componentobj/celltype.rb:82,162`、`optimize.rb` 内の代入はすべて `Celltype` インスタンスメソッド内）。個別の最適化判定は `Port` オブジェクト側（`componentobj/port.rb`）に持たせる:

| フラグ（所属） | 意味 |
|--------|------|
| `@b_cp_optimized`（Celltype） | セルタイプ内のいずれかの呼び口で最適化を実施した |
| `@b_cell_unique`（Port、CALL側のみ設定） | 呼び先セルが1つ（CBに格納不要） |
| `@b_VMT_useless`（Port） | VMT（関数テーブル）不要 |
| `@b_skelton_useless`（Port） | スケルトン関数不要 |

> [!note] 発見: CALL側とENTRY側で初期値が逆
> `Port#reset_optimize`（`port.rb:179-199`）は呼び口（`CALL`）側と受け口（`ENTRY`）側で真逆の初期化をする。呼び口側は `@b_VMT_useless`/`@b_skelton_useless`/`@b_cell_unique` すべて `false` から始まり、`optimize_call` が最適化条件を満たすたびに `true` を立てる悲観的初期化。受け口側は `$unopt`/`$unopt_entry` が偽である限り `@b_VMT_useless`/`@b_skelton_useless` を最初から `true` にする楽観的初期化——「最適化済み」を既定にしておき、7.3 の `optimize_entry` が対応する呼び口側の状態を見て条件を満たさない場合だけ `false` に倒す設計になっている。同名フラグが CALL/ENTRY で意味論・初期値ともに異なる点は生成コード読解上の落とし穴になりうる。

### 7.2 optimize_call（呼び口最適化）

各 Celltype の呼び口について、そのセルタイプの全セルを走査して呼び先（セル・受け口ポート）を収集し `uniq!` で重複除去する。

```
呼び先ポートが1種類のみ（port_ports.length==1）？
  Yes → 呼び口配列サイズが "[]"（可変長）なら最適化スキップ
        → @b_cp_optimized = true（Celltype側）
        呼び先セルも1つのみ（port_cells.length==1）？
          Yes → 受け口が optional未結合 or 配列でない？
                  Yes → cell_unique + VMT_useless + skelton_useless すべて true
                  No  → VMT_useless のみ true
          No  → 受け口が optional未結合 or 配列でない？
                  Yes → singleton でなければ VMT_useless + skelton_useless、
                        singleton なら VMT_useless のみ
                  No  → 最適化なし（受け口が配列の場合はここで打ち切り）
  No  → 最適化なし
```

例外:
- `[dynamic]` / `[ref_desc]` 指定の呼び口 → 最適化スキップ（`is_dynamic?`/`is_ref_desc?`）
- `omit`（optional 未結合）→ 呼び先集計に入る前に `@b_cp_optimized`・`skelton_useless`・`VMT_useless` を即座に true にして次のポートへ（他条件の判定をスキップ）
- 呼び口配列サイズが `[]`（可変長）→ 最適化スキップ（受け口へのポインタは省略できないが配列個数マクロは出力する、というコメント付きの暫定対策と明記されている）

最適化成立時、`Port#set_only_callee(callee_port, callee_cell)` で唯一の結合先を記録する（`@b_cell_unique` が true のときのみ意味を持つ）。

### 7.3 optimize_entry（受け口最適化）

呼び口最適化の結果をそのまま受け口側にコピーするのではなく、`Port#set_entry_VMT_skelton_useless(b_VMT_useless, b_skelton_useless)`（`port.rb:540-547`）を介して**偽の場合のみ受け口側フラグを false に倒す**（真の場合は何もしない、片方向にしか変化しない）:

```ruby
def set_entry_VMT_skelton_useless( b_VMT_useless, b_skelton_useless )
  if ! b_VMT_useless then
    @b_VMT_useless = false
  end
  if ! b_skelton_useless then
    @b_skelton_useless = false
  end
end
```

受け口は 7.1 の通り既定で `true`（最適化済み）のため、複数の呼び口から参照される受け口では、いずれか1つでも最適化されていない（`false` の）呼び口があればその時点で該当フラグが `false` に固定される——1回でも false を受け取ったフラグは以後の呼び出しで再び true には戻らない一方向の合流処理。`--unoptimize-entry`（`$unopt_entry`）または `-U`（`$unopt`）を指定すると `reset_optimize` の時点で受け口側の初期値そのものが `false` になり、`optimize_entry` を待たず最適化が無効化される。

---

