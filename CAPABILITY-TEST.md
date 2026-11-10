# Capability test — multi-lane, fan-out, tool use (2026-11-10)

Owner: "This should test the multi lane, fan out and tool use capability of
jcode." Measured from live processes and the build log, not from configuration.

## Multi-lane — VERIFIED

The dispatched `mutation-audit` phase ran on **deepseek-v4.1-flash**, read from
`/proc/2421179/cmdline`, not from the log that claimed it. The lane came from
the `Model lanes` table in `TURBOHERMES-POLICY.md`, parsed by the dispatcher.

Compress-project lanes assigned and re-verified by the same parser:

    friction-audit          -> glm-5.3            (architecture)
    protected-spans-audit   -> glm-5.3            (architecture)
    alternatives-audit      -> deepseek-v4.1-flash (verification)
    defluffer-salvage       -> deepseek-v4.1-flash (verification)

## Fan-out — VERIFIED

The `swarm` tool was called **4 times** by the running agent, and it produced a
real child process: pid 2424548, parent 2421179, running

    jcode-linux-x86_64.bin --provider openai-compatible \
      --provider-profile litellm --model deepseek-v4.1-flash serve

The build log shows the agent reasoning about swarm availability before using
it. This is jcode's own multi-agent fan-out, not Hermes-level parallelism.

Note on mechanism: jcode has no `--effort` flag for headless `run`, and swarm
mode is gated on `effort = "swarm"` in the source
(`swarm_reminder_tests.rs`, `effort: Some("swarm".into())`). The documented
`/effort swarm` path is a TUI concept. What was tested is the agent choosing to
call the `swarm` tool when the prompt asks for it, which is the same underlying
capability but not the same entry point. If the documented path must be tested,
that needs a daemon or interactive session.

## Tool use — VERIFIED

244 tool calls in the running build, tallied from the log:

    151  bash          15  agentgrep      4  swarm
     50  read           3  write          2  apply_patch
     11  edit           3  batch          5  bg

`agentgrep` is the rtk-backed code search from the six-tool policy and it is
being used, so the policy is live rather than filed. One hallucinated tool name
appeared ("ashedit"), which jcode rejected with a correct tool list.

## Two dispatcher defects found while wiring this

Both were silent-fallback bugs of the kind that look like coverage:

1. The phase parser keyed on the `v7 phase:` title prefix, so every
   `compress phase:` ticket fell back to the workhorse model with no warning.
2. The lane-table reader stopped at the first heading, so the compress table
   under a `###` sub-heading was never read at all.

Both fixed. The fallback now logs loudly when a phase is missing from the table,
and the dispatcher iterates all ready tickets instead of giving up when the
first cannot be claimed.

## Current state

One build live on deepseek-v4.1-flash, executing `mutation-audit`, fanning out
through the swarm tool. The compress phases are queued behind it in dependency
order and will dispatch as each clears, each on its own lane model.
