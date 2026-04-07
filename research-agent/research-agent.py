#!/usr/bin/env python3
"""
Research Agent - Level 1 (~200 lines)

A minimal agent specialized for research tasks.
Core capabilities: read documents, search/navigate, take notes, synthesize findings.

Usage:
    1. Set ANTHROPIC_API_KEY in .env file
    2. python research-agent.py
    3. Ask research questions
"""

from anthropic import Anthropic
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import os
import json

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL")
)
MODEL = os.getenv("MODEL_NAME", "claude-sonnet-4-20250514")
WORKDIR = Path.cwd()

SYSTEM = f"""You are a research agent at {WORKDIR}.

Your purpose: Conduct thorough, systematic research and provide well-organized findings.

Research process:
1. UNDERSTAND: Clarify the research question and scope
2. EXPLORE: Use find/grep/ls to locate relevant sources
3. READ: Examine documents, code, or data files
4. ANALYZE: Identify patterns, connections, and insights
5. SYNTHESIZE: Organize findings into clear, actionable summaries
6. DOCUMENT: Save notes and reports to the notes/ directory

Tools available:
- bash: Search files, run grep, navigate directories
- read_file: Examine document contents
- write_note: Save research findings to notes/
- list_notes: Review previously saved notes

Rules:
- Start broad, then narrow down based on findings
- Cite sources (file paths, line numbers) for key information
- Create structured notes with clear headings
- Summarize findings concisely when done
- If you need clarification, ask"""

# Core research tools
TOOLS = [
    {
        "name": "bash",
        "description": "Run shell command. Use for: find, grep, ls, tree, wc, etc. to explore and search.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read file contents. Use to examine documents, code, data files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to file"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max lines to read (optional)"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_note",
        "description": "Save a research note to notes/ directory. Use to document findings, insights, summaries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Note filename (e.g., 'findings.md', 'analysis.txt')"
                },
                "content": {
                    "type": "string",
                    "description": "Note content in markdown format"
                }
            },
            "required": ["filename", "content"]
        }
    },
    {
        "name": "list_notes",
        "description": "List all saved research notes in notes/ directory.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]


def safe_path(p: str) -> Path:
    """Ensure path stays within workspace."""
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool and return result."""
    
    if name == "bash":
        # Safety: block dangerous commands
        dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/sd"]
        if any(d in args["command"] for d in dangerous):
            return "Error: Dangerous command blocked"
        
        try:
            result = subprocess.run(
                args["command"],
                shell=True,
                cwd=WORKDIR,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = (result.stdout + result.stderr).strip()
            return output[:50000] if output else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out (60s)"
        except Exception as e:
            return f"Error: {e}"

    if name == "read_file":
        try:
            path = safe_path(args["path"])
            if not path.exists():
                return f"Error: File not found: {args['path']}"
            
            content = path.read_text()
            lines = content.splitlines()
            
            if "limit" in args and args["limit"]:
                lines = lines[:args["limit"]]
                lines.append(f"\n... ({len(content.splitlines()) - args['limit']} more lines)")
            
            return "\n".join(lines)[:50000]
        except Exception as e:
            return f"Error: {e}"

    if name == "write_note":
        try:
            # Create notes directory
            notes_dir = WORKDIR / "notes"
            notes_dir.mkdir(exist_ok=True)
            
            # Write note
            note_path = notes_dir / args["filename"]
            note_path.write_text(args["content"])
            
            return f"✓ Note saved: notes/{args['filename']} ({len(args['content'])} bytes)"
        except Exception as e:
            return f"Error: {e}"

    if name == "list_notes":
        try:
            notes_dir = WORKDIR / "notes"
            if not notes_dir.exists():
                return "No notes directory yet. Use write_note to create notes."
            
            notes = list(notes_dir.glob("*"))
            if not notes:
                return "No notes saved yet."
            
            result = ["Saved research notes:", ""]
            for note in sorted(notes):
                size = note.stat().st_size
                result.append(f"  - {note.name} ({size} bytes)")
            
            return "\n".join(result)
        except Exception as e:
            return f"Error: {e}"

    return f"Unknown tool: {name}"


def research(prompt: str, history: list = None) -> str:
    """Run the research agent loop."""
    if history is None:
        history = []
    
    history.append({"role": "user", "content": prompt})

    while True:
        response = client.messages.create(
            model=MODEL,
            system=SYSTEM,
            messages=history,
            tools=TOOLS,
            max_tokens=8000,
        )

        # Build assistant message
        history.append({"role": "assistant", "content": response.content})

        # If no tool calls, return text
        if response.stop_reason != "tool_use":
            return "".join(
                block.text for block in response.content 
                if hasattr(block, "text")
            )

        # Execute tools
        results = []
        for block in response.content:
            if block.type == "tool_use":
                # Display tool usage
                args_str = str(block.input)[:60]
                print(f"  > {block.name}: {args_str}...")
                
                # Execute and collect result
                output = execute_tool(block.name, block.input)
                print(f"    ✓ {output[:80]}")
                
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })

        history.append({"role": "user", "content": results})


if __name__ == "__main__":
    print("=" * 60)
    print("Research Agent")
    print("=" * 60)
    print(f"Workspace: {WORKDIR}")
    print(f"Notes directory: {WORKDIR}/notes/")
    print("\nCapabilities:")
    print("  • Search and explore files (bash, grep, find)")
    print("  • Read and analyze documents")
    print("  • Save research notes")
    print("\nType 'q' to quit, 'notes' to list saved notes.\n")
    
    history = []
    while True:
        try:
            query = input("Research> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if query in ("q", "quit", "exit", ""):
            print("Goodbye!")
            break
        
        if query == "notes":
            print(execute_tool("list_notes", {}))
            continue
        
        if query:
            print()
            result = research(query, history)
            print(f"\n{result}\n")