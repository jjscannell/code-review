# Code Review - Execution Instructions

This file defines HOW to execute the code-review skill.

---

## Version

**Current**: 0.8.0-beta

See [CHANGELOG.md](CHANGELOG.md) for full version history.

---

## Architecture

All agents use `general-purpose` subagent type, which has **full tool access including Write**. This means:

- Agents write their own report files directly
- Agents can run in parallel (background)
- No orchestration complexity needed
- Domain expertise comes from prompt files, not agent type

**Synthesis** features:
- Single canonical Issues Catalog with sequential IDs (#1, #2, #3...)
- Severity as separate field (allows re-prioritization without ID change)
- Reference-based views (no repeated details)
- Dependency validation (no circular deps)
- Action-oriented formatting with acceptance criteria

---

## Execution Pattern

### Step 1: Setup

```bash
mkdir -p docs/reviews
```

### Step 2: Parse Arguments

Determine which agents to run based on user input:
- `--preset alpha|strategic|full|quick` → Use preset agent list
- `--agents code,security,...` → Use explicit list
- `--gaming` → Add gaming module agents
- No args → Ask user interactively

### Step 3: Launch Agents (Parallel)

For each agent, spawn a Task with `run_in_background: true`:

```
Task({
  subagent_type: "general-purpose",
  prompt: "<contents of prompt_file>

    Write your findings to: docs/reviews/{output_file}

    Use the standard report format with Executive Summary,
    Critical/High/Medium/Low findings tables, Corrective Actions,
    and Visionary Recommendations.",
  description: "{agent focus} review",
  run_in_background: true
})
```

Launch up to 6 agents in parallel for efficiency.

### Step 4: Monitor Progress

Check agent completion by reading output files:
- Use `Glob` to check which files exist in `docs/reviews/`
- Report progress: "✓ code-quality.md complete (3/6)"

### Step 5: Synthesis

After all domain agents complete, run synthesis agent:

```
Task({
  subagent_type: "general-purpose",
  prompt: "<contents of prompts/synthesis.md>

    Read all reports in docs/reviews/ (except REMEDIATION-PLAN.md).

    Apply synthesis principles:
    1. Build single canonical Issues Catalog (assign sequential IDs: #1, #2, #3...)
    2. Assign severity as separate field (Critical/High/Medium/Low)
    3. Detect and consolidate duplicates
    4. Validate dependencies (check for circular deps)
    5. Use reference-based views (IDs only, no repeated details)
    6. Frame as actions with acceptance criteria
    7. Run quality gates before writing

    Write consolidated plan to docs/reviews/REMEDIATION-PLAN.md
    Target: 250-350 lines",
  description: "Synthesize review findings"
})
```

**Expected Output**:
- Compact document (~250-350 lines)
- Zero duplication
- Stable IDs (severity changes don't require renaming)
- Clear action items with acceptance criteria
- Validated dependencies
- Single point of update per issue

### Step 6: Report

After synthesis completes:
- List all generated reports
- Summarize critical/high findings count
- Note document length (should be 250-350 lines)
- Highlight any conflicts requiring human decision

---

## Report Format

Each agent's prompt file defines their domain expertise. All reports follow this structure:

```markdown
# {Domain} Review - {Project Name}

## Executive Summary
[2-3 sentence overview]

## Critical Findings (Must Fix)
| # | Issue | File:Line | Severity | Description |
|---|-------|-----------|----------|-------------|

## High Priority Findings
[Same format]

## Medium Priority Findings
[Same format]

## Low Priority Findings
[Same format]

## Corrective Actions
[Numbered list of specific fixes]

## Visionary Recommendations
[Forward-looking improvements]

## Metrics
- Files reviewed: X
- Issues found: Y (Critical: A, High: B, Medium: C, Low: D)

---
*Review Date: {date}*
```

---

## Synthesis Output Format

The consolidated remediation plan follows this deduplicated structure:

### Key Sections:
1. **Executive Summary** - Metrics, current state, blockers
2. **Cross-Cutting Themes** - Patterns across domains
3. **Issues Catalog** - SINGLE SOURCE OF TRUTH (all issue details here once)
   - Sequential IDs: #1, #2, #3...
   - Severity as column: Critical, High, Medium, Low
4. **Execution Strategy** - Phases with ID references only
5. **Task Grouping** - By domain/ROI with ID references only
6. **Dependencies Graph** - Visual + validation results
7. **Success Criteria** - Phase completion milestones

### Validation Before Output:
- ✓ All issue IDs unique and sequential
- ✓ Every issue has severity field
- ✓ All dependency references exist
- ✓ No circular dependencies
- ✓ Effort totals consistent
- ✓ No empty sections
- ✓ No DELETED markers
- ✓ No duplicate issue descriptions

---

## Progress Reporting

Keep the user informed:

```
Starting code review with preset: alpha
Agents: code, security, performance, ux, qa

Launching 5 agents in parallel...

Progress:
✓ code-quality.md (1/5)
✓ security.md (2/5)
✓ performance.md (3/5)
✓ ux.md (4/5)
✓ qa.md (5/5)

Running synthesis with v2.1 improvements...
✓ REMEDIATION-PLAN.md (289 lines, 0 duplications detected)

Code review complete.
- Reports: 6 files in docs/reviews/
- Critical issues: 8
- High priority: 15
- Document quality: ✓ Passed all validation gates
```

---

## Quick Reference

| Preset | Agents | Estimated Time | Synthesis Output |
|--------|--------|----------------|------------------|
| quick | 3 agents | ~2-4 min | ~180-220 lines |
| alpha | 5 agents | ~4-8 min | ~250-300 lines |
| strategic | 4 agents | ~3-6 min | ~220-280 lines |
| full | 9 agents | ~8-15 min | ~300-350 lines |
| full --gaming | 13 agents | ~12-20 min | ~350-400 lines |

---

## Error Handling

### Failure Modes & Recovery

#### 1. Output Directory Missing

**Symptom**: Agent fails with "directory not found" or write error
**Cause**: `docs/reviews/` doesn't exist
**Recovery**:
```bash
# Auto-create at start of execution
mkdir -p docs/reviews
```
**Prevention**: Step 1 of execution pattern handles this. If skipped, agents should create directory before writing.

#### 2. Agent Fails Mid-Execution

**Symptom**: Agent times out, crashes, or returns error
**Cause**: Codebase too large, network issue, or prompt edge case
**Recovery**:
1. Log: "⚠ {agent} failed: {error}"
2. Continue with other agents (don't block on one failure)
3. Note failed agents in synthesis input
4. Retry once with extended timeout (if timeout was cause)
5. After 1 retry, mark as skipped and proceed

**Example Output**:
```
⚠ performance agent failed (timeout after 5min)
  → Skipping performance review
  → Synthesis will note: "Performance review unavailable"
✓ Continuing with 4/5 agents...
```

#### 3. Synthesis Cannot Read Reports

**Symptom**: Synthesis agent reports missing files or empty content
**Cause**: Agents didn't complete, wrong output path, or permission issue
**Recovery**:
1. Check `docs/reviews/` for expected files
2. List what's present vs expected
3. If >50% of reports exist, synthesize available data with warning
4. If <50% exist, abort and report which agents failed

**Example**:
```
Synthesis input check:
✓ code-quality.md (2.1KB)
✓ security.md (1.8KB)
✗ performance.md (missing)
✓ ux.md (1.5KB)

Proceeding with 3/4 reports (75% coverage)
⚠ Synthesis will exclude performance findings
```

#### 4. Synthesis Validation Fails

**Symptom**: Quality gates report errors (circular deps, broken refs)
**Cause**: Complex inter-dependencies or synthesis logic edge case
**Recovery**:
1. Log which specific gate failed
2. Attempt auto-fix:
   - Circular deps → Break weakest link, add warning
   - Broken refs → Remove invalid reference
   - Duplicates → Merge into first occurrence
3. If auto-fix succeeds, output with `[AUTO-FIXED]` marker
4. If auto-fix fails, output with `[VALIDATION WARNING]` section

**Example**:
```
Quality gate results:
✓ All issue IDs unique
✗ Circular dependency: H3 <-> H7
✓ No empty sections

Auto-fix applied: Removed H7→H3 dependency (weaker link)
[AUTO-FIXED] Output contains 1 auto-corrected issue
```

#### 5. Codebase Too Large

**Symptom**: Agents timeout or return truncated results
**Cause**: Codebase exceeds practical review limits
**Recovery**:
1. Use `--preset quick` for large codebases (3 agents, focused scope)
2. Specify target directories: `/code-review --path src/core`
3. Exclude generated files: respect `.gitignore` patterns

**Recommendation**: For codebases >500 files, use targeted reviews on specific modules.

#### 6. Conflicting Agent Recommendations

**Symptom**: Synthesis detects contradictory advice
**Cause**: Legitimate trade-offs between domains (security vs UX, etc.)
**Recovery**:
1. Document conflict in "Conflicts Requiring Decision" section
2. Do NOT auto-resolve—these need human judgment
3. Provide trade-off analysis for each option
4. Flag blocking conflicts (need decision before proceeding)

### Graceful Degradation

The skill should always produce *something* useful:

| Failure State | Output |
|---------------|--------|
| All agents succeed | Full remediation plan |
| 1-2 agents fail | Partial plan + "missing coverage" note |
| >50% agents fail | Abbreviated plan + strong warning |
| All agents fail | Error report with diagnostics |
| Synthesis fails | Raw agent reports (skip synthesis) |

### Logging Levels

```
✓ Success message (green)
⚠ Warning - recoverable (yellow)
✗ Error - action needed (red)
ℹ Info - status update (blue)
```

---

## Examples

```
/code-review --preset quick
→ Runs: code, security, ux (3 agents in parallel)
→ Output: ~200 lines, deduplicated

/code-review --preset alpha
→ Runs: code, security, performance, ux, qa (5 agents)
→ Output: ~280 lines, zero duplication

/code-review --agents qa,ux --gaming
→ Runs: qa, ux + balance, player-journey, narrative, quant (6 agents)
→ Output: ~250 lines, action-oriented
```

---

## Design Benefits

### Current Design:
- 250-350 line remediation plan (compact)
- 0 instances of duplication
- 1 location to update per issue change
- Sequential IDs (#1, #2...) - stable across severity changes
- Action-oriented with acceptance criteria
- Automated dependency validation
- Quality gates prevent errors

### Metrics:
- **Maintenance burden**: Low (single update point)
- **Time to understand**: <5 minutes
- **Action clarity**: 100% (every issue has clear "done" criteria)
- **ID stability**: Severity changes don't require renaming
- **Error prevention**: Validation catches circular deps, broken refs
