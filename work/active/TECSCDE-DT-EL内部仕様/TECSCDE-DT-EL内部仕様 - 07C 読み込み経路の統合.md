---
date: 2026-09-22
description: "TECSCDE-DT-EL内部仕様書 第7C章（読み込み経路の統合）— 前回セッション復元・ファイルブラウザからの追加読み込み・消去ボタン・tecsgenオプション形式ファイルの一括読み込み・import自動追跡との統一。2026-10-19、通常CDLの編集可否と定義元への保存を現行実装に合わせて改訂。"
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

Domain note new from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章]]の続き（7.7節）として新規追加（2026-09-22）。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|第11章]]11.2節#7〜#11（いずれもユーザー要望・2026-09-22追加、「ファイルの発見経路によらず統一的に管理する」という共通テーマ）の設計をまとめる。

> [!info] #8/#10/#11の実装前提（2026-09-22追記）
> 本章が「既存のresolveImports()」と呼ぶ対象は、執筆当時は型定義のみで具体アルゴリズムが未確定だった。同日中に[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]が具体設計を確定した。本章の記述（7.7.2・7.7.4・7.7.5節）は変更していない——7D/7E章がその実装前提を満たす。

## 7.7 読み込み経路の統合 — 2026-09-22追加

決定事項（2026-09-22の追加方法を維持し、2026-10-19に編集可否を改訂）: #8ではファイルブラウザで選んだCDLを既存の主ファイルを置き換えずに`references`集合へ追加する。`editablePath`と`referencePaths`は主ファイルと追加読み込みファイルを区別するセッション上の役割であり、編集権限の区別ではない。手動追加と`import`自動追跡は同じ解決・重複抑止パイプラインを共有する。

**保存先**: `CdlDocumentLoader.loadSources()`は通常CDLのセルに編集可能フラグと定義元パスを保持する。`CdlSerializer.serializeSource()`は主ファイルも定義元で選別し、変更のある読み込み済みCDLを各元パスへ書き戻す（[[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約|4C]]）。新規・貼り付けセルは選択中の編集可能セルの定義元、選択がなければ主ファイルに属させる。Plugin生成セルは読み取り専用で保存しない。

### 7.7.1 前回セッションの復元（#7）

**2026-11-07、監査#9による契約更新**: 詳細は[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元|7H セッション保存と復元]]へ分離した（本章の25KB閾値による）。`lastSession`は`editablePath`・`referencePaths`に加え、`optionsFilePath`と`extraImportPaths`を同じスナップショットで保存する。主ファイル未確定は`editablePath: null`で表す。 7I.5の`sourceOrder`も同時に保存・復元し、主役と順序を別に保持する（三者監査#5、2026-11-09）。

起動時の優先順位は明示入力（CLI／関連付け確定要求） ＞ `lastSession` ＞ `public/samples`を維持する。復元時の再解析と保存済み探索パスの優先順位、失敗時のフォールバック、都度保存の時機と設定の部分更新、旧設定互換は7Hを正とする。起動時に`app:bootstrap`で渡す内容にも、オプションファイル・探索パス・再解析した`systemDirs`を含める。主パスの有無で復元対象を除外せず7H.0の判定表を使う。現行`5cf2d85`は未対応だった（2026-11-09。三者監査#7・#8は段0で実装済み、as of 2026-11-12）。

通常open・opts・手動追加・消去は[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I.7]]の共通guardを使う。最初のawait前の文書revisionも固定し、失効結果は適用・通知・セッション保存に使わない。現行`5cf2d85`は未対応だった（三者監査#6、2026-11-09。段0で実装済み、as of 2026-11-12）。

### 7.7.2 ファイルブラウザからの追加読み込み（#8）

決定(a): 主ファイルを置き換えずに`references`へ追加する。追加したCDLがユーザ定義CDLであれば、そのセルも編集可能とする（システム定義CDLのセルは`systemDefined`により既定で編集不可、第3章3.2節）。

**UI操作**: ツリー上の通常クリックは主ファイルとして開き、Ctrl+クリックは現在の主ファイルを維持して追加で読み込む。

> [!note] UI操作の選定経緯
> Ctrl+クリックは通常クリックの主ファイル切替と区別するために採用した。現在は追加読み込み操作として実装している。
>
> **追加時の未解決と基点（2026-11-17 決定、実装済み。v0.2.6 段3、コミット `2dcca6a`、ブランチ `v0.2.6-stage3`・未マージ、三者相違一覧 5-4・5-5）**: `addAsReference`は、追加したCDLの`import`が解決できなくても、全体の再解決で`import`が未解決になっても、`W-UNRESOLVED-REF-FILE`の警告にして追加を続ける（開く経路と同じ）。追加したCDL自身が見つからないとき（解決結果が空で未解決の診断があるとき）だけ、旧状態を保ち、`store.setTransientActionDiagnostics`で警告を出す。既に読み込み済み（診断なし）は何もしない。opts由来の相対`-I`・`-S`は、`contextImportPaths`で optsのあるディレクトリを基点に直し、追加の2回の解決（追加CDLの閉包と全体の再解決）の両方に使う。ストアが持つ原文（`getExtraImportPaths`）は変えない。

**重複判定**: 11.2節#8の決定どおり、選択したファイルが既に読み込み済み（editableまたはreferencesのいずれかと同一の正規化済み絶対パス）であれば無視する（第7章7.5節の`import`重複抑止と同じキー）。

**実現方式（#11との統合、7.7.5節）**: 新規クラスは設けず、`import`自動追跡と全く同じ読み込みパイプライン（第7章7.5節`FileService.resolveImports()`）を、手動選択したファイルを起点として1回実行する。`ImportRequest`に絶対パス指定の種別を追加する。

```ts
// shared/ipc-types.ts の ImportRequest 拡張（第7章7.5節）
interface ImportRequest {
  readonly kind: 'import' | 'import_C' | 'manual'; // 'manual' を追加
  readonly specifier: string; // kind: 'manual' の場合は絶対パスそのもの
}
```

```ts
// renderer/app/file-actions.ts
export async function addAsReference(store: AppStore, gateway: FileGateway, path: string): Promise<void> {
  if (store.hasDocument(path)) return; // 重複は無視（#8決定）
  const resolved = await gateway.resolveImports(store.editablePath, [{ kind: 'manual', specifier: path }], {
    importPaths: [],
  });
  applyResolvedReferences(store, resolved); // 選択ファイル自身とその再帰的import先を全てreferencesへ追加
}
```

`kind: 'manual'`は、`FileService.resolveImports()`内でパスの正規化・存在確認のみ行い（`base_dir`・`import_path`探索を経由しない——絶対パスが直接指定されているため）、以降の処理（UTF-8読み取り、モジュールBでの再帰的import解決、循環・重複抑止）は既存の`import`と完全に共有する。手動追加したファイル自身がさらに`import`していれば、その参照先も連鎖的にreferencesへ加わる——import自動追跡と同じ挙動になる（7.7.5節）。

未保存確認（7.6.4節`confirmDiscardChanges`）は不要——既存のeditableを置き換えないため。

### 7.7.3 消去ボタン（#9）— 新規作成の別名

決定（ユーザー確認済み）: [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.2節]]の新規作成（既定用紙の空図、ファイル名は保存まで未確定）と同一機能の別名として設計する。DT-EL実装には現状これに相当するツールバー操作が存在しないため（11.2節#9）、本節が初めて設計する。

```ts
// renderer/app/file-actions.ts
export async function newDocument(store: AppStore, gateway: FileGateway): Promise<void> {
  if (store.isDirty()) {
    const proceed = await gateway.confirmDiscardChanges(); // 7.6.4節と同じダイアログを再利用
    if (!proceed) return;
  }
  store.resetToBlank(); // 5.2節: 既定用紙、editable未確定（filePath: null）
}
```

**配線**: [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|第7B章7.6.5節]]と同様、ツールバーに`data-action="clear"`ボタンを追加し、`runAction`に`case 'clear':`を追加して`newDocument()`を呼ぶ。利用者向けラベルは要望どおり「消去」とするが、内部の関数名は外部仕様の用語（新規作成 = new）に揃える（既存の命名規則`openFromPath`/`chooseRoot`と同様、動作を表す名前とする）。

**影響範囲**: `references`集合・ファイルブラウザの展開状態（7.6.3節`expanded`/`children`）はクリアしない——消去は編集対象(editable)のみを空にする操作であり、参照ファイル一覧やツリーの展開状態はアプリケーション実行中の状態として維持する（3.5.1節「ツリーの展開状態はアプリケーション実行中の状態としてのみ保持する」と同じ扱い）。

**7.7.1節との関係**: 消去後は`editablePath: null`と保持したreferences・sourceOrderを保存する。未保存の主文書本文は復元しないが、空の主文書と参照集合は7H.0の有効セッションとして復元する。参照も空なら意図的な空状態の復元成功とし、samplesへ置換しない（2026-11-09）。

### 7.7.4 tecsgenオプション形式ファイルの一括読み込み（#10）

[[TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07L tecsgenオプション形式ファイルの一括読み込み|7.7.4 本文]]へ逐語で分離した（2026-11-17、25KB閾値。要旨: `.tecsgen-opts`を解析してCDLを一括で開き、最後を主ファイルにする。`-I`・`-S`・`-c`・`-k`・`-D`の解釈、システム定義CDL、`_CDL_FILES.txt`、`OpenResult.cpp`の受け渡しを定める）。

### 7.7.5 import自動追跡との統一（#11）

7.7.2節の設計により、11.2節#11(b)「発見経路（手動選択／import自動追跡）によらず同じ内部データ構造（documents/referencesの集合）で管理する」は**既に満たされる**——手動追加(`addAsReference`)は`kind: 'manual'`という種別が増えるだけで、`FileService.resolveImports()`以降の解決・重複抑止パイプラインは完全に共有される。

#11(c)「編集可否も統一する」は**2026-10-19に現行実装へ合わせて採用**した。主ファイル、手動追加、`import`自動追跡、前回セッション復元、`.tecsgen-opts`で列挙されたファイルのどの経路でも、ユーザ定義CDL由来のセルを編集可能とする（システム定義CDL由来のセルは既定で編集不可、第3章3.2節）。`locale`は定義元と保存先の識別に用い、主ファイルか`references`かによって編集を禁止しない。Plugin生成CDL由来のセルだけは読み取り専用とし、保存・セッション参照先へ含めない（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|DT外部仕様8.1節]]）。

ツリー上の追加読み込みファイルは主ファイルと区別して表示する（DT外部仕様3.5.1節）。この区別は編集権限の差を表さない。

```ts
// renderer/app/file-browser-panel.ts の render() を拡張（第7B章7.6.3節）
render(): void {
  // 既存: store.filePath と一致するノードへ「編集中」の強調クラスを付与
  // 追加: store.references の各パスと一致するノードへ「追加読み込み済み」の強調クラスを付与（主ファイルとは異なる見た目。編集可否の差ではない）
  // 主ファイルのパスとreferencesのパスは排他集合（開き方の区別であり編集権限の区別ではない）
}
```

色・アイコン等の具体的な様式はDT外部仕様3.5.1節に従って実装時に決める。表示すること自体は同節で規定済みである。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|TECSCDE-DT-EL内部仕様 第7B章（本節が前提とするファイルブラウザ基本設計）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|TECSCDE-DT-EL内部仕様 第7D章（本章#8/#10/#11が実装前提とするresolveImports()の具体設計）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（同、renderer側統合）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（7.5節、7D/7E章の分離元）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（11.2節#7〜#11、本節が解消する決定記録）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様 第3章（3.5.1節、Ctrl+クリック追加の画面規定）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05A 開く（読み込み）|TECSCDE-DT外部仕様 第5章（5.3節、追加読み込みとファイル別保存）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様 第8章（8.1節、通常CDLとPlugin生成CDLの編集可否）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
