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
| source-verification | verification | deepseek-v4.1-flash |
| mutation-audit | grunt | step-5-preview |
| fork-identity | grunt | step-5-preview |
| mutation-safety | grunt | step-5-preview |
| jcode-adapter | architecture | glm-5.3 |
| persistent-planning | architecture | glm-5.3 |

### turbohermes-compress (compression engine, project started 2026-11-10)

Fork of `zerosize-dev/friction` as `m3m007/turbohermes-compress`, pinned at its
`Release 0.6.20` commit, 12 crates, dual-licensed Apache-2.0 / MIT, builds clean
in 2m17s on this host. This project supersedes the defluffer work
(`turbohermes-hygiene`), of which only what survives audit is salvaged.

| Phase | Role | Model |
|---|---|---|
| friction-audit | architecture | glm-5.3 |
| alternatives-audit | grunt | step-5-preview |
| defluffer-salvage | grunt | step-5-preview |
| protected-spans-audit | architecture | glm-5.3 |
| offline-evaluation | verification | deepseek-v4.1-flash |

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
