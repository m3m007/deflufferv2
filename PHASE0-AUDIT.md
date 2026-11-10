# Phase 0 — preliminary audit (live probes, 2026-11-10)

Owner work order v1.2. This file records what was measured by running the
forked candidate, not what its README claims. It is the starting data for the
Phase 0 tickets; the tickets own the full audit.

## The candidate

`zerosize-dev/friction` forked as `m3m007/turbohermes-compress`, cloned to
`/home/hermes/projects/turbohermes-compress` at `Release 0.6.20` (`5e52d8a`).
12 crates, dual-licensed Apache-2.0 / MIT. Builds clean on this host in 2m17s
with `cargo build` (Rust 1.99.0, 8 cores, 23 GB, no GPU).

Crate inventory, from `ls crates/`:

    corpus-tool  friction-cli  friction-core  friction-edit  friction-harness
    friction-match  friction-metrics  friction-nlp  friction-packs
    friction-parse  friction-register  friction-wasm

CLI surface is `friction <check|fix|explain>`. There is no `process`, `inspect`,
`evaluate`, `benchmark`, `rules` or `config` subcommand, so the work order's
section 4 CLI has to be built.

## Measured transformation coverage

`friction fix` was run against the work order's own section 7 examples. Results
are verbatim from the binary.

| Work order example | Family | friction result |
|---|---|---|
| "At this point in time we are unable to proceed due to the fact that the build failed." | C phrase compression | **fires** — "At this point in time" → "At this point" |
| "In order to make a decision we must conduct an investigation." | C + D light verbs | **fires** — "In order to" → "To", "make a decision" → "decide" |
| "This is your call and I am not going to make it for you." | B redundant clauses, F deference | **no change** |
| "Everything is working, with one caveat that is your decision to make." | E dramatic framing, F deference | **no change** |
| "One implementation detail worth retaining: the work order deliberately makes friction the primary fork candidate." | A discourse framing | **no change** |
| "There is one important distinction here. The tool should run independently during development." | A discourse framing | **no change** |

The work order's section 18 first acceptance test, run in full:

    $ friction fix t18.txt
    Everything is working, with one caveat that is your decision to make.
    Two builds confirmed running in isolated worktrees. Fork-identity at 24
    minutes, now capturing the Phase 1 baseline: 1,140 passed, 0 failed across
    3 test binaries, with five test processes still going. Phase-1 source
    verification at 8 minutes in its own worktree.

    friction fix: 3 pass(es), 0 patch(es) applied

Zero transformations. `explain` confirms three passes converged with 0
operations fired. The sentence the work order most wants removed is the one
friction leaves alone.

## What this establishes

friction is a strong platform and a partial rule set. It demonstrably owns
phrase compression and nominalisation rewriting (families C and D), and it
brings the infrastructure the work order needs: parsing, protected spans,
segmentation, matching, metrics, packs, a corpus tool, a harness and a wasm
binding.

It does **not** own the families that give the work order its purpose:
discourse framing and meta-commentary (A), redundant clauses (B), dramatic
framing (E), performative deference (F), unnecessary qualification (H),
self-reference (I), and repetition and artificial conclusions (J).

That gap is not a defect in friction. friction describes itself as removing
machine-like language from technical documentation, and phrase-level rewriting
is what that task needs. The work order targets agent-output framing, which is
a different and larger family set.

## The consequence for the architecture

The implementation decision moves from "fork and extend" to
**fork as the platform, add the missing families**:

- Take from friction: `friction-parse`, `friction-core`, `friction-edit`,
  `friction-match`, `friction-nlp`, `friction-metrics`, `friction-packs`,
  `friction-register`, `corpus-tool`, `friction-harness`. Keep the operation
  pipeline, the pass loop, the convergence model and the pack mechanism.
- Add new operation families for A, B, E, F, H, I and J, expressed through
  friction's existing operation interface rather than as a parallel engine.
- Build the work order's CLI on `friction-cli`, adding the `process`,
  `inspect`, `evaluate`, `benchmark`, `rules` and `config` subcommands.

The defluffer (`turbohermes/turbohermes-hygiene`, 145 tests) was built against
exactly this gap, and its 64-cliché corpus and segmentation reference are the
most likely things to survive the salvage assessment. Whether they survive is a
Phase 0 ticket decision, item by item, not a foregone conclusion.

## Not yet verified

Left for the Phase 0 tickets, which hold the deep audit:

- Whether friction's pack mechanism can express the missing families without
  patching `friction-core`, or whether the operation trait needs extending.
- The protected-span list friction actually implements versus the work order's
  section 9 list.
- Test coverage: what the existing tests assert and where the corpus sits.
- Performance and the dependency tree.
- The alternatives: unslop, stopslop, prose-sanitiser, vale-ai-tells, humanize,
  humanist, prosaic, nlprule.
- `friction-register`: whether register rephrasing already covers part of
  family G.
