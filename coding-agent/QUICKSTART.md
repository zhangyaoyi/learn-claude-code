# Production Coding Agent - Quick Reference

## 🎯 What We Built

A **Level 5 production-ready coding agent** for large codebases (10k+ lines).

## 🛠️ 7 Core Tools

| Tool | Purpose | Key Features |
|------|---------|--------------|
| **bash** | Shell commands | Timeout, safety blocking |
| **read_file** | Read files | Line limits, large file handling |
| **write_file** | Create files | Auto-create directories |
| **edit_file** | Edit files | Surgical changes, exact matching |
| **TodoWrite** | Plan tasks | Progress tracking |
| **Task** | Delegate work | Subagents with isolated context |
| **load_skill** | Load expertise | On-demand domain knowledge |

## 🎭 4 Subagent Types

| Type | Tools | Use For |
|------|-------|---------|
| **explore** | bash, read | Searching, analyzing (read-only) |
| **code** | bash, read, write, edit | Implementation |
| **test** | bash, read | Running tests |
| **plan** | bash, read | Design strategy |

## 🚀 Quick Start

```bash
cd coding-agent
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
python coding-agent.py
```

## 💡 Key Commands

```
Code> <task>       # Give a coding task
Code> stats        # Session statistics
Code> todos        # Show task list
Code> help         # Help message
Code> q            # Quit
```

## 📊 Production Features

✅ **Error Handling**: Retry logic, timeouts, graceful degradation  
✅ **Logging**: Session logs in `logs/` directory  
✅ **Safety**: Path validation, command blocking  
✅ **Context Management**: Compression for long sessions  
✅ **State Tracking**: Todo lists, statistics  

## 🎓 Best Practices

### 1. Plan Before Code
```
TodoWrite -> Create task list
Task(plan) -> Design strategy
TodoWrite -> Update progress
Task(code) -> Implement
```

### 2. Use Subagents for Exploration
```
Task(explore) -> Search codebase
# Keeps main context clean!
```

### 3. Load Skills When Needed
```
load_skill("api-design")
# Domain expertise loaded on-demand
```

### 4. Compress Context Periodically
```
context_compress({"reason": "50 turns completed"})
```

## 📁 Project Structure

```
coding-agent/
├── coding-agent.py        # Main agent (~800 lines)
├── README.md              # Full docs (13 KB)
├── skills/                # Domain expertise
│   ├── example-patterns.md
│   └── api-design.md
└── logs/                  # Session logs
```

## 🔒 Safety Built-In

- Path escape attempts blocked
- Dangerous commands blocked (rm -rf /, sudo)
- Protected directories warning
- 120s timeout on all commands
- 50-turn limit on subagents

## 🎯 Perfect For

✅ Large codebases (10k+ lines)  
✅ Complex refactoring  
✅ Multi-file changes  
✅ Architecture redesigns  
✅ Long sessions  

## ❌ Overkill For

- Single-file edits  
- Quick bug fixes  
- Simple scripts  

## 📈 Session Stats

```
Duration: 12.3 minutes
Tool calls: 45
Context turns: 23
Tasks: 4/6 completed
```

## 🛠️ Create Custom Skills

```markdown
# skills/my-patterns.md

## My Pattern
Always use this approach:
...
```

Then: `load_skill("my-patterns")`

## 🐛 Troubleshooting

**"API failed after retries"**  
→ Check ANTHROPIC_API_KEY  

**"Context too long"**  
→ Use context_compress  

**"Subagent timeout"**  
→ Break task into smaller pieces  

---

**Remember**: This is Level 5 - production ready! 🚀