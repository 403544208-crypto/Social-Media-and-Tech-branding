"""Loads context Markdown files and injects them into a system prompt with caching."""
from pathlib import Path


CONTEXT_DIR = Path(__file__).parent.parent / "context"


def load_context() -> str:
    """Return all context files merged into one string, or empty string if none exist."""
    parts = []
    for md_file in sorted(CONTEXT_DIR.rglob("*.md")):
        text = md_file.read_text().strip()
        if text and not text.startswith("<!--"):
            # Only include files that have real content beyond the comment header
            lines = [l for l in text.splitlines() if not l.startswith("<!--")]
            content = "\n".join(lines).strip()
            if content:
                parts.append(f"## {md_file.stem.replace('_', ' ').title()}\n{content}")
    return "\n\n".join(parts)


def build_system_prompt(base_prompt: str) -> list[dict]:
    """Build a messages-API system prompt list with prompt-caching on the context block."""
    context = load_context()
    blocks = []
    if context:
        blocks.append({
            "type": "text",
            "text": context,
            "cache_control": {"type": "ephemeral"},
        })
    blocks.append({"type": "text", "text": base_prompt})
    return blocks
