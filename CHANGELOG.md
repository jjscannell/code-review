# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with pre-1.0 stages:
- 0.1-0.5: Ideation & prototyping
- 0.6: Pre-Alpha
- 0.7: Alpha
- 0.8: Beta
- 0.9: Release Candidate
- 1.0: Production Release

---

## [0.8.0-beta] - 2026-01-14

### Added
- **Error handling documentation**: Comprehensive failure mode coverage in instructions.md
- **Graceful degradation**: Skill produces partial results when agents fail
- **Auto-fix for validation failures**: Circular deps and broken refs handled automatically
- **CHANGELOG.md**: Proper version tracking
- **Test infrastructure**: Validation script and fixture directory structure
  - `tests/validate_synthesis.py` - Validates synthesis output against quality gates
  - `tests/fixtures/` - Test fixtures with sample agent reports

### Changed
- **ID scheme**: Changed from severity-prefixed (C1/H1/M1) to sequential (#1, #2, #3) with severity as separate field
- **Version numbering**: Aligned with semantic pre-release conventions (was 2.1.0, now 0.8.0-beta)

### Fixed
- Documentation now reflects beta status accurately

---

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

## Roadmap

### 0.9.0-rc (Planned)
- [ ] Test fixtures and validation script
- [ ] Performance benchmarks for large codebases
- [ ] User feedback integration

### 1.0.0 (Planned)
- [ ] Production-ready stability
- [ ] Community feedback incorporated
- [ ] Full test coverage
