---
date: 2026-07-15
description: "nlm source get の出力フォーマットを、実行結果と notebooklm-cli のソース（cli/source.py・output/formatters.py・core/client.py）の両方から確認した記録"
tags:
  - reference
  - notebooklm
  - cli
---

● Background command "Capture full nlm source get output with and without -j" failed with exit code 1

出力フォーマットを実行結果と notebooklm-cli のソースコード（nlm\cli\source.py、nlm\output\formatters.py、nlm\core\client.py）の両方から確認しました。

結論

nlm source get の出力は パースされていない生の RPC レスポンス（Google 内部 batchexecute API のネスト配列）です。notebook get などと違い、client.get_source() は結果を整形せずそのまま返すため（client.py:778）、人間向けのフィールド名は付きません。

出力モードは TTY 自動判別で 2 種類

- ターミナルで直接実行（TTY）: Source Details という見出しの後に value: [ネスト配列そのまま] が 1 行で出ます
- パイプ/リダイレクト時、または -j 指定時: 以下の JSON（indent=2）になります。パイプすると -j なしでも自動的に JSON になる点に注意（formatters.py:44）

実際の出力構造（このソースIDでの実測）

{
  "value": [
    [                                  // ソースレコード
      ["09545813-38d3-45f6-..."],      // [0][0][0] ソースID
      "Seven Sins of Numerical Linear Algebra – Nick Higham",  // [0][1] タイトル
      [                                // [0][2] メタデータ配列
        null,
        2459,                          // サイズ系の数値（推定: 単語数）
        [1778878049, 986947000],       // タイムスタンプ [秒, ナノ秒]
        ["58714d24-...", [秒, ナノ秒]], // 内部バージョンID + 時刻
        5,                             // ソース種別 enum（5 = Web URL と推定）
        null, 1,
        ["https://nhigham.com/2022/10/11/seven-sins-of-numerical-linear-algebra/"],  // [0][2][7][0] URL
        4460,                          // サイズ系の数値（推定: 文字数）
        null, null, null, null, null,
        [秒, ナノ秒]                    // 別のタイムスタンプ（推定: 最終同期）
      ],
      [null, 2]                        // [0][3] ステータス（2 = ready と推定）
    ],
    null,
    null,
    [ ... ]                            // [3] コンテンツのスパン情報: [開始, 終了, ["テキスト", []]] のネスト
  ]
}

実用上のポイント

スクリプトから値を取るなら jq でインデックスアクセスします:

nlm source get <ID> -j | jq -r '.value[0][1]'        # タイトル
nlm source get <ID> -j | jq -r '.value[0][0][0]'     # ソースID
nlm source get <ID> -j | jq -r '.value[0][2][7][0]'  # URL

きれいな構造化データが欲しい場合は、用途に応じて nlm source describe（AI要約＋キーワード、整形済み）や nlm source content（本文テキスト、Title:/Type:/Characters:/Content: 形式）の方が扱いやすいです。フィールド意味の一部（enum 値やカウントの単位）はコード上に定義がなく推定です。
Stop says: Session end checklist:
- Archive completed projects? (work/active/ -> work/archive/YYYY/)
- Update indexes? (Index.md, Memories.md, People & Context, Brag Doc)
- New notes linked? (orphans are bugs)
- Run /om-vault-audit if many notes were created/modified
