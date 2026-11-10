#!/usr/bin/env python3
"""turbohermes-watch — thin adapter over the Hermes kanban.

REDUCED 2026-11-10 from 536 lines to this. The old version reimplemented a phase
queue, dispatch caps, dependency ordering and state tracking, and produced six
bugs in one day: a pgrep self-match that made it think a build was always
running (so it never dispatched anything), an operator-precedence TypeError in
two places, and a phase["crate"] KeyError in three. Every one is a bug in
scratchpad code sitting beside a tested primitive.

The kanban already owns the queue, the ordering, the dispatch caps, the cooldown
guards, the worker scopes and the audit trail. So it owns them. This script does
the one thing the kanban cannot: spawn the jcode lane, which the kanban
dispatcher reports as "non-spawnable assignee - terminal lane".

The phase contracts live as kanban tickets (t_0e21e9aa through t_86892825),
linked parent->child so the kanban enforces work order v7's build order. This
script reads that queue and dispatches. It holds no phase data of its own.
"""
import re
import subprocess
import time
from pathlib import Path

# Owner 2026-11-10: "NEVER AGAIN USE GLM or deepseek WITHOUT MY Explicit
# instruction or approval. You clearly  lack judgement skill"
#
# This is a hard ban enforced in code, not a preference held in memory. Memory
# gets summarised, forgotten, or overridden by my own reasoning about which
# phase "deserves" a stronger model. The friction-audit burn of 224,505 GLM
# tokens on mechanical cataloguing is what this prevents. Only step-5-preview
# runs without a per-task approval given in chat.
FORBIDDEN_MODELS = {"glm-5.3", "deepseek-v4.1-flash", "glm-5.3-air", "deepseek-v4-pro"}
DEFAULT_LANE = "step-5-preview"

MAX_CONCURRENT = 2  # owner 2026-11-10: raised to test the claim that 2 builds endanger MemOS. That claim was inference, not measurement.

LOGDIR = Path("/home/hermes/.hermes/logs")
LOG = LOGDIR / "turbohermes-watch.log"
KANBAN_DIR = Path("/home/hermes/projects/agent-daemon")
ENV = Path("/home/hermes/.hermes/.env")
ASSIGNEE = "jcode"
# The standing policy. The model-lane table in section 1 is the single source of
# truth for which model runs which phase; this script reads it rather than
# hard-coding a model, because a hard-coded model is how the three-lane
# instruction (GLM 5.3 architecture, step-5-preview grunt, deepseek verification)
# silently became one lane running step-5-preview for everything.
POLICY = KANBAN_DIR / "TURBOHERMES-POLICY.md"
FALLBACK_MODEL = "step-5-preview"


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh:
        fh.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg))


def sh(cmd, timeout=120, cwd=None):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, cwd=str(cwd) if cwd else None)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def jcode_pids():
    """Pids of live jcode builds, verified via /proc/<pid>/comm.

    TWO BUGS LIVED HERE, both from the same wrong pattern. The old code used
    `pgrep -f 'jcode --provider-profile ...'`, but the real binary is
    `jcode-linux-x86_64.bin --provider-profile ...`, so the pattern never
    matched the build at all. It matched the bash wrapper instead, which is
    always alive, so the watchdog believed a build was always running and never
    dispatched anything. The first fix then filtered comm to exactly "jcode",
    which excluded the real binary (its comm is "jcode-linux-x86_64") and
    dispatched a SECOND build into the same tree, the incident edace42.

    Correct pattern: `--provider-profile litellm`, which is genuinely in the
    build's command line. Correct comm test: anything starting with "jcode".
    """
    rc, out = sh("pgrep -f -- '--provider-profile litellm'")
    if rc != 0 or not out.strip():
        return []
    all_jcode = set()
    for pid in out.strip().splitlines():
        pid = pid.strip()
        if not pid:
            continue
        try:
            with open("/proc/%s/comm" % pid) as fh:
                comm = fh.read().strip()
        except OSError:
            continue
        if comm.startswith("jcode"):
            all_jcode.add(pid)
    # Count TOP-LEVEL builds only. A build spawns swarm children whose command
    # line is identical, so counting every jcode process let one build with one
    # child fill a cap of 2 and starve every other project. The owner's
    # instruction was to raise the limit and measure; the limit was unreachable
    # because the counter was wrong, the same defect class as the pgrep
    # self-match that froze the first watchdog.
    top_level = []
    for pid in all_jcode:
        try:
            with open("/proc/%s/stat" % pid) as fh:
                ppid = fh.read().split(") ", 1)[1].split()[1]
        except (OSError, IndexError):
            continue
        if ppid not in all_jcode:
            top_level.append(pid)
    return sorted(top_level)


def ready_tickets():
    """Ready tickets for the jcode lane, in kanban order. The kanban has already
    applied its own dependency, cooldown and cap guards by the time a ticket is
    ready, so this list is authoritative and needs no second opinion."""
    rc, out = sh("hermes kanban list --assignee %s --status ready" % ASSIGNEE,
                 cwd=KANBAN_DIR)
    if rc != 0:
        return []
    ids = _ticket_ids(out)
    # Project order is explicit, not whatever kanban lists first. The v1.2
    # compression engine is the current work order; the v7 fork work is older.
    # Taking ids[0] meant a reclaimed fork ticket could jump ahead of the
    # compression phase the owner was waiting on, which read as dispatching the
    # wrong ticket.
    compress = [t for t in ids if "compress phase:" in _title(t)]
    other = [t for t in ids if t not in compress]
    return compress + other


def _title(ticket_id):
    rc, out = sh("hermes kanban show %s" % ticket_id, cwd=KANBAN_DIR)
    for line in out.splitlines():
        if "phase:" in line:
            return line.split("phase:", 1)[1].strip()
    return ""


def source_citation(ticket_id):
    """A ticket must quote the owner's words or the work-order line it implements.

    Owner 2026-11-10: "You need to audit every step you take in future. Time and
    time again you hallucinated non existent rules and made up stuff, substituting
    your ideas for my judgement and clear instructions."

    The fork-identity ticket cost 327,364 tokens on work that appears in no owner
    document. The only defence that survives my own optimism is mechanical: if a
    ticket cannot name the sentence it serves, it does not get a build.
    """
    rc, out = sh("hermes kanban show %s" % ticket_id, cwd=KANBAN_DIR)
    for line in out.splitlines():
        st = line.strip()
        if st.startswith("SOURCE:"):
            return st[len("SOURCE:"):].strip()
    return None

def model_for(ticket_id):
    """The model for a ticket's phase, read from the standing policy.

    Parses the "Model lanes" table in TURBOHERMES-POLICY.md section 1. The ticket
    title carries the phase name (`v7 phase: <name>`), which is the join key. Falls
    back to the workhorse model and says so in the log, so a missing row is loud
    rather than silent.
    """
    rc, out = sh("hermes kanban show %s" % ticket_id, cwd=KANBAN_DIR)
    title = ""
    for line in out.splitlines():
        # Prefix-independent: tickets are titled "v7 phase: <name>" and
        # "compress phase: <name>", and keying on one prefix silently sent every
        # other project's tickets to the fallback model.
        if "phase:" in line:
            title = line.split("phase:", 1)[1].strip()
            break
    phase = title.split()[0] if title else ""
    if not phase:
        log("model_for %s: no phase in title, using %s" % (ticket_id, FALLBACK_MODEL))
        return FALLBACK_MODEL, "unknown"
    if not POLICY.exists():
        log("model_for %s: no policy file, using %s" % (ticket_id, FALLBACK_MODEL))
        return FALLBACK_MODEL, phase
    lanes = {}
    in_table = False
    for line in POLICY.read_text().splitlines():
        # Read EVERY lane table in the file and merge them, so adding a project
        # never requires touching this parser. The first version stopped at the
        # next heading, which meant the compress project's table sat under a `###`
        # sub-heading and was never read: all four of its phases silently fell
        # back to the workhorse model.
        if "Model lanes" in line or line.strip().startswith("| Phase | Role | Model |"):
            in_table = True
            continue
        if in_table:
            if line.startswith("#"):
                in_table = False
                continue
            if line.strip().startswith("|") and "---" not in line:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 3 and cells[0] and cells[0] != "Phase":
                    lanes[cells[0]] = (cells[1], cells[2])
    if phase not in lanes:
        log("model_for %s: phase %s not in the policy lane table, using %s"
            % (ticket_id, phase, FALLBACK_MODEL))
        return FALLBACK_MODEL, phase
    role, model = lanes[phase]
    log("model_for %s: phase=%s role=%s model=%s" % (ticket_id, phase, role, model))
    return model, phase


def _shell_escape(text):
    """Escape a value for embedding inside a double-quoted shell string.

    The SOURCE citations contain double quotes, because they quote the owner's
    words. Substituted raw, the first embedded quote closed the shell string and
    the rest of the prompt was parsed as shell syntax, which is why three
    dispatches died with "syntax error near unexpected token" and produced no
    build at all.
    """
    return text.replace("\\", "\\\\").replace('"', '\\"')

def dispatch(ticket_id):
    model, phase = model_for(ticket_id)
    if model in FORBIDDEN_MODELS:
        log("REFUSING %s: model %s is banned without explicit owner approval in "
            "chat. Falling back is not permitted; the ticket waits for approval."
            % (ticket_id, model))
        return False
    citation = source_citation(ticket_id)
    if not citation:
        log("REFUSING %s (phase %s): no SOURCE citation. A ticket that cannot "
            "name the owner sentence or work-order line it serves is invented "
            "work and gets no build." % (ticket_id, phase))
        return False
    rc, _ = sh("hermes kanban claim %s" % ticket_id, cwd=KANBAN_DIR)
    if rc != 0:
        log("dispatch %s: claim failed rc=%d" % (ticket_id, rc))
        return False
    key = ""
    for line in ENV.read_text().splitlines():
        if line.startswith("LITELLM_MASTER_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    logf = LOGDIR / ("jcode-%s.log" % ticket_id)
    cmd = (
        "source %s 2>/dev/null; export JCODE_PROVIDER_LITELLM_API_KEY=\"%s\"; "
        "jcode --provider-profile litellm --model %s run "
        "\"AUTHORITY (quote it in your report): %s. "
        "Run: hermes kanban show %s --body, read that body, and execute it "
        "exactly. Work order v7 is the authority: reuse before write, and name "
        "every upstream file you copy or port from. "
        "FAN-OUT (documented swarm syntax, verified against jcode source): the "
        "swarm tool takes a required 'action' field. To fan out, either call "
        "swarm with action=launch, which runs your own todo list as one agent "
        "per lane, or call swarm with action=spawn plus a required 'label' and "
        "a 'prompt' describing that worker's lane. Do not invent other action "
        "names. If the work does not split into independent lanes, say so and "
        "stay serial rather than spawning for its own sake. "
        "Report only what you ran and observed.\""
        % (ENV, key, model, _shell_escape(citation), ticket_id)
    )
    with open(logf, "a") as lf:
        # Isolation (owner 2026-11-10): "Jcode should absolutely not affect
        # memos as memos is only used for Hermes." A build worker must never be
        # able to starve a Hermes service. nice -n 19 means the MemOS bridge
        # always wins a scheduling contest, so a saturated machine cannot time
        # out its health check. This is cheaper and more reversible than
        # cgroups and touches nothing in the plugin.
        subprocess.Popen(["nice", "-n", "19", "bash", "-lc", cmd],
                         cwd=str(KANBAN_DIR),
                         stdout=lf, stderr=subprocess.STDOUT,
                         start_new_session=True)
    log("DISPATCHED %s (phase %s) to jcode on model %s, log %s"
        % (ticket_id, phase, model, logf.name))
    return True


def _ticket_ids(out):
    """Ticket ids from kanban list output, marker-independent.

    The marker changes with the output context: `▶` when stdout is a terminal,
    `●` when it is captured, and `⊘`/`✓`/`◻` for other states. A parser keyed on
    the marker silently returns nothing when the context changes, which is how
    running_tickets() came back empty while a ticket was plainly in `running`.
    Match the id instead; it is stable.
    """
    ids = []
    for line in out.splitlines():
        for m in re.findall(r"\b(t_[a-f0-9]{8})\b", line):
            if m not in ids:
                ids.append(m)
    return ids


def running_tickets():
    """Tickets this lane has claimed but not yet completed.

    The defect this closes: dispatch() claims a ticket, which moves it to
    'running', and nothing ever completed it. A finished phase therefore sat in
    'running' forever and the next tick re-dispatched work that was already
    done. The kanban owns the state; this function is how the adapter tells the
    kanban the build is over.
    """
    rc, out = sh("hermes kanban list --assignee %s --status running" % ASSIGNEE,
                 cwd=KANBAN_DIR)
    if rc != 0:
        return []
    return _ticket_ids(out)


# A build that ends on one of these did not succeed, and completing its ticket
# would record a failure as a delivery. Leave it running and say why.
FAIL_SIGS = (
    "451 Unavailable For Legal Reasons",
    "Error: OpenAI-compatible chat request failed",
    "Traceback (most recent call last)",
    "panicked at",
)
# A log still being written is not a finished build. 180s of quiet is the bar.
QUIET_SECONDS = 180


def log_evidence(ticket_id):
    """(result_text, None) if the build can be completed, else (None, reason).

    Evidence comes from the build log and is reported verbatim: token counts,
    test-binary counts, and the last commit in the worktree. No invention.
    """
    logf = LOGDIR / ("jcode-%s.log" % ticket_id)
    if not logf.exists():
        return None, "no build log at %s" % logf
    age = time.time() - logf.stat().st_mtime
    if age < QUIET_SECONDS:
        return None, "log still active (%.0fs since last write, need %ds)" % (
            age, QUIET_SECONDS)
    text = logf.read_text(errors="replace")
    tail = text[-8000:]
    for sig in FAIL_SIGS:
        if sig in tail:
            return None, "build log ends on a failure signature: %s" % sig
    ev = []
    toks = re.findall(r"\[Tokens\] upload: (\d+)", text)
    if toks:
        ev.append("jcode tokens %s" % toks[-1])
    tests = re.findall(r"test result: ok\. (\d+) passed", text)
    if tests:
        ev.append("%d test binaries ok" % len(tests))
    rc, out = sh("git -C %s log --oneline -1" % (KANBAN_DIR.parent / "turbohermes-wt"),
                 timeout=30)
    if rc == 0 and out.strip():
        ev.append("last worktree commit %s" % out.strip().split()[0])
    if not ev:
        return None, "log has no measurable evidence (no tokens, no tests, no commit)"
    return "Build finished. Evidence from the log: %s." % "; ".join(ev), None


def complete_finished():
    """Close tickets whose build has provably finished. Returns count closed."""
    closed = 0
    for tid in running_tickets():
        result, why = log_evidence(tid)
        if result is None:
            log("NOT-COMPLETING %s: %s" % (tid, why))
            continue
        rc, out = sh("hermes kanban complete %s --result %s" % (
            tid, subprocess.list2cmdline([result])), cwd=KANBAN_DIR)
        if rc == 0:
            log("COMPLETED %s" % tid)
            closed += 1
        else:
            log("COMPLETE-FAILED %s rc=%d %s" % (tid, rc, out.strip()[:160]))
    return closed


def main():
    # Concurrency: this host runs 8 cores with ~19GB free and has run multiple
    # jcode builds side by side without trouble. The old "return if any build is
    # alive" guard was never an owner instruction and never a measured limit; it
    # was written here and it silently starved every project behind whichever
    # build happened to start first. Cap is now explicit and measured.
    alive = jcode_pids()
    if len(alive) >= MAX_CONCURRENT:
        log("AT CAP pids=%s (max %d)" % (",".join(alive), MAX_CONCURRENT))
        return
    # No build alive: anything this lane claimed is finished or dead. Close what
    # has evidence, leave the rest with a reason logged.
    complete_finished()
    tickets = ready_tickets()
    if not tickets:
        log("IDLE no ready %s tickets" % ASSIGNEE)
        return
    # Try every ready ticket, not just the first. A ticket that is already
    # claimed by a live build fails to claim, and giving up there left the next
    # project's phase waiting behind work that was already running.
    for tid in tickets:
        if dispatch(tid):
            return
    log("IDLE no ready %s ticket could be claimed" % ASSIGNEE)


if __name__ == "__main__":
    main()
