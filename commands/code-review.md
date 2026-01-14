---
argument-hint: [--preset <name>] [--agents <list>] [--gaming]
description: Multi-agent codebase review with automated synthesis
---

# Code Review

Launch review agents in parallel to analyze the codebase, then synthesize findings into a prioritized remediation plan.

## Parameters

- `--preset`: Use a predefined agent set (alpha, strategic, full, quick)
- `--agents`: Comma-separated list of specific agents
- `--gaming`: Include gaming-specific agents (balance, player-journey, narrative, quant)

## Presets

| Preset | Agents | Use Case |
|--------|--------|----------|
| `alpha` | code, security, performance, ux, qa | Pre-launch readiness |
| `strategic` | architecture, docs, product, qa | Long-term direction |
| `full` | All 9 core agents | Comprehensive review |
| `quick` | code, security, ux | Fast sanity check |

## Available Agents

### Core (9)
- `code`: Code quality, dead code, type safety, bugs
- `security`: Auth, validation, OWASP, secrets
- `performance`: N+1 queries, algorithms, bundle size
- `architecture`: Folder structure, patterns, tech debt
- `ux`: Accessibility, mobile, feedback, navigation
- `qa`: Test coverage, flaky tests, CI/CD
- `docs`: Documentation gaps, onboarding
- `dependencies`: Outdated packages, CVEs
- `product`: Feature completeness, roadmap

### Gaming Module
- `balance`: Economy loops, win rates, formula fairness
- `player-journey`: Tutorial, friction points, onboarding
- `narrative`: Terminology, lore consistency
- `quant`: Game economy modeling, probability

## Workflow

### Phase 1: Setup
```bash
mkdir -p docs/reviews
```

### Phase 2: Parse Arguments

If `$ARGUMENTS` contains `--preset alpha`:
  agents = [code, security, performance, ux, qa]
Else if `$ARGUMENTS` contains `--preset strategic`:
  agents = [architecture, docs, product, qa]
Else if `$ARGUMENTS` contains `--preset full`:
  agents = [code, security, performance, architecture, ux, qa, docs, dependencies, product]
Else if `$ARGUMENTS` contains `--preset quick`:
  agents = [code, security, ux]
Else if `$ARGUMENTS` contains `--agents`:
  agents = parse comma-separated list after --agents
Else:
  Ask user which preset or agents to use

If `$ARGUMENTS` contains `--gaming`:
  Add gaming agents: balance, player-journey, narrative, quant

### Phase 3: Launch Agents (Parallel)

For each agent in the selected list, spawn a Task agent that writes its own report:

```
Task({
  subagent_type: "general-purpose",
  prompt: "You are an expert {domain} reviewer.

  Review the codebase thoroughly for {focus area}.

  Write your findings to docs/reviews/{output_file}.

  Use this format:
  # {Domain} Review - {Project Name}

  ## Executive Summary
  [2-3 sentences]

  ## Critical Findings (Must Fix)
  | # | Issue | File:Line | Severity | Description |

  ## High Priority Findings
  | # | Issue | File:Line | Severity | Description |

  ## Medium Priority Findings
  [...]

  ## Corrective Actions
  [Numbered list of immediate fixes]

  ## Visionary Recommendations
  [Growth opportunities]

  ## Metrics
  - Files reviewed: X
  - Issues found: Y (Critical: A, High: B, Medium: C, Low: D)",
  description: "{Agent} review",
  run_in_background: true
})
```

Launch up to 6 agents in parallel. Monitor completion via output files.

### Phase 4: Synthesis (After All Agents Complete)

Spawn a synthesis agent:

```
Task({
  subagent_type: "general-purpose",
  prompt: "Read all reports in docs/reviews/ (except REMEDIATION-PLAN.md).

  Create docs/reviews/REMEDIATION-PLAN.md with:

  1. **Conflicts**: Where agents disagree
  2. **Dependencies**: Which fixes depend on others
  3. **Duplicates**: Same issue from multiple agents
  4. **Priority Matrix**: Cross-domain prioritization
  5. **Blockers**: Must fix before other work
  6. **Quick Wins**: High impact, low effort
  7. **Grouped Tasks**: Related changes to batch
  8. **Execution Order**: Recommended sequence

  Format as actionable remediation plan.",
  description: "Synthesize review findings"
})
```

### Phase 5: Report

After synthesis completes:
- List all generated reports
- Summarize critical/high findings count
- Highlight any conflicts requiring human decision

## Examples

```
/code-review --preset alpha
/code-review --preset full --gaming
/code-review --agents code,security,qa
/code-review --agents qa
```

## Output

Reports written to `docs/reviews/`:
- Individual agent reports (e.g., `code-quality.md`, `security.md`)
- `REMEDIATION-PLAN.md` - Consolidated synthesis with prioritized actions
