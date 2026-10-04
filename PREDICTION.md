# Pre-registration — modal ceiling and n_eff in multi-round debate

Written 2026-10-04 BEFORE any outcome metric was computed on the data (only
schema/duplicate/None counts were inspected, see data/README.md). Bridge:
arXiv 2510.01279 (TUMIX) -> arXiv 2606.28661 (modal ceiling / correlation
ceiling), judged 6/10.

## Data (public, CC-BY 4.0, zero inference spend)

DebateLedger open tier (HF `XINLI1997/DebateLedger`, snapshot 2026-09-30,
paper arXiv 2609.35279). Each record: one question, 3 agents, independent
round 0, then rounds 1..R where every agent sees all current answers;
parsed answer letter per agent per round; gold label. Protocol: TUMIX-style
all-to-all sharing, majority vote, but 3 homogeneous copies instead of 15
heterogeneous tool agents and no LLM judge.

- Primary P (6 files, 6,925 debates, MMLU-Pro, R=3): Gemini 3-flash (200),
  GPT-5.4-mini (200), Llama-3.1-8B (2,003; 13 duplicate question_ids),
  Phi-4-mini (2,161), Qwen3-4B (2,161), Qwen3-8B (200).
- Robustness R1 heterogeneous panels (3 × 200, MMLU-Pro, R=4; 3 different
  models per panel); R2 GSM8K free-form (3 × ~300, R=4); R3 reasoning
  on/off Qwen3-8B/32B (4 × 200, R=3). Only rounds 0..3 are used everywhere.

Correctness c[q,a,r] = 1 if agent a's parsed answer at round r equals the
gold label. `None` (parse failure) counts as incorrect for the agent and is
dropped from the vote. Majority at round r: plurality over non-None answers,
3-way tie / all-None -> "no mode" (counted as incorrect for MV; tie problems
form their own stratum S0 and are excluded from S+/S−).

## Hypotheses, exact statistics, falsifiers

Statistics are per model (file). Uncertainty: cluster bootstrap over
question_id, B = 2,000, percentile 95% CI. "Holds" = criterion met on at
least 4 of the 6 primary files; the small files (n = 200) are reported but
the decision uses all six equally, since each has its own CI.

**H1 — modal ceiling (reformulated).** B says plurality voting converges to
π_mode; in a refinement process the round-0 answers are the only ones that
are not already contaminated by sharing, so the operational claim is:
final majority accuracy MV_3 does not exceed the round-0 modal-hit rate
MV_0 = π_mode^(0) by more than noise, i.e. corrections and collapses net to
roughly zero, and across models MV_3 tracks MV_0.
- Statistic: D1 = MV_3 − MV_0 per model, with CI.
- Holds if the CI of D1 lies within [−0.03, +0.03] on >= 4/6 files AND
  the across-model Pearson r(MV_0, MV_3) over all 16 files >= 0.9.
- Falsified (debate beats the ceiling) if D1's CI is entirely above +0.03 on
  >= 3/6 files. Falsified in the other direction (debate destroys the mode)
  if entirely below −0.03 on >= 3/6.
- Note: with 3 agents the per-round π_mode IS the per-round MV correctness,
  so "MV_r tracks mean π_mode of round r" is an identity and is not tested.

**H2 — per-problem anti-scaling.** Split problems by the round-0 mode:
S+ (mode correct), S− (mode wrong, 2 or 3 agents agree on a wrong letter),
S0 (no mode). B's Corollary: on S− more sampling drives plurality to the
wrong mode. In refinement the analogue is that agents on S− drift toward
the shared wrong answer, so per-agent accuracy on S− FALLS with rounds.
Selection bias: conditioning on round 0 depresses A_0(S−) by construction
(<= 1/3), so round 0 is NOT compared; the trend is tested over rounds 1→3,
all of which are "future" relative to the conditioning.
- Statistics: A_r(S) = mean agent accuracy on stratum S at round r;
  D2 = A_3(S−) − A_1(S−); D2+ = A_3(S+) − A_1(S+);
  C_r = MV accuracy on S− at round r (correction rate), D2c = C_3 − C_1.
- Holds if D2 < 0 with CI excluding 0 on >= 4/6 files, AND D2c <= 0 (CI
  not entirely above 0) on >= 4/6. Expected size: D2 in [−0.08, −0.02].
- Falsified if D2 > 0 with CI excluding 0 on >= 3/6 (agents on wrong-mode
  problems keep recovering — refinement is self-correcting, not modal).
- Descriptive: the same on S+ (expected D2+ >= 0: agents join the correct
  mode); the S−/S+ asymmetry is the modal-ceiling signature.

**H3 — ρ_w rises, n_eff shrinks, and an n_eff-plateau stopping rule.**
B's ANOVA estimator on the 3 × Q correctness matrix of round r gives the
within-problem inter-agent correlation ρ_w^(r) (ICC(1), one-way random
effects over problems; also report the between-problem difficulty share
ρ_b as in B's two-stage decomposition) and n_eff^(r) = 3/(1 + 2 ρ_w^(r)).
- H3a holds if ρ_w^(r) is non-decreasing in r = 0..3 on >= 5/6 files and
  ρ_w^(3) − ρ_w^(0) > 0 with CI excluding 0 on >= 4/6. (Ringelmann 2606.02646
  reports the same direction with pairwise agreement on other data; this is
  a replication with B's estimator, not a new claim.)
- H3b stopping rule. Cohort-level rule: stop after the first round r >= 1
  with |n_eff^(r) − n_eff^(r−1)| < ε, ε = 0.05 (ε fixed now; a sweep over
  {0.02, 0.05, 0.10} is reported as sensitivity). Per-problem rule
  (practical analogue, no labels needed): stop a problem at the first round
  r >= 1 where the 3 answers are unanimous ("unanimity"). Baselines:
  fixed R=3 (upper cost), fixed R=1, and "oracle best round".
  Score each rule by (accuracy of the majority at the stopping round, mean
  number of rounds). Holds if the n_eff-plateau rule keeps accuracy within
  −0.01 of fixed-3 while using <= 2/3 of its rounds on >= 4/6 files;
  falsified if it loses > 0.02 on >= 3/6 or never stops before round 3 on
  >= 4/6. The LLM-judge rule of A cannot be scored (absent in the data).

**Robustness (descriptive, no decision):** repeat H1–H3 on R1 (hetero —
B/Ringelmann predict lower ρ_w^(0) and a weaker S− drift), R2 (GSM8K —
free-form answers make a wrong mode rarer, so S− is small), R3 (reasoning
on vs off).

**Sanity check (must pass before anything is interpreted):** our loader
reproduces DebateLedger's own counts on the primary cohort: 6,925 debates
and 253 collapses (initial majority correct, final majority wrong), using
their None-filter + alphabetical tie-break majority. If off by more than 2,
stop and fix the loader.

## Honest prior

H1 ~65% (DebateLedger's ρ = 0.82 and the small collapse rates point this
way, but Qwen3-8B reports 49% recovery, so some small files may exceed
+0.03). H2 ~55%: the direction is what every "conformity" paper reports,
but 2 rounds of trend with n(S−) ≈ 100 on the 200-question files is weak,
and Llama/Phi/Qwen-4B (n(S−) ≈ 1,000) will decide it. H3a ~85%. H3b ~40%:
with only 3 rounds the cohort-level plateau may land at r=2 trivially or
never, and unanimity will probably be the better practical rule — which is
itself an informative outcome for A's open question on Δr.
