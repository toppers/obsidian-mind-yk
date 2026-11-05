---
date: 2026-08-29
description: "MarkItDown — Office/PDF/画像/音声/Web/データ等をLLM前処理向けに構造化テキスト化するPythonユーティリティの対象フォーマット一覧控え"
tags:
  - reference
  - tool
  - markitdown
---

- Ptyhonユーティリティ
- 機械が効率よく読み取れる構造化テキストの生成
- LLM 前処理ツール
- 対象: 
	- Office文書: DOCX, XLSX, XLS, PPTX
	- PDF: PDF(pdfminer.six+pdfplumber)
	- 画像: JPG, PNG(EXIF + OCR + LLMキャプション)
	- 音声: WAV, MP3(メタデータ + 文字起こし)
	- Web: HTML, RSS, YouTube URL, Wikipedia
	- データ: CSV, JSON, XML
	- その他: ZIP, EPUB, Outlook, .msg, Jupyter Notebook

## Related

- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]