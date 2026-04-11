# Tmux Launch Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `tmux.sh` — a single script that opens a named tmux session with `./launch.sh` running in the bottom pane and a free shell in the top pane.

**Architecture:** `tmux.sh` wraps `./launch.sh` — it creates or attaches to a session named `unify`, splits the window 60/40, sends `./launch.sh` to the bottom pane, and focuses the top pane. The venv is handled entirely inside `launch.sh` so `tmux.sh` needs no Python awareness. README gets a one-liner addition pointing to `./tmux.sh`.

**Tech Stack:** Bash, tmux 3.x

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `tmux.sh` | Create | Entry-point for tmux dev environment |
| `README.md` | Modify | Add `./tmux.sh` note to Quick Start |

---

### Task 1: Create tmux.sh

**Files:**
- Create: `tmux.sh`

- [ ] **Step 1: Write `tmux.sh`**

Create `/home/klyons/ws/Unify_V2/tmux.sh` with the following content:

```bash
#!/usr/bin/env bash
# tmux.sh — Launch the Unify V2 dev environment in a tmux session.
#
# Layout:
#   ┌─────────────────────────────┐
#   │  top pane  (free shell)     │  ~60% — cursor starts here
#   ├─────────────────────────────┤
#   │  bottom pane  ./launch.sh   │  ~40%
#   └─────────────────────────────┘
#
# Usage: ./tmux.sh
#   - If session 'unify' already exists, attaches to it.
#   - Otherwise creates the session, starts ./launch.sh in the bottom pane,
#     and opens a free shell in the top pane.
#
# The Python venv is handled inside launch.sh — no extra setup needed here.

set -euo pipefail

SESSION="unify"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# If the session already exists, just attach to it.
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Session '$SESSION' already exists — attaching."
    exec tmux attach -t "$SESSION"
fi

# Create a new detached session. The first window starts as one full-height pane.
tmux new-session -d -s "$SESSION" -c "$REPO_ROOT"

# Split the window: current pane becomes top (~60%), new pane is bottom (~40%).
# -v = vertical split (horizontal divider), -p 40 = bottom pane gets 40% of height.
tmux split-window -v -p 40 -t "$SESSION" -c "$REPO_ROOT"

# Send ./launch.sh to the bottom pane (pane index 1).
tmux send-keys -t "${SESSION}:0.1" "./launch.sh" Enter

# Select the top pane (pane index 0) so the cursor lands there on attach.
tmux select-pane -t "${SESSION}:0.0"

# Attach to the session.
exec tmux attach -t "$SESSION"
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x /home/klyons/ws/Unify_V2/tmux.sh
```

- [ ] **Step 3: Verify syntax**

```bash
bash -n /home/klyons/ws/Unify_V2/tmux.sh
```

Expected: no output (syntax OK).

- [ ] **Step 4: Smoke test — create session**

Run from the repo root (outside any existing tmux session):

```bash
# Kill any leftover test session first
tmux kill-session -t unify 2>/dev/null || true

# Run the script (it will attach; immediately detach with Ctrl-b d to inspect)
# For non-interactive testing, use:
tmux kill-session -t unify 2>/dev/null || true
bash /home/klyons/ws/Unify_V2/tmux.sh &
sleep 2

# Verify session exists
tmux has-session -t unify && echo "PASS: session exists" || echo "FAIL: session not created"

# Verify two panes exist in window 0
PANE_COUNT=$(tmux list-panes -t unify:0 | wc -l)
[ "$PANE_COUNT" -eq 2 ] && echo "PASS: 2 panes" || echo "FAIL: expected 2 panes, got $PANE_COUNT"

# Verify active pane is index 0 (top)
ACTIVE_PANE=$(tmux display-message -t unify:0 -p '#{pane_index}')
[ "$ACTIVE_PANE" -eq 0 ] && echo "PASS: top pane active" || echo "FAIL: expected pane 0, got $ACTIVE_PANE"

# Clean up
tmux kill-session -t unify 2>/dev/null || true
```

Expected output:
```
PASS: session exists
PASS: 2 panes
PASS: top pane active
```

- [ ] **Step 5: Smoke test — attach-if-exists**

```bash
# Create session manually
tmux new-session -d -s unify -c /home/klyons/ws/Unify_V2

# Run tmux.sh — it should print "Session 'unify' already exists — attaching."
# and then attach (exec tmux attach). Run in background + kill quickly.
(tmux.sh 2>&1 & sleep 1; tmux kill-session -t unify 2>/dev/null) | grep -q "already exists" \
  && echo "PASS: attach-if-exists works" \
  || echo "FAIL: did not detect existing session"

tmux kill-session -t unify 2>/dev/null || true
```

Expected: `PASS: attach-if-exists works`

Note: `exec tmux attach` will fail in a headless test context (no terminal to attach to) — that's expected and OK. The important thing is the session detection message appears.

- [ ] **Step 6: Commit**

```bash
cd /home/klyons/ws/Unify_V2
git add tmux.sh
git commit -m "feat: add tmux.sh for split-pane dev environment"
```

---

### Task 2: Update README.md Quick Start

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Find the Quick Start section**

Read `/home/klyons/ws/Unify_V2/README.md`. Locate the Quick Start section. It currently ends with:

```
Open `http://localhost:5173` in your browser. Press **Ctrl+C** to stop both servers.
```

- [ ] **Step 2: Add the tmux.sh alternative after that line**

Insert the following block immediately after the line above (before the next `---` separator):

```markdown
Alternatively, use `./tmux.sh` to launch inside a tmux session — the app runs in the bottom pane and the top pane is free for other work:

```bash
./tmux.sh
```

If a `unify` tmux session is already running, this attaches to it instead of starting a new one.
```

- [ ] **Step 3: Verify the README renders cleanly**

Read the modified README and confirm:
- No unclosed code fences
- The new block appears between the Quick Start body and the next `---` section divider
- The paragraph and code fence are both present

- [ ] **Step 4: Commit**

```bash
cd /home/klyons/ws/Unify_V2
git add README.md
git commit -m "docs: add tmux.sh usage to README Quick Start"
```

---

## Self-Review

- [x] Spec requirement: `tmux.sh` created at repo root — covered by Task 1
- [x] Spec requirement: attach-if-exists — covered by Task 1 Step 5
- [x] Spec requirement: 60/40 split, top pane active — covered by Task 1 Steps 3-4
- [x] Spec requirement: `./launch.sh` sent to bottom pane — in the script content
- [x] Spec requirement: README updated — covered by Task 2
- [x] No placeholders, no TBDs
- [x] All commands are exact and complete
- [x] Venv note: explicitly documented in script comment that venv is handled by `launch.sh`
