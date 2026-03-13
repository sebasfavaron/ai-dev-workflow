#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHARED_MEMORY_ROOTS = [
    REPO_ROOT.parent / "agents-database",
    REPO_ROOT.parent / "Code" / "agents-database",
]
SHARED_MEMORY_ROOT = Path(
    next((str(path) for path in DEFAULT_SHARED_MEMORY_ROOTS if path.exists()), str(DEFAULT_SHARED_MEMORY_ROOTS[0]))
)
SHARED_MEMORY_SRC = SHARED_MEMORY_ROOT / "src"
SHARED_MEMORY_DB = SHARED_MEMORY_ROOT / "data" / "shared-agent-memory.sqlite3"
SOURCE_REF = "ai-dev-workflow"


def load_memory_service():
    if str(SHARED_MEMORY_SRC) not in sys.path:
        sys.path.insert(0, str(SHARED_MEMORY_SRC))
    from shared_agent_memory import MemoryService  # type: ignore

    return MemoryService(str(SHARED_MEMORY_DB))


def compact(text: str, limit: int = 200) -> str:
    normalized = " ".join(text.split())
    return normalized if len(normalized) <= limit else normalized[: limit - 3] + "..."


def feature_context_path(feature_id: str | None) -> Path:
    agents_dir = REPO_ROOT / ".agents"
    if feature_id:
        return agents_dir / "feature-contexts" / f"{feature_id}.json"
    current = agents_dir / "current-feature"
    if not current.exists():
        raise FileNotFoundError("No current feature selected")
    return agents_dir / "feature-contexts" / f"{current.read_text().strip()}.json"


def ingest_note(args: argparse.Namespace) -> dict:
    service = load_memory_service()
    payload = {
        "id": f"mem_{uuid.uuid4().hex}",
        "type": args.type,
        "scope": args.scope,
        "project_id": args.project_id,
        "repo_id": args.repo_id,
        "title": args.title,
        "content": args.content,
        "summary": compact(args.content),
        "confidence": args.confidence,
        "freshness": args.freshness,
        "source_ref": SOURCE_REF,
        "evidence_ref": SOURCE_REF,
        "metadata": {"kind": args.kind, "repo_root": str(REPO_ROOT)},
    }
    return service.ingest(payload)


def sync_feature(args: argparse.Namespace) -> dict:
    service = load_memory_service()
    context_path = feature_context_path(args.feature_id)
    context = json.loads(context_path.read_text())
    feature_id = context.get("id") or context_path.stem
    repo_summaries = []
    repos = context.get("repos", {})
    for repo_name, repo_ctx in repos.items():
        repo_summaries.append(
            f"{repo_name}: branch={repo_ctx.get('branch')} pr={repo_ctx.get('pr', {}).get('number')} state={repo_ctx.get('pr', {}).get('state')}"
        )
    content = "\n".join(
        line
        for line in [
            f"Feature: {feature_id}",
            f"Title: {context.get('title') or context.get('summary') or ''}".strip(),
            f"Type: {context.get('type') or ''}".strip(),
            f"Issue: {context.get('issue', {}).get('url') or context.get('issue', {}).get('number') or ''}".strip(),
            f"Repos: {'; '.join(repo_summaries)}" if repo_summaries else "Repos:",
            f"Summary: {context.get('summary') or ''}".strip(),
        ]
        if line.strip()
    )
    payload = {
        "id": f"feature_{feature_id}",
        "type": "episode",
        "scope": "agent",
        "project_id": None,
        "repo_id": None,
        "title": f"AI Dev Workflow feature {feature_id}",
        "content": content,
        "summary": compact(content),
        "confidence": 0.88,
        "freshness": 0.85,
        "source_ref": SOURCE_REF,
        "evidence_ref": str(context_path),
        "metadata": {
            "feature_id": feature_id,
            "repo_count": len(repos),
            "repo_names": sorted(repos.keys()),
        },
    }
    return service.ingest(payload)


def search_memory(args: argparse.Namespace) -> dict:
    service = load_memory_service()
    payload = service.search(
        args.query,
        scopes=[args.scope] if args.scope else ["global", "project", "repo", "agent", "session"],
        limit=args.limit,
    )
    if args.repo_only:
        payload["results"] = [
            result for result in payload["results"] if result.get("memory", {}).get("source_ref") == SOURCE_REF
        ]
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shared-memory helpers for ai-dev-workflow")
    sub = parser.add_subparsers(dest="command", required=True)

    add_note = sub.add_parser("add-note")
    add_note.add_argument("--title", required=True)
    add_note.add_argument("--content", required=True)
    add_note.add_argument("--type", default="artifact")
    add_note.add_argument("--scope", default="agent", choices=["global", "project", "repo", "agent", "session"])
    add_note.add_argument("--project-id", default=None)
    add_note.add_argument("--repo-id", default=None)
    add_note.add_argument("--kind", default="workflow_note")
    add_note.add_argument("--confidence", type=float, default=0.9)
    add_note.add_argument("--freshness", type=float, default=0.9)
    add_note.set_defaults(func=ingest_note)

    sync = sub.add_parser("sync-feature")
    sync.add_argument("--feature-id", default=None)
    sync.set_defaults(func=sync_feature)

    search = sub.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--scope", default=None, choices=["global", "project", "repo", "agent", "session"])
    search.add_argument("--repo-only", action="store_true")
    search.set_defaults(func=search_memory)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(json.dumps(args.func(args), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
