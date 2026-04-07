# Research Agent

A minimal AI agent specialized for research tasks - exploring, analyzing, and synthesizing information.

## Design Philosophy

This agent follows the **"model is the agent"** principle:

- **Simple**: Just 4 core tools. The model figures out the workflow.
- **Focused**: Designed for research - search, read, analyze, document.
- **Transparent**: ~200 lines of clear, readable Python.

The agent doesn't have hardcoded workflows. Instead, it has capabilities and a research-oriented system prompt. The model decides how to approach each task.

## Capabilities

| Tool | Purpose | Example Uses |
|------|---------|--------------|
| `bash` | Search & navigate | `find . -name "*.py"`, `grep -r "function"`, `ls -la` |
| `read_file` | Examine documents | Read papers, code, data files |
| `write_note` | Save findings | Document insights, create summaries |
| `list_notes` | Review notes | See what you've already documented |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run the agent
python research-agent.py
```

## Example Research Sessions

### Code Exploration
```
Research> Find all uses of the authenticate function and explain how it works

  > bash: grep -r "authenticate" --include="*.py" .
    ✓ Found 12 occurrences across 4 files...
  > read_file: auth/login.py
    ✓ Read 234 lines...
  > read_file: auth/middleware.py
    ✓ Read 156 lines...
  > write_note: authentication-analysis.md
    ✓ Note saved...

The authenticate function is used in 3 main places:
1. login.py:23 - Main login endpoint
2. middleware.py:45 - Request authentication
3. api/routes.py:12 - API key validation
...
```

### Document Analysis
```
Research> Analyze all the PDF files and summarize their key findings

  > bash: find . -name "*.pdf"
    ✓ Found 5 PDF files...
  > read_file: reports/q1-report.pdf
    ✓ Extracted text from PDF...
  > read_file: reports/q2-report.pdf
    ✓ Extracted text from PDF...
  > write_note: report-summary.md
    ✓ Note saved...

Based on the 5 reports analyzed:
- Q1 shows 23% growth in...
- Key challenge identified in...
...
```

### Comparative Research
```
Research> Compare the implementation patterns in the React and Vue components

  > bash: find src -name "*.jsx" -o -name "*.vue"
    ✓ Found 23 React and 18 Vue components...
  > read_file: src/components/UserProfile.jsx
    ✓ Read 89 lines...
  > read_file: src/components/UserProfile.vue
    ✓ Read 76 lines...
  > write_note: framework-comparison.md
    ✓ Note saved...

Comparison of React vs Vue patterns:
1. State Management: React uses hooks, Vue uses reactive()
2. Component Structure: React uses JSX, Vue uses SFC
...
```

## Notes Directory

All research notes are saved to `notes/`:

```
notes/
├── authentication-analysis.md
├── report-summary.md
└── framework-comparison.md
```

Use the `notes` command to list saved notes:

```
Research> notes
Saved research notes:
  - authentication-analysis.md (2,341 bytes)
  - report-summary.md (1,892 bytes)
  - framework-comparison.md (3,102 bytes)
```

## Architecture

### Level 1 Agent (Simple & Focused)

```
┌─────────────────────────────────────┐
│         Research Agent              │
├─────────────────────────────────────┤
│  System Prompt (Research Process)   │
│  - Understand question              │
│  - Explore sources                  │
│  - Read & analyze                   │
│  - Synthesize findings              │
│  - Document results                 │
├─────────────────────────────────────┤
│  Tools (4 capabilities)              │
│  • bash (search/navigate)           │
│  • read_file (examine)              │
│  • write_note (document)            │
│  • list_notes (review)              │
├─────────────────────────────────────┤
│  Loop: perceive → decide → act      │
└─────────────────────────────────────┘
```

### Why Only 4 Tools?

Following the principle: **Start with 3-5 capabilities. Add more only when real usage shows the need.**

These 4 tools cover most research tasks:
- `bash` provides unlimited flexibility (grep, find, wc, tree, etc.)
- `read_file` for deep examination
- `write_note` for documentation
- `list_notes` for context management

If you find yourself needing additional capabilities, consider:
- `web_search` - for online research
- `database_query` - for data analysis
- `http_request` - for API exploration

## Customization

### Add Web Search

```python
# In TOOLS list:
{
    "name": "web_search",
    "description": "Search the web for information",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
}

# In execute_tool():
if name == "web_search":
    # Integrate with search API (DuckDuckGo, Google, etc.)
    ...
```

### Add Domain Knowledge

Edit the `SYSTEM` prompt to inject expertise:

```python
SYSTEM = f"""You are a research agent at {WORKDIR}.

DOMAIN EXPERTISE:
{load_expert_knowledge()}

RESEARCH PROCESS:
...
"""
```

### Add Subagents (Level 3)

For complex research with multiple exploration threads:

```python
# Add Task tool to spawn isolated research agents
# See: skills/agent-builder/references/subagent-pattern.py
```

## Extending the Agent

### Level 2: Add TodoWrite for Planning

For multi-step research projects, add task tracking:

```python
{
    "name": "TodoWrite",
    "description": "Update research plan and track progress",
    "input_schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "status": {"enum": ["pending", "in_progress", "completed"]}
                    }
                }
            }
        }
    }
}
```

### Level 3: Add Task for Parallel Exploration

Spawn child agents for independent research threads:

```python
{
    "name": "Task",
    "description": "Spawn a subagent for focused research",
    "input_schema": {...}
}
```

## Troubleshooting

### "Error: Dangerous command blocked"
The agent blocks potentially destructive commands. Safe for research, but you can modify the `dangerous` list in `execute_tool()` if needed.

### Notes not saving
The `notes/` directory is created automatically. Check permissions if issues persist.

### Rate limiting
Add delays between tool calls or implement retry logic with exponential backoff.

## Principles Applied

From the agent-builder philosophy:

✅ **Start simple** - 4 tools, ~200 lines  
✅ **Trust the model** - No hardcoded workflows  
✅ **Constraints focus** - Research-specific system prompt  
✅ **Context protection** - Notes directory for persistence  
✅ **Progressive complexity** - Clear path to Level 2/3/4  

## Resources

- [Agent Philosophy](../skills/agent-builder/references/agent-philosophy.md) - Deep dive
- [Minimal Agent](../skills/agent-builder/references/minimal-agent.py) - Base template
- [Tool Templates](../skills/agent-builder/references/tool-templates.py) - More capabilities
- [Subagent Pattern](../skills/agent-builder/references/subagent-pattern.py) - Context isolation