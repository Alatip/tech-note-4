"""Render results/summary.json + posthoc.json + control json into results/tables.md (numbers never typed by hand)."""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
S = json.load(open(f"{OUT}/summary.json")); F, V = S["files"], S["verdict"]
P = json.load(open(f"{OUT}/posthoc.json")); C = json.load(open(f"{OUT}/control_self_vs_peer.json"))
def short(n): return n.replace("debate_traces_", "").replace("_peer_r3_mt8192_n200", "").replace("_n200", "").replace("_n300", "")
def ci(x, c, d=3): return f"{x:+.{d}f} [{c[0]:+.{d}f}, {c[1]:+.{d}f}]"
L = []
L.append("## T1 — per file: majority accuracy by round, H1, H2, H3\n")
L.append("| group | file | n | MV0 | MV1 | MV2 | MV3 | D1 = MV3−MV0 [CI] | n(S−) | D2 = A3−A1 on S− [CI] | D2c = MV3−MV1 on S− [CI] | ICC0 | ICC3 | ΔICC [CI] | n_eff0→3 |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for n, s in F.items():
    c = s["ci"]
    L.append(f"| {s['group']} | {short(n)} | {s['n']} | {s['MV'][0]:.3f} | {s['MV'][1]:.3f} | {s['MV'][2]:.3f} | {s['MV'][3]:.3f} | {ci(s['D1'], c['D1'])} | {s['n_Sminus']} | {ci(s['D2'], c['D2'])} | {ci(s['D2c'], c['D2c'])} | {s['ICC'][0]:.3f} | {s['ICC'][3]:.3f} | {ci(s['dICC'], c['dICC'])} | {s['n_eff'][0]:.2f}→{s['n_eff'][3]:.2f} |")
L.append("\n## T2 — stopping rules (majority accuracy at stop, mean rounds)\n")
L.append("| group | file | fixed-1 | fixed-3 | unanimity (r≥1) | n_eff ε=0.02 | ε=0.05 | ε=0.10 | oracle best round |")
L.append("|---|---|---|---|---|---|---|---|---|")
for n, s in F.items():
    r = s["rules"]; f = lambda k: f"{r[k][0]:.3f} / {r[k][1]:.2f}"
    L.append(f"| {s['group']} | {short(n)} | {f('fixed1')} | {f('fixed3')} | {f('unanimity')} | {f('neff_eps0.02')} | {f('neff_eps0.05')} | {f('neff_eps0.1')} | {r['oracle'][0]:.3f} |")
L.append("\n## T3 — POST-HOC: majority-correct rate by round, problems split by round-0 state\n")
L.append("S−/3-0 = all three agents wrong at round 0 (no correct minority); S−/2-1 = one correct agent; S+/2-1 = two correct; S0 = three different answers.\n")
L.append("| group | file | n S−/3-0 | corrected r1 / r2 / r3 [CI r3] | n S−/2-1 | corrected r1 / r2 / r3 [CI r3] | n S+/2-1 | still correct r1 / r2 / r3 | n S0 | correct r1 / r2 / r3 |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for n, r in P["subsets"].items():
    g = F[n]["group"]
    def cell(lab, ci_=True):
        v = r.get(lab)
        if not v: return "– | –"
        s = f"{v['n']} | " + " / ".join(f"{x:.3f}" for x in v["MV"][1:])
        if ci_: s += f" [{v['MV3_ci'][0]:.2f}, {v['MV3_ci'][1]:.2f}]"
        return s
    L.append(f"| {g} | {short(n)} | {cell('S-_3-0')} | {cell('S-_2-1')} | {cell('S+_2-1', False)} | {cell('S0', False)} |")
L.append(f"\nAcross 16 files: Pearson r(MV0, D1) = {P['r_mv0_d1']:.3f}; D1 ≈ {P['intercept']:+.3f} {P['slope']:+.3f}·MV0.\n")
L.append("## T4 — POST-HOC control: peer debate vs self-only revision, Qwen3-8B (n=200 each)\n")
L.append("| run | MV0 | MV3 | ΔMV | agent acc 0→3 | ICC0 | ICC3 | unanimity 0→3 | S−/3-0 corrected r3 (n) | S−/2-1 corrected r3 (n) | S+/2-1 kept r3 (n) |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
for k, v in C.items():
    L.append(f"| {k} | {v['MV'][0]:.3f} | {v['MV'][3]:.3f} | {v['MV'][3]-v['MV'][0]:+.3f} | {v['A'][0]:.3f}→{v['A'][3]:.3f} | {v['ICC'][0]:.3f} | {v['ICC'][3]:.3f} | {v['unan'][0]:.3f}→{v['unan'][3]:.3f} | {v['S-_3-0']['MV'][3]:.3f} ({v['S-_3-0']['n']}) | {v['S-_2-1']['MV'][3]:.3f} ({v['S-_2-1']['n']}) | {v['S+_2-1']['MV'][3]:.3f} ({v['S+_2-1']['n']}) |")
L.append("\n## Verdict counts (6 primary files)\n")
L.append("```\n" + json.dumps(V, indent=1) + "\n```")
open(f"{OUT}/tables.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
