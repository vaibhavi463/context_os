# ADR 0004: Google Gemini 2.5 Flash LLM Provider Integration

## Status
Accepted

## Context
The AI agent platform requires rapid completion speed, long context window support, native tool schemas, and cost-efficient inference.

## Decision
We integrate Google Gemini 2.5 Flash via official `google-genai` SDK with `GenerateContentConfig`, dynamic token usage & cost tracking, and `tenacity` retries.

## Consequences
- Sub-second latency for complex agent multi-turn queries.
- Transparent token usage and cost accounting.
