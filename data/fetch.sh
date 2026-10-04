#!/bin/sh
# Downloads the DebateLedger open-tier traces used by run.py / posthoc.py / control.py (~20 MB, CC-BY 4.0).
set -e
cd "$(dirname "$0")"
B=https://huggingface.co/datasets/XINLI1997/DebateLedger/resolve/main/abc_exp/results
for f in debate_traces_gemini_3-flash debate_traces_openai_gpt-5.4-mini debate_traces_vllm_llama-3.1-8b \
         debate_traces_vllm_phi-4-mini debate_traces_vllm_qwen3-4b debate_traces_vllm_qwen3-8b \
         debate_traces_hetero_dsv4f_msl4_local4b_n200 debate_traces_hetero_dsv4f_msl4_scout_n200 debate_traces_hetero_msl4_llama70b_dsv4f_n200 \
         debate_traces_gsm8k_llama_4_scout_n300 debate_traces_gsm8k_local_qwen3_4b_n300 debate_traces_gsm8k_mistral_small_4_n300 \
         debate_traces_vllm_q8b_thinkON_peer_r3_mt8192_n200 debate_traces_vllm_q8b_thinkOFF_peer_r3_mt8192_n200 \
         debate_traces_vllm_q32b_thinkON_peer_r3_mt8192_n200 debate_traces_vllm_q32b_thinkOFF_peer_r3_mt8192_n200 \
         debate_traces_vllm_q8b_thinkON_self_r3_mt8192_n200 debate_traces_vllm_q8b_thinkOFF_self_r3_mt8192_n200; do
  [ -s $f.jsonl ] || curl -sL -o $f.jsonl $B/$f.jsonl
done
ls -la *.jsonl | wc -l
