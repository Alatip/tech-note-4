# Already-done check — bridge 2510.01279 (TUMIX) -> 2606.28661 (modal ceiling)

Date: 2026-10-04. Searched: web search (arXiv 2025–2026) for multi-agent
debate × majority convergence / stopping rules / inter-agent correlation;
Semantic Scholar citation graphs of 2606.28661 (7 citers), 2510.01279
(13 citers) and 2609.35279 (0 citers); the swarm-lbd corpus cards
(2609.33974, 2510.12697, 2608.05956, 2511.07784, 2608.02827).

Hypothesis under test (judge, strength 6/10): in TUMIX-style refinement,
(i) majority-vote accuracy after round r is bounded by / tracks π_mode;
(ii) refinement helps only on problems whose first-round mode is correct and
HURTS (anti-scales) on problems whose first-round mode is wrong; (iii) a
stopping rule on the change of n_eff = n/[1+(n−1)ρ_w] between rounds matches
or beats the LLM judge on cost/accuracy.

## Verdict: PARTLY done. The ingredients exist in two 2026 papers; the
## per-problem anti-scaling test, the modal-ceiling reading of debate and a
## correlation-based stopping rule do not.

| paper | what it does | overlap | gap |
|---|---|---|---|
| **Ringelmann Effect in Multi-Agent LLM Systems, arXiv 2606.02646** (Jun 2026) | Qwen2.5-7B/32B etc., MMLU-Hard / GSM-Hard / GPQA, N up to 30, debate vs self-correction vs noise placebo, 3 rounds. Computes pairwise agreement ρ and **N_eff^corr = N/(1+(N−1)ρ_ICC)** on correctness indicators per round; shows ρ rises over debate rounds (GSM-Hard 0.51 -> 0.78), mean-field contraction theorem ρ^(τ) ≈ 1−(1−ρ^(0))(1−α)^(kτ); initial ρ^(0) sets the ceiling; heterogeneous teams the only lever. Cites neither A nor B. | **Closest.** Covers the premise of (iii): rounds raise ρ and shrink n_eff, measured with the same design-effect formula. | Fixed 3 rounds, no stopping rule; no per-problem split by initial-mode correctness (no anti-scaling test); no π_mode; cohort-level only. |
| **DebateLedger / Measuring Collapse and Correction in Homogeneous-Panel LLM Debate, arXiv 2609.35279** (NeurIPS 2026 D&B; data CC-BY 4.0 on HF `XINLI1997/DebateLedger`) | 3 copies of one model × 3 rounds on MMLU-Pro, 6,925 debates (6 models) + extensions (hetero panels, GSM8K, reasoning on/off). 2×2 ledger initial-majority × final-majority (preserved / collapse / correction / unrepaired), onset round, 253 collapses; R1 features predict collapse (AUC 0.67 -> 0.77); freeze-after-R1 replay is net-negative. | Conditions on initial majority correctness — the same split as (ii) — but counts majority transitions only. Initial-majority accuracy is noted as a "close comparator" (ρ = 0.821 across models). | No per-round accuracy curves on the initially-wrong subset (anti-scaling); no ρ / n_eff / π_mode; no stopping rule beyond freeze-at-R1. **Its traces are the data for this test.** |
| Multi-Agent Debate for LLM Judges with Adaptive Stability Detection, 2510.12697 (in corpus) | 7 copies, up to 10 rounds; stop when the Beta-Binomial mixture of per-round correct counts stops changing (KS < 0.05); theory assumes conditional independence. | A distribution-stability stopping rule for debate. | Needs gold labels to fit the correct-count distribution; ignores correlation; no per-problem anti-scaling. |
| Sequential Consensus for Multi-Agent LLM Debates, 2605.19193 | Wald SPRT on a judge's consensus score; 3 heterogeneous frontier agents, MMLU/GSM8K 200 items. | Stopping rule with error guarantees. | Judge-score based, not agreement/ρ; collapses on MMLU (caps at R_max on 99.5%). |
| EMS: Majority-then-Stopping, 2604.02863 | Stop once the leading answer cannot be overturned by remaining agents. | Agreement-based early stop. | Single round of voting, not refinement. |
| Talk Isn't Always Cheap, 2509.05396 | Debate lowers accuracy over rounds; correct agents flip to wrong under peer pressure. | Qualitative anti-scaling. | No conditioning on initial mode, no ρ. |
| Can LLM Agents Really Debate?, 2511.07784 (in corpus) | Knight-Knave-Spy puzzles; "agents rarely overturn an incorrect majority". | Same direction as (ii). | Logic puzzles, 3-agent teams, no per-round correlation. |
| Estornell & Liu 2024 (NeurIPS), Smit et al. 2024 "Should we be going MAD?" | Debate ≈ majority dynamics; debate rarely beats voting. | Folk version of (i). | No modal-ceiling quantification. |
| Modal-ceiling citers (2610.01014, 2609.39560, 2609.26144, 2608.21262…) | Voting under budgets, self-repulsive sampling, verifier voting, exceedance design effect. | Use B's tools on i.i.d. samples. | None applies B to refinement rounds. |

TUMIX itself: code and logs not released as of 2026-10-04 (only a third-party
Go re-implementation, github.com/zchee/tumix). So A's own 15-agent traces
cannot be re-analysed; DebateLedger's 3-agent traces are the closest public
substitute (3 agents, 4 answer states per problem, gold labels, ~9k debates).

## Consequence for the test

- Novelty that remains: (a) the **per-problem anti-scaling** test — accuracy
  trajectory on problems whose round-0 mode is wrong vs correct, with the
  selection bias handled (condition on round 0, test rounds 1→3); (b) the
  **modal-ceiling reading**: final majority accuracy vs round-0 modal-hit
  rate, i.e. whether corrections and collapses net to zero; (c) B's ANOVA
  ρ_w / ρ_b per round (Ringelmann has pairwise agreement; same quantity in a
  different estimator — acknowledge, do not oversell); (d) an **n_eff-plateau
  stopping rule** scored against fixed-3 and stop-at-unanimity. Expect a
  reviewer to call (c) a replication of Ringelmann on a public dataset.
- What cannot be tested here: the LLM-judge stopping rule of A (no judge in
  the data; 3 rounds only, so "plateau" can be detected only at r=2 or 3);
  15 heterogeneous tool agents (we have 3 homogeneous copies, plus 3 small
  heterogeneous panels of 200). Hypothesis (i) as written is degenerate on
  one panel of 3 (π_mode of a single round IS the majority-vote correctness),
  so it is reformulated in PREDICTION.md.
- Zero inference spend: pure re-analysis.
