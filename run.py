"""Modal ceiling and n_eff in multi-round debate — re-analysis of DebateLedger traces.

Protocol and falsification criteria: PREDICTION.md (committed before this
script ran). numpy only. Usage: uv run python run.py  (from this folder).
Writes results/<file>.json, results/summary.json, results/run.log.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)
RMAX = 3          # rounds used everywhere: 0..3
K = 3             # agents
B = 2000          # bootstrap replicates
SEED = 0
EPS_MAIN = 0.05
EPS_SWEEP = (0.02, 0.05, 0.10)

PRIMARY = [
    "debate_traces_gemini_3-flash", "debate_traces_openai_gpt-5.4-mini",
    "debate_traces_vllm_llama-3.1-8b", "debate_traces_vllm_phi-4-mini",
    "debate_traces_vllm_qwen3-4b", "debate_traces_vllm_qwen3-8b",
]
GROUPS = {"P": PRIMARY}
GROUPS["R1-hetero"] = sorted(os.path.basename(p)[:-6] for p in glob.glob(f"{DATA}/debate_traces_hetero_*.jsonl"))
GROUPS["R2-gsm8k"] = sorted(os.path.basename(p)[:-6] for p in glob.glob(f"{DATA}/debate_traces_gsm8k_*.jsonl"))
GROUPS["R3-think"] = sorted(os.path.basename(p)[:-6] for p in glob.glob(f"{DATA}/debate_traces_vllm_q*think*.jsonl"))

LOG = open(os.path.join(OUT, "run.log"), "w")


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


# ---------------------------------------------------------------- loading
def norm(x):
    return None if x is None else str(x).strip()


def load(name):
    """-> dict(qids, gold, ans[Q][R+1][K] (str|None), model, legacy_fields)"""
    rows = [json.loads(l) for l in open(f"{DATA}/{name}.jsonl")]
    qids, gold, ans, legacy = [], [], [], []
    for r in rows:
        if "initial_states" in r:
            rounds = [[norm(s["answer"]) for s in r["initial_states"]]]
            for t in r["round_traces"]:
                rounds.append([norm(a["answer"]) for a in t])
        else:
            rounds = [[norm(a) for a in r["initial_answers"]]]
            for t in r["round_traces"]:
                rounds.append([norm(a) for a in t["answers"]])
            legacy.append((bool(r["initial_correct"]), bool(r["final_correct"]),
                           norm(r["initial_majority"]), [norm(t["majority"]) for t in r["round_traces"]]))
        assert all(len(x) == K for x in rounds), (name, r["question_id"])
        if len(rounds) < RMAX + 1:
            raise SystemExit(f"{name}: only {len(rounds)-1} rounds")
        qids.append(r["question_id"]); gold.append(norm(r["correct_label"])); ans.append(rounds[: RMAX + 1])
    model = rows[0].get("model") or rows[0].get("model_name")
    return dict(name=name, qids=qids, gold=gold, ans=ans, model=model, legacy=legacy, n=len(rows))


def plurality(a, tiebreak=False):
    """Mode of non-None answers. 3-way tie -> None (or alphabetical if tiebreak)."""
    c = Counter(x for x in a if x is not None)
    if not c:
        return None
    top = max(c.values())
    winners = sorted(k for k, v in c.items() if v == top)
    if len(winners) > 1:
        return winners[0] if tiebreak else None
    return winners[0]


def arrays(d):
    Q = d["n"]
    C = np.zeros((RMAX + 1, Q, K), dtype=np.int8)       # agent correctness
    MV = np.zeros((RMAX + 1, Q), dtype=np.int8)          # majority correct (tie -> 0)
    MODE = np.empty((RMAX + 1, Q), dtype=object)
    UNAN = np.zeros((RMAX + 1, Q), dtype=bool)           # all 3 non-None and equal
    for q in range(Q):
        g = d["gold"][q]
        for r in range(RMAX + 1):
            a = d["ans"][q][r]
            C[r, q] = [1 if x == g else 0 for x in a]
            m = plurality(a)
            MODE[r, q] = m
            MV[r, q] = 1 if m == g else 0
            UNAN[r, q] = (None not in a) and len(set(a)) == 1
    # strata by round-0 mode
    strat = np.array([1 if MODE[0, q] == d["gold"][q] else (0 if MODE[0, q] is None else -1) for q in range(Q)])
    return C, MV, UNAN, strat


# ---------------------------------------------------------------- statistics
def icc1(y):
    """One-way ANOVA intraclass correlation, y: (Q, K)."""
    Q, k = y.shape
    y = y.astype(float)
    gm = y.mean()
    qm = y.mean(1)
    msb = k * ((qm - gm) ** 2).sum() / (Q - 1)
    msw = ((y - qm[:, None]) ** 2).sum() / (Q * (k - 1))
    den = msb + (k - 1) * msw
    return float((msb - msw) / den) if den > 0 else float("nan")


def stats(C, MV, UNAN, strat, idx):
    """All point statistics on the problems in idx (array of indices)."""
    C, MV, UNAN, strat = C[:, idx], MV[:, idx], UNAN[:, idx], strat[idx]
    Q = len(idx)
    out = {}
    out["MV"] = [float(MV[r].mean()) for r in range(RMAX + 1)]
    out["A"] = [float(C[r].mean()) for r in range(RMAX + 1)]
    out["D1"] = out["MV"][RMAX] - out["MV"][0]
    for lab, s in (("Splus", 1), ("Sminus", -1), ("S0", 0)):
        m = strat == s
        out[f"n_{lab}"] = int(m.sum())
        if m.sum() > 0:
            out[f"A_{lab}"] = [float(C[r][m].mean()) for r in range(RMAX + 1)]
            out[f"MV_{lab}"] = [float(MV[r][m].mean()) for r in range(RMAX + 1)]
        else:
            out[f"A_{lab}"] = [float("nan")] * (RMAX + 1)
            out[f"MV_{lab}"] = [float("nan")] * (RMAX + 1)
    out["D2"] = out["A_Sminus"][RMAX] - out["A_Sminus"][1]
    out["D2plus"] = out["A_Splus"][RMAX] - out["A_Splus"][1]
    out["D2c"] = out["MV_Sminus"][RMAX] - out["MV_Sminus"][1]
    out["ICC"] = [icc1(C[r]) for r in range(RMAX + 1)]
    rb = out["ICC"][0]
    out["rho_b"] = rb
    out["rho_w"] = [(out["ICC"][r] - rb) / (1 - rb) if rb < 1 else float("nan") for r in range(RMAX + 1)]
    out["n_eff"] = [K / (1 + (K - 1) * max(rho, 0.0)) for rho in out["ICC"]]
    out["dICC"] = out["ICC"][RMAX] - out["ICC"][0]
    out["unanimity_rate"] = [float(UNAN[r].mean()) for r in range(RMAX + 1)]
    # pairwise agreement on raw answers is not available here (correctness only); use UNAN as proxy
    # stopping rules
    rules = {}
    rules["fixed1"] = (out["MV"][1], 1.0)
    rules["fixed3"] = (out["MV"][RMAX], float(RMAX))
    # per-problem unanimity at first r>=1
    stop = np.full(Q, RMAX)
    for r in range(RMAX, 0, -1):
        stop = np.where(UNAN[r], r, stop)      # smallest r>=1 with unanimity (later rounds overwritten by earlier)
    acc = MV[stop, np.arange(Q)].mean()
    rules["unanimity"] = (float(acc), float(stop.mean()))
    # oracle best round per problem (upper bound)
    rules["oracle"] = (float(MV[1:].max(0).mean()), float("nan"))
    # cohort n_eff plateau
    for eps in EPS_SWEEP:
        rstar = RMAX
        for r in range(1, RMAX + 1):
            if abs(out["n_eff"][r] - out["n_eff"][r - 1]) < eps:
                rstar = r
                break
        rules[f"neff_eps{eps}"] = (out["MV"][rstar], float(rstar))
    out["rules"] = rules
    return out


def boot(C, MV, UNAN, strat, qids, keys, rng):
    """Cluster bootstrap over question_id. Returns {key: (lo, hi)} for scalar keys
    and list keys (per-round)."""
    clusters = {}
    for i, q in enumerate(qids):
        clusters.setdefault(q, []).append(i)
    cl = list(clusters.values())
    n = len(cl)
    acc = {k: [] for k in keys}
    for _ in range(B):
        pick = rng.integers(0, n, n)
        idx = np.concatenate([cl[j] for j in pick])
        s = stats(C, MV, UNAN, strat, idx)
        for k in keys:
            v = s
            for part in k.split("/"):
                v = v[int(part)] if part.isdigit() else v[part]
            acc[k].append(v)
    return {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for k, v in acc.items()}


def fmt(x, ci=None, d=3):
    s = f"{x:+.{d}f}" if isinstance(x, float) and not np.isnan(x) else str(x)
    if ci:
        s += f" [{ci[0]:+.{d}f}, {ci[1]:+.{d}f}]"
    return s


# ---------------------------------------------------------------- main
def main():
    rng = np.random.default_rng(SEED)
    summary = {}
    # sanity check on primary cohort
    tot, coll, mism = 0, 0, 0
    for name in PRIMARY:
        d = load(name)
        tot += d["n"]
        for (ic, fc, im, ms), rounds, g in zip(d["legacy"], d["ans"], d["gold"]):
            coll += int(ic and not fc)
            if plurality(rounds[0], tiebreak=True) != im:
                mism += 1
            for r in range(1, RMAX + 1):
                if plurality(rounds[r], tiebreak=True) != ms[r - 1]:
                    mism += 1
    say(f"SANITY primary cohort: debates={tot} (expect 6925), collapses={coll} (expect 253), "
        f"majority mismatches vs DebateLedger fields={mism}")
    if abs(tot - 6925) > 0 or abs(coll - 253) > 2:
        say("SANITY FAILED — stop"); sys.exit(1)

    keys = ["D1", "D2", "D2plus", "D2c", "dICC"] + [f"MV/{r}" for r in range(RMAX + 1)] + \
           [f"ICC/{r}" for r in range(RMAX + 1)] + [f"A_Sminus/{r}" for r in range(RMAX + 1)] + \
           [f"MV_Sminus/{r}" for r in range(RMAX + 1)] + [f"A_Splus/{r}" for r in range(RMAX + 1)]
    for grp, names in GROUPS.items():
        for name in names:
            d = load(name)
            C, MV, UNAN, strat = arrays(d)
            idx = np.arange(d["n"])
            s = stats(C, MV, UNAN, strat, idx)
            ci = boot(C, MV, UNAN, strat, d["qids"], keys, rng)
            s["ci"] = ci
            s["group"], s["model"], s["n"] = grp, d["model"], d["n"]
            s["unanimity_rate"] = s["unanimity_rate"]
            json.dump(s, open(f"{OUT}/{name}.json", "w"), indent=1)
            summary[name] = s
            say(f"\n=== [{grp}] {name}  model={d['model']}  n={d['n']}  "
                f"S+={s['n_Splus']} S-={s['n_Sminus']} S0={s['n_S0']}")
            say("  round      :", "  ".join(f"r{r}" for r in range(RMAX + 1)))
            say("  MV acc     :", "  ".join(f"{v:.3f}" for v in s["MV"]))
            say("  agent acc  :", "  ".join(f"{v:.3f}" for v in s["A"]))
            say("  A on S-    :", "  ".join(f"{v:.3f}" for v in s["A_Sminus"]))
            say("  A on S+    :", "  ".join(f"{v:.3f}" for v in s["A_Splus"]))
            say("  MV on S-   :", "  ".join(f"{v:.3f}" for v in s["MV_Sminus"]), " (correction rate)")
            say("  ICC        :", "  ".join(f"{v:.3f}" for v in s["ICC"]), f"  rho_b={s['rho_b']:.3f}")
            say("  rho_w(shar):", "  ".join(f"{v:.3f}" for v in s["rho_w"]))
            say("  n_eff      :", "  ".join(f"{v:.3f}" for v in s["n_eff"]))
            say("  unanimity  :", "  ".join(f"{v:.3f}" for v in s["unanimity_rate"]))
            say(f"  H1 D1=MV3-MV0   : {fmt(s['D1'], ci['D1'])}")
            say(f"  H2 D2=A3-A1 S-  : {fmt(s['D2'], ci['D2'])}   D2+ S+: {fmt(s['D2plus'], ci['D2plus'])}   "
                f"D2c MV S-: {fmt(s['D2c'], ci['D2c'])}")
            say(f"  H3 dICC=ICC3-0  : {fmt(s['dICC'], ci['dICC'])}")
            say("  rules (acc, mean rounds): " + "; ".join(f"{k}=({a:.3f}, {r:.2f})" for k, (a, r) in s["rules"].items()))

    # across-model tracking (H1 second clause)
    mv0 = np.array([summary[n]["MV"][0] for n in summary]); mv3 = np.array([summary[n]["MV"][RMAX] for n in summary])
    r_all = float(np.corrcoef(mv0, mv3)[0, 1])
    pr = [n for n in PRIMARY]
    r_p = float(np.corrcoef([summary[n]["MV"][0] for n in pr], [summary[n]["MV"][RMAX] for n in pr])[0, 1])
    slope = float(np.polyfit(mv0, mv3, 1)[0])
    say(f"\nH1 across-model Pearson r(MV0, MV3): all {len(summary)} files r={r_all:.3f} slope={slope:.3f}; primary 6 r={r_p:.3f}")

    # verdicts on primary
    def within(ci, lo, hi): return ci[0] >= lo and ci[1] <= hi
    v = {}
    v["H1_within"] = sum(within(summary[n]["ci"]["D1"], -0.03, 0.03) for n in pr)
    v["H1_above"] = sum(summary[n]["ci"]["D1"][0] > 0.03 for n in pr)
    v["H1_below"] = sum(summary[n]["ci"]["D1"][1] < -0.03 for n in pr)
    v["H2_neg"] = sum(summary[n]["ci"]["D2"][1] < 0 for n in pr)
    v["H2_pos"] = sum(summary[n]["ci"]["D2"][0] > 0 for n in pr)
    v["H2c_notpos"] = sum(not (summary[n]["ci"]["D2c"][0] > 0) for n in pr)
    v["H3a_monotone"] = sum(all(np.diff(summary[n]["ICC"]) >= -1e-12) for n in pr)
    v["H3a_dpos"] = sum(summary[n]["ci"]["dICC"][0] > 0 for n in pr)
    k = f"neff_eps{EPS_MAIN}"
    v["H3b_ok"] = sum((summary[n]["rules"][k][0] >= summary[n]["rules"]["fixed3"][0] - 0.01) and
                      (summary[n]["rules"][k][1] <= 2 * RMAX / 3) for n in pr)
    v["H3b_lose"] = sum(summary[n]["rules"][k][0] < summary[n]["rules"]["fixed3"][0] - 0.02 for n in pr)
    v["H3b_never"] = sum(summary[n]["rules"][k][1] >= RMAX for n in pr)
    v["r_all"], v["r_primary"], v["slope_all"] = r_all, r_p, slope
    say("\nVERDICT COUNTS (of 6 primary files):", json.dumps(v, indent=1))
    json.dump({"files": summary, "verdict": v}, open(f"{OUT}/summary.json", "w"), indent=1)


if __name__ == "__main__":
    main()
