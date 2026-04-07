# Research Agent - Quick Reference

## 🎯 What We Built

A **Level 1 research agent** with 4 core capabilities:

| Tool | Capability | Purpose |
|------|-----------|---------|
| `bash` | Search & Navigate | `find`, `grep`, `ls`, `tree`, etc. |
| `read_file` | Examine | Read documents, code, data |
| `write_note` | Document | Save findings to `notes/` |
| `list_notes` | Review | See previously saved notes |

## 📁 Project Structure

```
research-agent/
├── research-agent.py    # Main agent (~200 lines)
├── requirements.txt    # Dependencies
├── .env.example       # API key template
├── .gitignore         # Ignore patterns
├── README.md          # Full documentation
└── test_tools.py      # Tool verification
```

## 🚀 Quick Start

```bash
cd research-agent

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env: add ANTHROPIC_API_KEY=sk-ant-xxx

# Run agent
python research-agent.py
```

## 💡 Example Research Tasks

### Code Exploration
```
Research> Find all API endpoints and document their authentication requirements
Research> Analyze the error handling patterns in the codebase
Research> Map out the data flow from user input to database
```

### Document Research
```
Research> Summarize the key findings from all PDF reports
Research> Compare the requirements in the spec files
Research> Extract all TODO comments and organize by priority
```

### Data Analysis
```
Research> Analyze the CSV files and identify trends
Research> Find duplicate records in the data files
Research> Generate statistics from the log files
```

## 🎨 Architecture

```
┌─────────────────────────────┐
│   Research Agent (Level 1)  │
├─────────────────────────────┤
│  Model: claude-sonnet-4     │
│  Loop: perceive → act       │
├─────────────────────────────┤
│  Capabilities (4 tools):    │
│  • bash (explore)           │
│  • read_file (examine)      │
│  • write_note (document)    │
│  • list_notes (review)      │
├─────────────────────────────┤
│  Knowledge:                 │
│  Research process in prompt │
└─────────────────────────────┘
```

## 📊 Level Progression

Your agent is **Level 1** (4 tools, ~200 lines). Future upgrades:

| Level | Add | When You Need |
|-------|-----|---------------|
| **2** | TodoWrite | Multi-step planning |
| **3** | Task tool | Parallel exploration |
| **4** | Skills | Domain expertise |
| **5** | Teams | Complex projects |

**Rule**: Only upgrade when real usage shows the need!

## 🔧 Customization Ideas

### Add Web Research
```python
# Add to TOOLS list
{
    "name": "web_search",
    "description": "Search the web",
    "input_schema": {...}
}
```

### Add Database Access
```python
{
    "name": "query_db",
    "description": "Run SQL query",
    "input_schema": {...}
}
```

### Add HTTP Requests
```python
{
    "name": "http_get",
    "description": "Make HTTP request",
    "input_schema": {...}
}
```

## 🎓 Key Design Decisions

### Why 4 Tools?
Following the principle: **Start with 3-5 capabilities.**

These 4 cover 90% of research tasks. The model combines them creatively.

### Why No Workflow?
**Trust the model.** The system prompt explains the research process, but doesn't force it.

The model decides: search first? read multiple files? take notes incrementally?

### Why Notes Directory?
**Context persistence.** Research often spans multiple sessions. Notes survive between runs.

### Why Bash vs Specialized Tools?
**Flexibility.** One `bash` tool provides: `grep`, `find`, `wc`, `tree`, `sort`, `uniq`, etc.

No need to implement each as a separate tool.

## 📚 Resources

- **Full Documentation**: `README.md`
- **Agent Philosophy**: `../skills/agent-builder/references/agent-philosophy.md`
- **Tool Templates**: `../skills/agent-builder/references/tool-templates.py`
- **Subagent Pattern**: `../skills/agent-builder/references/subagent-pattern.py`

## 🐛 Troubleshooting

**"Module not found"**
```bash
pip install anthropic python-dotenv
```

**"API key not found"**
```bash
# Check .env file exists and has key
cat .env
```

**"Dangerous command blocked"**
The agent blocks `rm -rf /`, `sudo`, etc. Safe for research!

## 🎯 Next Steps

1. ✅ Agent is built and ready
2. Configure `.env` with your API key
3. Run `python research-agent.py`
4. Try research tasks!
5. Note what capabilities you actually need
6. Consider Level 2+ upgrades based on real usage

---

**Remember**: The model IS the agent. Your code just gives it capabilities. Keep it simple! 🚀