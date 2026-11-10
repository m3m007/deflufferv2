# TurboHermes standing policy

**This file is the authority for TurboHermes project policy.** It is read by the
dispatcher (`~/.hermes/scripts/turbohermes-watch.py`) for the model-lane
assignment, and it is pointed to from long-term memory so a fresh session loads
it. It supersedes any recollection; if memory and this file disagree, this file
wins and memory is wrong.

Adopted 2026-11-10 on the owner's instruction: "Go ahead. After that, prune your
memory."

## 1. Model lanes — three models, three roles

Owner's instruction, verbatim: "Glm 5.3 for architecture , step 5 preview for
grunt work, deepseek v4.1 flash for verification."

| Phase | Role | Model |
|---|---|---|
| source-verification | verification | step-5-preview |
| mutation-audit | grunt | step-5-preview |
| fork-identity | grunt | step-5-preview |
| mutation-safety | grunt | step-5-preview |
| jcode-adapter | architecture | step-5-preview |
| persistent-planning | architecture | step-5-preview |

### turbohermes-compress (compression engine, project started 2026-11-10)

Fork of `zerosize-dev/friction` as `m3m007/turbohermes-compress`, pinned at its
`Release 0.6.20` commit, 12 crates, dual-licensed Apache-2.0 / MIT, builds clean
in 2m17s on this host. This project supersedes the defluffer work
(`turbohermes-hygiene`), of which only what survives audit is salvaged.

| Phase | Role | Model |
|---|---|---|
| friction-audit | architecture | step-5-preview |
| alternatives-audit | grunt | step-5-preview |
| defluffer-salvage | grunt | step-5-preview |
| protected-spans-audit | architecture | step-5-preview |
| offline-evaluation | verification | step-5-preview |

Rules:
- A phase's model comes from this table, not from a default and not from
  whatever the previous phase used.
- step-5-preview is the workhorse. Do not spend GLM or Deepseek quota on
  mechanical work: the owner's standing instruction is "make sure deepseek, glm
  and alibaba cloud isnt drained excessively and that step 5 preview is the
  workhorse".
- Classify by what the task DOES, never by the phase name. "Audit" is not a
  role. A source audit that produces an inventory is grunt work; a source audit
  that ends in a structural decision is architecture work. Naming a phase
  "verification" does not make it verification, and this exact keyword error put
  mutation-audit, alternatives-audit and defluffer-salvage on Deepseek while the
  rule above forbade it.
- verification means checking output another lane produced. Producing a new
  artifact is grunt work. Deciding structure that later phases depend on is
  architecture work.

- All three are verified reachable through the LiteLLM proxy on 127.0.0.1:4000.
  Re-verify before a long run; a model that returns empty content at low
  max_tokens is a max_tokens problem, not a model problem.
- jcode's own default is `swarm_model = "inherit"`, so any subagent it spawns
  inherits the lane model automatically. No extra wiring needed for that.

## 2. Language scope — English only (owner, 2026-11-10)

**English only. No Portuguese.**

Applies to every phase of every project. Concretely:

- When copying stopslop's rule inventory in as a friction pack, take the
  English rules and their tests. Drop the `PtBr` mirror regexes and the
  `natlangs: &[NatLang::En, NatLang::PtBr]` entries. 27 stopslop source files
  carry Portuguese, 105 mirror regexes, and none of it ships.
- The work order's corpus item 7, "Multilingual examples for future support",
  is out of scope. Build the seven English corpora only.
- No Portuguese detection, no Portuguese segmentation, no Portuguese test
  fixtures, no Portuguese documentation.
- English dialect is not in scope of this rule: British and American English
  are both English. prose-sanitiser's `crates/uk` is a dialect checker, not a
  second language, and is not excluded by this instruction.

## 3. The fork decision

BlockCell is forked as the TurboHermes supervisor. `m3m007/turbohermes`, parent
`blockcell-labs/blockcell`, pinned `5ca38be861b4a3e8f7a1e8d332e242b42ed25710`.
The architecture document decides this in its first sentence: "Build TurboHermes
as a fork of BlockCell, but do not merge jcode or Graphicle into the BlockCell
runtime." jcode and graphicle are subsystems connected through adapters, never
merged. The fork is an executed phase, never a pending permission.

## 4. Reuse before write

Order, stop at the first that works: use as is, fork and modify, copy in, port
and adapt and merge, write glue only. Greenfield code where a proven tested
primitive exists is a defect, not a choice. The full rule and the approved
sources are in the work order (v7) and `REUSE_MAP.md`.

## 5. Tool set

Six tools, each with a mechanical trigger in the pre_tool guard: rtk, rg,
gitleaks, cargo-deny, cargo fmt and clippy, graphicle. Everything else is
situational. Full policy and the demoted list with reasons: `TOOL-POLICY.md`.

## 6. Quality gates that are not optional

The baseline for the fork is **2,654 tests passing across 32 binaries**, measured
before the rename. After the rename it is **2,657 across 32 binaries, 0 failed**.
Any change that drops below the baseline is a failure, not a rounding note.

## 7. Source documents

- Architecture: `TURBOHERMES-ARCHITECTURE-v2.md` and the owner's core
  architecture document.
- Work order: `TurboHermes_Work_Order_v7.md`. Both texts are orders; where the
  work order is more specific, it wins.
- Reuse map: `turbohermes-fork/REUSE_MAP.md`.
- Decisions: this directory's `DECISIONS.md`.

## 8. Review trigger

Re-read this policy when the owner asks, when a lane's model stops responding,
or when a phase's role is ambiguous. The review question is always: does the
running system actually do what this file says?

## 9. The audit gate — no citation, no build (owner, 2026-11-10)

Owner: "You need to audit every step you take in future. Time and time again you
hallucinated non existent rules and made up stuff, substituting your ideas for my
judgement and clear instructions."

**Rule.** Every ticket, phase, rule or task must carry a `SOURCE:` line quoting
the owner's words or the work-order line it implements. The dispatcher refuses to
dispatch a ticket without one. This is enforced in
`scripts/turbohermes-watch.py` by `source_citation()` and tested both ways: an
uncited ticket is refused, a cited ticket passes.

**Why mechanical and not a promise.** The fork-identity ticket cost 327,364
tokens on work that appears in no owner document. The word "identity" occurs
nowhere in work order v7; its only appearance in any owner document is in the
v1.2 acceptance test, where the owner himself wrote "Fork-identity at 24 minutes"
describing the status of his own builds. I read a progress report as a work item.
An intention to be more careful does not survive contact with optimism. A gate
that refuses does.

**Audit result, all ten tickets checked against the work order's phase list:**

| Ticket | Phase | Verdict |
|---|---|---|
| t_0e21e9aa | source-verification | REAL — v7 "verify every source at a pinned commit" |
| t_750043a8 | mutation-audit | REAL — v7 "Phase 1 Assessment: mutation-pipeline audit" |
| t_cad97583 | mutation-safety | REAL — v7 "Phase 2 Fork and supervisor: mutation safety" |
| t_33ad8c8c | jcode-adapter | REAL — v7 "Phase 3 jcode integration" |
| t_86892825 | persistent-planning | REAL — v7 "Phase 3A Persistent planning" |
| t_a4e74c16 | fork-identity | **INVENTED — archived** |
| t_53bccb0c | friction-audit | REAL — v1.2 section 16 Phase 0 |
| t_a73792e9 | alternatives-audit | REAL — v1.2 section 5 |
| t_83949f12 | defluffer-salvage | REAL — owner chat, quoted |
| t_f31d1c27 | protected-spans-audit | REAL — v1.2 sections 9 and 16 |

One of ten was fiction. All ten now carry a citation.

**Corollary, the owner's second point.** Downloading a repository from GitHub at
a pinned commit *is* the verification. Re-proving the provenance of something
already authenticated by the act of obtaining it is waste, not diligence. This is
a one-person research server, not an enterprise audit target.

## 10. Hard model ban — step-5-preview only (owner, 2026-11-10)

Owner: "NEVER AGAIN USE GLM or deepseek WITHOUT MY Explicit instruction or
approval. You clearly  lack judgement skill."

**Banned without per-task approval given in chat:** `glm-5.3`, `glm-5.3-air`,
`deepseek-v4.1-flash`, `deepseek-v4-pro`.

**Enforced in code, not in memory.** `FORBIDDEN_MODELS` in
`scripts/turbohermes-watch.py` makes `dispatch()` refuse any ticket whose lane
resolves to a banned model. It does not fall back and it does not warn: the
ticket waits for your approval. Tested both directions before being trusted.

**Why a ban and not a preference.** The friction-audit build burned 224,505 GLM
tokens, 221,952 of them cache reads, on mechanical cataloguing of 88,000 lines,
multiplied by eight swarm workers because jcode's `swarm_model = "inherit"`
propagates the lane to every child. It reached a decision already written down
before it ran. Memory cannot prevent that: it gets summarised, and my own
reasoning about which phase "deserves" a stronger model overrides it. A refusal
in the dispatch path cannot be reasoned away.

**Every lane in this policy now points at step-5-preview.** The three-lane table
is retained as documentation of the roles you specified, but no lane resolves to
a banned model. If you want a specific piece of work on glm-5.3 or deepseek, say
so in chat for that task and it runs.

## 11. Two different audits: identity is not one (owner, 2026-11-10)

Owner: "Do you understand that if we install anything proven from GitHub we will
not audit its identity more than a quick cursory check? When working in depth
with a repo, developer models should be able to uncover unsafe code."

**Identity: cursory only.** A repository pulled from GitHub at a pinned commit is
accepted as what it claims to be. Licence, last commit date, star count, and that
the pinned commit exists. Nothing further. The fork-identity ticket cost 327,364
tokens re-proving the provenance of something already authenticated by the act of
downloading it, and the word "identity" appeared in no owner document. That work
is archived and must not be recreated.

**Safety: uncovered by the developer model during deep work, not by a separate
upfront audit.** The model that reads the code in depth is the audit. This is
cheaper than a gate, and it is a gate nobody maintains, which is worse than no
gate. The consequence is a dispatch-prompt obligation, not a pipeline stage: every
developer build is instructed to flag unsafe code it encounters, with file and
line, in its report. Unsafe means: `unsafe` blocks, raw pointer dereference,
command execution built from string concatenation, network calls to
non-allowlisted hosts, secret material in source, and any dependency that
transitively pulls a crate outside the approved set.

**The division of labour.** Cursory identity check at selection time. Safety
findings surface in the developer's own report at work time. Neither is a
blocking gate; both are reported. A finding stops the work, it does not stop the
dispatch.
