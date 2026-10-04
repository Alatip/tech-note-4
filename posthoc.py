"""POST-HOC (not pre-registered) decomposition, written after run.py results were seen.
Splits S- (round-0 mode wrong) into S-/3-0 (all three agents wrong at round 0: no correct
minority) and S-/2-1 (one correct agent at round 0), and reports per-round agent accuracy
and majority-correct (correction) rate for each, with cluster bootstrap CIs. Also the
across-model relation between the net debate gain D1 and round-0 majority accuracy MV0.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import load, arrays, GROUPS, RMAX, OUT, B, SEED

rng = np.random.default_rng(SEED)
res = {}
lines = []
for grp, names in GROUPS.items():
    for name in names:
        d = load(name); C, MV, UNAN, strat = arrays(d)
        n0 = C[0].sum(1)                       # correct agents at round 0
        sub = {"S-_3-0": (strat == -1) & (n0 == 0), "S-_2-1": (strat == -1) & (n0 == 1),
               "S+_2-1": (strat == 1) & (n0 == 2), "S+_3-0": (strat == 1) & (n0 == 3), "S0": strat == 0}
        clusters = {}
        for i, q in enumerate(d["qids"]): clusters.setdefault(q, []).append(i)
        cl = list(clusters.values())
        r = {}
        for lab, m in sub.items():
            idx = np.where(m)[0]
            if len(idx) == 0: continue
            A = [float(C[k][idx].mean()) for k in range(RMAX + 1)]
            M = [float(MV[k][idx].mean()) for k in range(RMAX + 1)]
            bs = []
            for _ in range(B):
                pick = rng.integers(0, len(cl), len(cl)); ii = np.concatenate([cl[j] for j in pick]); ii = ii[m[ii]]
                bs.append(float(MV[RMAX][ii].mean()) if len(ii) else np.nan)
            r[lab] = dict(n=int(len(idx)), A=A, MV=M, MV3_ci=[float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))])
        res[name] = r
        lines.append(f"\n[{grp}] {name} n={d['n']}")
        for lab, v in r.items():
            lines.append(f"  {lab:7s} n={v['n']:5d}  agent acc r0..3: " + " ".join(f"{x:.3f}" for x in v["A"]) +
                         "   majority-correct r0..3: " + " ".join(f"{x:.3f}" for x in v["MV"]) +
                         f"   MV3 CI [{v['MV3_ci'][0]:.3f}, {v['MV3_ci'][1]:.3f}]")
summ = json.load(open(f"{OUT}/summary.json"))["files"]
mv0 = np.array([summ[n]["MV"][0] for n in summ]); d1 = np.array([summ[n]["D1"] for n in summ])
rho = float(np.corrcoef(mv0, d1)[0, 1]); sl, ic = np.polyfit(mv0, d1, 1)
lines.append(f"\nAcross 16 files: Pearson r(MV0, D1=MV3-MV0) = {rho:.3f}; D1 ~ {ic:+.3f} {sl:+.3f}*MV0")
pr = [n for n in summ if summ[n]["group"] == "P"]
lines.append("Primary 6: " + "; ".join(f"{n.split('traces_')[1]}: MV0={summ[n]['MV'][0]:.3f} D1={summ[n]['D1']:+.3f}" for n in pr))
txt = "\n".join(lines); print(txt)
open(f"{OUT}/posthoc.log", "w").write(txt + "\n"); json.dump(dict(subsets=res, r_mv0_d1=rho, slope=float(sl), intercept=float(ic)), open(f"{OUT}/posthoc.json", "w"), indent=1)
