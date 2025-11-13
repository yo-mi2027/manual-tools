from __future__ import annotations
import re
import unicodedata
from typing import Iterable, List, Tuple

from app.schemas.search import (
    SearchTextRequest, SearchHit,
    FindExceptionsRequest, ExceptionHit
)
from app.repositories.manual import ManualRepository, SectionNotFound

# 許容する“区切り”の集合（可読のためクラスにしてまとめる）
# 空白(\s) / 全角空白(\u3000) / 中点 / スラッシュ(全半角) / 各種ハイフン
_SEP_CLASS = r"[\s\u3000・/／\-\u2010\u2011\u2012\u2013\u2014]*"

def _nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s.replace("\r\n", "\n").replace("\r", "\n"))

def _iter_sections(repo: ManualRepository, manual: str, section_id: str | None) -> Iterable[Tuple[str, str]]:
    if section_id:
        try:
            sec = repo.get_section(manual, section_id)
            yield section_id, _nfkc(sec["text"])
        except SectionNotFound:
            return
        return
    for sid in repo.list_sections(manual):
        try:
            sec = repo.get_section(manual, sid)
        except SectionNotFound:
            continue
        yield sid, _nfkc(sec["text"])

def _make_snippet(text: str, start: int, end: int, width: int = 80) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(text) else ""
    return prefix + text[left:right].strip() + suffix

def _build_loose_regex(query: str) -> str:
    """
    文字間に任意の区切り（空白/中点/スラッシュ/ハイフン等）が入ってもマッチする正規表現を生成。
    例: '帝王切開' → '帝{sep}王{sep}切{sep}開'
    """
    q = _nfkc(query)
    parts = [re.escape(ch) for ch in q]
    return _SEP_CLASS.join(parts)

def search_text(repo: ManualRepository, req: SearchTextRequest) -> List[SearchHit]:
    flags = 0 if req.case_sensitive else re.IGNORECASE

    if req.mode == "plain":
        pattern = re.escape(req.query)
    elif req.mode == "loose":
        pattern = _build_loose_regex(req.query)
    else:  # "regex"
        pattern = req.query

    try:
        regex = re.compile(pattern, flags)
    except re.error:
        # 不正な正規表現はプレーン一致にフォールバック
        regex = re.compile(re.escape(req.query), flags)

    results: List[SearchHit] = []
    for sid, text in _iter_sections(repo, req.manual_name, req.section_id):
        m = regex.search(text)
        if not m:
            continue
        snippet = _make_snippet(text, m.start(), m.end())
        results.append(SearchHit(section_id=sid, snippet=snippet))
        if len(results) >= req.limit:
            break
    return results

# 例外抽出はそのまま（必要になったら語彙を増やす）
_EXCEPTION_TERMS = [
    r"留意", r"注意", r"例外", r"対象外", r"禁止",
    r"適用しない", r"支払われない", r"支給されない",
    r"不支給", r"不適用", r"除外", r"取り扱わない"
]
_EXCEPTION_RE = re.compile("|".join(_EXCEPTION_TERMS))

def find_exceptions(repo: ManualRepository, req: FindExceptionsRequest) -> List[ExceptionHit]:
    hits: List[ExceptionHit] = []
    for sid, text in _iter_sections(repo, req.manual_name, req.section_id):
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if not _EXCEPTION_RE.search(ln):
                continue
            ctx = [lines[i - 1].strip()] if i - 1 >= 0 else []
            ctx.append(ln.strip())
            if i + 1 < len(lines):
                ctx.append(lines[i + 1].strip())
            snippet = " ".join([c for c in ctx if c])
            if snippet:
                hits.append(ExceptionHit(section_id=sid, text=snippet))
                if len(hits) >= req.limit:
                    return hits
    return hits