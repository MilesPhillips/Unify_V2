# Tmux Launch Environment Design

**Date:** 2026-04-11  
**Status:** Approved

---

## Goal

Provide a single script (`tmux.sh`) that creates a two-pane tmux session for Unify V2 development: the bottom pane runs the app via `./launch.sh`, the top pane is a free shell for other work.

---

## Architecture

A single new shell script `tmux.sh` at the repo root. It is entirely independent of `launch.sh` — `launch.sh` is unchanged and still works on its own.

---

## Behavior

### If session `unify` already exists

Attach to it immediately:

```bash
tmux attach -t unify
```

No layout changes, no duplicate server processes.

### If session `unify` does not exist

1. Create a new detached tmux session named `unify`, starting in the repo root directory
2. Split the window horizontally: top pane ~60% of terminal height, bottom pane ~40%
3. Send `./launch.sh` followed by Enter to the bottom pane
4. Select the top pane (cursor lands here on attach)
5. Attach to the session

---

## Layout

```
┌─────────────────────────────────┐
│                                 │
│   top pane — free shell         │  ~60% height, active on attach
│                                 │
├─────────────────────────────────┤
│   bottom pane — ./launch.sh     │  ~40% height
└─────────────────────────────────┘
```

---

## Files

| File | Action | Purpose |
|---|---|---|
| `tmux.sh` | Create | Entry-point script |
| `README.md` | Modify | Add `./tmux.sh` note to Quick Start |

---

## Session name

`unify` — matches the project name, short, easy to type in `tmux attach -t unify`.

---

## Non-goals

- No status bar customization
- No additional windows/panes beyond the two described
- No changes to `launch.sh`
- No changes to how `launch.sh` selects the database (that prompt still appears in the bottom pane)
