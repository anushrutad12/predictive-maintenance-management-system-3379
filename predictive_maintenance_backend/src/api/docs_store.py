"""
Minimal persistence layer for docs-style pages (Architecture, User Stories, etc.).

We keep storage intentionally lightweight:
- Data is persisted to a local JSON file under the backend container directory.
- If the file doesn't exist, it's initialized with a small seed dataset.

This supports UI workflows:
- Left nav tree (list pages)
- Page content rendering (sections)
- Right rail TOC ("On this page")
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class DocSeed:
    """Seed dataset for docs pages."""
    data: Dict[str, Any]


DEFAULT_SEED = DocSeed(
    data={
        "version": 1,
        "updated_at": _utc_now_iso(),
        "pages": [
            {
                "id": "architecture",
                "slug": "architecture",
                "title": "Architecture",
                "summary": "High-level system architecture and core components.",
                "pill_tabs": [
                    {"id": "overview", "label": "Overview"},
                    {"id": "components", "label": "Components"},
                    {"id": "deployment", "label": "Deployment"},
                ],
                "sections": [
                    {
                        "id": "architecture",
                        "title": "Architecture",
                        "level": 2,
                        "body_markdown": (
                            "This page describes the overall architecture of the Predictive Maintenance "
                            "Management System, including key containers and their responsibilities."
                        ),
                    },
                    {
                        "id": "core-components",
                        "title": "Core components",
                        "level": 2,
                        "body_markdown": (
                            "- **Frontend (Angular):** Docs-style UI (sidebar nav, main content, TOC)\n"
                            "- **Backend (FastAPI):** REST endpoints for docs navigation/content\n"
                            "- **Database:** (future) durable storage for equipment telemetry, alerts, and work orders"
                        ),
                    },
                    {
                        "id": "deployment",
                        "title": "Deployment",
                        "level": 2,
                        "body_markdown": (
                            "The system is split into independently deployable services. "
                            "Environment variables configure base URLs and runtime behavior."
                        ),
                    },
                ],
            },
            {
                "id": "user-stories",
                "slug": "user-stories",
                "title": "User Stories",
                "summary": "User stories describing UI flows and API expectations.",
                "pill_tabs": [],
                "sections": [
                    {
                        "id": "overview",
                        "title": "Overview",
                        "level": 2,
                        "body_markdown": (
                            "This page lists user stories and supporting API surface for "
                            "documentation-style navigation and content."
                        ),
                    },
                    {
                        "id": "models",
                        "title": "Models",
                        "level": 2,
                        "body_markdown": (
                            "- `DocPage`: id, slug, title, summary\n"
                            "- `DocSection`: id, title, level, body_markdown\n"
                            "- `TocItem`: id, title, level (derived from sections)"
                        ),
                    },
                    {
                        "id": "routes",
                        "title": "Routes",
                        "level": 2,
                        "body_markdown": (
                            "- `GET /docs/nav`\n"
                            "- `GET /docs/pages`\n"
                            "- `GET /docs/pages/{slug}`\n"
                            "- `GET /docs/pages/{slug}/toc`"
                        ),
                    },
                    {
                        "id": "schemas",
                        "title": "Schemas",
                        "level": 2,
                        "body_markdown": "All endpoints return JSON and are documented in OpenAPI.",
                    },
                ],
            },
        ],
    }
)


class DocsStore:
    """
    JSON-file backed store for documentation pages.

    Thread-safe and minimal. Not intended for high concurrency.
    """

    def __init__(self, data_file_path: str) -> None:
        self._data_file_path = data_file_path
        self._lock = threading.Lock()
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        os.makedirs(os.path.dirname(self._data_file_path), exist_ok=True)
        if not os.path.exists(self._data_file_path):
            self._write(DEFAULT_SEED.data)

    def _read(self) -> Dict[str, Any]:
        with open(self._data_file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]) -> None:
        data = dict(data)
        data["updated_at"] = _utc_now_iso()
        tmp_path = f"{self._data_file_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self._data_file_path)

    def _find_page_by_slug(self, data: Dict[str, Any], slug: str) -> Optional[Dict[str, Any]]:
        for p in data.get("pages", []):
            if p.get("slug") == slug:
                return p
        return None

    # PUBLIC_INTERFACE
    def get_nav(self) -> Dict[str, Any]:
        """Return navigation tree data suitable for a left sidebar."""
        with self._lock:
            data = self._read()
            items = [
                {
                    "id": p.get("id"),
                    "slug": p.get("slug"),
                    "title": p.get("title"),
                    "summary": p.get("summary", ""),
                }
                for p in data.get("pages", [])
            ]
            return {"items": items, "updated_at": data.get("updated_at")}

    # PUBLIC_INTERFACE
    def list_pages(self) -> List[Dict[str, Any]]:
        """Return a light list of pages."""
        with self._lock:
            data = self._read()
            return [
                {
                    "id": p.get("id"),
                    "slug": p.get("slug"),
                    "title": p.get("title"),
                    "summary": p.get("summary", ""),
                }
                for p in data.get("pages", [])
            ]

    # PUBLIC_INTERFACE
    def get_page(self, slug: str) -> Optional[Dict[str, Any]]:
        """Return a full doc page (sections included)."""
        with self._lock:
            data = self._read()
            page = self._find_page_by_slug(data, slug)
            if not page:
                return None
            # Return a copy to avoid accidental mutation
            return json.loads(json.dumps(page))

    # PUBLIC_INTERFACE
    def get_toc(self, slug: str) -> Optional[List[Dict[str, Any]]]:
        """Return 'On this page' TOC derived from sections."""
        page = self.get_page(slug)
        if not page:
            return None
        toc: List[Dict[str, Any]] = []
        for s in page.get("sections", []):
            toc.append(
                {
                    "id": s.get("id"),
                    "title": s.get("title"),
                    "level": s.get("level", 2),
                }
            )
        return toc


def default_docs_store() -> DocsStore:
    """
    Create a default store instance.

    The data file path is relative to the backend container; we avoid hard-coding
    absolute paths so the app works in different environments.
    """
    # src/api/docs_store.py -> <container_root>/data/docs.json
    container_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_path = os.path.join(container_root, "data", "docs.json")
    return DocsStore(data_file_path=data_path)
