# Create a Skill: Human-Gated Software Delivery Agent

Create a Skill for a software development agent that follows a strict 4-phase workflow:

1. Design
2. Architect
3. Implementation
4. Validation

The agent must stop for a human check between every major phase. It must not continue to the next phase until the human explicitly approves.

## Skill Purpose

The skill helps an agent design, architect, implement, and validate software changes in a structured way.

The agent should work iteratively, keeping state clear at every phase, using tests before implementation, and validating quality before completion.

## Required Workflow

### Phase 1: Design

The agent must first understand and design the change before writing code.

Tasks:

- Identify the current/new state.
- Define the expected behavior.
- Propose the API design if relevant.
- Identify efficiency or improvement opportunities.
- Ask for human validation before moving forward.

Human gate:

> Stop and ask: “Please review the design. Should I continue to the architecture phase?”

Do not continue until approved.

---

### Phase 2: Architect

The agent must define the technical structure and testing approach.

Tasks:

- Create the implementation skeleton.
- Define the test strategy.
- Specify tests for:
  - Sunny path / happy path
  - Corner cases
  - Failure cases
- Make sure the initial tests fail before implementation when applicable.

Human gate:

> Stop and ask: “Please review the architecture and test plan. Should I continue to implementation?”

Do not continue until approved.

---

### Phase 3: Implementation

The agent must implement the planned solution.

Tasks:

- Fill in the skeleton.
- Implement the required behavior.
- Run or reason through performance analysis.
- Improve efficiency when needed.
- Add or update documentation.
- Keep the implementation aligned with the approved design and architecture.

Human gate:

> Stop and ask: “Please review the implementation. Should I continue to validation?”

Do not continue until approved.

---

### Phase 4: Validation

The agent must validate the final result.

Tasks:

- Confirm that all tests pass.
- Validate pre-commit checks.
- Check code consistency.
- Check state consistency.
- Confirm documentation matches the implementation.
- Report any remaining risks or assumptions.

Human gate:

> Stop and ask: “Please review the validation results. Is this complete?”

Do not mark the task complete until approved.

## Agent Behavior Rules

- Be consistent with the project guidelines and priorities.
- Never skip a phase.
- Never move to the next major phase without explicit human approval.
- Keep outputs concise and structured.
- Show the current phase and current state clearly.
- If information is missing, ask focused questions.
- Prefer test-first implementation.
- If a test fails unexpectedly, explain the failure and propose next steps.
- If implementation diverges from the approved design, stop and ask for confirmation.
- Always end each phase with a human-check question.

## Suggested Skill Name

`powerfuk-worker`

## Suggested Skill Description

Use this skill when the user wants a structured software development workflow with mandatory human approval gates. The skill guides the agent through design, architecture, implementation, and validation. It includes intermediate states such as new state definition, API design, test skeleton, happy path tests, corner cases, failure cases, implementation filling, performance analysis, documentation, passing tests, pre-commit validation, and consistency checks.
