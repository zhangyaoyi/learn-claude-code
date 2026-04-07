#!/usr/bin/env python3
"""
Production Coding Agent - Level 5 (~800 lines)

A powerful agent for large-scale codebase management (10k+ lines).
Features: planning, subagents, skills, context management, robust error handling.

Usage:
    1. Set ANTHROPIC_API_KEY in .env
    2. python coding-agent.py
    3. Give complex coding tasks
"""

from anthropic import Anthropic
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any
import subprocess
import json
import time
import sys
import os
import re

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL")
)

MODEL = os.getenv("MODEL_NAME", "claude-sonnet-4-20250514")
WORKDIR = Path.cwd()
SKILLS_DIR = WORKDIR / "skills"
LOGS_DIR = WORKDIR / "logs"
MAX_CONTEXT_TURNS = int(os.getenv("MAX_CONTEXT_TURNS", "50"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "120"))

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
SKILLS_DIR.mkdir(exist_ok=True)

# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM = f"""You are a production coding agent at {WORKDIR}.

## Purpose
Handle complex, large-scale coding tasks in codebases with 10,000+ lines of code.

## Capabilities
- **Planning**: Break down complex tasks into tracked steps (TodoWrite)
- **Delegation**: Spawn specialized subagents for parallel work (Task)
- **Knowledge**: Load domain expertise on-demand (load_skill)
- **File Operations**: Read, write, edit files with precision
- **Search**: Navigate large codebases efficiently

## Workflow Philosophy
1. **UNDERSTAND**: Clarify requirements, scope, constraints
2. **PLAN**: Create structured task list with TodoWrite
3. **EXPLORE**: Use subagents to search codebase without polluting context
4. **IMPLEMENT**: Make focused, minimal changes
5. **VERIFY**: Test changes, check for regressions
6. **DOCUMENT**: Update relevant docs and comments

## Large Codebase Strategies
- Use `Task(explore)` for broad searches - keeps main context clean
- Load skills for domain patterns: `load_skill("react-patterns")`
- Compress context periodically: ask for summaries
- Work incrementally: one component at a time
- Prefer `edit_file` over `write_file` for surgical changes

## Tool Usage Guidelines
- **TodoWrite**: Plan first, update as you progress
- **Task**: Delegate exploration and implementation to subagents
- **load_skill**: Load domain knowledge when stuck or uncertain
- **read_file**: Use `limit` parameter for large files
- **edit_file**: Prefer for existing files (surgical changes)
- **bash**: Use `find`, `grep`, `rg` for codebase navigation

## Production Quality Standards
- ✅ Handle errors gracefully
- ✅ Maintain backward compatibility
- ✅ Write self-documenting code
- ✅ Consider edge cases
- ✅ Test critical paths
- ✅ Update affected documentation

## Constraints
- One task in_progress at a time
- Read files before editing
- Test after changes when possible
- Document breaking changes
- Respect .gitignore patterns

Work systematically. Think before acting. Quality over speed."""

# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOLS = [
    # Core file operations
    {
        "name": "bash",
        "description": "Execute shell command. Use for: find, grep, rg, git, npm, python, etc. Timeout: 120s.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read file contents. Use `limit` for large files. Returns up to 50KB.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"},
                "limit": {"type": "integer", "description": "Max lines to read (optional)"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to file. Creates parent directories. Use for new files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in file. Use for surgical edits to existing files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"},
                "old_text": {"type": "string", "description": "Exact text to find (must match precisely)"},
                "new_text": {"type": "string", "description": "Replacement text"}
            },
            "required": ["path", "old_text", "new_text"]
        }
    },
    
    # Planning and tracking
    {
        "name": "TodoWrite",
        "description": "Update task list. Use to plan and track progress on complex tasks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Complete list of tasks",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Task description"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                            "activeForm": {"type": "string", "description": "Present tense: 'Writing tests'"}
                        },
                        "required": ["content", "status", "activeForm"]
                    }
                }
            },
            "required": ["items"]
        }
    },
    
    # Subagent delegation
    {
        "name": "Task",
        "description": "Spawn a specialized subagent for focused work. Subagents have ISOLATED context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Short task name (3-5 words)"},
                "prompt": {"type": "string", "description": "Detailed instructions for subagent"},
                "agent_type": {
                    "type": "string",
                    "enum": ["explore", "code", "test", "plan"],
                    "description": "explore (read-only), code (full), test (run tests), plan (design)"
                }
            },
            "required": ["description", "prompt", "agent_type"]
        }
    },
    
    # Domain expertise
    {
        "name": "load_skill",
        "description": "Load domain expertise on-demand. Use when you need patterns, best practices, or domain knowledge.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Skill name (e.g., 'react-patterns', 'api-design')"}
            },
            "required": ["name"]
        }
    },
    
    # Context management
    {
        "name": "context_compress",
        "description": "Request a summary of conversation so far. Use when context gets long.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "Why compression is needed"}
            },
            "required": ["reason"]
        }
    },
]

# =============================================================================
# AGENT TYPES FOR SUBAGENTS
# =============================================================================

AGENT_TYPES = {
    "explore": {
        "description": "Read-only agent for searching, analyzing, and exploring code",
        "tools": ["bash", "read_file"],
        "prompt": "You are an exploration agent. Search and analyze code WITHOUT modifying files. Return a concise summary of what you found. Cite file paths and line numbers."
    },
    "code": {
        "description": "Full agent for implementing features and fixing bugs",
        "tools": ["bash", "read_file", "write_file", "edit_file"],
        "prompt": "You are a coding agent. Implement the requested changes. Make minimal, focused edits. Return a summary of what you changed."
    },
    "test": {
        "description": "Agent for running and analyzing tests",
        "tools": ["bash", "read_file"],
        "prompt": "You are a testing agent. Run tests, analyze failures, and report results. Do NOT modify code."
    },
    "plan": {
        "description": "Planning agent for designing implementation strategies",
        "tools": ["bash", "read_file"],
        "prompt": "You are a planning agent. Analyze the codebase and output a numbered implementation plan. Do NOT make changes. Be specific about files and approaches."
    },
}

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

class AgentState:
    """Track agent state across the conversation."""
    
    def __init__(self):
        self.todos: List[Dict[str, str]] = []
        self.context_turns: int = 0
        self.total_tools_calls: int = 0
        self.session_start: float = time.time()
        self.last_compress_turn: int = 0
    
    def update_todos(self, items: List[Dict[str, str]]) -> None:
        """Update todo list."""
        self.todos = items
        self.display_todos()
    
    def display_todos(self) -> None:
        """Display current todo list."""
        if not self.todos:
            return
        
        print("\n" + "="*60)
        print("Task List")
        print("="*60)
        for i, item in enumerate(self.todos, 1):
            status_icon = {
                "pending": "○",
                "in_progress": "◉",
                "completed": "✓"
            }.get(item["status"], "○")
            
            print(f"{status_icon} {i}. {item['content']}")
            if item["status"] == "in_progress" and "activeForm" in item:
                print(f"   → {item['activeForm']}")
        print("="*60 + "\n")
    
    def should_compress(self) -> bool:
        """Check if context compression is needed."""
        return (
            self.context_turns - self.last_compress_turn >= MAX_CONTEXT_TURNS
            and self.context_turns > 0
        )
    
    def stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        elapsed = time.time() - self.session_start
        return {
            "elapsed_minutes": round(elapsed / 60, 1),
            "tool_calls": self.total_tools_calls,
            "context_turns": self.context_turns,
            "tasks_total": len(self.todos),
            "tasks_completed": sum(1 for t in self.todos if t["status"] == "completed")
        }

state = AgentState()

# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================

def safe_path(p: str) -> Path:
    """Ensure path stays within workspace."""
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def execute_bash(command: str) -> str:
    """Execute shell command with safety checks."""
    # Block dangerous commands
    dangerous_patterns = [
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+~",
        r">\s*/dev/sd",
        r"mkfs",
        r"dd\s+if=",
        r":()\s*{\s*:\|:&\s*}",  # Fork bomb
        r"sudo\s+rm",
        r"chmod\s+777\s+/",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return f"Error: Dangerous command blocked (matches pattern: {pattern})"
    
    # Check for gitignore patterns (optional safety)
    gitignore = WORKDIR / ".gitignore"
    if gitignore.exists():
        # Basic check - don't modify node_modules, .env, etc.
        protected = ["node_modules", ".env", ".git", "__pycache__"]
        for protected_dir in protected:
            if f"rm -rf {protected_dir}" in command or f"rm -rf ./{protected_dir}" in command:
                return f"Warning: About to delete {protected_dir}. Confirm if intentional."
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )
        
        output = (result.stdout + result.stderr).strip()
        
        # Truncate very long outputs
        if len(output) > 50000:
            output = output[:50000] + f"\n\n... (truncated, {len(output)} total bytes)"
        
        return output if output else "(no output)"
    
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {TIMEOUT_SECONDS}s"
    except Exception as e:
        return f"Error: {e}"


def execute_read_file(path: str, limit: Optional[int] = None) -> str:
    """Read file contents with optional line limit."""
    try:
        file_path = safe_path(path)
        
        if not file_path.exists():
            return f"Error: File not found: {path}"
        
        if not file_path.is_file():
            return f"Error: Not a file: {path}"
        
        content = file_path.read_text()
        lines = content.splitlines()
        
        if limit and limit < len(lines):
            lines = lines[:limit]
            lines.append(f"\n... ({len(content.splitlines()) - limit} more lines)")
        
        result = "\n".join(lines)
        
        # Truncate very large files
        if len(result) > 50000:
            result = result[:50000] + f"\n\n... (truncated, file has {len(content)} total bytes)"
        
        return result
    
    except Exception as e:
        return f"Error: {e}"


def execute_write_file(path: str, content: str) -> str:
    """Write content to file, creating parent directories."""
    try:
        file_path = safe_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        
        return f"✓ Wrote {len(content):,} bytes to {path}"
    
    except Exception as e:
        return f"Error: {e}"


def execute_edit_file(path: str, old_text: str, new_text: str) -> str:
    """Replace exact text in file."""
    try:
        file_path = safe_path(path)
        
        if not file_path.exists():
            return f"Error: File not found: {path}"
        
        content = file_path.read_text()
        
        if old_text not in content:
            return f"Error: Text not found in {path}"
        
        # Count occurrences
        count = content.count(old_text)
        if count > 1:
            return f"Error: Text appears {count} times in {path}. Please be more specific."
        
        # Perform replacement
        new_content = content.replace(old_text, new_text, 1)
        file_path.write_text(new_content)
        
        return f"✓ Edited {path} (replaced {len(old_text)} chars with {len(new_text)} chars)"
    
    except Exception as e:
        return f"Error: {e}"


def execute_todo_write(items: List[Dict[str, str]]) -> str:
    """Update task list."""
    try:
        state.update_todos(items)
        return f"✓ Updated task list ({len(items)} tasks)"
    except Exception as e:
        return f"Error: {e}"


def execute_task(description: str, prompt: str, agent_type: str) -> str:
    """Spawn a subagent with isolated context."""
    if agent_type not in AGENT_TYPES:
        return f"Error: Unknown agent type: {agent_type}"
    
    config = AGENT_TYPES[agent_type]
    
    print(f"\n{'='*60}")
    print(f"Subagent [{agent_type}]: {description}")
    print(f"{'='*60}")
    
    # Agent-specific system prompt
    sub_system = f"""You are a {agent_type} subagent at {WORKDIR}.

{config['prompt']}

Rules:
- Work autonomously to complete the task
- Return a clear, concise summary
- Do NOT ask for clarification - make reasonable assumptions"""

    # Filter tools for this agent type
    allowed_tools = config["tools"]
    sub_tools = [t for t in TOOLS if t["name"] in allowed_tools]
    
    # ISOLATED message history (key feature!)
    sub_messages = [{"role": "user", "content": prompt}]
    
    start_time = time.time()
    tool_count = 0
    
    # Run subagent loop
    max_turns = 50  # Prevent runaway subagents
    turns = 0
    
    while turns < max_turns:
        turns += 1
        
        try:
            response = client.messages.create(
                model=MODEL,
                system=sub_system,
                messages=sub_messages,
                tools=sub_tools,
                max_tokens=8000,
            )
        except Exception as e:
            return f"Error: Subagent API call failed: {e}"
        
        # Check if done
        if response.stop_reason != "tool_use":
            break
        
        # Execute tools
        tool_calls = [b for b in response.content if b.type == "tool_use"]
        results = []
        
        for tc in tool_calls:
            tool_count += 1
            
            # Execute the tool
            if tc.name == "bash":
                output = execute_bash(tc.input["command"])
            elif tc.name == "read_file":
                output = execute_read_file(tc.input["path"], tc.input.get("limit"))
            elif tc.name == "write_file":
                output = execute_write_file(tc.input["path"], tc.input["content"])
            elif tc.name == "edit_file":
                output = execute_edit_file(tc.input["path"], tc.input["old_text"], tc.input["new_text"])
            else:
                output = f"Error: Unknown tool: {tc.name}"
            
            results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": output
            })
            
            # Progress indicator
            elapsed = time.time() - start_time
            sys.stdout.write(f"\r  [{agent_type}] {description} ... {tool_count} tools, {elapsed:.1f}s")
            sys.stdout.flush()
        
        sub_messages.append({"role": "assistant", "content": response.content})
        sub_messages.append({"role": "user", "content": results})
    
    # Final progress update
    elapsed = time.time() - start_time
    print(f"\r  [{agent_type}] {description} - done ({tool_count} tools, {elapsed:.1f}s)\n")
    
    # Extract and return ONLY the final text
    for block in response.content:
        if hasattr(block, "text"):
            return block.text
    
    return "(subagent returned no text)"


def execute_load_skill(name: str) -> str:
    """Load domain expertise from skills directory."""
    try:
        skill_file = SKILLS_DIR / f"{name}.md"
        
        if not skill_file.exists():
            # Check for .txt extension
            skill_file = SKILLS_DIR / f"{name}.txt"
            if not skill_file.exists():
                return f"Error: Skill not found: {name}\n\nAvailable skills: {list_skills()}"
        
        content = skill_file.read_text()
        
        print(f"\n{'='*60}")
        print(f"Loaded skill: {name}")
        print(f"{'='*60}\n")
        
        return f"Skill loaded: {name}\n\n{content}"
    
    except Exception as e:
        return f"Error: {e}"


def list_skills() -> str:
    """List available skills."""
    skills = list(SKILLS_DIR.glob("*.md")) + list(SKILLS_DIR.glob("*.txt"))
    if not skills:
        return "No skills available"
    return ", ".join(sorted(s.stem for s in skills))


def execute_context_compress(reason: str) -> str:
    """Request context compression."""
    state.last_compress_turn = state.context_turns
    return f"Context compression requested: {reason}\n\nPlease provide a concise summary of:\n1. What has been done so far\n2. What remains to be done\n3. Key decisions made\n4. Important context to preserve"


# =============================================================================
# MAIN TOOL DISPATCHER
# =============================================================================

def execute_tool(name: str, args: dict) -> str:
    """Dispatch tool call to implementation."""
    state.total_tools_calls += 1
    
    # Log tool call
    log_tool_call(name, args)
    
    # Dispatch to implementation
    if name == "bash":
        return execute_bash(args["command"])
    
    if name == "read_file":
        return execute_read_file(args["path"], args.get("limit"))
    
    if name == "write_file":
        return execute_write_file(args["path"], args["content"])
    
    if name == "edit_file":
        return execute_edit_file(args["path"], args["old_text"], args["new_text"])
    
    if name == "TodoWrite":
        return execute_todo_write(args["items"])
    
    if name == "Task":
        return execute_task(args["description"], args["prompt"], args["agent_type"])
    
    if name == "load_skill":
        return execute_load_skill(args["name"])
    
    if name == "context_compress":
        return execute_context_compress(args["reason"])
    
    return f"Error: Unknown tool: {name}"


# =============================================================================
# LOGGING
# =============================================================================

def log_tool_call(name: str, args: dict) -> None:
    """Log tool call to file."""
    log_file = LOGS_DIR / f"session_{time.strftime('%Y%m%d')}.log"
    
    timestamp = time.strftime('%H:%M:%S')
    args_preview = str(args)[:100]
    
    log_line = f"[{timestamp}] {name}: {args_preview}\n"
    
    try:
        log_file.parent.mkdir(exist_ok=True)
        with open(log_file, "a") as f:
            f.write(log_line)
    except Exception:
        pass  # Fail silently


# =============================================================================
# MAIN AGENT LOOP
# =============================================================================

def agent(prompt: str, history: List[Dict] = None) -> str:
    """Run the agent loop with retries and error handling."""
    if history is None:
        history = []
    
    history.append({"role": "user", "content": prompt})
    state.context_turns += 1
    
    # Check if context compression needed
    if state.should_compress():
        print("\n⚠️  Context getting long. Consider using context_compress tool.\n")
    
    consecutive_errors = 0
    
    while True:
        try:
            response = client.messages.create(
                model=MODEL,
                system=SYSTEM,
                messages=history,
                tools=TOOLS,
                max_tokens=8000,
            )
            
            # Reset error counter on success
            consecutive_errors = 0
            
        except Exception as e:
            consecutive_errors += 1
            
            if consecutive_errors >= MAX_RETRIES:
                return f"Error: API call failed after {MAX_RETRIES} retries: {e}"
            
            # Exponential backoff
            wait_time = 2 ** consecutive_errors
            print(f"\n⚠️  API error, retrying in {wait_time}s... ({consecutive_errors}/{MAX_RETRIES})")
            time.sleep(wait_time)
            continue
        
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
                args_preview = str(block.input)[:60]
                print(f"  > {block.name}: {args_preview}...")
                
                # Execute and collect result
                output = execute_tool(block.name, block.input)
                
                # Display result preview
                output_preview = output[:100].replace('\n', ' ')
                print(f"    ✓ {output_preview}")
                
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })
        
        history.append({"role": "user", "content": results})
        state.context_turns += 1


# =============================================================================
# CLI INTERFACE
# =============================================================================

def print_banner():
    """Print startup banner."""
    stats = state.stats()
    
    print("\n" + "="*60)
    print("Production Coding Agent - Level 5")
    print("="*60)
    print(f"Workspace: {WORKDIR}")
    print(f"Model: {MODEL}")
    print(f"Skills: {SKILLS_DIR}")
    print(f"Logs: {LOGS_DIR}")
    print("\nCapabilities:")
    print("  • File operations: read, write, edit")
    print("  • Planning: TodoWrite for task tracking")
    print("  • Delegation: Task for subagents")
    print("  • Knowledge: load_skill for domain expertise")
    print("  • Context: compression for long sessions")
    print("\nSubagent Types:")
    for name, config in AGENT_TYPES.items():
        print(f"  • {name}: {config['description']}")
    print("\nType 'q' to quit, 'stats' for session info, 'help' for commands.\n")


def print_help():
    """Print help information."""
    print("""
Commands:
  <task>     Give the agent a coding task
  stats      Show session statistics
  todos      Show current task list
  help       Show this help message
  q          Quit

Special Tools:
  TodoWrite         Plan and track tasks
  Task              Spawn subagent (explore/code/test/plan)
  load_skill        Load domain expertise
  context_compress  Compress conversation history

Examples:
  "Add authentication to the API"
  "Refactor the database layer"
  "Find all uses of deprecated functions"
  "Create a test suite for the auth module"
""")


def print_stats():
    """Print session statistics."""
    stats = state.stats()
    print("\n" + "="*60)
    print("Session Statistics")
    print("="*60)
    print(f"Duration: {stats['elapsed_minutes']} minutes")
    print(f"Tool calls: {stats['tool_calls']}")
    print(f"Context turns: {stats['context_turns']}")
    print(f"Tasks: {stats['tasks_completed']}/{stats['tasks_total']} completed")
    print("="*60 + "\n")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print_banner()
    
    history = []
    
    while True:
        try:
            query = input("Code> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break
        
        # Handle special commands
        if query in ("q", "quit", "exit", ""):
            print_stats()
            print("Goodbye!")
            break
        
        if query == "help":
            print_help()
            continue
        
        if query == "stats":
            print_stats()
            continue
        
        if query == "todos":
            state.display_todos()
            continue
        
        # Run agent
        if query:
            print()
            try:
                result = agent(query, history)
                print(f"\n{result}\n")
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Type 'q' to quit.\n")
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                traceback.print_exc()