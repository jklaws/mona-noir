# events/

Per-player **append-only case-note batches** sync here from a badge as
`events/<handle>/<batch_id>.json`. They are the anti-cheat / chain-of-custody trail:
high-value outcomes (rare drops, perfect cracks, PvP results) stay `pending` until a
GitHub Action validates the batch and updates the player's confirmed state.

This file only exists to keep the directory in the repo.
