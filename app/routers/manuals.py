from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any

from app.repositories.manual import (
    ManualRepository,
    ManualNotFound,
    SectionNotFound,
    TocLoadError,
)
from app.deps import get_repo

# ★ 追加 import
from app.schemas.search import (
    SearchTextRequest, SearchTextResponse,
    FindExceptionsRequest, FindExceptionsResponse
)
from app.services.search import search_text as svc_search_text, find_exceptions as svc_find_exceptions

router = APIRouter()

def _strip_children_if_needed(data: Dict[str, Any], hierarchical: bool) -> Dict[str, Any]:
    if hierarchical:
        return data
    # 章のみ：children を落として返す
    if "toc" in data:
        pruned = []
        for e in data["toc"]:
            d = dict(e)
            d.pop("children", None)
            pruned.append(d)
        return {"manual": data["manual"], "toc": pruned}
    return data

@router.get("/list_manuals")
def list_manuals(repo: ManualRepository = Depends(get_repo)):
    return repo.list_manuals()

@router.get("/get_toc")
def get_toc(
    manual_name: str = Query(...),
    hierarchical: bool = Query(False),
    repo: ManualRepository = Depends(get_repo),
):
    try:
        toc = repo.load_toc(manual_name)
        return _strip_children_if_needed(toc.model_dump(), hierarchical)
    except ManualNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TocLoadError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list_sections")
def list_sections(
    manual_name: str,
    repo: ManualRepository = Depends(get_repo),
):
    try:
        return repo.list_sections(manual_name)
    except ManualNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/get_section")
def get_section(
    manual_name: str,
    section_id: str,
    repo: ManualRepository = Depends(get_repo),
):
    try:
        return repo.get_section(manual_name, section_id)
    except ManualNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SectionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/get_outline")
def get_outline(
    manual_name: str,
    section_id: str,
    repo: ManualRepository = Depends(get_repo),
):
    try:
        return repo.get_outline(manual_name, section_id)
    except ManualNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SectionNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/resolve_reference")
def resolve_reference(
    manual_name: str,
    ref_text: str,
    repo: ManualRepository = Depends(get_repo),
):
    try:
        sid = repo.resolve_reference(manual_name, ref_text)
        return {"target_section": sid} if sid else {"target_section": None}
    except ManualNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------------------------
# ★ 新規: /search_text
# ---------------------------
@router.post("/search_text", response_model=SearchTextResponse)
def search_text(
    body: SearchTextRequest,
    repo: ManualRepository = Depends(get_repo),
):
    try:
        results = svc_search_text(repo, body)
        return {"results": results}
    except ManualNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------------------------
# ★ 新規: /find_exceptions
# ---------------------------
@router.post("/find_exceptions", response_model=FindExceptionsResponse)
def find_exceptions(
    body: FindExceptionsRequest,
    repo: ManualRepository = Depends(get_repo),
):
    try:
        results = svc_find_exceptions(repo, body)
        return {"results": results}
    except ManualNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
