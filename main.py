#!/usr/bin/env python3
"""AI Content Producer — CLI entry point."""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


def cmd_chat(_args):
    from src.chat import run
    run()


def cmd_sync(_args):
    from src.github_sync import sync
    sync()


def cmd_context(_args):
    from src.context_manager import load_context
    ctx = load_context()
    if ctx:
        print(ctx)
    else:
        print("(no context yet — chat first to build it up)")


def main():
    parser = argparse.ArgumentParser(
        description="AI Content Producer — context-aware Claude chat",
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("chat", help="Start an interactive chat session (default)")
    sub.add_parser("sync", help="Push context/ changes to GitHub")
    sub.add_parser("context", help="Print current accumulated context")

    args = parser.parse_args()

    if args.cmd == "sync":
        cmd_sync(args)
    elif args.cmd == "context":
        cmd_context(args)
    else:
        cmd_chat(args)


if __name__ == "__main__":
    main()
