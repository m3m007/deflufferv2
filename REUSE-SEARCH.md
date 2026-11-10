# Reuse search for the missing transformation families (2026-11-10)

Owner: "does the work order name other existing rust projects or rust crates
which can do it be modified to do what we need? If not, search GitHub. So we
minimise Bugy Greenfield code. I would rather reuse an existing tested proven
primitive, with glue."

Every candidate below was **run**, not read about. The test input is the work
order's own section 18 acceptance text and its section 7 examples.

## The eight alternatives the work order names

| Project | Language | Licence | What it actually is | Result on the work order's examples |
|---|---|---|---|---|
| friction | Rust | Apache-2.0 / MIT | 12-crate editing engine, forked as the project | Fires on C and D only. Zero on framing. |
| stopslop | Rust | MIT | Linter, 68 rules, 8 categories, 4,306 lines in `rhetoric/` | Zero findings. Detection only, no edit, no lib API. |
| prose-sanitiser | Rust | Apache-2.0 / MIT | 7 crates, `crates/slop` holds design/prose/rules | Statistical metrics, not transformations. |
| prosaic | Rust | — | 122 files | Not the post-processing engine per the work order. |
| unslop | none | — | An agent **skill** (AGENTS.md, SKILL.md, presets, evals), not an engine | 303 pattern strings, mostly documentation. |
| vale-ai-tells | none | — | A Vale YAML style package | Rule data, not Rust. |
| humanize | Python | — | 15 files, 73 patterns | Python; work order forbids it in the runtime. |
| humanist | Python | — | 11 files, 39 patterns | Python; same bar. |
| nlprule | — | — | Clone came back **empty** | Benchmark target for segmentation only. |

## GitHub search, nine queries plus crates.io

    ai slop / defluff / verbose text simplify / wordiness / text simplification /
    plain language rewrite / cliche detection / concise writing / ai writing
    detector / prose linter / ai tells removal / meta commentary removal /
    llm output cleanup / humanize text rewrite

Nothing does the job. The hits and why each fails:

- `pbakaus/impeccable` (107k stars, Rust, Apache-2.0) — "the design vocabulary
  for your coding agent". Design steering, not text compression.
- `mat-1/slopcheck` (54 stars, Rust) — detects AI-authored code in a project and
  its dependencies. Wrong target, and no licence file.
- `SlopLabs/slopos` (31 stars, Rust, GPL-3.0) — an OS written by AI agents.
- `kitten/prosemd-lsp` (178 stars, Rust, LGPL-2.1) — markdown proofreading LSP,
  last pushed 2023-03-26.
- `itto-hiramoto/kaede` (19 stars, Rust, Apache-2.0) — "writing servers
  concisely", about server code.
- `epoko77-ai/im-not-ai` (6,491 stars, Python), `lynote-ai/humanize-text`
  (3,494 stars, Python) — humanisation services, and the work order prohibits
  general-purpose LLM rewriting and Python in the runtime.
- `HugoLopes45/llmstrip` (14 stars, Rust, **MIT**) — the closest miss. "Strip
  LLM writing patterns from prose, code comments, and commits." Its
  `cli/src/rules/text.rs` is 36 KB. **It fires**: "due to the fact that" →
  "because", "In order to" → "To". **It does not fire** on any framing example,
  including "It is worth noting that the build passed."

## Conclusion: no tested primitive does the framing families

Three Rust projects were run. All three cover phrase compression and light
verbs. None covers discourse framing (A), redundant clauses (B), dramatic
framing (E), performative deference (F), unnecessary qualification (H),
self-reference (I), or repetition and artificial conclusions (J).

That is not an oversight in the search. stopslop's `colon_reveal` rule is
explicitly engineered to stay silent on ordinary technical writing, using a
closed reveal-noun set so that "The return value: a boolean" never matches.
It is calibrated for a different corpus. llmstrip targets LLM-ism phrases
("delved", "dig deeper", "could potentially"). friction targets machine-like
documentation prose.

## The reuse-first architecture that follows

Maximum reuse, bounded new code:

1. **friction is the platform.** Fork it. Take `friction-parse`,
   `friction-core`, `friction-edit`, `friction-match`, `friction-nlp`,
   `friction-metrics`, `friction-packs`, `friction-register`, `corpus-tool`,
   `friction-harness`. Keep its operation pipeline, pass loop, convergence model
   and pack mechanism. Build the work order's CLI on `friction-cli`.
2. **stopslop's rule inventory is copied in, not reimplemented.** MIT, 68 rules
   with tests, a `RuleDef` registry, a tier system, prose language detection for
   English and Portuguese, and tree-sitter parsing. Copy the rule files and
   their tests as a friction pack. Its rules become the detection layer that
   feeds `report` and `suggest` modes.
3. **llmstrip's `text.rs` phrase inventory is copied in.** MIT, 36 KB of tested
   LLM-ism phrases, with an integration test suite.
4. **The framing families are the only new code.** Written new, expressed
   through friction's existing operation interface, because nothing tested
   exists for them anywhere on GitHub or crates.io.

The defluffer's 64-cliché corpus is the one prior asset that may already cover
part of family A. That is a Phase 0 ticket decision, item by item.

## Search space of the negative claim

Per the owner's standing rule that a negative claim carries its search space:
GitHub repository search across 14 queries (listed above, both sorted by stars
and unfiltered), crates.io keyword search, and the eight projects named in the
work order, all cloned and read. Not searched: GitLab, sourceforge, or
non-indexed personal repos, and no claim is made about those.
