# Testing Framework

This directory contains test fixtures and validation tools for the code-review skill.

## Directory Structure

```
tests/
├── README.md                    # This file
├── validate_synthesis.py        # Synthesis output validator
└── fixtures/
    └── ralf-quick/              # Test fixture: quick preset on Ralf project
        └── inputs/              # Agent reports (inputs to synthesis)
            ├── code-quality.md
            ├── security.md
            └── ux.md
```

## Validation Script

### Usage

```bash
# Validate a synthesis output
python tests/validate_synthesis.py docs/reviews/REMEDIATION-PLAN.md

# Validate against a fixture
python tests/validate_synthesis.py tests/fixtures/ralf-quick/output/REMEDIATION-PLAN.md
```

### What It Checks

| Check | Description |
|-------|-------------|
| Required sections | Executive Summary, Issues Catalog, Execution Strategy |
| ID scheme | Sequential IDs (#1, #2, #3...) not severity-prefixed (C1, H1) |
| Severity field | Separate column in Issues Catalog table |
| No duplicates | Issue descriptions not repeated across sections |
| Dependency refs | All referenced IDs exist in catalog |
| Document length | 150-400 lines (target: 250-350) |
| Empty sections | No section headers without content |
| Placeholders | No DELETED/TODO/XXX markers |

### Exit Codes

- `0`: All checks passed
- `1`: One or more checks failed

## Test Fixtures

### ralf-quick

**Source**: Quick preset (code, security, ux) run against the Ralf Orchestrator project
**Agents**: 3 (code-quality, security, ux)
**Issues found**: 90 (after deduplication)

**Inputs** (agent reports):
- `code-quality.md` - 245 lines, 40 issues
- `security.md` - 164 lines, 22 issues
- `ux.md` - 292 lines, 28 issues

**Usage**:
```bash
# Copy inputs to docs/reviews/
cp tests/fixtures/ralf-quick/inputs/*.md docs/reviews/

# Run synthesis (manually invoke skill)
# Then validate output
python tests/validate_synthesis.py docs/reviews/REMEDIATION-PLAN.md
```

## Adding New Fixtures

1. Create directory: `tests/fixtures/{name}/inputs/`
2. Copy agent reports to `inputs/`
3. Optionally add `expected/REMEDIATION-PLAN.md` for exact comparison
4. Document in this README

## Future Enhancements

- [ ] Automated fixture runner script
- [ ] Expected output comparison (fuzzy match)
- [ ] CI integration
- [ ] Performance benchmarks
