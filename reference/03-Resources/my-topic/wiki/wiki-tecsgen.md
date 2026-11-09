---
date: 2026-05-31
tags: [tecs, tool, codegen]
type: concept
status: active
description: "[[tecs-overview]] CDLファイルからインタフェースコードを生成するツール。Rubyスクリプトとして動作。"
---

# tecsgen (TECS ジェネレータ)

tecsgenは、[[tecs-cdl]]記述のCDLファイルを入力として、Cのインタフェースコードを生成するTECSジェネレータです。

## 動作環境

- Rubyスクリプトとして動作
- V1.3以降: exerb版は廃止
- Cプリプロセッサ（デフォルト: `gcc -E -D TECSGEN`）を使用

## 主要オプション

| オプション | 説明 |
|-----------|------|
| `-D` | Cマクロ定義 |
| `-G` | コード生成[[tecs-region]]限定 |
| `-I` | イン[[tecs-port]]パス指定 |
| `-L` | Rubyライブラリパス |
| `-R` | RAM[[imp-initialize]]生成 |
| `-U` | 最適化無効 |

## 生成ファイル

- `Makefile.templ` — ビルド設定テンプレート
- `global_tecsgen.h` — グローバルヘッダ（`INITIALZE_TECS()`マクロを含む）

## See Also

- [[tecs-cdl]]
- [[tecsflow]]
- [[tecsmerge]]

## Counter-Arguments and Gaps

- V1.3.1.0時点の実装に対応（最新版との乖離あり）
