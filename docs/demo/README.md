# Editor capture

Recorded on 23 October 2026 from the cleanup checkout. The commit containing these files identifies the reviewed source. The host was Linux aarch64 with Bun 1.4.2. The OpenTUI submodule remained pinned to 027d1375196afedbe280699fb5877a068f9d18ad.

```sh
git submodule update --init --recursive
bun install --frozen-lockfile
bun run check
bun run package:build
```

Strict checks passed, including the configuration ledger: 165 settings, 153 effective, 10 incompatible and two missing; 1117 of 1141 checks proved. Those remaining gaps are not counted as passes. The loaded latency audit in AGENTS.md remains open; no performance gate was run or claimed for documentation-only changes.

A genuine 110 × 30 PTY ran the direct source command and the packaged dist/xi binary against a fictional TypeScript file. Each run inserted the final comment, saved with `:w`, checked the actual file bytes and exited normally with `:q`. XDG config/state/data/cache paths were isolated, with an explicit sample config. The image replays the source session through xterm.js; it is not a mock editor. editor.ansi is the original terminal stream and screen.txt records its rendered text.

Reproduce the editing path with the root README commands. `example.ts` contains the saved fixture. The sample config disables automatic formatting: the initial default TypeScript save failed because Biome was absent. No claim is made for formatting, LSP, Git, tasks, multiple selections, all Vim semantics, tutorial behavior or other platforms.

The separate `bun run xi:dev:build` completed, but executing that bundle failed with an unresolved relative `tree-sitter-*.wasm` path. The direct source path and packaged binary worked. This documentation update leaves runtime source, dependency revisions and performance budgets unchanged and does not claim the development bundle is fixed.

The isolated default theme lookup also fell back when its named theme was unavailable. The provided config explicitly selects the built-in xi-light theme; both source and packaged edit/save checks were repeated with that config. This does not qualify every theme.
