# TURBOHERMES
## Work order: deterministic agent-output compression and style engine

Version 1.2

## 1. Mission

Build a Rust tool that reduces unnecessary verbosity in AI-generated agent messages.

The tool removes redundant wording, meta-commentary, dramatic framing, performative deference, inflated vocabulary, repetition and other language that adds tokens without adding information.

The output should be concise, direct, ordinary language.

Examples:

Input:
"This is your call and I am not going to make it for you."

Output:
"Your call."

Input:
"Everything is working, with one caveat that is your decision to make."

Output:
"Everything is working. One decision remains."

Input:
"One implementation detail worth retaining: the work order deliberately makes friction the primary fork candidate."

Output:
"The work order uses friction as the primary fork candidate."

Input:
"There is one important distinction here. The tool should run independently during development."

Output:
"The tool should run independently during development."

The tool must preserve meaning, technical information, conditions, uncertainty, numbers, decisions, commands and relevant qualifications.

Primary objective: reduce token count while preserving information and readability.

## 2. Product and development strategy

Build TurboHermes as a standalone tool first.

The initial product must work independently of any agent framework. It must accept text, process it, and return the edited text together with an optional report explaining what changed.

Do not build production-agent integration in this phase.

Develop the internal architecture with later integration in mind. The same editing engine must be usable through:

- Standalone CLI.
- Rust library API.
- Later agent integration through an embedded library or service interface.

Keep the editing engine independent of the CLI, storage, telemetry and model-provider implementations.

Do not introduce dependencies on Hermes, OpenHands, Blockcell or another agent framework into the core.

The standalone implementation must be fully testable without a running agent.

## 3. Model architecture

Use different models for development-time evaluation and production-time decisions.

### 3.1 Development and training: capable LLM judge

Use StepFun 5 Preview or a comparable capable model for offline evaluation and training work.

The model is not part of the production editing path.

Use it to:

- Evaluate whether a proposed transformation preserves meaning.
- Identify unnecessary wording and explain why it adds no information.
- Label examples by transformation category.
- Compare original and transformed passages.
- Identify false positives and over-editing.
- Generate candidate training examples.
- Evaluate readability and ambiguity.
- Help discover recurring patterns that deterministic rules can handle.
- Produce adjudication data for decision-model training or fine-tuning.

The LLM judge must evaluate the original and edited text in context.

It must distinguish:
- Meaning preservation.
- Information preservation.
- Clarity.
- Concision.
- Grammar.
- Changes in tone.
- Changes in certainty.
- Changes in implied commitments.

Do not treat an LLM judge's score as ground truth. Maintain a human-reviewed evaluation set. Use the judge to increase evaluation coverage and identify disagreements.

Store the original text, edited text, proposed transformation, evaluation result, model version and rule version. Make evaluations reproducible.

### 3.2 Production: decision and classification models

For production-time decisions requiring semantic classification, use a decision model in the Cloudflare Clef family or a comparable model.

Research and implement against the Clef decision-model approach.

Clef takes a state and typed questions with predefined answer options. It returns probabilities for those options rather than generating free-form prose.

Relevant models currently include:

- Clef: 27B.
- Clef-flash: 9B.
- Clef-omni: multimodal mixture-of-experts model.

Clef uses a Qwen backbone and a non-autoregressive decision process. The model scores permitted schema choices rather than generating an explanation token by token. Cloudflare also describes probability calibration and reinforcement-learning-based fine-tuning for decision tasks.

Official references:
- https://blog.cloudflare.com/clef-decision-models/
- https://developers.cloudflare.com/workers-ai/models/clef/
- https://developers.cloudflare.com/ai/models/
- https://github.com/cloudflare

### 3.3 What the decision model does

The decision model classifies cases where deterministic rules cannot safely decide what to do.

Example questions:

- Is this sentence primarily meta-commentary?
- Does the opening phrase add information?
- Is the second clause redundant?
- Is this phrase performative deference?
- Is this an artificial contrast or rhetorical construction?
- Does deleting this span preserve the meaning of the surrounding text?
- Which transformation category applies?
- Should the engine edit, leave unchanged or request review?

Use bounded answer schemas.

Example decision:

State:
Original sentence, surrounding context, proposed transformation and relevant rule.

Questions:
1. Is the proposed transformation semantically safe?
   - yes
   - no
   - uncertain

2. What kind of language is present?
   - meta_commentary
   - redundant_qualification
   - performative_deference
   - dramatic_framing
   - inflated_vocabulary
   - repetition
   - substantive_content
   - other

3. What should the engine do?
   - apply
   - reject
   - review

The model returns probabilities for the permitted options.

The Rust engine applies the decision policy. The model does not edit the text.

### 3.4 Production decision policy

Use deterministic rules first.

Call the decision model only when a semantic decision is required and the deterministic engine cannot resolve the case safely.

The model must never be called simply to decide whether a known phrase can be removed by an established rule.

Use empirically calibrated thresholds. Do not assume that a model's reported probability is automatically a reliable confidence score.

Initial policy:

- High confidence: eligible for automatic application, subject to transformation-specific safety requirements.
- Intermediate confidence: leave unchanged or send to review.
- Low confidence: leave unchanged.

Determine actual thresholds from the labelled evaluation corpus.

For high-impact transformations, require stronger evidence than for simple deletion of a known framing phrase.

Do not allow the model to introduce new prose or rewrite passages.

### 3.5 Model-provider abstraction

Implement a provider-independent decision interface.

The editing engine must not depend directly on Cloudflare's API, a specific Clef model ID or a particular inference provider.

Define a stable internal request and response schema.

The interface must support:
- Cloudflare Workers AI.
- Locally hosted decision models.
- Other Jev/System One-compatible decision models where practical.
- Mock providers for tests.
- A no-model configuration.

Keep provider configuration outside the core editing logic.

Record provider, model ID, model version, schema version, latency and returned probabilities for every decision.

Do not make network calls from the editing engine itself. Use an injected decision-provider interface.

Production must continue to work when the decision service is unavailable. In that situation, apply deterministic rules and leave unresolved cases unchanged.

No runtime dependency on StepFun or another general-purpose LLM.

## 4. Standalone tool requirements

Build a usable CLI.

Suggested commands:

- `turbohermes process input.txt`
- `turbohermes process --stdin`
- `turbohermes inspect input.txt`
- `turbohermes evaluate corpus.jsonl`
- `turbohermes benchmark corpus.jsonl`
- `turbohermes rules list`
- `turbohermes config show`

Support:
- Standard input and output.
- File input and output.
- Plain text.
- Markdown.
- JSON input and output.
- Batch processing.
- Dry-run mode.
- Explain mode.
- Profile selection.
- Rule enable/disable configuration.

The default output should be the edited text, without a commentary preamble.

Provide optional structured output containing:
- Original text.
- Edited text.
- Token count before and after.
- Token reduction.
- Applied transformations.
- Rule identifiers.
- Model decisions, if used.
- Confidence values.
- Processing time.
- Warnings or unresolved cases.

Do not add explanatory prose to the normal output.

## 5. Existing code and project research

Do not build a replacement from scratch before inspecting existing implementations.

### Primary candidate: friction

Repository:
https://github.com/zerosize-dev/friction

Inspect the source, Cargo manifests, dependency tree, APIs, tests, licences and implementation details.

The project describes a deterministic engine for removing machine-like language from technical documentation. Its operations include ritual deletion, gated span deletion, paired substitution, derivational pivots, frame-gated deletion, frame rewriting, clause restructuring and register rephrasing.

It is the primary candidate for reuse or forking.

Do not assume its README describes a stable library API. Establish what is actually reusable from the source.

Phase 0 must decide whether to:
- Fork and extend the existing implementation.
- Reuse selected modules.
- Port selected algorithms into TurboHermes.

Do not commit to a fork before the source and dependency audit.

Reference:
https://github.com/zerosize-dev/friction

### Additional projects to inspect

`unslop`
https://github.com/theclaymethod/unslop

`stopslop`
https://github.com/mgiovani/stopslop

`prose-sanitiser`
https://github.com/DreamLab-AI/prose-sanitiser

`vale-ai-tells`
https://github.com/tbhb/vale-ai-tells

`humanize`
https://github.com/ccf/humanize

`humanist`
https://github.com/itsryanlenk/humanist

`prosaic`
https://github.com/wildmason/prosaic

`nlprule`
https://github.com/bminixhofer/nlprule

Inspect the code and licences. Identify reusable algorithms, test cases, rule inventories and evaluation methods.

Do not introduce Python into the production runtime merely because a useful research project uses Python.

### Research conclusions to retain

The humanisation research identifies recurring patterns:

- Inflated significance.
- Formulaic transitions.
- Artificial contrasts.
- Repeated summary statements.
- Generic validating openers.
- Performative deference.
- Abstract nouns and inflated vocabulary.
- Superficial analysis.
- Repeated phrases.
- Unnecessary conclusions.
- Predictable rhetorical structures.

Use these as candidate transformation categories, not as a blacklist of phrases.

The objective is to remove unnecessary language while preserving the author's meaning and voice. Do not manufacture a more human-sounding personality.

`prosaic` is worth studying for structured-event-to-language generation and discourse tracking. It is not the primary post-processing engine.

`nlprule` is worth benchmarking for sentence segmentation, grammar and linguistic analysis. Do not add it without measuring its value against the existing implementation.

## 6. Governing writing principle

Do not narrate the answer. Give the answer.

This is an actionable transformation category.

Detect language that announces, introduces, evaluates or explains the answer instead of providing information.

Examples:

- "One implementation detail worth retaining:"
- "There is one important distinction here."
- "The point worth noting is..."
- "Here is why this matters."
- "Let me explain..."
- "I will now outline..."
- "The key takeaway is..."
- "It is worth mentioning that..."
- "A useful way to think about this is..."

Remove the framing when the following content stands independently.

If a sentence only announces the next sentence, delete it.

If a phrase introduces a point without adding information, remove it.

Do not remove a sentence merely because it introduces a topic. It must be redundant or add no substantive information.

This rule must be tested in context. A phrase dictionary alone cannot reliably determine whether a sentence is useful.

## 7. Transformation rules

Implement transformation families as independently testable modules.

### A. Discourse framing and meta-commentary

Remove phrases that announce the answer, narrate the structure or comment on the act of responding.

Examples:
- "One thing to keep in mind is..."
- "The important point here is..."
- "There is a caveat worth mentioning..."
- "Let's break this down."
- "I will walk you through..."
- "To put it simply..."

Delete the framing and retain the information.

### B. Redundant clauses

Remove clauses that repeat or merely restate the preceding statement.

Example:
"This is your call and I am not going to make it for you."

Becomes:
"Your call."

Do not remove a clause that adds a real condition, consequence or limitation.

### C. Phrase compression

Replace verbose expressions with ordinary equivalents.

Examples:
- "At this point in time" -> "Now"
- "In order to" -> "To"
- "Due to the fact that" -> "Because"
- "Has the ability to" -> "Can"
- "A large number of" -> "Many"
- "In the event that" -> "If"

### D. Light verbs and nominalisations

Prefer direct verbs where meaning is unchanged.

Examples:
- "Make a decision" -> "Decide"
- "Provide an explanation" -> "Explain"
- "Conduct an investigation" -> "Investigate"
- "Perform an assessment" -> "Assess"

Do not rewrite established technical terms.

### E. Dramatic framing

Remove unnecessary suspense, urgency and theatrical language.

Examples:
- "Everything is working, with one caveat that is your decision to make."
- "There is a critical issue that needs to be addressed."
- "The real problem is..."
- "This changes everything."
- "The situation is more nuanced than it first appears."

Retain actual severity, urgency and consequences. Do not flatten meaningful warnings.

### F. Performative deference

Remove excessive statements of respect for user autonomy or repeated assurances that the user decides.

Examples:
- "This is your call and I am not going to make it for you."
- "Ultimately, the decision rests entirely with you."
- "I will leave that entirely in your hands."
- "Of course, only you can decide what is right for you."

Retain a concise decision statement where useful.

### G. Inflated or abstract vocabulary

Prefer ordinary language.

Examples:
- "The binding constraint" -> "The main constraint"
- "Structurally" -> state the actual structural issue, or delete it.
- "The safe one" -> identify the actual option and why it is safer.
- "Operationalise" -> "Implement"
- "Utilise" -> "Use"

Do not replace precise technical vocabulary with vague everyday words.

### H. Unnecessary qualification

Remove qualifications that do not materially change the claim.

Examples:
- "It is perhaps worth considering..."
- "It may be useful to note that..."
- "In many respects..."
- "To some extent..."

Preserve real uncertainty, probability, scope and conditions.

### I. Self-reference

Remove unnecessary references to the assistant's own process, intentions or limitations.

Examples:
- "I would suggest..."
- "I want to emphasise..."
- "I should point out..."
- "I will not overcomplicate this."
- "I can help with that."

Keep first-person language when it carries actual information or commitment.

### J. Repetition and artificial conclusions

Remove:
- Repeated summaries.
- Conclusions that restate the preceding paragraph.
- Repeated qualifications.
- Repeated descriptions of the same benefit.
- Punchline endings that add no information.
- Formulaic final offers.

Do not delete a conclusion that introduces a genuine decision or implication.

## 8. Editing pipeline

Use a staged pipeline.

1. Parse the input and identify protected spans.
2. Segment into blocks, sentences and clauses.
3. Apply deterministic transformations.
4. Identify unresolved candidate transformations.
5. Call the decision provider only for those candidates.
6. Apply only transformations allowed by the decision policy.
7. Run preservation and integrity checks.
8. Measure token count before and after.
9. Return the result and optional structured report.

The engine must support transformations that operate on:
- Individual phrases.
- Clauses.
- Sentences.
- Adjacent sentences.
- Larger discourse units where context is required.

Do not process every sentence independently. Some redundant framing can only be detected by examining the following sentence or paragraph.

## 9. Protected content and safety

Never alter the following by default:

- Code blocks.
- Inline code.
- Shell commands.
- Configuration files.
- URLs.
- Markdown links.
- File paths.
- Identifiers.
- API names.
- Product names.
- Model names.
- Version numbers.
- Numeric values.
- Dates.
- Quoted source material.
- Structured data.
- Legal or contractual language.
- Explicit requirements and constraints.

Preserve:
- Negation.
- Causality.
- Conditions.
- Exceptions.
- Quantities.
- Comparisons.
- Attribution.
- Uncertainty.
- Commitments.
- Technical distinctions.

Use conservative defaults.

If the engine cannot establish that a transformation preserves meaning, leave the text unchanged.

No model decision may override protected-span rules.

## 10. Profiles

Implement configurable profiles.

### Coding agent

Priorities:
- Remove progress-report theatre.
- Remove repeated status descriptions.
- Remove unnecessary explanations of completed actions.
- Preserve commands, file paths, test results, errors and implementation decisions.
- Preserve exact technical details.

### Personal agent

Priorities:
- Remove performative deference.
- Remove excessive reassurance.
- Remove generic conversational openings.
- Remove unnecessary caveats.
- Preserve relevant context and intent.

### Operational

Priorities:
- Concise status.
- Clear decisions.
- Explicit blockers.
- Exact results.
- No dramatic framing.
- No redundant narration.

### General concise

Apply the full transformation set conservatively.

Profiles should change rule weights and thresholds, not introduce unrelated rewriting behaviour.

## 11. Rust implementation

Use existing proven code where possible.

Inspect the existing friction implementation before selecting dependencies.

Evaluate:
- `pulldown-cmark` for Markdown parsing.
- `aho-corasick` for efficient phrase matching.
- `regex` for pattern matching.
- `icu_segmenter` for sentence segmentation.
- Existing linguistic code in friction.
- `nlprule` for grammar and linguistic analysis.
- `serde` for structured input and output.
- `similar` for edit diffs.
- `proptest` for property-based testing.
- `insta` for snapshot testing.
- `cargo-fuzz` for parser and transformation fuzzing.
- `tiktoken-rs` or an appropriate tokenizer for token measurement.

Benchmark alternatives. Do not include dependencies without a measurable purpose.

Keep the core library independent of command-line parsing and external model clients.

Suggested logical modules:

- `parser`
- `protected_spans`
- `segmenter`
- `rules`
- `transform`
- `decision`
- `providers`
- `validation`
- `token_metrics`
- `telemetry`
- `profiles`
- `cli`

The decision interface should be asynchronous where required by remote inference. Deterministic transformations must remain usable without an async runtime if practical.

## 12. Evaluation and telemetry

Token reduction is a primary metric.

Measure:
- Input tokens.
- Output tokens.
- Absolute token savings.
- Percentage reduction.
- Transformations applied.
- Rejected transformations.
- Model calls.
- Model latency.
- Total processing latency.
- Preservation failures.
- Human corrections.

Use a consistent tokenizer for before/after comparisons. Record the tokenizer and version.

Maintain separate evaluation corpora:

1. Deliberately verbose agent output.
2. Already concise human-written text.
3. Concise technical output.
4. Technical instructions and commands.
5. Ambiguous examples.
6. Adversarial examples where deleting a qualification would change meaning.
7. Multilingual examples for future support.

Initial acceptance targets:

- At least 10% median token reduction on deliberately verbose examples.
- At least 95% meaning preservation on the human-reviewed evaluation set.
- No more than 2% median token reduction on already-concise control examples.
- No increase in ambiguity.
- No changes to protected technical content.

Report results separately by transformation family and profile.

Do not hide a weak transformation category behind aggregate scores.

## 13. Offline judge and training workflow

Create a repeatable offline evaluation process.

For each candidate transformation:

1. Save the original passage.
2. Save the proposed edit.
3. Identify the rule or model decision responsible.
4. Ask the capable LLM judge to evaluate meaning, information, clarity and concision.
5. Store the evaluation.
6. Sample disagreements for human review.
7. Add adjudicated examples to the regression corpus.

Use the resulting labelled data to improve:
- Deterministic rules.
- Decision schemas.
- Confidence thresholds.
- Future fine-tuning of a decision model.

Do not train on unreviewed model-generated labels as though they were ground truth.

Keep the judge out of the runtime path.

## 14. Standalone and future integration interfaces

The standalone CLI is the first deliverable.

The library API is developed alongside it.

Define a stable request structure containing:
- Text.
- Profile.
- Editing mode.
- Optional metadata.
- Optional decision-provider configuration.

Define a stable result structure containing:
- Edited text.
- Transformation report.
- Token metrics.
- Decision metadata.
- Processing metadata.

Keep all agent-specific concerns outside the core.

Later integration should be able to call the library directly, or run TurboHermes as a local service if isolation is preferable.

Do not require a production agent to parse human-readable CLI output. Provide structured output and a stable API.

Do not add an agent-specific protocol until there is an actual integration target.

## 15. Modes

Implement:

- `off`: return original text.
- `report`: identify candidate changes without applying them.
- `suggest`: return proposed edits.
- `safe-fix`: apply only transformations meeting strict safety criteria.
- `review`: include uncertain cases for inspection.

The default standalone mode should be `safe-fix`.

The decision provider must be optional. If it is disabled or unavailable, the engine uses deterministic rules only.

## 16. Development phases

### Phase 0: source and architecture audit

Inspect friction and the other candidate projects.

Verify:
- Source-level implementation.
- API stability.
- Dependencies.
- Licence compatibility.
- Test coverage.
- Performance.
- Reusable transformation logic.
- Existing protected-span handling.

Produce a short audit report and an implementation decision.

Do not start a greenfield replacement before this work is complete.

### Phase 1: standalone deterministic engine

Implement the parser, protected spans, segmentation, deterministic transformations, profiles and CLI.

No production model calls.

Build the initial evaluation corpus and token measurement.

### Phase 2: offline evaluation

Integrate the capable LLM judge into the development workflow.

Generate and adjudicate examples.

Tune transformations against the evaluation corpus.

### Phase 3: decision-provider interface

Implement the provider abstraction and a mock provider.

Add a Clef-compatible provider.

Test typed questions, probability responses, thresholds, timeouts, unavailable services and invalid responses.

The engine must remain functional without the provider.

### Phase 4: production decision path

Enable model-assisted classification for unresolved cases.

Measure accuracy, latency, cost and transformation quality.

Compare model-assisted decisions against deterministic-only processing.

Do not use a model call where a deterministic rule already resolves the case.

### Phase 5: integration readiness

Test the Rust library independently of the CLI.

Document the API and structured result schema.

Test concurrent use, repeated calls, configuration isolation and provider failure.

Do not implement production-agent integration yet.

## 17. Prohibitions

- No general-purpose LLM rewriting in production.
- No AI detection.
- No personality simulation.
- No generic humanisation rewrite pass.
- No unnecessary paraphrasing.
- No rewriting merely to vary sentence length.
- No removal of meaningful qualifications.
- No modification of protected content.
- No model dependency for deterministic transformations.
- No silent failure when a model provider is unavailable.
- No agent-framework dependency in the core.
- No production integration before the standalone tool is validated.
- No greenfield reimplementation of existing functionality without source audit and benchmarks.

## 18. First acceptance test

Input:

"Everything is working, with one caveat that is your decision to make. Two builds confirmed running in isolated worktrees. Fork-identity at 24 minutes, now capturing the Phase 1 baseline: 1,140 passed, 0 failed across 3 test binaries, with five test processes still going. Phase-1 source verification at 8 minutes in its own worktree."

Expected behaviour:

- Remove the dramatic framing.
- Remove performative deference.
- Preserve the two build statuses.
- Preserve elapsed times.
- Preserve all test counts.
- Preserve the fact that five test processes are still running.
- Preserve the separate source-verification status.
- Do not invent completion or success.
- Do not rewrite technical terms.

The tool must produce a shorter result without losing any of those facts.

## 19. Completion criteria

Deliver:

1. Source audit of friction and relevant alternatives.
2. Standalone Rust CLI.
3. Reusable Rust library.
4. Deterministic transformation engine.
5. Protected-span handling.
6. Configurable profiles and modes.
7. Token measurement and telemetry.
8. Offline LLM-judge evaluation workflow.
9. Clef-compatible decision-provider interface.
10. Regression and preservation test corpus.
11. Benchmarks and evaluation report.
12. API documentation for future agent integration.

The standalone tool must be useful without a model provider and must continue working if a remote decision service fails.

Remove words that add nothing. Replace inflated language with ordinary language. Do not narrate the answer. Give the answer. Preserve the information. Measure the savings.