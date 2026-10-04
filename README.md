# tech-note-4 — Debate Is Not Sampling

Companion code for the technical note **"Debate Is Not Sampling"**
(alatip.github.io/debate-is-not-sampling/): the modal ceiling of test-time
scaling (arXiv:2606.28661) does not transfer to multi-round debate. On public
DebateLedger traces (arXiv:2609.35279) three-agent debate beats the round-0
modal-hit rate on every weak model and corrects 31–45% of problems where all
three agents started wrong; what transfers is the correlation ceiling — the
within-problem inter-agent ICC rises every round and the panel is one
effective voter by round 3.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23133114.svg)](https://doi.org/10.5281/zenodo.23133114) — archived release v1.0. The note itself: [doi:10.5281/zenodo.23133060](https://doi.org/10.5281/zenodo.23133060).

Order of reading, which is also the order the files were written in:

1. `ALREADY-DONE.md` — prior-art check before anything was run.
2. `PREDICTION.md` — pre-registration: data, hypotheses, statistics,
   falsification criteria, honest prior. Written before the first number.
3. `run.py` — the pre-registered experiment, numpy only (~15 s).
4. `posthoc.py`, `control.py` — the two post-hoc additions (all-wrong vs
   one-correct split; peer vs self-only control). Labelled as post-hoc.
5. `RESULTS.md` — findings, verdicts, limitations.
6. `results/*.json`, `results/tables.md` — every reported number;
   `tables.py` renders the tables, `results/fig*.svg` are the figures.

## Run

```
pip install -r requirements.txt     # numpy only
./data/fetch.sh                     # ~20 MB of DebateLedger traces (CC-BY 4.0)
python3 run.py                      # sanity check (6,925 / 253) + H1–H3, writes results/
python3 posthoc.py
python3 control.py
python3 tables.py
```

Data: Hugging Face dataset `XINLI1997/DebateLedger`, open tier, snapshot
2026-09-30. Model text is `null` in that tier; parsed answers, gold labels
and round structure are complete. See `data/README.md`.
