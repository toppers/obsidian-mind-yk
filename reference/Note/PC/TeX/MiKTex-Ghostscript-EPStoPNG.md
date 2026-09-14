---
date: 2026-08-04
description: "MiKTeX 同梱 Ghostscript(mgs.exe)で EPS を PNG へ1段変換する PowerShell 手順。-dEPSCrop が必須な理由、一括変換スクリプト、markdownize.rb の FIG_EXT 連携、miktex-epstopdf が動かない件"
tags:
  - reference
  - tex
  - ghostscript
  - powershell
---

MiKTeX 同梱の Ghostscript（`mgs.exe`）で1段で変換できます。全34ファイルで検証済みです。

## 1ファイル

```powershell
$gs = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\mgs.exe"
& $gs -q -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r150 -sDEVICE=png16m `
      -o Fig1-BasicJoin.png Fig/Fig1-BasicJoin.eps
```

オプションの意味:

| オプション        | 意味                                                                                |
| ----------------- | ----------------------------------------------------------------------------------- |
| `-dEPSCrop`       | **必須**。EPS の `%%BoundingBox` で切り出す。付けないとページ全体（余白付き）になる |
| `-r150`           | 解像度 dpi。BBox の pt 寸法 × r/72 が出力ピクセル数                                 |
| `-sDEVICE=png16m` | 24bit フルカラー。透過が欲しければ `pngalpha`、白黒線画なら `pnggray`               |
| `-o`              | 出力先。`-dBATCH -dNOPAUSE` と併せて対話モードに入らないようにする                  |

`-dEPSCrop` が重要な理由は、この図が LibreOffice Impress からのエクスポートで、スライド全面の白背景を含んでいるためです。`Fig1-BasicJoin.eps` の実インク範囲は `-1 0 720 540` ですが、宣言されている BBox は `80 100 550 380` で、余白を落とすよう手で調整されています。その値は `base/Fig/boundingboxes.txt` に記録されています。LaTeX ビルドも同じ BBox で切り出しているので、`-dEPSCrop` を付ければ PDF と同じ見た目になります。

## 一括変換

```powershell
$gs  = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\mgs.exe"
$out = "base\Fig\png"
New-Item -ItemType Directory -Force $out | Out-Null

Get-ChildItem base\Fig -Filter *.eps | ForEach-Object {
    & $gs -q -dSAFER -dBATCH -dNOPAUSE -dEPSCrop -r150 -sDEVICE=png16m `
          -o (Join-Path $out "$($_.BaseName).png") $_.FullName
}
```

検証結果: `base/` と `rpc/` の EPS 全34ファイルが失敗0で変換でき、合計 559 KB（150dpi）。日本語ラベルも正しく描画されました。最大は `Fig6-1-TransparentRPCDedicated.png` の 29 KB です。元の EPS が 800 KB あるので、**PNG のほうが大幅に小さくなります**。

## markdownize.rb との連携

変換した PNG を使う場合、`base/markdownize.rb` 冒頭の定数を書き換えてください。

```ruby
FIG_EXT = ".png"
```

出力先を `Fig/` 直下にすれば（上の例の `$out` を `base\Fig` にする）パスもそのまま合います。`Fig/png/` に分けた場合は `markdownize.rb` の `print_figure` 内の `Fig/#{label}` も直す必要があります。

## 補足

- `miktex-epstopdf` 経由（EPS→PDF→PNG）も一般的な手順ですが、**この環境では動きません**（`miktex-epstopdf` が起動時に失敗します。`kanji-config-updmap` と同様に Perl 依存の可能性）。Ghostscript 直接なら1段で済むのでそちらを使ってください。
- 解像度は用途次第です。Markdown をブラウザで読むだけなら `-r150`、印刷や拡大表示も想定するなら `-r300`。`Fig1-BasicJoin` は BBox が 470×280 pt なので、150dpi で 979×583 px、300dpi で 1958×1167 px になります。
- 図の元データは `base/Fig/*.odp`（LibreOffice Impress）です。図そのものを直す場合は EPS ではなく `.odp` を編集して再エクスポートし、`boundingboxes.txt` の BBox も合わせて更新してください。

`miktex-epstopdf` はこの環境では動きません。Ghostscript 直接が1段で済むので、全34ファイルで一括変換を検証します。

## Related

- [[TECS仕様書(tecs-0-md)-index]]