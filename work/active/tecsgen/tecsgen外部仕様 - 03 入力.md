---
date: 2026-08-16
description: "tecsgen外部仕様書 第3章（入力）— CDLファイル、Cプリプロセッサ連携。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 3 of 10.

## 3. 入力

### 3.1 CDL ファイル

- 拡張子: `.cdl`
- 文字エンコーディング: UTF-8（SJIS / EUC も対応）
- 複数ファイルを指定した場合の処理: 指定順に順次 import される（後続ファイルは前ファイルの名前空間を参照可）

#### 3.1.1 CDL 記述要素の対応状況

| CDL 要素 | 対応バージョン | 備考 |
|---------|--------------|------|
| シグニチャ記述 | 〜 V1.3 | callback / context / deviate 指定子 |
| セルタイプ記述 | 〜 V1.3 | active / singleton / generate / idx_is_id |
| 複合セルタイプ（composite） | V1.5.0 | |
| 組上げ記述（セル記述） | 〜 V1.3 | through / prototype 指定子 |
| ネームスペース（namespace） | 〜 V1.3 | |
| リージョン（region） | 〜 V1.3 | node / linkunit / domain / class |
| 呼び口制限（restrict） | V1.4.0 | |
| 動的結合（[dynamic]/[ref_desc]） | V1.4.0 | |
| ファクトリ（factory{}/FACTORY{}） | 〜 V1.3 | |
| アロケータ（send/receive） | 〜 V1.3 | |

### 3.2 C プリプロセッサ連携

`import_C` ディレクティブで C ヘッダを取り込む際、C プリプロセッサ（cpp）を使用する。

- デフォルト cpp コマンド: `gcc -E -DTECSGEN`
- 環境変数 `TECS_CPP` でデフォルトをオーバーライド可能（`-c` オプションも同様）
- `-D` / `-I` でマクロ定義・インクルードパスを指定

---

