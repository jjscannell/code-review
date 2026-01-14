#!/usr/bin/env python3
"""
Synthesis Output Validator

Validates that REMEDIATION-PLAN.md follows the expected structure and quality gates:
- Sequential ID scheme (#1, #2, #3...)
- Severity as separate field
- No duplicate issue descriptions
- All dependency references exist
- Required sections present
- Document length within target range

Usage:
    python validate_synthesis.py <path-to-remediation-plan.md>
    python validate_synthesis.py tests/fixtures/ralf-quick/output/REMEDIATION-PLAN.md
"""

import re
import sys
from pathlib import Path
from collections import Counter
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    passed: bool
    message: str
    details: Optional[str] = None


class SynthesisValidator:
    """Validates synthesis output against quality gates."""

    REQUIRED_SECTIONS = [
        "Executive Summary",
        "Issues Catalog",
        "Execution Strategy",
    ]

    OPTIONAL_SECTIONS = [
        "Cross-Cutting Themes",
        "Task Grouping",
        "Dependencies Graph",
        "Success Criteria",
        "Conflicts Requiring Decision",
        "Risk Assessment",
        "Recommendations",
    ]

    # New ID scheme: #1, #2, #3...
    ID_PATTERN = re.compile(r'#(\d+)')

    # Old ID scheme (should NOT be present): C1, H1, M1...
    OLD_ID_PATTERN = re.compile(r'\b([CHM]\d+)\b')

    # Severity values
    VALID_SEVERITIES = {'Critical', 'High', 'Medium', 'Low'}

    # Target document length
    MIN_LINES = 150
    MAX_LINES = 400

    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')
        self.results: list[ValidationResult] = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        checks = [
            self.check_required_sections,
            self.check_id_scheme,
            self.check_no_old_ids,
            self.check_severity_field,
            self.check_no_duplicates,
            self.check_dependency_references,
            self.check_document_length,
            self.check_no_empty_sections,
            self.check_no_deleted_markers,
        ]

        for check in checks:
            result = check()
            self.results.append(result)

        return all(r.passed for r in self.results)

    def check_required_sections(self) -> ValidationResult:
        """Verify all required sections are present."""
        missing = []
        for section in self.REQUIRED_SECTIONS:
            # Look for ## Section Name or # Section Name
            pattern = rf'^#{1,2}\s+{re.escape(section)}'
            if not re.search(pattern, self.content, re.MULTILINE | re.IGNORECASE):
                missing.append(section)

        if missing:
            return ValidationResult(
                False,
                f"Missing required sections: {', '.join(missing)}",
                "Required: " + ", ".join(self.REQUIRED_SECTIONS)
            )
        return ValidationResult(True, "All required sections present")

    def check_id_scheme(self) -> ValidationResult:
        """Verify IDs follow sequential #N pattern."""
        ids = self.ID_PATTERN.findall(self.content)

        if not ids:
            return ValidationResult(
                False,
                "No issue IDs found (expected #1, #2, #3...)",
                "IDs should follow pattern: #1, #2, #3..."
            )

        # Check for gaps in sequence (warning, not failure)
        int_ids = sorted(set(int(i) for i in ids))
        expected = list(range(1, max(int_ids) + 1))
        gaps = set(expected) - set(int_ids)

        if gaps and len(gaps) > len(int_ids) * 0.2:  # More than 20% gaps
            return ValidationResult(
                False,
                f"Large gaps in ID sequence: missing {sorted(gaps)[:10]}...",
                f"Found IDs: {int_ids[:10]}..."
            )

        return ValidationResult(
            True,
            f"ID scheme valid ({len(set(ids))} unique IDs)",
            f"Range: #1 to #{max(int_ids)}"
        )

    def check_no_old_ids(self) -> ValidationResult:
        """Ensure old severity-prefixed IDs (C1, H1, M1) are not used."""
        old_ids = self.OLD_ID_PATTERN.findall(self.content)

        # Filter out false positives (like "C1" in code blocks or paths)
        # Only count IDs that appear in table rows or reference lists
        suspicious = []
        for match in re.finditer(r'\b([CHM]\d+)\b', self.content):
            # Check if it's in a markdown table or looks like an issue reference
            line_start = self.content.rfind('\n', 0, match.start()) + 1
            line_end = self.content.find('\n', match.end())
            line = self.content[line_start:line_end if line_end != -1 else None]

            if '|' in line or match.group(1) in line.split(','):
                suspicious.append(match.group(1))

        if suspicious:
            unique_old = list(set(suspicious))[:10]
            return ValidationResult(
                False,
                f"Old ID scheme detected: {', '.join(unique_old)}",
                "Use #1, #2, #3 instead of C1, H1, M1"
            )

        return ValidationResult(True, "No old ID scheme detected")

    def check_severity_field(self) -> ValidationResult:
        """Verify severity is a separate field in the Issues Catalog."""
        # Look for table with Severity column
        table_header_pattern = r'\|\s*ID\s*\|.*Severity.*\|'

        if not re.search(table_header_pattern, self.content, re.IGNORECASE):
            return ValidationResult(
                False,
                "Issues Catalog missing Severity column",
                "Table should have: | ID | Severity | Action Required | ..."
            )

        # Check severity values are valid
        severity_pattern = r'\|\s*(Critical|High|Medium|Low)\s*\|'
        severities = re.findall(severity_pattern, self.content, re.IGNORECASE)

        if not severities:
            return ValidationResult(
                False,
                "No severity values found in Issues Catalog",
                f"Valid values: {', '.join(self.VALID_SEVERITIES)}"
            )

        return ValidationResult(
            True,
            f"Severity field present ({len(severities)} entries)",
            f"Distribution: {Counter(s.title() for s in severities)}"
        )

    def check_no_duplicates(self) -> ValidationResult:
        """Check for duplicate issue descriptions."""
        # Extract issue descriptions from catalog (text after severity in table rows)
        # Pattern: | #N | Severity | Description text |
        desc_pattern = r'\|\s*#\d+\s*\|\s*(?:Critical|High|Medium|Low)\s*\|\s*([^|]+)\|'
        descriptions = re.findall(desc_pattern, self.content, re.IGNORECASE)

        if not descriptions:
            return ValidationResult(
                True,
                "Could not extract descriptions for duplicate check",
                "Manual review recommended"
            )

        # Normalize and check for duplicates
        normalized = [d.strip().lower()[:100] for d in descriptions]  # First 100 chars
        counts = Counter(normalized)
        duplicates = {k: v for k, v in counts.items() if v > 1}

        if duplicates:
            dup_list = list(duplicates.keys())[:3]
            return ValidationResult(
                False,
                f"Duplicate descriptions found: {len(duplicates)} duplicates",
                f"Examples: {dup_list}"
            )

        return ValidationResult(True, "No duplicate descriptions detected")

    def check_dependency_references(self) -> ValidationResult:
        """Verify all referenced IDs exist in the catalog."""
        # Get all defined IDs (in catalog)
        catalog_section = self._extract_section("Issues Catalog")
        if not catalog_section:
            return ValidationResult(
                False,
                "Cannot find Issues Catalog section",
                "Section required for dependency validation"
            )

        defined_ids = set(self.ID_PATTERN.findall(catalog_section))

        # Get all referenced IDs (everywhere)
        all_ids = set(self.ID_PATTERN.findall(self.content))

        # IDs referenced but not defined
        undefined = all_ids - defined_ids

        if undefined:
            return ValidationResult(
                False,
                f"References to undefined IDs: {sorted(undefined)[:10]}",
                f"Defined IDs: {sorted(defined_ids)[:10]}..."
            )

        return ValidationResult(
            True,
            "All ID references valid",
            f"Validated {len(all_ids)} references against {len(defined_ids)} definitions"
        )

    def check_document_length(self) -> ValidationResult:
        """Verify document length is within target range."""
        line_count = len(self.lines)

        if line_count < self.MIN_LINES:
            return ValidationResult(
                False,
                f"Document too short: {line_count} lines (min: {self.MIN_LINES})",
                "May indicate incomplete synthesis"
            )

        if line_count > self.MAX_LINES:
            return ValidationResult(
                False,
                f"Document too long: {line_count} lines (max: {self.MAX_LINES})",
                "May indicate duplication - review for repeated content"
            )

        return ValidationResult(
            True,
            f"Document length OK: {line_count} lines",
            f"Target range: {self.MIN_LINES}-{self.MAX_LINES}"
        )

    def check_no_empty_sections(self) -> ValidationResult:
        """Check for empty section headers."""
        # Find section headers followed by another header or end of file
        empty_pattern = r'^(#{1,3}\s+[^\n]+)\n+(?=#{1,3}\s|\Z)'
        matches = re.findall(empty_pattern, self.content, re.MULTILINE)

        # Filter to actual empty sections (headers with no content before next header)
        empty_sections = []
        for match in matches:
            # Check if there's only whitespace between this header and next
            idx = self.content.find(match)
            if idx != -1:
                next_header = re.search(r'\n#{1,3}\s', self.content[idx + len(match):])
                if next_header:
                    between = self.content[idx + len(match):idx + len(match) + next_header.start()]
                    if not between.strip():
                        empty_sections.append(match.strip())

        if empty_sections:
            return ValidationResult(
                False,
                f"Empty sections found: {len(empty_sections)}",
                f"Examples: {empty_sections[:3]}"
            )

        return ValidationResult(True, "No empty sections detected")

    def check_no_deleted_markers(self) -> ValidationResult:
        """Check for DELETED placeholders that should be removed."""
        deleted_patterns = [
            r'\bDELETED\b',
            r'\[REMOVED\]',
            r'\[TODO\]',
            r'XXX',
        ]

        found = []
        for pattern in deleted_patterns:
            if re.search(pattern, self.content, re.IGNORECASE):
                found.append(pattern)

        if found:
            return ValidationResult(
                False,
                f"Placeholder markers found: {found}",
                "Remove all DELETED/TODO/XXX markers before finalizing"
            )

        return ValidationResult(True, "No placeholder markers found")

    def _extract_section(self, section_name: str) -> Optional[str]:
        """Extract content of a specific section."""
        pattern = rf'^#{1,2}\s+{re.escape(section_name)}[^\n]*\n(.*?)(?=^#{1,2}\s|\Z)'
        match = re.search(pattern, self.content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        return match.group(1) if match else None

    def report(self) -> str:
        """Generate validation report."""
        lines = ["=" * 60, "SYNTHESIS VALIDATION REPORT", "=" * 60, ""]

        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed

        for result in self.results:
            status = "✓" if result.passed else "✗"
            lines.append(f"{status} {result.message}")
            if result.details and not result.passed:
                lines.append(f"  └─ {result.details}")

        lines.append("")
        lines.append("-" * 60)
        lines.append(f"RESULT: {passed}/{len(self.results)} checks passed")

        if failed == 0:
            lines.append("STATUS: PASSED")
        else:
            lines.append(f"STATUS: FAILED ({failed} issues)")

        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_synthesis.py <path-to-REMEDIATION-PLAN.md>")
        print("\nExample:")
        print("  python validate_synthesis.py docs/reviews/REMEDIATION-PLAN.md")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    content = filepath.read_text()

    validator = SynthesisValidator(content)
    passed = validator.validate_all()

    print(validator.report())

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
