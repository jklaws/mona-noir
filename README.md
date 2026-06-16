# MONA NOIR: Ghost in the Graph

A hacking / collect-a-thon game for the **GitHub Universe badge** (Pimoroni Badger 2350).
This repository is the game's **online backend and live world** — gameplay events from
badges become real GitHub activity here (commits, issues, releases), and a GitHub Action
recomputes the leaderboard and the global "Graph restored" meter.

> Status: early scaffold. The on-device game lives in the badge firmware; this repo is the
> shared world that in-person (IR) and remote (Wi-Fi) players both contribute to.

## How it works
- **Crack a node / mint a pin** → a commit to `players/<handle>.json` (greens your real
  contribution graph).
- **Breach another player** → an Issue `BREACH: @you -> @victim (pin: ...)` plus a commit
  moving the pin; the victim re-cracks the node to recover it.
- **Leaderboard + Graph meter** → `tools/aggregate.py` runs in GitHub Actions on every push
  to `players/**` and rewrites `leaderboard.json` and `graph_state.json`.
- **Live status page** → `docs/` is served by GitHub Pages and shows the Graph meter and
  leaderboard.

## Layout
- `world/world.json` — the districts (nodes), their tiers, and physical IR beacon codes.
- `data/pins.json` — every collectible pin, by rarity tier and set.
- `data/drop_tables.json` — which pins drop at which tier / on a perfect crack.
- `players/<handle>.json` — one file per player (score, restored nodes, pin collection).
- `events/<handle>/` — append-only case-note batches synced from a badge (anti-cheat trail).
- `leaderboard.json`, `graph_state.json` — **derived** state (written by the Action; do not edit by hand).
- `tools/aggregate.py` — the aggregator the Action runs.
- `docs/index.html` — the GitHub Pages live board.

## Districts (map 1:1 to the badge's IR beacons)
See `world/world.json`. Each district has a physical NEC beacon code (address `0x45`,
commands `0x11`–`0x99`), so in-person players crack it over infrared while remote players
crack the same node over Wi-Fi.

## Setup
1. **Pages:** Settings → Pages → Source = `main` / `/docs` to publish the live board.
2. **Actions:** Settings → Actions → General → Workflow permissions = **Read and write** so
   the aggregator can commit derived state.

## Run the aggregator locally
`python tools/aggregate.py` — reads `players/*.json`, rewrites `leaderboard.json` and
`graph_state.json`. Standard library only.
