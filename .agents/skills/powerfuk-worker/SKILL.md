---
name: powerfuk-worker
description: Follow a strict human-gated software delivery workflow for repository changes. Use when Codex must design, architect, implement, and validate a software change in separate phases with explicit human approval before moving to the next phase, especially for structured feature work, refactors, bug fixes, or test-and-doc aligned delivery.
---

# Powerfuk Worker

Guide software delivery through four mandatory phases:

1. Design
2. Architect
3. Implementation
4. Validation

Never skip a phase. Never continue past a phase gate without explicit human approval.

## Start

1. Inspect the relevant repository context before proposing changes.
2. Read repository instructions and the affected code, tests, and docs in scope.
3. Rebuild the current state from source artifacts instead of assumptions.
4. State the current phase and the current known state clearly.
5. Ask focused follow-up questions only when missing information blocks safe progress.

Read [references/repository-rules.md](references/repository-rules.md) before planning or editing so the workflow stays aligned with this repository's priorities.

Agent interface definitions live in [agents/](agents/): [openai.yaml](agents/openai.yaml) for ChatGPT and [claude.yaml](agents/claude.yaml) for Claude Code. Both share this SKILL.md and the same references — no duplication needed.

## Global Rules

- Keep outputs concise, structured, and phase-aware.
- Prefer test-first work when it is practical.
- Stop and ask for confirmation if implementation must diverge from approved design or architecture.
- Explain unexpected test failures and propose the next safe step before continuing.
- Keep code, tests, documentation, and validation aligned with the latest approved phase state.
- Treat each phase result as a checkpoint artifact for human review.

## Phase Loading

Load only the current phase file unless a cross-phase dependency requires checking another phase.

- For design work, read [references/phase-1-design.md](references/phase-1-design.md).
- For architecture and test planning, read [references/phase-2-architect.md](references/phase-2-architect.md).
- For implementation, read [references/phase-3-implementation.md](references/phase-3-implementation.md).
- For validation, read [references/phase-4-validation.md](references/phase-4-validation.md).

## Phase Sequence

1. Complete design and stop for approval.
2. Complete architecture and stop for approval.
3. Complete implementation and stop for approval.
4. Complete validation and stop for approval.

If a later phase reveals a necessary earlier-phase change, return to that phase, update the plan, and ask for approval again before proceeding.
