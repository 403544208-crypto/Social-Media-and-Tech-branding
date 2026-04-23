"""Interactive streaming chat with Claude Opus 4.7, with /save and /sync commands."""
import uuid
import anthropic

from .context_manager import build_system_prompt
from .logger import append_turn, read_session
from .extractor import extract_and_update
from .github_sync import sync

BASE_SYSTEM = """\
You are a helpful AI assistant. Respond in the same language the user writes in.
When the user writes /save "<note>", acknowledge that you will save the note.
"""

_COMMANDS = {"/save", "/sync", "/quit", "/exit"}


def _print_stream(stream) -> str:
    """Stream response to stdout, return full text."""
    full = []
    for text in stream.text_stream:
        print(text, end="", flush=True)
        full.append(text)
    print()
    return "".join(full)


def _handle_save(note: str, client: anthropic.Anthropic, session_id: str):
    from pathlib import Path
    from datetime import date
    templates_dir = Path(__file__).parent.parent / "context" / "templates"
    templates_dir.mkdir(exist_ok=True)
    fname = templates_dir / f"{date.today().isoformat()}_note.md"
    with fname.open("a") as f:
        f.write(f"- {note}\n")
    print(f"[saved → {fname.relative_to(Path(__file__).parent.parent)}]")


def run():
    client = anthropic.Anthropic()
    session_id = str(uuid.uuid4())[:8]
    messages: list[dict] = []
    system_blocks = build_system_prompt(BASE_SYSTEM)

    print("AI Content Producer — 输入 /quit 退出，/save \"<笔记>\" 保存，/sync 同步到 GitHub")
    print("-" * 60)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        # ── /quit ──────────────────────────────────────────────────────────
        if user_input.lower() in ("/quit", "/exit"):
            break

        # ── /sync ──────────────────────────────────────────────────────────
        if user_input.lower() == "/sync":
            sync()
            continue

        # ── /save "<note>" ─────────────────────────────────────────────────
        if user_input.lower().startswith("/save "):
            note = user_input[6:].strip().strip('"').strip("'")
            _handle_save(note, client, session_id)
            continue

        # ── Normal chat turn ───────────────────────────────────────────────
        messages.append({"role": "user", "content": user_input})
        append_turn("user", user_input, session_id)

        with client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=system_blocks,
            messages=messages,
        ) as stream:
            print("Claude: ", end="")
            reply = _print_stream(stream)

        messages.append({"role": "assistant", "content": reply})
        append_turn("assistant", reply, session_id)

    # ── Session end: auto-extract preferences ──────────────────────────────
    print("\n[session end] 正在提取偏好...")
    turns = read_session(session_id)
    extract_and_update(turns, client)
    print("[done] context/ 文件已更新。运行 /sync 或重启时自动注入。")
