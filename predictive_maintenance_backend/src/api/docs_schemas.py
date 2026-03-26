"""
Pydantic schemas for docs-style pages (navigation, page content, TOC).

These are deliberately minimal and aligned to the UI flows:
- sidebar nav (list of pages)
- doc page detail (sections)
- "On this page" TOC
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DocNavItem(BaseModel):
    """A single navigation item for the left sidebar."""
    id: str = Field(..., description="Stable page id.")
    slug: str = Field(..., description="URL slug for the page (used in routing).")
    title: str = Field(..., description="Display title for the page.")
    summary: str = Field("", description="Short summary shown in lists or tooltips.")


class DocNavResponse(BaseModel):
    """Response wrapper for navigation list."""
    items: List[DocNavItem] = Field(..., description="Ordered list of top-level doc pages.")
    updated_at: Optional[str] = Field(None, description="ISO timestamp of last store update.")


class DocPillTab(BaseModel):
    """Optional pill-tab metadata shown near the top of a doc page."""
    id: str = Field(..., description="Tab id; UI can use this as a filter key.")
    label: str = Field(..., description="Tab label.")


class DocSection(BaseModel):
    """A documentation section (rendered as markdown in the UI)."""
    id: str = Field(..., description="Anchor id used for in-page navigation/TOC.")
    title: str = Field(..., description="Section title.")
    level: int = Field(2, ge=1, le=6, description="Heading level (e.g., 2 => h2).")
    body_markdown: str = Field(..., description="Markdown body content for this section.")


class DocPageSummary(BaseModel):
    """Lightweight page list item."""
    id: str = Field(..., description="Stable page id.")
    slug: str = Field(..., description="URL slug for the page.")
    title: str = Field(..., description="Display title.")
    summary: str = Field("", description="Short summary.")


class DocPageDetail(BaseModel):
    """Full doc page detail, including sections and optional pill tabs."""
    id: str = Field(..., description="Stable page id.")
    slug: str = Field(..., description="URL slug for the page.")
    title: str = Field(..., description="Display title.")
    summary: str = Field("", description="Short summary.")
    pill_tabs: List[DocPillTab] = Field(default_factory=list, description="Optional pill tabs.")
    sections: List[DocSection] = Field(default_factory=list, description="Ordered doc sections.")


class TocItem(BaseModel):
    """A derived TOC item for the right rail."""
    id: str = Field(..., description="Anchor id (matches a section id).")
    title: str = Field(..., description="TOC display title.")
    level: int = Field(2, ge=1, le=6, description="Heading level for indentation.")
