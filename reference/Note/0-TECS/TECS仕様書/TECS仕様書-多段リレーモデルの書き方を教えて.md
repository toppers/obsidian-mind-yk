---
date: 2026-06-12T00:00:00.000Z
description: "TECSウィキ（tecs-0/仕様書ベース）クエリ回答 — 多段リレーモデルの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

●  tecs-0 ウィキで多段リレーモデルを検索します。

  Searched for 2 patterns (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  Added 1 line
      2
      3  ## [2026-06-12] query | "RPCの書き方を教えて" → answered from 3 wiki articles + 2 raw (standard)
      4  ## [2026-06-12] query | "アロケータの書き方を教えて" → answered from 2 wiki articles + 3 raw (standard)
      5 +## [2026-06-12] query | "多段リレーモデルの書き方を教えて" → no content found in tecs-0 wiki (standard)
      6
      7  ## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles (2 wiki + 1 raw) (standard)
      8  ## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 4 articles + 2 raw (standard)

● ---
  tecs-0 ウィキには「多段リレーモデル」に関する記述がありません。

  wiki/ と raw/ の両方を全文検索しましたが、「多段」「リレー」「relay」のいずれもヒットしませんでした。

  tecs-0 ウィキは TOPPERS 仕様書（第2〜4章）をベースにしており、多段リレーモデルはその仕様書では記述されていないか、未 ingest の状態です。

  ---
  Knowledge gaps:
  - 多段リレーモデルは tecs-0 仕様書（Chap2〜Chap4）に記載がないか、writeme.txt で「未記述課題」扱いの可能性があります
  - tecs ウィキには記述があります（TCD 記法記事 + imp-allocator.md の <= リレーアロケータ例）— /wiki:query --wiki tecs 多段リレーモデル
  で確認済みの情報が参考になります
  - より詳細な仕様が必要な場合は、tecsgen ソースコード（E:\Crepo\ykominami-svn-2\tecsgen\trunk）またはReadTheDocs の TCD リファレンスを /wiki:ingest
  することを推奨します
