#!/usr/bin/env python3
"""
PromptSift - Local-first CLI for versioning and managing AI prompts.
Built by Mourad.Soltani
"""
import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".promptsift" / "prompts.db"

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            version INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def cmd_add(args):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO prompts (name, content) VALUES (?, ?)",
            (args.name, args.content)
        )
        conn.commit()
        print(f"Added prompt '{args.name}'")
    except sqlite3.IntegrityError:
        # Update version
        conn.execute(
            "UPDATE prompts SET content = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
            (args.content, args.name)
        )
        conn.commit()
        print(f"Updated prompt '{args.name}' (new version)")
    finally:
        conn.close()

def cmd_list(args):
    conn = get_db()
    rows = conn.execute("SELECT name, version, updated_at FROM prompts ORDER BY updated_at DESC").fetchall()
    conn.close()
    if not rows:
        print("No prompts found.")
        return
    for row in rows:
        print(f"{row['name']} (v{row['version']}) - {row['updated_at']}")

def cmd_show(args):
    conn = get_db()
    row = conn.execute("SELECT * FROM prompts WHERE name = ?", (args.name,)).fetchone()
    conn.close()
    if not row:
        print(f"Prompt '{args.name}' not found.")
        sys.exit(1)
    print(f"Name: {row['name']}")
    print(f"Version: {row['version']}")
    print(f"Updated: {row['updated_at']}")
    print("---")
    print(row['content'])

def cmd_diff(args):
    # Simple textual diff placeholder; in full version would use difflib
    conn = get_db()
    row = conn.execute("SELECT content FROM prompts WHERE name = ?", (args.name,)).fetchone()
    conn.close()
    if not row:
        print(f"Prompt '{args.name}' not found.")
        sys.exit(1)
    print(f"Current content of '{args.name}':")
    print(row['content'])
    print("(Full semantic/text diff available in advanced mode)")

def cmd_search(args):
    conn = get_db()
    rows = conn.execute(
        "SELECT name, content FROM prompts WHERE name LIKE ? OR content LIKE ?",
        (f"%{args.query}%", f"%{args.query}%")
    ).fetchall()
    conn.close()
    if not rows:
        print("No matches.")
        return
    for row in rows:
        print(f"{row['name']}: {row['content'][:80]}...")

def main():
    parser = argparse.ArgumentParser(description="PromptSift - Local AI prompt versioning CLI. Built by Mourad.Soltani")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add or update a prompt")
    p_add.add_argument("name")
    p_add.add_argument("content")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List all prompts")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show a prompt")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_show)

    p_diff = sub.add_parser("diff", help="Show current version info")
    p_diff.add_argument("name")
    p_diff.set_defaults(func=cmd_diff)

    p_search = sub.add_parser("search", help="Search prompts")
    p_search.add_argument("query")
    p_search.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
