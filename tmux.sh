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
command -v tmux &>/dev/null || { echo "Error: tmux is not installed." >&2; exit 1; }

SESSION="unify"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Guard: nested tmux sessions break terminal capabilities.
if [[ -n "${TMUX:-}" ]]; then
    echo "Error: already inside a tmux session." >&2
    echo "To switch to the '$SESSION' session: tmux switch-client -t $SESSION" >&2
    exit 1
fi

# If the session already exists, just attach to it.
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Session '$SESSION' already exists — attaching."
    exec tmux attach -t "$SESSION"
fi

# Create a new detached session with a default terminal size.
# The explicit -x/-y ensures split-window works even when launched headlessly.
tmux new-session -d -s "$SESSION" -c "$REPO_ROOT" -x 220 -y 50

# Split the window: current pane becomes top (~60%), new pane is bottom (~40%).
# -v = horizontal divider (top/bottom split), -l 40% = bottom pane gets 40% of height.
tmux split-window -v -l 40% -t "$SESSION" -c "$REPO_ROOT"

# Send ./launch.sh to the bottom pane (pane index 1).
tmux send-keys -t "${SESSION}:0.1" "./launch.sh" Enter

# Select the top pane (pane index 0) so the cursor lands there on attach.
tmux select-pane -t "${SESSION}:0.0"

# Attach to the session.
exec tmux attach -t "$SESSION"
