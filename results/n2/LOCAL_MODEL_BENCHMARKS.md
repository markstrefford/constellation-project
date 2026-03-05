# Local Model Benchmarks: Hub Pricing JSON Compliance

**Date:** 2026-03-05
**Hardware:** MacBook Pro M2, 16GB RAM
**Task:** Single-asset hub pricing — LLM returns structured JSON with a price and reasoning for one asset at a time
**Tool:** `python -m llm.validate_json_compliance --per-asset --json-mode -n 10`

Part of the CONSTELLATION open research project — benchmarking local LLMs for real-time multi-agent economic simulation. Results published as we go.

## Results Summary

| Metric | qwen2.5:14b | qwen3:8b | qwen3:14b |
|---|---|---|---|
| **Pass rate** | 100% | 100% | 90% |
| **Avg latency** | 5.6s | 46.8s | 85.1s |
| **p50 latency** | 2.5s | 45.2s | 92.7s |
| **p95 latency** | 30.9s | 85.0s | 120.1s |
| **Price changes** | 7/10 | 2/10 | 0/10 |
| **HOLDs** | 3/10 | 8/10 | 9/10 |
| **Timeouts** | 0 | 0 | 1 |

## Key Findings

### 1. qwen2.5:14b is the clear winner for local development

At 2.5s median latency, it's **18x faster** than qwen3:8b and **37x faster** than qwen3:14b on Apple Silicon with 16GB RAM. It also produces the most decisive pricing behavior — changing prices 70% of the time vs near-zero for qwen3 models.

### 2. qwen3's thinking mode adds massive overhead with no benefit

qwen3 models use `<think>...</think>` blocks for chain-of-thought reasoning before responding. On constrained hardware (16GB RAM), this thinking phase dominates inference time. For a structured JSON task like pricing, the extra reasoning doesn't improve output quality — it actually makes the model more conservative.

### 3. qwen3 models are excessively conservative

Both qwen3 models overwhelmingly chose to hold prices at their current values, even in scenarios with clear supply/demand imbalances. The thinking mode appears to make the model "overthink" and talk itself into inaction. qwen2.5:14b makes more active, economically reasonable pricing decisions.

### 4. Model size vs architecture matters more than raw parameters

qwen3:8b (smaller, with thinking) is slower than qwen2.5:14b (larger, without thinking) on the same hardware. The thinking overhead outweighs the parameter count advantage. For structured output tasks, a larger model without chain-of-thought is preferable to a smaller model with it.

## Task Description

Each prompt asks the LLM to set a price for a single asset on a hub planet. The model receives:
- Current planet state (stock levels, prices, wealth)
- Production and consumption rates
- Market overview (neighboring hub prices and stock)
- Net flow calculations (stock change per tick)

The model must return valid JSON:
```json
{
  "price": 1.45,
  "reasoning": "Lowering the price attracts more suppliers..."
}
```

### Success Criteria

- **OK** — Valid JSON parsed, reasoning present, price changed
- **HOLD** — Valid JSON parsed, reasoning present, price maintained (valid decision)
- **FAIL** — JSON parse failure or no reasoning extracted

Both OK and HOLD count as passes — the model correctly understood and responded to the prompt. FAIL indicates a JSON compliance issue.

## Methodology

- 10 prompts per model, cycling through 3 synthetic planet states and 3 assets
- `--json-mode` enabled (requests structured JSON output from Ollama)
- `--per-asset` mode (one LLM call per asset, simpler JSON schema)
- All models run locally via Ollama on the same hardware
- 120s timeout per request

## Implications for Deployment

- **Local development:** Use qwen2.5:14b — fast enough for real-time sim integration at ~2.5s per asset decision
- **Production (GPU server):** qwen3 models may perform better with adequate VRAM (24GB+) where thinking overhead is less impactful. Cloud APIs (Together, Groq) eliminate hardware constraints entirely
- **Decision interval tuning:** With 3 assets at 2.5s each, a full pricing round takes ~7.5s on qwen2.5:14b. A `decision_interval` of 10+ ticks gives comfortable headroom
