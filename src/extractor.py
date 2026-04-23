"""Uses Claude Haiku 4.5 to extract style/values preferences from a completed conversation."""
import anthropic
from pathlib import Path


CONTEXT_DIR = Path(__file__).parent.parent / "context"

_EXTRACTION_PROMPT = """\
You are a preference extractor. Given a conversation between a user and an AI assistant, extract any insights about the user's:
1. Writing style preferences (tone, format, length, language mix, etc.)
2. Values and opinions (what they care about, their priorities, things they dislike)
3. Recurring patterns (topics they return to, how they make decisions)

Rules:
- Only extract what is clearly demonstrated in the conversation — do not speculate.
- Be concise. Bullet points preferred.
- If nothing meaningful can be extracted, output exactly: NO_INSIGHTS
- Do NOT include personal data (names, phone numbers, etc.).

Output two sections:
### Style
<bullet points or "nothing extracted">

### Values
<bullet points or "nothing extracted">
"""


def extract_and_update(turns: list[dict], client: anthropic.Anthropic):
    """Run Haiku extraction on turns and merge insights into context files."""
    if not turns:
        return

    conversation_text = "\n".join(
        f"{t['role'].upper()}: {t['content']}" for t in turns
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=_EXTRACTION_PROMPT,
        messages=[{"role": "user", "content": conversation_text}],
    )

    result = response.content[0].text.strip()
    if result == "NO_INSIGHTS":
        return

    _merge_section(result, "### Style", CONTEXT_DIR / "style.md")
    _merge_section(result, "### Values", CONTEXT_DIR / "values.md")


def _merge_section(full_output: str, header: str, target: Path):
    """Append extracted bullets from `header` section into target Markdown file."""
    lines = full_output.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == header)
    except StopIteration:
        return

    bullets = []
    for line in lines[start + 1:]:
        if line.startswith("###"):
            break
        stripped = line.strip()
        if stripped and stripped != "nothing extracted":
            bullets.append(stripped)

    if not bullets:
        return

    existing = target.read_text()
    new_entries = "\n".join(bullets)
    if not existing.strip() or existing.strip().endswith("-->"):
        target.write_text(existing.rstrip() + "\n\n" + new_entries + "\n")
    else:
        target.write_text(existing.rstrip() + "\n" + new_entries + "\n")
