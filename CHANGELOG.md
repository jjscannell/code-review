
## [0.8.1-beta] - 2026-01-14

### Added
- **Error handling documentation**: Comprehensive failure mode coverage in instructions.md
- **Graceful degradation**: Skill produces partial results when agents fail
- **Auto-fix for validation failures**: Circular deps and broken refs handled automatically
- **CHANGELOG added**: Tracking development updates
- **Test infrastructure**: Validation script and fixture directory structure
  - `tests/validate_synthesis.py` - Validates synthesis output against quality gates
  - `tests/fixtures/` - Test fixtures with sample agent reports

### Changed
- **ID scheme**: Changed from severity-prefixed (C1/H1/M1) to sequential (#1, #2, #3) with severity as separate field



## [0.7.0-alpha] - 2026-01-10

### Added
- **Synthesis deduplication**: Single source of truth pattern for issues
- **Dependency validation**: Checks for circular dependencies and missing references
- **Quality gates**: Automated validation before writing output
- **Action-oriented output**: "Remove X, implement Y" format with acceptance criteria

### Changed
- Synthesis output reduced 40% (450+ lines → 250-350 lines)
- Issues defined once in catalog, referenced by ID elsewhere

---

## [0.6.0-pre-alpha] - 2026-01-05

### Added
- **Parallel execution**: Up to 6 agents run simultaneously
- **Direct file writing**: Agents write own report files
- **General-purpose agents**: All agents use same subagent type with domain expertise from prompts

### Changed
- Simplified architecture (removed specialized agent types)

---

## [0.5.0] - 2026-01-01

### Added
- Initial skill implementation
- 25 review agents across 3 tiers (core, extended, gaming)
- Basic synthesis agent
- Preset configurations (quick, alpha, strategic, full)
- README and instructions documentation

---
