# Code Review Skill

**Version**: 0.8.0-beta | [Changelog](CHANGELOG.md)

A global Claude Code skill that launches multiple specialized agents in parallel to review any codebase, automatically synthesizes findings, and produces a prioritized remediation plan.

## Installation

Add the following to your `~/.claude/settings.json`:

```json
{
  "skills": {
    "code-review": {
      "path": "~/.claude/skills/code-review",
      "global": true,
      "description": "Multi-agent codebase review with automated synthesis"
    }
  }
}
```

## Manual Usage (Without Slash Command)

If the slash command isn't registered, you can invoke the skill manually:

1. **Full Review**: Ask Claude to "Run the code-review skill with the alpha preset"
2. **Single Agent**: Ask Claude to "Read the code-reviewer prompt from ~/.claude/skills/code-review/prompts/core/code-reviewer.md and use it to review this codebase"
3. **With Synthesis**: After running agents, ask Claude to "Read the synthesis prompt and create a REMEDIATION-PLAN.md from all reports in docs/reviews/"

## Quick Start

```bash
# Interactive mode - choose agents
/code-review

# Use a preset
/code-review --preset alpha

# Select specific agents
/code-review --agents code,security,performance

# Include gaming-specific agents
/code-review --gaming
```

## Presets

| Preset | Agents | Use Case | Output Size |
|--------|--------|----------|-------------|
| `alpha` | code, security, performance, ux, qa | Pre-launch readiness | ~280 lines |
| `strategic` | architecture, docs, product, qa | Long-term direction | ~250 lines |
| `full` | All 9 core agents | Comprehensive review | ~320 lines |
| `quick` | code, security, ux | Fast sanity check | ~200 lines |

## Available Agents

### Core Agents (9)
| ID | Focus |
|----|-------|
| `code` | Code quality, dead code, type safety, bugs |
| `security` | Auth, validation, OWASP, secrets |
| `performance` | N+1 queries, algorithms, bundle size, memory |
| `architecture` | Folder structure, patterns, tech debt |
| `ux` | Accessibility, mobile, feedback, navigation |
| `qa` | Test coverage, flaky tests, CI/CD |
| `docs` | Documentation gaps, duplication, onboarding |
| `dependencies` | Outdated packages, CVEs, version conflicts |
| `product` | Feature completeness, roadmap, positioning |

### Extended Agents (12)
| ID | Focus |
|----|-------|
| `debug` | Complex issue diagnosis, root cause analysis |
| `error` | Error patterns, correlation, cascade prevention |
| `chaos` | Resilience testing, failure scenarios |
| `accessibility` | WCAG compliance, screen readers, keyboard nav |
| `api` | API consistency, documentation, DX |
| `database` | Query optimization, indexes, schema design |
| `devops` | CI/CD, containerization, deployment |
| `refactor` | Safe transformations, pattern improvements |
| `dx` | Build performance, tooling, developer experience |
| `compliance` | Regulatory frameworks, data privacy, standards |
| `pentest` | Offensive security, vulnerability validation |
| `technical-writer` | API docs, user guides, technical content |

### Gaming Module (4)
Use `--gaming` flag to include:

| ID | Focus |
|----|-------|
| `balance` | Economy loops, win rates, formula fairness |
| `player-journey` | Tutorial, friction points, onboarding flow |
| `narrative` | Terminology, lore consistency, flavor text |
| `quant` | Game economy modeling, probability analysis |

## Output

Reports are generated in `docs/reviews/`:

```
docs/reviews/
├── code-quality.md
├── security.md
├── performance.md
├── ux.md
├── qa.md
└── REMEDIATION-PLAN.md   <-- Consolidated synthesis
```

Each report follows this structure:
- Executive Summary
- Critical Findings (must fix)
- High Priority Findings
- Medium Priority Findings
- Corrective Actions (tactical)
- Visionary Recommendations (growth)
- Metrics

## Synthesis

After all agents complete, a synthesis agent automatically:
1. Reads all domain reports
2. **Builds single canonical Issues Catalog** (assigns sequential IDs: #1, #2, #3...)
3. **Assigns severity as separate field** (Critical/High/Medium/Low)
4. **Detects and consolidates duplicates** (same issue flagged by multiple agents)
5. **Validates dependencies** (checks for circular deps, missing references)
6. Maps dependencies between fixes
7. Identifies conflicts between recommendations
8. Prioritizes holistically across domains
9. **Produces deduplicated `REMEDIATION-PLAN.md`** with:
   - Executive Summary with metrics
   - Cross-Cutting Themes
   - **Issues Catalog** (single source of truth - all details here)
   - **Execution Strategy** (phases with ID references only)
   - **Task Grouping** (by domain/ROI with ID references only)
   - Dependencies Graph with validation results
   - Success Criteria

### Output Quality

The synthesis produces **action-ready, deduplicated plans**:

| Metric | Target |
|--------|--------|
| Document length | 250-350 lines |
| Duplication | 0 instances |
| Update burden | 1 location per issue |
| ID stability | Severity changes don't rename IDs |
| Validation | Automated quality gates |

### Example Output Structure

```markdown
## Issues Catalog (Single Source of Truth)
| ID | Severity | Action Required | Location | Impact | Effort |
| #1 | Critical | Remove hardcoded credentials → env config | auth.py:30 | Auth bypass | 2h |
| #2 | Critical | Implement parameterized queries | db.py:45 | SQL injection | 4h |
| #3 | High | Add type annotations to core functions | main.py:100 | Type safety | 12h |

## Execution Strategy
Phase 1 (Week 1): #1, #2 [IDs only - full details in catalog above]
Phase 2 (Week 2): #3, #4, #5

## Task Grouping
Security Hardening (6h): #1, #2
Code Quality (20h): #3, #4
```

**Key Benefits**:
- Each issue defined once, referenced everywhere
- IDs are stable (severity can change without renaming)
- Update one location, change propagates automatically

## Examples

### Pre-Alpha Launch Review
```bash
/code-review --preset alpha
```
Runs code, security, performance, ux, qa agents to ensure launch readiness.
Output: ~280 lines, 0 duplication, action-ready.

### Game Project Full Review
```bash
/code-review --preset full --gaming
```
Runs all 9 core agents + 4 gaming agents for comprehensive game project review.
Output: ~350 lines with gaming-specific insights.

### Quick Security Check
```bash
/code-review --agents security,pentest
```
Focused security review with both defensive and offensive perspectives.
Output: ~180 lines, security-focused action items.

### Database-Focused Review
```bash
/code-review --agents code,database,performance
```
Review optimized for database-heavy applications.
Output: ~220 lines with query optimization focus.

## Customization

To modify agent behavior, edit the prompt templates in:
- `prompts/core/` - Core agent prompts
- `prompts/extended/` - Extended agent prompts
- `prompts/gaming/` - Gaming module prompts
- `prompts/synthesis.md` - Synthesis agent prompt (deduplication + validation logic)

## Testing

Validate synthesis output against quality gates:

```bash
python tests/validate_synthesis.py docs/reviews/REMEDIATION-PLAN.md
```

The validator checks:
- Sequential ID scheme (#1, #2, #3...)
- Severity as separate column
- No duplicate descriptions
- All dependency references valid
- Document length within range
- No empty sections or placeholder markers

See `tests/README.md` for fixture documentation.

## Troubleshooting

### Agent Fails or Times Out
If an agent doesn't complete:
- Check if `docs/reviews/` directory exists (create with `mkdir -p docs/reviews`)
- For large codebases (>500 files), use `--preset quick` or target specific paths
- The skill will continue with remaining agents and note the gap in synthesis

### Synthesis Output Too Long (>400 lines)
If synthesis produces >400 lines:
- Check for duplication (search for repeated issue descriptions)
- Ensure synthesis.md prompt is current version (single source of truth pattern)
- Report issue if using current prompt but still seeing duplication

### Validation Warnings
Synthesis may emit warnings:
- "Issue X depends on non-existent Y" - broken dependency reference
- "Circular dependency detected" - A depends on B, B depends on A
- "Issue description appears N times" - duplication detected

These are caught by quality gates. Auto-fix is attempted; check `[AUTO-FIXED]` markers in output.

### Missing Acceptance Criteria
Every issue in Issues Catalog should have acceptance criteria. If missing:
- Synthesis agent needs clearer guidance
- Check that prompt_file for domain agents includes corrective actions
- May need to manually add criteria post-generation

### Partial Results
If fewer agents complete than expected:
- Check Progress output for `⚠` warnings
- Synthesis will proceed with available data if >50% succeed
- Review "Missing Coverage" section in output for gaps

See `instructions.md` § Error Handling for full recovery procedures.
