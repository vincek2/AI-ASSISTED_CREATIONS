#!/usr/bin/env python3
"""Dependency-free structural checks for this skill repository."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
OPENAI_YAML = ROOT / "agents" / "openai.yaml"
EXPECTED_NAME = "account-historical-value-analyzer"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def frontmatter(text: str) -> str:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md must begin with YAML frontmatter")
    return match.group(1)


def field(block: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*(.+?)\s*$", block)
    if not match:
        fail(f"SKILL.md frontmatter is missing '{name}'")
    return match.group(1).strip().strip('"\'')


def main() -> None:
    if not SKILL.is_file():
        fail("SKILL.md is missing")
    if not OPENAI_YAML.is_file():
        fail("agents/openai.yaml is missing")

    text = SKILL.read_text(encoding="utf-8")
    header = frontmatter(text)

    if field(header, "name") != EXPECTED_NAME:
        fail(f"skill name must be '{EXPECTED_NAME}'")
    if len(field(header, "description")) < 40:
        fail("skill description is too short to support reliable discovery")

    required_phrases = (
        "UNADJUSTED DAILY CLOSE",
        "REVIEW_REQUIRED",
        "account_value[d] = SUM",
        "SELL Must Never Be Carried Forward",
    )
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"critical invariant is missing: {phrase}")

    ui = OPENAI_YAML.read_text(encoding="utf-8")
    if "$account-historical-value-analyzer" not in ui:
        fail("default prompt must explicitly reference the skill")

    print("Skill repository validation passed.")


if __name__ == "__main__":
    main()
