---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書。TECSCDE-DT外部仕様（デスクトップ版）を、TypeScriptクラスベース設計でElectron固有に実装するための内部仕様。main/renderer/preloadのプロセス境界設計が中心。全11章執筆完了。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

# TECSCDE-DT-EL 内部仕様（Electron・クラスベース）

> [!info] 文書状態
> **全11章執筆完了（2026-09-05）** — [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（デスクトップ版、Electron/Tauri言語非依存）を、**TypeScriptクラスベース設計で、Electronに固有化して**実装するための内部仕様として起こした。2つの先行文書の交点に位置する。
>
> | 軸 | 先行文書 | 本書での扱い |
> |---|---|---|
> | クラス設計（`Cell`/`Command`/`History`等） | [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様\|TECSCDE-TS内部仕様]] | **そのまま踏襲**（第3〜6章・第8章）。モデル・コマンド・描画・表示制御は実行環境に依存しないため変更しない |
> | デスクトップ機能（ネイティブfs・tecsgen実行・OSクリップボード） | [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様\|TECSCDE-DT外部仕様]] | **Electronに固有化**（第7章・第9章）。Tauriとの両立を考慮する必要がなくなったため、Electron固有のAPI（Node.js `fs`・`child_process`・`clipboard`・`dialog`）を直接使う設計に書き換える |
> | **プロセス境界（main/renderer/preload）** | **どちらの先行文書にもない** | **本書が新規に追加する中心的な設計**（第2章）。Electronのセキュリティモデル（`contextIsolation`）は、Node.js APIを直接使えるmainプロセスと、Webページ相当のrendererプロセスを分離するため、9モジュール（A〜I）のどれがどちらのプロセスで動くかを新たに決定する必要がある |
>
> **本書は設計提案として起こしたが、2026-09-06に実装着手——第11章11.4節の最初の2単位（モデル+CDL round trip・UI前のIPCゲートウェイ疎通）が完了している。** 詳細: [[TECSCDE-DT-EL実装]]。

## 目次

1. [[TECSCDE-DT-EL内部仕様 - 01 概要]]
2. [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]] — 本書の中心。main/renderer/preloadへのモジュール配置とIPC契約
3. [[TECSCDE-DT-EL内部仕様 - 03 モデル設計]] — [[TECSCDE-TS内部仕様]]と同一（変更なし、rendererプロセスで動作）
4. [[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]] — 同上
5. [[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]] — 同上
6. [[TECSCDE-DT-EL内部仕様 - 06 表示制御設計]] — 同上
7. [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 - 07 ファイルI/O設計]] — Electron固有化。`dialog`/`fs`をmainプロセスに置き、`FileGateway`でIPC経由公開（インポート参照先解決含む）
8. [[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]] — [[TECSCDE-TS内部仕様]]と同一（変更なし、rendererプロセスで動作。mainプロセスのtecsgen実行結果・フォールバック警告も集約）
9. [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計]] — Electron固有化。`child_process`（tecsgen・Cプリプロセッサ実行）をmainプロセスに置き、`TecsgenGateway`でIPC経由公開
10. [[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]] — main/renderer/preloadのディレクトリ構成とIPCチャネル一覧
11. [[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]]

## Related

- [[TECSCDE-DT-EL実装]] — 本書に基づく実装の進捗ノート（2026-09-06着手）
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]] — 本書が実装する外部仕様（デスクトップ版）
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]] — 姉妹文書（Tauri・Rust）。同じ外部仕様・同じモジュール分割から出発するが、言語・プロセスモデルの違いにより設計が分岐する
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — 本書が踏襲するクラス設計の一次情報源（ブラウザ版）
- [[TECSCDE内部仕様]] — さらに元となる関数/インタフェースベースの内部仕様（ブラウザ版）
- [[TECSCDE-JS-TS実装]] — ブラウザ版の実際の実装（本書はこれとは別系統）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装（本書はデスクトップ・Electron版という別ラインの検討）
