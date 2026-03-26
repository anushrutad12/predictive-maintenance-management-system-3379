"""
Docs-style endpoints for UI flows (Architecture / User Stories pages).

Endpoints:
- GET /docs/nav                -> left sidebar navigation list
- GET /docs/pages              -> list pages (lightweight)
- GET /docs/pages/{slug}       -> page detail with sections (markdown)
- GET /docs/pages/{slug}/toc   -> right-rail TOC derived from sections
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from src.api.docs_schemas import (
    DocNavResponse,
    DocPageDetail,
    DocPageSummary,
    TocItem,
)
from src.api.docs_store import default_docs_store

router = APIRouter(prefix="/docs", tags=["Docs"])

_store = default_docs_store()


@router.get(
    "/nav",
    response_model=DocNavResponse,
    operation_id="get_docs_nav",
    summary="Get docs navigation items",
    description="Returns items used for the left sidebar navigation tree/list.",
)
def get_docs_nav() -> DocNavResponse:
    """Return navigation items for docs pages."""
    data = _store.get_nav()
    return DocNavResponse(**data)


@router.get(
    "/pages",
    response_model=List[DocPageSummary],
    operation_id="list_docs_pages",
    summary="List docs pages",
    description="Returns a lightweight list of docs pages (id/slug/title/summary).",
)
def list_docs_pages() -> List[DocPageSummary]:
    """List docs pages."""
    return [DocPageSummary(**p) for p in _store.list_pages()]


@router.get(
    "/pages/{slug}",
    response_model=DocPageDetail,
    operation_id="get_docs_page",
    summary="Get docs page detail",
    description="Returns full docs page content including sections (markdown).",
)
def get_docs_page(slug: str) -> DocPageDetail:
    """Get a docs page by slug."""
    page = _store.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail=f"Doc page not found for slug='{slug}'")
    return DocPageDetail(**page)


@router.get(
    "/pages/{slug}/toc",
    response_model=List[TocItem],
    operation_id="get_docs_page_toc",
    summary="Get 'On this page' TOC for a docs page",
    description="Returns TOC entries derived from the page's sections.",
)
def get_docs_page_toc(slug: str) -> List[TocItem]:
    """Get a derived TOC for a docs page."""
    toc = _store.get_toc(slug)
    if toc is None:
        raise HTTPException(status_code=404, detail=f"Doc page not found for slug='{slug}'")
    return [TocItem(**t) for t in toc]
