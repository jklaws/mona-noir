#!/usr/bin/env python3
"""Aggregate player files into leaderboard.json and graph_state.json.

Reads players/*.json, computes each player's score + collection, and writes the derived
leaderboard (sorted, with a tier label) and the global Graph-restored meter. Standard
library only; run by .github/workflows/aggregate.yml on every push to players/**.
"""
import json
import glob
import os
import datetime

TIERS = ["Intern", "Triage Detective", "Merge Sleuth", "Graph Guardian", "Root Key Holder"]
NODE_TARGET = 10  # districts including the Root Node

MAX_SCORE = 200000
MAX_NODES = 10
MAX_PINS = 22
KEY = bytes.fromhex(os.environ["MONA_KEY"]) if os.environ.get("MONA_KEY") else None


def _dv(h, sc, nodes, pins, uid):
    m = ("%s|%d|%s|%s" % (h, sc, ",".join(sorted(nodes)), ",".join(sorted(pins)))).encode()
    v = 0xcbf29ce484222325
    for b in KEY + uid + m:
        v ^= b
        v = (v * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % v


def _valid(p):
    sc = int(p.get("score", 0))
    nodes = p.get("nodes_restored", []) or []
    pins = p.get("pins", []) or []
    if sc < 0 or sc > MAX_SCORE:
        return False
    if len(nodes) > MAX_NODES or len(pins) > MAX_PINS:
        return False
    if KEY is None:
        return True
    dev = p.get("device")
    chk = p.get("chk")
    if not dev or not chk:
        return False
    try:
        uid = bytes.fromhex(dev)
    except Exception:
        return False
    h = p.get("github_handle") or p.get("player_id")
    return _dv(h, sc, nodes, pins, uid) == chk


def tier_for(rank, total):
    if total <= 0:
        return TIERS[0]
    if rank == 0:
        return TIERS[4]            # #1 operative = Root Key Holder
    q = rank / total
    if q < 0.10:
        return TIERS[3]
    if q < 0.35:
        return TIERS[2]
    if q < 0.70:
        return TIERS[1]
    return TIERS[0]


def main():
    players = []
    for path in sorted(glob.glob("players/*.json")):
        if os.path.basename(path) == "example.json":
            continue
        try:
            with open(path) as f:
                p = json.load(f)
        except Exception:
            continue
        if not _valid(p):
            print("skip (failed verification):", os.path.basename(path))
            continue
        players.append({
            "handle": p.get("github_handle") or p.get("player_id"),
            "score": int(p.get("score", 0)),
            "pins": len(p.get("pins", []) or []),
            "nodes": len(p.get("nodes_restored", []) or []),
        })

    players.sort(key=lambda x: (x["score"], x["pins"]), reverse=True)
    total = len(players)
    standings = []
    for i, pl in enumerate(players):
        pl["rank"] = i + 1
        pl["tier"] = tier_for(i, total)
        standings.append(pl)

    now = datetime.datetime.utcnow().isoformat() + "Z"
    note = "Derived state - rewritten by tools/aggregate.py. Do not edit by hand."

    with open("leaderboard.json", "w") as f:
        json.dump({"tiers": TIERS, "standings": standings, "updated_at": now, "note": note}, f, indent=2)

    nodes_total = sum(pl["nodes"] for pl in players)
    pct = max(0, min(100, round((nodes_total / len(players) / NODE_TARGET) * 100))) if players else 0
    with open("graph_state.json", "w") as f:
        json.dump({
            "restored_percent": pct,
            "nodes_restored_total": nodes_total,
            "milestones": {
                "10": "Rare pins enter the pool",
                "25": "Defense pins unlock",
                "50": "NULLCAT corruption events begin",
                "75": "Ultra-rare chances unlock",
                "100": "Root Node opens",
            },
            "updated_at": now,
            "note": note,
        }, f, indent=2)

    print("aggregated %d players; graph %d%%" % (total, pct))


if __name__ == "__main__":
    main()
