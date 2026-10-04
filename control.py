"""POST-HOC control (not pre-registered): peer debate vs self-only revision on the same
model/questions (DebateLedger Qwen3-8B think ON/OFF, n=200 each). In self-only runs each
agent sees only its own previous answer, so any round-to-round gain is re-sampling /
self-correction, not peer influence. Reports MV per round, agent accuracy, ICC, and the
correction rate on S-/3-0 (all three wrong at round 0) and S-/2-1.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import load, arrays, RMAX, OUT, icc1
out = {}
for think in ("ON", "OFF"):
    for mode in ("peer", "self"):
        name = f"debate_traces_vllm_q8b_think{think}_{mode}_r3_mt8192_n200"
        d = load(name); C, MV, UNAN, strat = arrays(d)
        n0 = C[0].sum(1)
        row = dict(n=d["n"], MV=[float(MV[r].mean()) for r in range(RMAX+1)], A=[float(C[r].mean()) for r in range(RMAX+1)],
                   ICC=[icc1(C[r]) for r in range(RMAX+1)], unan=[float(UNAN[r].mean()) for r in range(RMAX+1)])
        for lab, m in (("S-_3-0", (strat==-1)&(n0==0)), ("S-_2-1", (strat==-1)&(n0==1)), ("S+_2-1", (strat==1)&(n0==2))):
            row[lab] = dict(n=int(m.sum()), MV=[float(MV[r][m].mean()) for r in range(RMAX+1)] if m.sum() else None)
        out[f"think{think}_{mode}"] = row
        print(f"\n{name}  MV0={row['MV'][0]:.3f}")
        print("  MV r0..3 :", " ".join(f"{x:.3f}" for x in row["MV"]), "  agent:", " ".join(f"{x:.3f}" for x in row["A"]))
        print("  ICC r0..3:", " ".join(f"{x:.3f}" for x in row["ICC"]), "  unanimity:", " ".join(f"{x:.3f}" for x in row["unan"]))
        for lab in ("S-_3-0", "S-_2-1", "S+_2-1"):
            v = row[lab]; print(f"  {lab} n={v['n']:3d} majority-correct r0..3:", " ".join(f"{x:.3f}" for x in v["MV"]) if v["MV"] else "-")
json.dump(out, open(f"{OUT}/control_self_vs_peer.json", "w"), indent=1)
