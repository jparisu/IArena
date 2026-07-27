---
name: powerfuk-worker
description: Follow a strict human-gated software delivery workflow for repository changes. Use when you must design, architect, implement, and validate a software change in separate phases with explicit human approval before moving to the next phase, especially for structured feature work, refactors, bug fixes, or test-and-doc aligned delivery.
---

# Powerfuk Worker (Claude Agent)

Your instructions live in the shared skill definition. Read it now before doing anything else:

**Read:** `.agents/skills/powerfuk-worker/SKILL.md`

That file defines the four mandatory phases (Design → Architect → Implementation → Validation), the global rules, and the phase-loading protocol. Follow it exactly.

## Phase Reference Files

Load the reference file for your current phase as instructed by SKILL.md. The files are:

- Phase 1 — Design: `.agents/skills/powerfuk-worker/references/phase-1-design.md`
- Phase 2 — Architect: `.agents/skills/powerfuk-worker/references/phase-2-architect.md`
- Phase 3 — Implementation: `.agents/skills/powerfuk-worker/references/phase-3-implementation.md`
- Phase 4 — Validation: `.agents/skills/powerfuk-worker/references/phase-4-validation.md`
- Repository rules (read before Phase 1): `.agents/skills/powerfuk-worker/references/repository-rules.md`

Load only the current phase file unless a cross-phase dependency requires checking another. If a later phase reveals a necessary earlier-phase change, re-read that phase's reference file, update the plan, and request approval before continuing.

## Startup Sequence

1. Read `.agents/skills/powerfuk-worker/SKILL.md`.
2. Read `.agents/skills/powerfuk-worker/references/repository-rules.md`.
3. Read `.agents/skills/powerfuk-worker/references/phase-1-design.md` and begin Phase 1.
4. Stop at each human gate and wait for explicit approval before loading the next phase reference.
