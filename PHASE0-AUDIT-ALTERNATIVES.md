# Phase 0 — alternatives audit (task `t_a73792e9`)

Owner work order v1.2 §5 "Additional projects to inspect", audited against the
eight Phase 0 verification dimensions in v1.2 §16. Authority: work order v7
(`WORK-ORDER-v7.md`), rule **reuse before write, name every upstream file copied
or ported**.

This file is the consolidation. The seven per-project lane reports are the
evidence and live beside it in
`/home/hermes/.hermes/kanban/workspaces/t_a73792e9/`:

| Lane file | Project | Pinned HEAD |
|---|---|---|
| `lane-unslop.md` | unslop (theclaymethod) | `17ed39c9d0b522f44190ff0c6233867eadee192a` |
| `lane-stopslop.md` | stopslop (mgiovani) | `2278d4877c7bf07278f4d0819a09ccb0592689d6` |
| `lane-prose-sanitiser.md` | prose-sanitiser (DreamLab-AI) | `9f1c67193e9164717479c0f88a611aa5f7355ca7` |
| `lane-vale-ai-tells.md` | vale-ai-tells (tbhb) | `51f646e366ba7c9dcb078ebeae345b7ff353eb3b` |
| `lane-humanize-humanist.md` | humanize (ccf) + humanist (itsryanlenk) | `db51ff3f405db5fa522e03fdb517b0a4cac846fd` / `7efed2768cebab6404ad98da1f6d647c0da18d66` |
| `lane-prosaic.md` | prosaic (wildmason) | `6307f7a4c2d689f46d03356d38fd1132563bd93a` |
| `lane-nlprule.md` | nlprule (bminixhofer) | `ebb54617ea5f3378c0dc63486631724b7e97e13c` |

All eight HEADs re-verified live at audit time with `git rev-parse HEAD` in
`/home/hermes/projects/upstream/`. Every lane was read-only: nothing in any
upstream repo was modified, committed, built or installed, except that
`nlprule` was cloned during this task (it was the one missing repo) and two
lanes built in their own scratch directories.

Counts in this file are the **measured** ones. Where a lane's number and a
README's number disagreed, the measured number is recorded and the disagreement
is called out. Where I re-measured a load-bearing number myself, it is marked
**[coordinator-verified]**.

---

## 1. The eight Phase 0 dimensions, answered per project

Work order v1.2 §16 asks, for each candidate: (1) language and licence,
(2) algorithm or rule inventory, (3) is it a post-processing engine or something
else, (4) does it beat what friction already has, (5) reusable transformation
logic and every file that would be copied or ported, (6) the cost to port,
(7) what it does not cover, (8) the decision.

| Project | Lang / licence | Inventory | Engine? | Beats friction? | Decision |
|---|---|---|---|---|---|
| **unslop** | Python, MIT **in prose only, no LICENSE file** | 20 scripts / 7,382 lines; 16 literal + 36 regex tells; 494 phrase rows + ~90 regexes in the catalogue | **No** — agent skill + detection layer; `suggest.py` emits `suggested_replacement: null` | **Yes, on 3 things friction has nothing for**: must-preserve constraint taxonomy, silhouette (idea-arrangement) scorer with a committed human reference distribution, adversarial eval corpus | **Port 6 scripts + copy 7 data assets** |
| **stopslop** | Rust, MIT `Copyright (c) 2026 Giovani` | 57 rules (`SLOP001`–`057`), 122 English regex statics + 11 prose panels, 1,166 tests | **No** — linter; `Diagnostic.fix` is a human-readable hint, never applied | **Partly** — self-reference (I) and discourse framing (A) are real deltas; families B and protected spans it does not have | **Extract pattern data; do not take the engine** |
| **prose-sanitiser** | Rust, dual MIT OR Apache-2.0 | 7 crates / 138 `.rs` / 34,702 lines / 732 tests; Layer A = 1,361,157 codepoint verdicts; 15 slop rules; VarCon 32,523 lines | **Partly** — Layer A unicode strip is a real deterministic rewrite lane; Layer B is an LLM hook | **Yes, on one thing friction has zero of**: invisible Unicode / homoglyph / stego / bidi handling | **Port the unicode crate + the digest-gate pattern; do not take slop tables, media, or the LLM hook** |
| **vale-ai-tells** | YAML for Vale (Go), MIT `Copyright (c) 2025-2026 Tony Burns` | 170 rule files; 3,415 pattern entries **[coordinator-verified]**; 2,354 test cases / 609 negative; 620 `exceptions:` entries | **No** — linter rule data; 2 of 170 rules carry replacement text | **Yes, on breadth** — 1,925 literal tokens vs friction's 18 substitution pairs; families E, F, I get coverage friction lacks | **Port phrase data through friction's attestation pipeline; copy the test + FP corpus** |
| **humanize** | Python, MIT `Copyright (c) 2026 ccf` | 909-line scanner + a 304-feature StoryScope taxonomy with a human/AI gap table | **No** — prompt + counters | **Partly** — the taxonomy is the best-cited research inventory in the lane | **Reference only** |
| **humanist** | Python, MIT, **with a CC BY-SA 4.0 carve-out** | 42-rule checker + FP corpus discipline | **No** — checker reports, never edits | **Partly** — the FP-guard methodology is the best engineering in either repo | **Reference only; the vendored catalog is licence-blocked** |
| **prosaic** | Rust, dual MIT OR Apache-2.0 | 14 crates, 1,401 tests; 2,381-line discourse tracker; 1,509 lines of English grammar | **No — the opposite problem.** It *generates* text and avoids repetition; we *remove* repetition | **No** | **Study only, port nothing** |
| **nlprule** | Rust MIT OR Apache-2.0, **rule binaries LGPLv2.1** | 3,749 compiled grammar rules / 14 categories; English SRX 77 rules vs friction's 6; `grammar.xml` 1,642 rules + 714 rulegroups; stale since 2022-02-04 | **Yes** — `Rules::correct` rewrites (verified live: `"She was not been here since Monday."` → `"She was not here since Monday."`) | **No, on both axes.** Segmentation: 18/98 golden disagreements (all over-splits on title abbreviations) and 76.6x slower. Grammar: friction has none, but 46% of the rules are typos/collocations and **0 measured hits** on nominalization, deference and inflated vocabulary | **Do not adopt. Rule data: LGPLv2.1 (+ a GPL portion), do not copy** |

---

## 2. The five findings that matter

### 2.1 Two licence findings change what is legally available

**humanist's vendored pattern catalog is CC BY-SA 4.0, not MIT.** The repo
measures rather than asserts it: 618 words across 51 maximal verbatim runs of
≥6 words = 27.5% of the operative catalog, derived from Wikipedia's *Signs of
AI writing*. ShareAlike is not satisfied by MIT, so nothing from
`plugins/humanist/skills/humanist/third_party/humanizer/SKILL.md` can be copied
under the humanist MIT grant. This is the hardest licence constraint found in
Phase 0. (`docs/attribution.md` §2, `NOTICE.md:21-41`.)

**nlprule's rule binaries are LGPLv2.1** (LanguageTool v5.2). `binaries/LICENSE`
is the LGPLv2.1 text and `binaries/README.md:1-3` says so explicitly. nlprule's
own code is MIT OR Apache-2.0, but the `*.bin` data is not. An LGPL rule set
cannot be copied into a permissively-licensed Rust workspace.

**unslop has no LICENSE file at all.** MIT appears only in `README.md:512` and
`SKILL.md:4`. If anything is ported, the fork must **write its own MIT notice**
naming upstream, author (`claytonkim`) and pinned commit, and record the copy in
`THIRD-PARTY.md`. Documented gap, not a blocker.

**VarCon is clean and is the only verbatim-copyable dataset found.** Permissive
(Atkinson/Titze/Kuenning notices), sha256
`75af63da46ec12d7eb14b9f1ba8d3898d484dd6872755b73c921b215875a3629`, 32,523
lines, vendored with a sidecar that explicitly warns off the GPL/LGPL
alternatives. **[coordinator-verified: hash and line count reproduced exactly.]**

### 2.2 friction's invisible-Unicode hole is real and exactly one crate closes it

friction protects identifiers, paths, URLs and numbers by parse-time structural
exclusion plus a handful of per-op guards. It has **zero** invisible-Unicode
handling: no zero-width, no confusables, no bidi policy. A zero-width-joined or
homoglyph-wrapped identifier is prose to friction and can be rewritten.
`prose-sanitiser`'s `crates/unicode/` is a deterministic codepoint-decision
engine over 1,361,157 verdicts with a SHA-256 golden gate, and it includes
**stego decoding**, not just detection.

**[coordinator-verified: `grep -rln 'zero_width\|U+200B\|invisible'` over
`crates/*/src/` returns 9 files, and every "invisible" hit is prose inside a
doc-comment, not handling code.]**

### 2.3 Every candidate's tell inventory lacks friction's core safety property

friction refuses to ship a rewrite without attestation: every
`deletion_span`, `substitution_pair` and `ritual_frame` carries `source` ∈
{seed, mined, mined-paired, curated-seed} and most carry measured corpus counts.
**None of the audited inventories has this.** vale-ai-tells has 68 of 170 rules
carrying a *human-corpus* FP count, which is a different quantity. stopslop's
`RuleDef` has no evidence fields at all. Dropping any of these phrase lists into
friction's packs without the gate stack would regress exactly the property that
makes the fork trustworthy.

The port is therefore never "copy the files". It is "run the phrases through
friction's own mining/attestation pipeline, or hand-curate each one". The owner
decision between those two routes changes the cost by roughly 10x and is still
open.

### 2.4 friction's biggest structural gap is the one unslop already solves

friction's audit records that numbers, file paths, identifiers, version numbers
and dates are **missing** as protected spans, and that digit runs are not even
tokens in the detection tokenizer, so `1,140` is invisible to every channel.
unslop's `extract_constraints.py` + `validate_preservation.py` contain most of
the missing pass in ~600 lines: 22 constraint families, currency-magnitude
comparison (`$47.3M` ≠ `$47.3 billion`), the `12`-in-`120` whole-number guard, a
28-family unit-synonym table, time variants, quarter ordinals, version numbers,
file paths, and four semantic-drift warnings (negation drop, scope-word loss,
conditional drop, weak-modal→strong-modal strengthening).

The risk is named in the lane report and should be treated as load-bearing:
friction's digit-blindness is the accidental safety property today, so widening
the tokenizer to admit digits is the risky half of the port, not the safe half.

### 2.5 Two upstream repos are failing their own integrity gates at the pinned commits

- **unslop**: `python3 scripts/check_packs.py` lists exactly **32** of the 62
  manifest categories as having no implementation. **[coordinator-verified: the
  command output lists 32 names, e.g. `academic_excess`, `colon_reveal`,
  `reasoning_chain`.]** The 62-category taxonomy is documentation, not rules.
- **vale-ai-tells**: `TODO.md:5` says `AIAdjectiveNounPairs` "stays at `warning`
  level pending false positive calibration", but the file is at `level: error`
  and its FP section is still marked "Intentionally sparse".
  **[coordinator-verified: `grep level styles/ai-tells/AIAdjectiveNounPairs.yml`
  → `level: error`.]**

Both are honest-recorded upstream states, not port blockers, but both mean the
README numbers cannot be taken at face value.

---

## 3. Per-project port candidates (every file, exact path, licence, action)

The friction pack target format is `crates/friction-packs/packs/inventory-en-v1.toml`
and its parser `crates/friction-packs/src/inventory.rs`. The parser enforces
closed sets: `Anchor` ∈ {sentence_initial, mid_sentence, trailing},
`RepairKind` ∈ {delete, diagnostic_only}. A substitution's replacement must pass
`check_closure` (`validate.rs:273-316`) and `check_disjointness`.

### 3.1 unslop — port now (6 scripts + 7 data assets)

Pinned `17ed39c9`. MIT (prose only — see §2.1). Ladder steps 3 and 4; the Python
is a source, the Rust is the artifact. **No Python enters the runtime.**

| # | Source file | Action | What it gives | Difficulty |
|---|---|---|---|---|
| 1 | `scripts/extract_constraints.py` | port-adapt | 22 constraint families + proper-noun/bare-number passes, span dedup | Low-medium; tokenizer widening is the risky half |
| 2 | `scripts/validate_preservation.py` | port-adapt | Type-aware comparison + 4 semantic-drift warnings | Medium, ~280 lines of pure functions |
| 3 | `scripts/banned_phrase_scan.py` | port-adapt | 16 phrases + 36 regexes, masked-span scan, 5 domain suppressions, O(n log n) containment sweep | Medium |
| 4 | `scripts/structure_scan.py` | port-adapt | 14 macro metrics; check overlap with `friction-metrics/{rhythm,symmetry,signals}.rs` first | Low-medium |
| 5 | `scripts/silhouette_scan.py` + `evals/fixtures/silhouette/human_reference.json` | port-adapt + copy-in | 5 discourse metrics + committed human reference distribution | Medium |
| 6 | `scripts/_lang.py` | port-adapt | 77-word function-word table, English decline, prose-view stripper | Low |
| 7 | `scripts/calibrate_pairs.py` | port-adapt | 5 reversible transforms with `NotExpressible` refusal discipline | Medium-high |
| 8 | `scripts/check_suggestions.py` | port-adapt (design) | 4-gate acceptance contract for any rewrite | Low |
| 9 | `scripts/suggest.py`, `diff_check.py`, `readability_metrics.py` | port-adapt | Detector→rewriter interface, over-edit guard, readability | Low |
| 10 | `references/taboo-phrases.md` | copy-in as rule source | 494 phrase rows + ~90 human-reviewed regexes | Each entry needs its own red-first treatment |
| 11 | `evals/fixtures/pairs/` (17 pairs) | copy-in | Minimal-pair FP/FN discipline friction lacks | — |
| 12 | `evals/core-benchmark.json`, `core-benchmark-v2.json`, `core-holdout-v9.json` | copy-in | Typed `protected_spans` + `constraints` corpus | — |
| 13 | `evals/fixtures/contracts/scanner-examples.json` (41), `preservation-examples.json` (10) | copy-in | Executable contract rows | — |
| 14 | `evals/adversarial-evals.json` | copy-in (reference) | 29 adversarial rows | — |
| 15 | `references/{core-contract,fact-preservation,edit-library,rubric}.md` | copy-in (reference) | 24 worked before/after patterns, 8-dimension rubric | — |

**Not reusable:** `wiki_sync.py` (network), all `SKILL.md` / `references/commands/*`
prompt files, the voice-* and harvest-* scripts, the 32 unimplemented pack
categories.

### 3.2 stopslop — extract data, do not take the engine

Pinned `2278d487`. MIT `Copyright (c) 2026 Giovani`. **Corrects POLICY.md §2: the
Portuguese mirror-regex count is 42, not 105.** **[coordinator-verified: 27
source files carry Portuguese, confirmed; the regex count of 42 comes from the
lane's grep of `_PT_BR` `LazyLock<Regex>` declarations.]**

Highest-value extractions:

| Source file | What it gives | Difficulty |
|---|---|---|
| `src/prose_words.rs` | 11 English regex panels; `VOCAB_TIER1/TIER2` is already a weighted closed list with a one-tier-per-word invariant | Low to extract, high to admit |
| `src/rules/verbosity/weak_verb.rs` | A tested 14-entry phrase→fix table (`made a decision`→`decided`) — literally friction's family C + D in stopslop's dialect | **Lowest-friction port in the repo** |
| `src/rules/artifact/residue.rs` | The I-family payload: self-ID, knowledge-cutoff, refusal, reasoning-chain, opener/closer/ack-loop groups | High but highest value; only the `RE_ANYWHERE` group ports without a schema change (~20 entries) |
| `src/rules/rhetoric/{opener,contrast,colon_reveal,puffery,recap,outline_section,parallelism,promo}.rs` | Families A, E, J patterns | Medium |
| `src/rules/verbosity/{hedging,filler,vocabulary,hyphen}.rs` | Families H, G phrase lists | Medium; mostly confirms what friction already ships |
| `src/rules/sourcing/weasel.rs` | Family H attribution patterns | Medium |

**Structural blockers, both requiring an owner decision:** friction's `Anchor`
has no block/line/paragraph concept, and stopslop's density rules
(`N >= max(3, ceil(3 * words / 1000))`) have no pack family at all. Realistic
yield of the highest-value slice: ~120-150 candidate patterns, of which perhaps
40-60 survive as deletion spans or substitution pairs without inventing
anything.

### 3.3 prose-sanitiser — port the unicode crate and the digest-gate pattern

Pinned `9f1c671`. Dual MIT OR Apache-2.0.

| # | Source path | Action | What it gives |
|---|---|---|---|
| 1 | `crates/unicode/src/{lib,tables,rules,decide,confusables,stego,bidi,check,report}.rs` | **port** | Layer A codepoint decision engine. Closes friction's zero-coverage invisible-Unicode hole. Acceptance: a golden digest over friction's own codepoint×context×mode surface + a must-strip/must-preserve harness |
| 2 | `crates/cli/tests/layer_a_parity.rs` + `fixtures/layer_a_decisions.json` | **port the pattern, not the data** | The measured-rebaseline discipline: a table change ships a measured diff, a retained superseded digest, and a reason string. The most transferable engineering artefact in the repo |
| 3 | `crates/core/src/{confidence,fixability,severity,finding}.rs` | port conceptually | Three-axis finding model + "only `Fixability::Mechanical` may be auto-fixed" |
| 4 | `crates/core/src/suppress.rs` | candidate | Vale-compatible HTML-comment suppression; friction has none. Decide after checking the pack format |
| 5 | `crates/uk/data/varcon.txt` + `LICENSE-VarCon` + `build.rs` | copy verbatim permitted | The only verbatim-copyable data in the repo. Dialect, not a compression feature. The licence header is worth copying as a template regardless |
| 6 | `crates/uk/src/exclude.rs` | read as a cross-check, do not port | Friction's parse-time structural exclusion is strictly stronger |

**Not reusable:** `crates/slop/` (11 of 14 ids are judgement-tier tells; would
reintroduce the unmeasured-rule class friction's demotion fence exists to
demote), `crates/slop/src/design/` (a CSS linter despite the path),
`crates/cli/src/rewrite/` (LLM hook), `crates/media/`, `crates/server/`, the
website crawler, and the `ps-eval` TPR@1% numbers (not in the repo, therefore
not citable).

### 3.4 vale-ai-tells — port the phrase data through attestation

Pinned `51f646e`. MIT `Copyright (c) 2025-2026 Tony Burns`.

**[coordinator-verified, independent recount with `ruamel.yaml`: 3,415 pattern
entries = 3,305 `tokens:` + 30 `raw:` + 80 `swap:`; 156 of the regex tokens
carry lookaround. The lane reports 3,433 and 175. The ~18-entry difference is a
classification-heuristic difference on tokens that are neither plain literals
nor obvious regexes, not a counting error. Use the lane's per-file counts, not
either aggregate, when sizing a port.]**

**[coordinator-verified: 170 test files, 2,354 cases, 609 `absent:` (25.9%) —
exactly the lane's numbers.]**

Top port candidates, all MIT, all pure data:

| Source path | Target | Why |
|---|---|---|
| `styles/ai-tells/HedgingPhrases.yml` (71 literals) | deletion_spans | Family H, friction has nothing |
| `styles/ai-tells/SycophancyMarkers.yml` (20) | deletion_spans | Family F, friction has nothing |
| `styles/ai-tells/SelfReference.yml` (46) | deletion_spans / ritual_frames | Family I, friction has nothing |
| `styles/ai-tells/{UrgencyInflation,PromotionalPuffery,NarrativePivots}.yml` (53/55/53) | deletion_spans | Family E |
| `styles/ai-tells/OverusedVocabulary.yml` (168) | substitution_pairs / deletion_spans | Family G; dedup against friction's closed list first |
| `styles/ai-tells/{OpeningCliches,ClosingPleasantries}.yml` (92/99) | ritual_frames | Families A/E and F/J |
| `styles/ai-tells-experimental/VocabularySwap.yml` (71 swaps) | substitution_pairs | Already in replacement form; multi-option values need a choice rule |
| `styles/ai-tells/HouseStyle.yml` (9 swaps) | substitution_pairs | The only rule Vale can actually rewrite |
| 19 rules' `exceptions:` lists (620 entries) | port alongside their rule | The FP-suppression logic; maps onto `unless_followed_by` |
| `tests/**/*.test.yml` (170 files, 2,354 cases) | copy as evaluation asset | 26% negative assertions — the part friction's suite lacks most |
| `test-false-positives.md` (1,686 lines, 134 sections) | copy as evaluation asset | The negative corpus friction lacks |
| `tools/corpus-build.sh` | copy as methodology | The pre-LLM-corpus recipe, independent of Vale |

**Not reusable:** Vale (Go binary), the 9 Tengo scripts, the 3 metric rules, the
`.vale*.ini` configs, the agent template, the vocab allowlist, the third-party
Google/write-good/proselint styles, `CHANGELOG.md`, `README.md`.

**The blocking unknown:** Vale's `existence` semantics (`nonword: true` on 94
rules, code-span masking, paragraph-as-unit scope, the 3.17→3.24 `%%`-escape
breakage) cannot be reproduced without the binary, which is not installed. A
ported rule's hit set will differ. This needs an owner decision before any port
work starts.

### 3.5 humanize + humanist — reference only

Both are prompts plus Python checkers; neither rewrites. humanize's StoryScope
taxonomy (304 features with a human/AI gap table) is the best-cited research
inventory in the lane. humanist's `tests/fp_guard.py` + 24-document provenance
manifest is the single best piece of engineering in either repo and is worth
copying as a *method*. The vendored humanizer catalog is licence-blocked
(§2.1). `ai-tropes.md` is seeded from tropes.fyi, which states no licence;
attribution is the safe course.

### 3.6 prosaic — study only, port nothing

It solves the opposite problem. Its 2,381-line Centering-Theory discourse
tracker, 1,509 lines of hand-written English grammar and 7,834-line engine all
serve *generating* text and *avoiding* repetition. TurboHermes-compress removes
repetition from text that already exists. Porting `DiscourseState`/`Session`
would break friction's idempotence and rayon-determinism gates. The one
transferable idea is a design pattern: deterministic anti-repeat ring buffers
with a family-budget gate, to be clean-room reimplemented inside
`friction-match` if a family-J detector is ever wanted.

### 3.7 nlprule — segmentation study, rule data LGPL

Pinned `ebb54617` (2022-02-04, v0.6.4) — **~4.5 years with no commits**;
the gap between the `0.6.4` tag (2021-04-24) and HEAD is a single docs-link
fix, last real code commit 2021-06-07. That staleness is itself a finding and
it bit the lane directly: the crate's own `compile` binary does not build
against current dependencies (7 errors, clap 3.0-beta.1 → 3.2 API rename).

**[coordinator-verified: read directly from the lane's raw benchmark output
`nlprule-scratch/bench_out.txt`, 173 lines, process confirmed exited.]**

### Segmentation: friction wins outright

| Measurement | friction `SrxSegmenter` | nlprule `Tokenizer::sentencize` |
|---|---|---|
| friction's 98 golden cases vs the golden file | **0 of 98 disagree** | — |
| agreement with friction on the golden set | — | **80 agree / 18 disagree (18.4%)** |
| 32 hard cases (abbreviations, decimals, ellipses, quotes, brackets, URLs, dashes) | — | **24 agree / 8 disagree** |
| 50 real docs (25 human + 25 LLM from `corpus/`) | 30 identical / 20 differing | |
| corpus throughput, 50 docs / 317,696 bytes | **0.261 s → 5,936 KB/s, 0.168 ms/KB** | **19.995 s → 77.6 KB/s, 12.889 ms/KB (76.6x slower)** |
| full `pipe` (segment + tag + chunk + disambiguate) | — | 240.079 s → 6.46 KB/s, 154.8 ms/KB |
| sentence count over the corpus | 11,590 | 12,075 (+485, +4.2% over-splitting) |

**Every one of the 18 golden disagreements is nlprule over-segmenting.** It
splits on `Mr.`, `Mrs.`, `Dr.`, `Prof.`, `St.`, `Rev.`, `Gen.`, `Capt.`,
`approx.`, `etc.`, `U.S. Dept.`, and arbitrary initials (`W. E. B.`, `J. R. R.`,
`T.`) — precisely the nonbreaking-prefix cases an SRX ruleset exists to handle.
On `Mr. and Mrs. Smith met Dr. Jones.` nlprule produces 5 sentences where
friction produces 2. It also splits on ellipses. The corpus result is the same
story: 4.2% more sentences. The lane traced the cause to nlprule's own SRX
`afterbreak` rule `[^\p{Lu}]|I`, which declines when a capitalized word
follows.

Why the speed gap matters for a port: friction compiles 5 regexes once from a
**6.3 KB embedded ruleset**. nlprule runs the same SRX algorithm but
deserializes an **11.6 MB bincode tokenizer** first and does FST dictionary
lookups per sentence. The 12.9 ms/KB is the tokenizer's cost, not the
algorithm's.

### Grammar: real corrector, wrong data, wrong subject

Measured from the compiled `en_rules.bin`: **3,749 grammar rules across 14
categories** — GRAMMAR 1,450, TYPOS 798, CONFUSED_WORDS 723, COLLOCATIONS 209,
REDUNDANCY 133, STYLE 97, PUNCTUATION 102, TYPOGRAPHY 61, PLAIN_ENGLISH 81,
CASING 35, NONSTANDARD_PHRASES 25, COMPOUNDING 19, SEMANTICS 11, WIKIPEDIA 5.
(The XML source has 1,642 `<rule>` elements plus 714 `<rulegroup>` elements;
the compile step flattens rulegroups, hence the larger compiled count.)

`Rules::correct` **is a rewriter** — `rules.rs:139-152` calls `suggest` then
`apply_suggestions` splices `replacements()[0]` in. Verified live:
`"She was not been here since Monday."` → `"She was not here since Monday."`
It picks the first replacement when several are offered, which is a blunt
instrument against friction's "never invents content" contract.

**Coverage of the compression engine's five tell families is essentially nil.**
Measured, 0 suggestions on: inflated vocabulary (`"performed an analysis … in
order to facilitate the implementation"`), LVC (`"performed an analysis of the
logs"`), `in order to` (the rule exists in XML at `grammar.xml:83353` but is
`default="off"`), performative deference (`"It is important to note that …"`),
hedging beyond one redundant bigram, and nominalization (`"The implementation
of the validation of the configuration resulted in the reduction of the error
rate."`). Two partial hits exist: `REDUNDANCY/MIGHT_PERHAPS/0` and
`REDUNDANCY/BASIC_FUNDAMENTALS/0`. All PLAIN_ENGLISH probes returned 0 because
that category — the most relevant one — is `default="off"` upstream
(`grammar.xml:87119`). Controls were respected: code-bearing prose
(`"The parser returns a Vec of tokens."`, ``"Run `cargo test` before pushing."``)
was left unchanged.

46% of the rule set (TYPOS + CONFUSED_WORDS + COLLOCATIONS = 1,730 of 3,749)
is generic typo correction, which is a different product. Grammar throughput
is 205-214 ms/KB (`suggest` 63.72 s, `correct` 66.43 s over the same corpus),
i.e. 1,274x slower than friction's segmenter alone.

### Licence: the rule data is LGPLv2.1, with a GPL portion inside

`binaries/README.md:1-3` (verbatim): *"The nlprule binaries (`*.bin`) are
derived from LanguageTool v5.2 and licensed under the LGPLv2.1 license. …
Under LGPLv2.1 §6(a) this does not have any implications on the license of
nlprule itself."* `binaries/LICENSE` is the LGPLv2.1 text. The rule sources
carry their own header: `enzip/en/grammar.xml:1-30` names *"Copyright (C)
2001-2019 Daniel Naber, Marcin Miłkowski and the LanguageTool contributors"*
and notes that *"Portions of rules are converted from After The Deadline
grammar checker … licensed under GNU GPL"* — so there is a **GPL** component
inside the LGPL bundle.

The §6(a) argument is correct only for *linking* nlprule-as-a-library. It does
not make the rule data permissive. Copying `en_rules.bin`, or porting
`nlprule/src/compile/` to re-derive it, into the deflufferv2 workspace means
distributing an LGPLv2.1 (+ GPL) derivative in an MIT/Apache-2.0 workspace.

### Build cost, measured

| Step | Result |
|---|---|
| `cargo build --release -p nlprule` | **2m21s**, 53 crates, exit 0 |
| `cargo build --release --bin compile` | **FAILED, exit 101**, 7 errors (clap API rename) |
| Workaround `mkbins` bin (12 lines, no clap) | **2m01s**, exit 0 |
| Generating the `.bin` files from the build dir | **16.4 s** |
| Bench crates | 1m22s each |

Dependency tree: 150 crates, 21 direct, including **`onig 6.5.3`** (→
`onig_sys` → `cc` + `pkg-config`, i.e. a **C library build**), `rayon`,
`rayon-cond`, `fst`, `bincode`, `srx 0.1.4`. The `onig` C dependency is a
real cost: friction's workspace has no C dependencies, and `friction-wasm`
would inherit it.

The `.bin` files total **19.2 MB of derived data that must ship with the
crate**, against friction's 6.3 KB embedded SRX.

### The one thing worth reading

`nlprule/src/utils/regex.rs` (492 lines): a pluggable onig / fancy-regex
backend behind one `Regex` type, with a `regex-all-test` cross-checking
backend that runs both engines and asserts equivalence. Port the
*backend-swap + equivalence-test* pattern, not the file.

---

## 4. What none of them cover

Friction's gap list survives this audit almost intact:

- **Family B (redundant clauses)** — nothing in any of the eight repos does
  cross-clause redundancy, semantic similarity or dedup. vale-ai-tells'
  `README.md:410-437` "Known patterns not covered" independently confirms this
  from the other direction. Still a must-build.
- **Protected spans for numbers/paths/URLs/identifiers/versions/dates** — only
  unslop has a real implementation, and it is 600 lines of Python, not Rust.
  Still a must-build, now with a reference implementation.
- **Evidence fencing** — friction's advantage over all eight, not a gap.
- **A heading-scoped edit channel** — 7 vale-ai-tells rules and several stopslop
  rules are heading-scoped; friction's `prose_scope` excludes headings from edit
  scope. Widening it is a safety decision, not a port.
- **A density/occurrence channel** — 3 vale metric rules, 2 vale occurrence
  rules, ~6 stopslop density rules, and unslop's structure metrics all need a
  channel friction does not have.

---

## 5. Decisions this audit forces on the owner

1. **Attestation route.** Do ported phrases go through friction's
   `corpus-tool mine-inventory` / `mine-paired` pipeline, or through hand
   curation? This is the single biggest cost lever, roughly 10x, and it is the
   difference between a defensible port and a regression.
2. **Anchor schema.** Extend `Anchor` with block/line/paragraph variants (closes
   stopslop's SLOP011 opener/closer groups and several vale heading rules), or
   accept `MidSentence` and lose the precision that makes those rules work?
3. **Widen the tokenizer past digit-blindness?** This is required to port
   unslop's constraint extractor, and it is the removal of an accidental safety
   property. It should be its own task with its own acceptance test.
4. **Vale semantics without Vale.** Install Vale to validate ports (it is not
   installed and is Go/MIT, so it is a dev-only dependency), or accept that the
   2,354 test cases cannot serve as ground truth and rebuild the harness?
5. **Heading scope.** Widen edit scope to headings, build a separate heading
   channel, or drop the 7 heading-scoped rules?
6. **Is a UK/US dialect pack in scope?** VarCon is the only verbatim-copyable
   data found, and it is a dialect table, not a compression feature.
7. **Is a density/metric family wanted at all?** If the fork's contract is
   "delete, substitute a fixed pack string, or derive a verb", then ~11 rules
   across three repos are structurally inadmissible and only their phrase lists
   are portable.

---

## 6. Corrections recorded during this audit

- **POLICY.md §2's "105 Portuguese mirror regexes" is wrong; it is 42.** 27
  source files is correct. **[coordinator-verified: the file count.]**
- **REUSE_MAP.md:315 names "llmstrip phrases" and "defluffer corpus"** as the
  alternatives-audit's candidates. The work order v1.2 §5 list is the eight
  repos in this file; llmstrip and defluffer belong to `t_83949f12`
  (defluffer-salvage). Recorded so the two tasks do not overlap.
- **The friction baseline path cited in two lane briefs was stale.**
  `/home/hermes/projects/turbohermes-compress` no longer exists; the project was
  renamed to `deflufferv2/` mid-audit (git history intact, HEAD `6f9a5f7`,
  remote `m3m007/deflufferv2`). Both lanes found this independently and used
  `/home/hermes/projects/deflufferv2/REUSE_MAP.md`. **REUSE_MAP.md itself still
  contains stale `turbohermes-compress` paths and should be corrected.**
- **Vale aggregate token count is heuristic-dependent.** The lane's 3,433 and my
  independent 3,415 differ by classification on ~18 tokens. Per-file counts
  agree. Use per-file counts.
- **Three lanes reported completion before writing their deliverable.** eagle,
  dove and giraffe each sent a summary with no file on disk and were asked to
  write it. Recorded so the swarm pattern is visible, not silent.
