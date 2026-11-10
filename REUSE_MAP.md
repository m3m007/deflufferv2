# REUSE_MAP.md — friction Phase 0 audit and reuse decision

Task `t_53bccb0c` (compress phase: friction-audit). Written 2026-11-10.
**Path correction (2026-11-10, during task `t_a73792e9`):** the repo was
renamed from `turbohermes-compress` to `deflufferv2` mid-audit. Git history is
intact (remote `m3m007/deflufferv2`). Line 9 below is kept as the historical
record of where the audit happened, but the live path is
`/home/hermes/projects/deflufferv2`; every later reference to the old path has
been corrected.
Repo audited: `turbohermes-compress` (renamed to `deflufferv2`; fork of
`zerosize-dev/friction` Release 0.6.20, commit `5e52d8a`; local HEAD `7338326`
is 5 commits past it, doc-only: 1,259 insertions of top-level markdown, zero
crate files — verified with `git diff 5e52d8a..HEAD --stat`).

Method: read-only source audit, verified from source and not from the README.
Eight audit lanes ran in parallel (swarm), each writing a cited report under
`/home/hermes/.hermes/kanban/workspaces/t_53bccb0c/lane-*.md`:

| Lane report | Scope |
|---|---|
| `lane-crate-boundaries.md` | crate ownership, dependency tree, external deps, risk flags |
| `lane-api-stability.md` | library-vs-CLI verdicts for the 7 named crates + core |
| `lane-transform-families.md` | the 8 operation kinds, rule inventory, A-J mapping, pass loop |
| `lane-protected-spans.md` | protection mechanisms vs the work order's §9 list |
| `lane-test-coverage.md` | 1,523 tests, snapshots, proptests, determinism gates, gaps |
| `lane-perf-build.md` | profiles, warm-up, caches, rayon sites, embedding costs |
| `lane-packs-extensibility.md` | the four pack extension axes and their costs |
| `lane-core-extension-surface.md` | core extension points, CLI subcommand cost, licence provenance |

The coordinator independently re-verified the load-bearing facts from source
(spine types, dep edges, pass loop, gates, rule counts, licence files, the
absence of A/E/F/I rules — greps recorded in the session log).

## 1. What the 12 crates are and own

| Crate | Owns (from source) | Size |
|---|---|---|
| `friction-core` | shared domain types: `Document`/`Block`/`ProseUnit`/`Sentence`/`Token`, `Patch`/`Tier`, `Finding`, `RuleId`, `MetricVector`, `Envelope`, `Lang`, span validation, `token_class` regex fragments. No parsing, NLP, or metrics. The single leaf: every other crate depends on it. | 1,801 |
| `friction-parse` | markdown → `Document`: pulldown-cmark block tree + prose extraction with byte-exact ranges. Prose excludes code blocks, inline code, link destinations, HTML, footnote markers, checkboxes, frontmatter. | 2,428 |
| `friction-nlp` | SRX segmentation, perceptron POS tagging, arc-eager dependency parsing, inflection/lemmatization, chunking, LVC tables, lexicon. Weights embedded or runtime-installed. | 11,058 |
| `friction-packs` | 19 versioned data packs (inventory, DMS index, attestation, frame program, register bands, jargon, evidence pairs), embedded via `include_str!`/`include_bytes!`, offline by construction. | 15,073 |
| `friction-match` | fix-time detection, six channels (DMS, literal, LVC, contrast frames, jargon, overuse). Never rewrites text. `prose_scope` is the one edit-scope enforcement point. | 5,186 |
| `friction-register` | two separable halves: feature detectors (counts) and transducers (rewrites T4-T13). Consumed only by friction-edit. | 6,830 |
| `friction-edit` | the repair engine: `Engine::fix_document` over a bounded two-pass loop (ritual deletion, substitution, pivot, gated deletion, dejust, frame rewrite) + one restructure pass + one register pass. | 9,139 |
| `friction-metrics` | document-level register diagnostics (symmetry, lexical, rhythm, signals) → `MetricVector` for `check`. | 3,347 |
| `friction-harness` | fixture-driven regression harness: 21 literal fixtures, total-ordered score, accept/reject/rank gates. | 2,916 |
| `friction-cli` | the shipped `friction` binary: `check`/`fix`/`explain`, SARIF/JSON output, mimalloc. Command cores are bin-private. | 4,465 |
| `friction-wasm` | wasm-bindgen wrapper: 6-export contract (`init_engine`, `fix_text`, `check_text`, `suggest_text`, `explain_text`, `engine_version`), heavy assets runtime-installed. | 574 |
| `corpus-tool` | dev-only (`publish = false`) corpus mining, pack generation, adjudication, validation. The offline producer of everything friction-packs embeds. | 20,808 |

Dependency shape (verified from every Cargo.toml, cross-checked with
`cargo metadata --no-deps`): 5-layer DAG, no cycles. `friction-core` is the
leaf; `friction-nlp` (9 dependents) and `friction-packs` (6) are spine crates;
`friction-edit` is the engine layer; CLI/wasm/corpus-tool sit on top. The two
apparent back-edges (edit dev→corpus-tool, match dev→harness) are dev-only and
documented in-source as non-cycles. External risk flags: network access exists
only in corpus-tool (`ureq`, Ollama generation); `srx` in friction-nlp keeps a
build-time `download-binaries` default (ONNX runtime fetch into OUT_DIR) —
relevant for hermetic builds; mimalloc is the only native code in the shipped
binary. `unsafe_code = "deny"` workspace-wide, edition 2024, rust-version 1.96.

## 2. Library API or CLI-shaped?

Work-order question: do `friction-parse`, `friction-edit`, `friction-match`,
`friction-nlp`, `friction-metrics`, `friction-packs`, `friction-register`
expose a stable library API or are they CLI-shaped?

Answer, from source: **all seven are genuine libraries** — `src/lib.rs` only,
no `main.rs`, no `[[bin]]`, coherent pub roots, and de-facto API consumption by
4 sibling consumers each (cli, wasm, corpus-tool, harness, plus engine
crates). None is CLI-shaped. The CLI-shaped code is `friction-cli` (command
cores private to the bin) and `corpus-tool`, both off the named list.

But none is **stable** in the semver sense: all at 0.1.0, never published to
crates.io (the release workflow ships binaries + npm + wasm artifacts only),
no CHANGELOG, no git tags, doc lints disabled. The repo's real stability
instruments pin *output bytes* (insta snapshots, byte-fence corpus discipline,
the wasm 6-export contract), not API signatures. Verdict for all 8 crates
(7 + core): **LIBRARY-BUT-UNSTABLE**.

The practical seam exists today: `friction_edit::Engine::new()` +
`fix_document(source) -> (String, EditReport)` (crates/friction-edit/src/lib.rs:55,91),
`friction_parse::parse`/`parse_with` (crates/friction-parse/src/lib.rs:102,116),
`friction_packs::PackSet::for_lang` (crates/friction-packs/src/registry.rs:549).
There is **no operation trait** anywhere — new transformation families are
added by editing friction-edit/friction-register internals + pack data per
`docs/EXTENDING.md`, not by implementing an interface. "Stable library
consumer" is therefore not an option; the real choice is vendoring.

## 3. Transformation families actually implemented

The 8 operation kinds claimed upstream, where each lives (from source, plus
live `friction fix` probes):

1. **Ritual deletion** — `try_ritual_deletion`
   (crates/friction-edit/src/sentence.rs:718), 9 `[[ritual_frames]]` in
   crates/friction-packs/packs/inventory-en-v1.toml:651+.
2. **Gated span deletion** — `run_deletion` (sentence.rs:1019), 11
   `[[deletion_spans]]` (inventory-en-v1.toml:101+), gate stack
   `check_deletion_gates` (crates/friction-edit/src/gates.rs:125):
   seam-bigram attestation, clause completeness, POS-skeleton.
3. **Paired substitution** — `run_substitution` (sentence.rs:801), 18
   `[[substitution_pairs]]` (inventory-en-v1.toml:273+).
4. **Derivational pivot** — `run_pivot` (sentence.rs:930), max 2/sentence,
   31 `[[lvc_pairs]]` (inventory-en-v1.toml:843+) +
   crates/friction-nlp/src/lvc.rs tables.
5. **Frame-gated `just`-deletion** — `run_frame_dejust` (sentence.rs:1117),
   markers just/merely/simply, detection reused from
   crates/friction-match/src/frame.rs:100.
6. **Frame rewriting** — `run_frame_rewrite` (sentence.rs:1191) over the
   compiled pack frame-pack-en-v1.bin from frame-rules-en-v1.toml (measured:
   rules_ship 282, rules_flip 78, rules_surface 919, rules_pilot 21;
   quarantine/no_evidence/staged_surface are non-compiling evidence buckets).
   Compile fence demotes unattested/human-tilted rules to report-only.
7. **Clause restructuring** — run once after the bounded loop
   (crates/friction-edit/src/document.rs:260): T10-T13 in
   crates/friction-register/src/transduce.rs:1871,2177,2351,2518. Note:
   docs/OPERATIONS.md:53 says two ship; source ships four.
8. **Register rephrasing** — last pass (document.rs:272),
   `run_register` (crates/friction-edit/src/register.rs:559), Wilson-banded
   greedy homing over 5 transducers (T4/T5/T6/T7/T9) + 2 detect-only features.

Pass loop: `MAX_PASSES = 2` bounded repair loop (early break on convergence),
then exactly one restructure pass, then exactly one register pass. Idempotence
pinned by test (third run == second run, byte-for-byte, over fixtures + 50
TRAIN docs).

Against the work order's A-J families:

| Family | friction coverage | Where |
|---|---|---|
| C phrase compression | **full** | ops 3+6, substitution pairs + frame rules |
| D light verbs / nominalisation | **full** | op 4 (31 LVC pairs) + T5 unpack |
| G inflated vocabulary | **full for an adjudicated closed list** (utilize, leverage, showcase, delve...) | op 6 vsub.* rules + sub.utilize/leverage |
| A discourse framing | narrow slice (assertive openers only: "it is important to note that", "in conclusion", "crucially") | deletion spans + opener frame rules |
| J repetition / artificial conclusions | partial (formulaic closing offers via ritual frames; conclusion markers; no content-repetition detection) | ritual frames + conn.conclusion-opener |
| B redundant clauses | **nothing** | no semantic similarity or dedup machinery |
| E dramatic framing | **nearly nothing** (marketing literals only: "thrilled to announce") | k="d" frame rules |
| F performative deference | **nothing** | no rule, no channel |
| H unnecessary qualification | **nothing for hedged forms** (hedges counted, never edited) | features.rs counts only |
| I self-reference | **nothing** (first-person only counted) | features.rs counts only |

Structural reason, verified from source: the engine is a closed-set,
evidence-fenced, gate-checked substitution engine with a no-synthesis
contract (every patch deletes, substitutes a fixed pack string, or derives a
verb via static morphology — friction-edit/src/lib.rs:1-15). Families B/E/F/H/I
need machinery friction deliberately does not have. This matches the prior
live probe (PHASE0-AUDIT.md) and was re-verified by direct grep: no
deference/dramatic-framing/self-reference rules exist in any pack or edit
module.

## 4. Protected-span handling

There is **no dedicated protected-span structure** (no `protected_spans`
module; zero grep hits). Protection is three-layered by architecture:

1. **Parse-time structural exclusion** (crates/friction-parse/src/extract.rs):
   code blocks, inline code, link destinations, HTML, frontmatter never enter
   any prose range, so no operation can match them. Enforced before any
   operation exists.
2. **Scope allowlisting** (crates/friction-match/src/token.rs:129-191,
   `prose_scope`/`is_in_scope`): Paragraph/BlockQuote/ListItem/Footnote
   only; headings and table cells are out of edit scope. The named
   enforcement point, reused by every channel and the edit layer
   (crates/friction-edit/src/document.rs:305).
3. **Per-operation guards**: double-quoted span guard
   `in_quoted_span` (crates/friction-edit/src/gates.rs:267) enforced at 12
   candidate sites across all operations; frame-pack `Guard` targets
   (frame-rules-en-v1.toml, frame channel only); backtick decline in register
   transducers (crates/friction-register/src/transduce.rs:869); identifier
   casing guard (sentence.rs:184).

Against the work order's §9 list: **covered** — fenced/indented code blocks,
inline code, markdown link markup/destinations, frontmatter, quoted material
(double quotes), headings/table cells (out of scope). **Partial** — bare URLs
in prose, shell commands/config outside code spans, structured data inline.
**Missing** — file paths, identifiers (casing-only exception), API/product/
model names, version numbers, **numeric values**, dates, legal language.

The critical hazard for the §18 acceptance test: numbers have no guard.
Digit runs are not even tokens in the detection tokenizer
(`WORD_OR_PUNCTUATION` = letters + `.,;:!?`; crates/friction-match/src/token.rs:46),
so `1,140` is invisible to every channel; word-numerals ("five") are ordinary
tokens with no guard. They survive today only because the closed rule
inventory happens not to fire across them — protection by coincidence, not
construction. The tokenizer's digit-blindness is in fact the accidental
safety property the §18 test currently leans on; a new rule whose span
overlaps a number word would delete it with nothing to stop it. A real
protected-span pass for numbers, paths, URLs, identifiers is a must-build
for the fork (option (a) — extend parse-time exclusion — matches friction's
own architecture and is the least invasive; see
lane-protected-spans.md §5).

## 5. Test coverage and what the tests assert

Measured live: **1,523 `#[test]`** across the 12 crates (corpus-tool 371,
friction-packs 234, friction-nlp 166, friction-edit 150, friction-register
130, friction-match 103, harness 109, cli 81, metrics 62, parse 63, core 54,
wasm 0). Plus: 80 insta snapshots pinning the full byte output of
`check` json/text, `explain`, and `fix` stdout over a pinned 20-doc corpus
selection (crates/friction-cli/tests/snapshot.rs); 2 proptests (parse
round-trip; span exactness); a rayon-determinism gate (1/2/8 threads × 3
reruns in fresh child processes); a full-corpus tagger-determinism CI job;
idempotence over fixtures + 50 TRAIN docs; 3 libFuzzer targets (not
CI-wired); CI gates fmt/clippy/test + holdout discipline; release re-runs the
test suite. Compile check `cargo test --workspace --no-run` exit 0 (~3 min).

What the tests actually assert: byte-exact engine outputs (fixtures +
snapshots), gate semantics (mention_guard, prose_only, diagnostic_only),
per-transducer exact strings over hand-built parses, pack parse/compile
invariants, drift guards forcing TOML↔bin lockstep, determinism across
threads and runs. Gaps relevant to the fork: no stored corpus-wide golden
(byte-fence is a manual two-binary procedure); no performance regression
test (throughput_bench reports, asserts nothing); friction-wasm has zero
tests; guard semantics lack an end-to-end suppression test; 3 engine-fixture
tests are `#[ignore]`d with documented root causes.

## 6. Performance characteristics

From source + the measured prior build (PHASE0-AUDIT.md: clean build 2m17s,
Rust 1.99.0, 8 cores): release profile thin-LTO + codegen-units=1, panic
deliberately unwind (catch_unwind guard around a known pulldown-cmark panic
class). Startup engineered: weights load as zero-copy hash-table views over
embedded `.bin` statics (no HashMap built); packs are LazyLock statics warmed
on 3 detached threads by `friction fix` (registry.rs:549-586); DMS TOML
parse (~90 ms) was eliminated by the precompiled `.bin`. Runtime: bounded
two-pass loop + restructure + register; two per-document sentence caches;
9 ordered-par_iter rayon sites (byte-identical output pinned by test); debug
invariant guards compile away in release; mimalloc in the CLI. The only bench
is an example (`throughput_bench`) that measures ms/KB on ~700 B and ~7 KB
inputs and asserts nothing; the stated target is sub-10 ms/KB. Embedding
cost: ~58 MB of embedded data in the native binary (27.5 MB DMS + 18.5 MB
parser + 3.8 MB tagger weights + ~8.4 MB other packs), with wasm refusing
the three biggest via runtime install seams. Hazard for hermetic builds:
`srx` default features fetch ONNX binaries at build time.

## 7. Licence position

Code, docs, SRX ruleset, curated TOML data: dual **MIT OR Apache-2.0**
(LICENSE-MIT, LICENSE-APACHE, workspace Cargo.toml:8; SRX header
crates/friction-nlp/data/friction-en.srx:5-13 explicitly not derived from
LanguageTool/Okapi). Weights: MIT-clean (gold drafted offline with spaCy
`en_core_web_sm` MIT; nothing embedded; reproduction pinned to
spaCy 3.8.14 / en_core_web_sm 3.8.0 — crates/friction-nlp/weights/NOTICE.md).
Both MIT and Apache-2.0 are permissive and GPL-compatible; dual-licensed
code imposes only notice/attribution retention. **Decision item for the
owner**: the corpus carries 97 CC-BY-SA (2.5/3.0/4.0) and 37 CC-BY human
documents (corpus/manifest.jsonl per-doc licences); corpus-derived
statistical artifacts (evidence packs, envelope bands, frame-rule evidence,
the gold behind the weights) are derivatives of mixed-licence text.
Redistributing or regenerating them under a different umbrella needs the
owner's call on attribution and share-alike; internal use of the forked
artifacts as shipped is the status quo. Flagged to the DECISIONS register,
not decided here. The npm scope (@mhriaznov) and web/ playground hard-code
upstream GitHub-raw coordinates a published fork must re-point.

## 8. DECISION: fork-and-extend

Of the three options the work order names:

1. **Fork and extend** — take the whole workspace as the platform, extend
   in-tree. ✅ **Chosen.**
2. Reuse selected modules — link crates as-is from a separate codebase.
   ❌ Rejected: there is no stable published API (all 0.1.0, unpublished, no
   changelog), no operation trait to implement against, and the extension
   recipe (docs/EXTENDING.md) prescribes in-tree edits to friction-edit,
   friction-register, and the packs. "Reusing modules" without forking
   would mean re-deriving a parallel engine and fighting upstream churn
   with no versioning contract to track.
3. Port selected algorithms — reimplement chosen pieces elsewhere.
   ❌ Rejected: the reusable value is not one algorithm but the platform —
   parse/NLP/pack/match/edit/harness plus 1,523 tests, the byte-fence
   discipline, determinism doctrine, and the corpus pipeline. Porting
   forfeits the tests and the corpus evidence for zero licence or size
   benefit (MIT/Apache permits direct reuse).

Rationale, from the audit:

- friction's infrastructure is exactly the work order's Phase 1 skeleton:
  parsing, segmentation, protected-span foundations (structural exclusion +
  gates), matching channels, packs, metrics, harness, CLI shell, wasm. All
  12 crates are needed, so "selected modules" has no cut line.
- The extension path is real and documented (docs/EXTENDING.md per
  expansion type), the pack layer is a high-value low-friction content
  extension target (typed parse + 4 build-time audits + drift guards), and
  new subcommands are four localized edits in friction-cli.
- The missing families (A beyond its narrow slice, B, E, F, H, I, J beyond
  formulaic offers) are additive work on top of the platform, not reasons
  to abandon it: they slot in as new inventory entries, transducers, and
  gated deletion spans, exactly as T10-T13 and the register transducers
  were added upstream.
- Cost to undo stays low: the fork already exists (m3m007/deflufferv2,
  formerly m3m007/turbohermes-compress, at Release 0.6.20), the licence is
  permissive, and the fork's history so far is doc-only.

## 9. REUSE_MAP — every upstream file the fork builds on

| Upstream file/module (from zerosize-dev/friction @ 5e52d8a) | Reuse as | Why |
|---|---|---|
| `crates/friction-core/src/*` (document.rs, block.rs, patch.rs, finding.rs, rule.rs, span.rs, token_class.rs, metrics.rs, envelope.rs, lang.rs, error.rs) | **keep whole, extend** | the spine: Document/Patch/Tier/RuleId model every new family must emit into |
| `crates/friction-parse/src/lib.rs`, `src/extract.rs`, `src/html.rs` | **keep whole, extend** | markdown→Document prose extraction; the structural-exclusion layer the new protected-span pass extends (parse-time exclusion is the chosen design for numbers/paths/URLs/identifiers) |
| `crates/friction-nlp/src/*` (segment_srx.rs, tag_perceptron.rs, dep_perceptron.rs, dep_arceager.rs, inflect.rs, chunk.rs, lvc.rs, lexicon.rs) + `weights/*`, `data/friction-en.srx`, `data/lexicon-en.toml` | **keep whole** | segmentation/tagging/parsing/inflection backbone, MIT-clean weights |
| `crates/friction-packs/src/*` + `packs/inventory-en-v1.toml`, `packs/frame-rules-en-v1.toml`, `packs/register-en-v1.toml`, `packs/attestation-en-v1.*`, `packs/dms-index-en-v1.*`, `packs/pooled-attest-en-v1.*`, `packs/jargon-*`, `packs/envelope-en-v2.toml`, `packs/*-evidence-en-v1.*` | **keep whole, extend content** | the evidence-fenced rule data; new families add entries/packs here (the well-paved road per lane-packs-extensibility) |
| `crates/friction-match/src/*` (token.rs, literal.rs, frame.rs, frame_rewrite.rs, dms.rs, jargon.rs, overuse.rs, span.rs, tagging.rs) | **keep whole, extend** | detection channels; `prose_scope` stays the enforcement point; new families' detection slots in as channels or frame templates |
| `crates/friction-edit/src/*` (lib.rs, document.rs, sentence.rs, gates.rs, splice.rs, register.rs, restructure.rs, nearnoop.rs, parse_ctx.rs) | **keep whole, extend in-tree** | the engine: new operation families land here as gated functions + pass wiring, per docs/EXTENDING.md |
| `crates/friction-register/src/features.rs`, `src/transduce.rs` | **keep whole, extend** | detector/transducer pattern (T4-T13) is the template for new family implementations |
| `crates/friction-metrics/src/*` | **keep whole, extend** | `check` diagnostics + `MetricVector` telemetry the work order's metrics/profiles build on |
| `crates/friction-harness/src/*` + `docs/research/fixtures.json` | **keep whole, extend** | the regression/scoring harness; the fork's new-family fixtures follow its accept/reject/rank discipline |
| `crates/friction-cli/src/main.rs`, `src/check.rs`, `src/fix.rs`, `src/explain.rs`, `src/common.rs` | **keep whole, extend** | CLI shell; the work order's `process`/`inspect`/`evaluate`/`benchmark`/`rules`/`config` subcommands are four-edit additions on this pattern |
| `crates/friction-wasm/src/lib.rs` | **keep, re-point** | 6-export wasm contract; a published fork must re-point web/npm upstream coordinates |
| `crates/corpus-tool/src/*` | **keep whole** | pack pipeline + acceptance checks (validate/holdout/pack-check); dev-only, network quarantined |
| `docs/OPERATIONS.md`, `docs/EXTENDING.md`, `docs/WASM.md`, `docs/research/*` | **keep whole** | the extension manual and evidence records; the fork's verification ritual inherits the byte-fence |
| `fuzz/fuzz_targets/*` | **keep whole** | the 4-oracle fuzz contract on fix_document |
| `corpus/*` (as-is use; see §7 CC-BY-SA decision item) | **keep, owner decision pending** | training/attestation evidence base |

New code (not from friction, to be written in the fork): the protected-span
extension for numbers/paths/URLs/identifiers; families B, E, F, H, I and the
non-formulaic parts of A and J as new gated operations/transducers/pack
entries; the work order's CLI subcommands, profiles, token measurement, and
provider abstraction (Phase 1+). The alternatives-audit (child task
t_a73792e9) owns the external reuse candidates and records them in
`PHASE0-AUDIT-ALTERNATIVES.md` in this directory; the eight lane reports it
consolidates live in `/home/hermes/.hermes/kanban/workspaces/t_a73792e9/`.

## 10. Corrections recorded during the audit

- Two workers initially mis-verified a sibling lane's file as their own
  deliverable; both were redirected and produced their correct lane files
  (flamingo, skunk). Recorded so the swarm pattern is visible, not silent.
- Upstream doc-vs-source discrepancies found: OPERATIONS.md:53 says two
  restructure constructions, source ships four (T10-T13); README's "848
  rules" vs measured 849 rules_surface rewrites; fix.rs module doc says
  "five-operation" while six sentence-level ops run. The counts in this file
  are the measured ones.
- A live-probe bug worth fixing upstream-side: `sub.will_walk_you_through`
  has no subject-agreement guard ("I will walk you through" → "I covers the
  setup"). The fork inherits this as a known issue for its own family-C
  regression tests.
