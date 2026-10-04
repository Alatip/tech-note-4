# Data provenance

All files downloaded 2026-10-04 from the Hugging Face dataset
`XINLI1997/DebateLedger` (open tier, CC-BY 4.0, last modified 2026-09-30),
path `abc_exp/results/`, with `curl -L .../resolve/main/...`. Paper:
"Measuring Collapse and Correction in Homogeneous-Panel LLM Debate",
arXiv 2609.35279 (NeurIPS 2026 D&B). Model-generated text is `null` in
this tier; parsed answers, gold labels and round structure are complete.

Primary cohort (legacy schema: `initial_answers`, `round_traces[].answers`,
3 rounds): `debate_traces_{gemini_3-flash, openai_gpt-5.4-mini,
vllm_llama-3.1-8b, vllm_phi-4-mini, vllm_qwen3-4b, vllm_qwen3-8b}.jsonl`
(6,925 debates).

Extensions (new schema: `initial_states[].answer`,
`round_traces[][].answer`): heterogeneous panels `debate_traces_hetero_*`
(3 x 200, 4 rounds), GSM8K `debate_traces_gsm8k_*` (300/299/300, 4 rounds),
reasoning on/off `debate_traces_vllm_q{8b,32b}_think{ON,OFF}_peer_r3_*`
(4 x 200, 3 rounds); self-only controls (agent sees only its own previous answer)
`debate_traces_vllm_q8b_think{ON,OFF}_self_r3_*` (2 x 200), downloaded after the
pre-registered run for the post-hoc control in control.py.

Docs copied verbatim: HF-README.md (dataset card), README_REPRO.md,
DEBATE_EVAL_ARTIFACT_DATASHEET.md, CONDITIONAL_COLLAPSE_TABLE.md,
conditional_collapse_table.json, per_debate_r1_features.schema.json.

Pre-analysis inspection only (before PREDICTION.md): row counts, duplicate
question_ids (Llama-3.1-8B: 13), `None` answer counts (<= 1.2% per file),
number of rounds per file. No outcome metric was computed.
