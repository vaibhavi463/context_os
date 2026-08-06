# ADR 0003: Model Context Protocol (MCP) & Human-in-the-Loop (HITL) Gate

## Status
Accepted

## Context
AI agents executing operational write actions (such as account remediation or rate limit resets) present risk if allowed unmonitored execution.

## Decision
We decouple tool definitions using Model Context Protocol (FastMCP) and enforce a Human-in-the-Loop (HITL) Security Gate for all write operations. Write tools issue cryptographically signed HMAC approval tokens requiring explicit operator authorization before execution.

## Consequences
- Completely blocks 100% of unauthorized or autonomous state mutations.
- Provides immutable audit trails for every requested and approved tool execution.
