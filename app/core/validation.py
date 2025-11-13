from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import re

from app.schemas.toc import TocFile

class ValidationIssue:
    def __init__(self, level: str, msg: str):
        self.level = level  # "WARN" / "ERROR"
        self.msg = msg
    def __repr__(self) -> str:
        return f"[{self.level}] {self.msg}"

_CHAPTER_IN_TITLE = re.compile(r"^第\d+章(?:-\d+)?\s+")
_ID_PREFIX = re.compile(r"^(?P<num>\d{2})(?:-(?P<sub>\d+))?")

def validate_toc_relaxed(toc: TocFile, manuals_root: Path) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if not isinstance(toc.toc, list) or len(toc.toc) == 0:
        raise ValueError("toc must be a non-empty array")

    seen_ids = set()
    for e in toc.toc:
        # file の形式・存在（存在しなくてもWARNに留める）
        if "/" in e.file or "\\" in e.file or not e.file.endswith(".txt"):
            issues.append(ValidationIssue("WARN", f"file suspicious: {e.file}"))
        p = manuals_root / toc.manual / e.file
        if not p.exists():
            issues.append(ValidationIssue("WARN", f"file missing: {p}"))

        # id 重複
        if e.id in seen_ids:
            issues.append(ValidationIssue("WARN", f"duplicate id: {e.id}"))
        seen_ids.add(e.id)

        # title の基本形（第n章）チェック（緩め）
        if not _CHAPTER_IN_TITLE.match(e.title):
            issues.append(ValidationIssue("WARN", f"title may not start with '第...章': {e.title}"))

    return issues
