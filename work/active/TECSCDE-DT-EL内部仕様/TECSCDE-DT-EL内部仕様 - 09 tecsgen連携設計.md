---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第9章（tecsgen連携設計）— mainプロセスのTecsgenRunnerクラス（child_process.execFile）とrenderer側TecsgenGatewayによるElectron固有のサブプロセス実行実装。2026-09-21、TecsgenCommandBuilderが-k（CDLファイル文字コード指定）を組み立てていないギャップを発見・記録（未検証・未決事項）。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 9 of 11. Electron固有化の中心章の1つ。

## 9. tecsgen連携設計

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様第8章8.4節]]が採用した「tecsgenをサブプロセスとして直接実行する」を、Electronの`child_process`で実現する。コマンド文字列の組み立て（`TecsgenCommandBuilder`）は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|TECSCDE-TS内部仕様第9章]]の設計を**そのまま踏襲、変更なし**——第2章2.3節のとおり、この部分は純粋な文字列処理でありrendererに残る。新規に追加するのは実際の実行部分である。

> [!warning] `-k`（CDLファイルの文字コード指定）が組み立て対象に含まれていない（2026-09-21、tecsgenのCLIオプション調査で発見）
> [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|tecsgen外部仕様第5章]]によれば、tecsgenはCDLファイルの文字コードを`-k, --kcode`（既定`euc`）で指定する。実装（`E:\Ccur\typescript\TECSCDE-DT-EL\src\renderer\tecsgen\command-builder.ts`の`TecsgenCommandBuilder.buildArgs`）は`-I`・`-D`・`-c`のみを組み立てており、`-k`は渡していない。**踏襲元のTS内部仕様第9章では実害がなかった**——ブラウザ版は「コマンド文字列を提示するだけで実行しない」設計（外部仕様8.4.2）だったため、文字コード不一致があってもtecsgenが実際に動くことはなかった。しかしDT-EL版は8.4節でtecsgenを実際にサブプロセス実行するため、この欠落がそのまま実行時の挙動に影響しうる。**(inferred、未検証)**: CDLファイルはUTF-8前提（[[TECSCDE外部仕様]]5.1.2節）だが、tecsgen既定の`euc`のまま渡すと、日本語コメント等を含むUTF-8のCDLファイルをtecsgenが正しく読めない可能性がある。実際に文字化け・構文エラーが発生するかは未検証。対処案（`-k utf8`を`buildArgs`に追加する）は未実装、第11章の未決事項として扱う。

### 9.1 `TecsgenRunner`クラス（mainプロセス）

```ts
// main/tecsgen-runner.ts
export interface CppResult {
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number | null;
  readonly executableFound: boolean;
}

class TecsgenRunner {
  async run(args: readonly string[]): Promise<TecsgenResult> {
    try {
      const { stdout, stderr } = await execFileAsync('tecsgen', args, { timeout: 30_000 });
      return { stdout, stderr, exitCode: 0, executableFound: true };
    } catch (err) {
      const e = err as ExecFileException;
      if (e.code === 'ENOENT') {
        // 実行ファイルが見つからない（第2章2.4節の新規制約）
        return { stdout: '', stderr: '', exitCode: null, executableFound: false };
      }
      return { stdout: e.stdout ?? '', stderr: e.stderr ?? '', exitCode: e.code ?? 1, executableFound: true };
    }
  }

  async preprocess(headerPath: string, cppCommand?: string): Promise<CppResult> {
    // __tool_info__("tecsgen") の cpp 指定、または既定の gcc -E -DTECSGEN
    const cmd = cppCommand?.trim() || 'gcc -E -DTECSGEN';
    const [exec, ...baseArgs] = cmd.split(/\s+/);
    try {
      const { stdout, stderr } = await execFileAsync(exec!, [...baseArgs, headerPath], { timeout: 30_000 });
      return { stdout, stderr, exitCode: 0, executableFound: true };
    } catch (err) {
      const e = err as ExecFileException;
      if (e.code === 'ENOENT') {
        return { stdout: '', stderr: '', exitCode: null, executableFound: false };
      }
      return { stdout: e.stdout ?? '', stderr: e.stderr ?? '', exitCode: e.code ?? 1, executableFound: true };
    }
  }

  async version(): Promise<string | null> {
    const result = await this.run(['--version']);
    return result.executableFound ? result.stdout.trim() : null;
  }
}
```

`run()`は`tecsgen`が非0で終了する場合（構文・意味エラーがある場合、[[TECSCDE外部仕様]]9.1.1の`run2`直前の`exit 1`に相当）も例外として扱われるため、`try/catch`で捕捉し、標準出力・標準エラー出力は失敗時でも保持する——エラーがあってもインポートを中断しない（[[TECSCDE外部仕様]]9.1.2）という方針と同様、実行が失敗してもその出力自体は提示する。

### 9.2 IPCハンドラの登録（main）

```ts
// main/ipc.ts
const tecsgenRunner = new TecsgenRunner();

ipcMain.handle('tecsgen:generate', (_e, args: readonly string[]) => tecsgenRunner.run(args));
ipcMain.handle('tecsgen:preprocess', (_e, headerPath: string, cppCommand?: string) => tecsgenRunner.preprocess(headerPath, cppCommand));
ipcMain.handle('tecsgen:version', () => tecsgenRunner.version());
```

### 9.3 `TecsgenGateway`クラス（renderer）

```ts
// renderer/tecsgen-gateway.ts
class TecsgenGateway {
  generate(args: readonly string[]): Promise<TecsgenResult> { return window.tecscde.tecsgen.generate(args); }
  preprocess(headerPath: string, cppCommand?: string): Promise<CppResult> { return window.tecscde.tecsgen.preprocess(headerPath, cppCommand); }
  version(): Promise<string | null> { return window.tecscde.tecsgen.version(); }
}
```

### 9.4 実行結果の診断への変換

```ts
class TecsgenResultParser {
  // <ファイル名>:<行>:<列>: error|warning: <メッセージ> を解析する（TECSCDE外部仕様9.1.1の書式）
  static parse(result: TecsgenResult): readonly Diagnostic[] {
    if (!result.executableFound) {
      return [Diagnostic.error('E-TECSGEN-NOT-FOUND', 'tecsgen実行ファイルが見つかりません。環境変数PATHを確認してください。')];
    }
    const lines = (result.stdout + result.stderr).split('\n');
    return lines
      .map(line => this.parseLine(line))
      .filter((d): d is Diagnostic => d !== null);
  }

  private static parseLine(line: string): Diagnostic | null { /* 正規表現で書式を解析し Diagnostic.error/warning を構築 */ return null; }
}
```

解析結果は第8章の`DiagnosticsCollector.report()`へそのまま渡す。tecsgen実行結果由来の診断も、CDLインポート時の診断（第8章）と**同じ一覧・同じジャンプ機構**で提示する——[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 09 エラーと警告|TECSCDE-DT外部仕様第9章]]が定める発生源の統合方針をそのままクラス設計に反映したものである。

### 9.5 実行の起点

「実行(Generate)」操作（[[TECSCDE-DT外部仕様]]8.4.2節）はモジュールG（UIシェル）から`TecsgenGateway.generate()`を呼ぶ。実行は利用者が明示的にトリガーする操作に限り、保存やインポートのたびに自動実行しない方針は[[TECSCDE-DT外部仕様]]と同一。

### 9.6 `import_C`のCプリプロセッサ実行とフォールバック

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.1節]]が定める`import_C`の2経路の優先順位を実装する。

1. 第7章7.5節で`import_C`対象のCヘッダが解決された際、rendererは`TecsgenGateway.preprocess(headerPath, cpp)`を呼ぶ。
2. プリプロセッサの実行が成功（`executableFound === true && exitCode === 0`）した場合、展開後の`stdout`テキストをrendererの`CdeclExtractor`（モジュールB、設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|9B章]]）へ渡し、`typedef`／`struct`定義を取り込む。
3. プリプロセッサが見つからない（`executableFound === false`）または実行に失敗した（`exitCode !== 0`）場合は、未展開の生ヘッダテキストに対して`CdeclExtractor`を実行する**フォールバック経路**へ切り替える。
4. フォールバック時は第8章の`W-CPP-FALLBACK`警告を発行し、`#include`未展開・`#ifdef`未評価の差分が生じ得る旨を利用者に提示する。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|TECSCDE-DT-EL内部仕様 第9B章（9.6節が名前を挙げる`CdeclExtractor`自体の設計、2026-09-23）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様 第8章（本章が実装する外部仕様、8.1・8.4節）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|TECSCDE-TS内部仕様 第9章（TecsgenCommandBuilderの一次情報源、`-k`欠落を実害なく踏襲した設計）]]
- [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|tecsgen外部仕様 第5章（`-k`/`--kcode`の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（`-k`欠落の未決事項記録）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（インポート参照先解決）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-DT-EL内部仕様 第8章（診断の集約先・W-CPP-FALLBACK）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（プロセス配置の根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
