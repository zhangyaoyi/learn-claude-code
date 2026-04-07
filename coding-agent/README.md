# Production Coding Agent

A **Level 5 production-ready coding agent** designed for large-scale codebases (10,000+ lines). Features planning, subagent delegation, domain expertise, and robust error handling.

## 🎯 Key Features

### Production Ready
- ✅ **Error Handling**: Retry logic, timeouts, graceful degradation
- ✅ **Logging**: Session logs for debugging and audit trails
- ✅ **Safety**: Path validation, command blocking, protected directories
- ✅ **Context Management**: Compression for long sessions
- ✅ **State Tracking**: Todo lists, progress monitoring

### Large Codebase Capabilities
- ✅ **Planning**: TodoWrite for breaking down complex tasks
- ✅ **Delegation**: Task tool for spawning specialized subagents
- ✅ **Context Isolation**: Subagents with clean context (no pollution)
- ✅ **Domain Expertise**: load_skill for on-demand knowledge
- ✅ **Efficient Navigation**: Optimized for 10k+ line projects

### 7 Core Tools
1. **bash** - Shell commands (find, grep, git, npm, etc.)
2. **read_file** - Examine files (with line limits for large files)
3. **write_file** - Create new files
4. **edit_file** - Surgical edits to existing files
5. **TodoWrite** - Plan and track tasks
6. **Task** - Delegate to specialized subagents
7. **load_skill** - Load domain expertise

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Production Coding Agent (Level 5)              │
├─────────────────────────────────────────────────────────┤
│  Core Loop: perceive → decide → act → respond           │
├─────────────────────────────────────────────────────────┤
│  Planning Layer                                         │
│  • TodoWrite for task tracking                          │
│  • Progress monitoring                                  │
│  • Context compression                                  │
├─────────────────────────────────────────────────────────┤
│  Delegation Layer                                        │
│  • Task tool for subagents                             │
│  • Agent types: explore, code, test, plan              │
│  • Isolated contexts                                   │
├─────────────────────────────────────────────────────────┤
│  Knowledge Layer                                         │
│  • load_skill for domain expertise                     │
│  • On-demand loading                                    │
│  • Skills directory                                    │
├─────────────────────────────────────────────────────────┤
│  Safety Layer                                           │
│  • Path validation                                     │
│  • Dangerous command blocking                          │
│  • Timeout enforcement                                 │
│  • Protected directories                              │
├─────────────────────────────────────────────────────────┤
│  Production Features                                    │
│  • Retry logic (exponential backoff)                   │
│  • Session logging                                     │
│  • Error handling                                      │
│  • State management                                    │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
cd coding-agent
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env: Add your ANTHROPIC_API_KEY

# 3. Run
python coding-agent.py
```

## 💡 Usage Examples

### Large Refactoring
```
Code> Refactor the authentication system to use OAuth2

  > TodoWrite: Plan the refactoring
    ✓ Created 5 tasks
  
  > Task(explore): Analyze current auth implementation
    ✓ Found auth code in 12 files
  
  > TodoWrite: Mark analysis complete
    ✓ Updated tasks
  
  > Task(plan): Design OAuth2 integration
    ✓ Created implementation plan
  
  > TodoWrite: Start implementation
    ✓ Task 1 in progress
  
  > edit_file: auth/login.py
    ✓ Updated authentication logic
  
  > Task(test): Run tests for auth module
    ✓ All tests passing
  
  ...
```

### Bug Investigation
```
Code> Find the memory leak in the API handler

  > Task(explore): Search for unclosed connections
    [explore] Searching codebase ... 23 tools, 12.3s
    ✓ Found potential leak in api/handler.py:145
  
  > read_file: api/handler.py, limit=200
    ✓ Read 200 lines
  
  > Task(code): Fix the connection leak
    ✓ Added connection.close() in finally block
```

### Code Analysis
```
Code> Map all database queries and identify N+1 problems

  > TodoWrite: Create analysis plan
    ✓ 4 tasks created
  
  > Task(explore): Find all database queries
    ✓ Found 89 queries across 23 files
  
  > Task(explore): Identify query patterns
    ✓ Detected 12 potential N+1 problems
  
  > TodoWrite: Update progress
    ✓ 2/4 tasks complete
  
  > load_skill: database-patterns
    ✓ Loaded skill: database-patterns
  
  > TodoWrite: Complete analysis
    ✓ All tasks complete
```

## 🔧 Tools Reference

### TodoWrite - Task Planning
```python
# Plan complex work
TodoWrite({
  "items": [
    {"content": "Analyze current implementation",
     "status": "in_progress",
     "activeForm": "Analyzing current implementation"},
    {"content": "Design new architecture",
     "status": "pending",
     "activeForm": "Designing new architecture"},
    {"content": "Implement changes",
     "status": "pending",
     "activeForm": "Implementing changes"},
    {"content": "Write tests",
     "status": "pending",
     "activeForm": "Writing tests"},
  ]
})
```

### Task - Subagent Delegation
```python
# Spawn read-only exploration agent
Task({
  "agent_type": "explore",
  "description": "Find API endpoints",
  "prompt": "Search codebase for all API endpoints. List file paths and line numbers."
})

# Spawn code implementation agent
Task({
  "agent_type": "code",
  "description": "Implement auth",
  "prompt": "Add JWT authentication to the API routes in routes/api.py"
})

# Spawn test agent
Task({
  "agent_type": "test",
  "description": "Run auth tests",
  "prompt": "Run all tests in tests/auth/ and report failures"
})

# Spawn planning agent
Task({
  "agent_type": "plan",
  "description": "Design migration",
  "prompt": "Create a migration plan from REST to GraphQL"
})
```

### load_skill - Domain Expertise
```python
# Load React patterns
load_skill({"name": "react-patterns"})

# Load API design best practices
load_skill({"name": "api-design"})

# Load database optimization
load_skill({"name": "database-patterns"})
```

### context_compress - Context Management
```python
# When context gets long
context_compress({"reason": "Working on large codebase, context at 45 turns"})
```

## 🎭 Subagent Types

| Type | Tools | Purpose |
|------|-------|---------|
| **explore** | bash, read_file | Read-only search and analysis |
| **code** | bash, read_file, write_file, edit_file | Full implementation |
| **test** | bash, read_file | Run tests, analyze failures |
| **plan** | bash, read_file | Design implementation strategy |

**Key Feature**: Subagents run with **isolated context** - they don't see the parent conversation. This prevents "context pollution" in large projects.

## 📁 Project Structure

```
coding-agent/
├── coding-agent.py       # Main agent (~800 lines)
├── requirements.txt      # Dependencies
├── .env.example          # Configuration template
├── .gitignore            # Ignore patterns
├── README.md             # This file
├── skills/               # Domain expertise
│   ├── example-patterns.md
│   └── api-design.md
└── logs/                 # Session logs (auto-created)
    └── session_YYYYMMDD.log
```

## 🎓 Production Best Practices

### 1. Plan Before Implementing
```
# Good: Plan first
Code> Add user authentication
  > TodoWrite: Create plan
    ✓ 5 tasks
  > Task(plan): Design auth system
    ✓ Plan created
  > TodoWrite: Start implementation
    ...

# Bad: Jump straight to code
Code> Add user authentication
  > write_file: auth.py
    # Starts coding without understanding
```

### 2. Use Subagents for Exploration
```
# Good: Isolate exploration
Code> Find all API endpoints
  > Task(explore): Find endpoints
    ✓ Found 45 endpoints
  # Main context stays clean

# Bad: Pollute main context
Code> Find all API endpoints
  > bash: find . -name "*.py" | xargs grep "route"
    ✓ 234 matches
  > read_file: file1.py
  > read_file: file2.py
  # ... many reads pollute main context
```

### 3. Load Skills When Stuck
```
Code> Optimize database queries
  > Task(explore): Find slow queries
    ✓ Found N+1 in users.py
  
  > load_skill: database-patterns
    ✓ Loaded skill: database-patterns
  
  # Now has domain expertise to solve properly
```

### 4. Compress Context Periodically
```
Code> [After 50+ turns working on large refactor]
  > context_compress: "Large refactor, need summary"
    ✓ Please provide a concise summary...
  
  # Agent summarizes, freeing context space
```

### 5. Use edit_file for Existing Files
```
# Good: Surgical edit
> edit_file: auth.py
    old_text: "def login(user):"
    new_text: "def login(user, remember=False):"
    ✓ Edited auth.py

# Bad: Rewrite entire file
> write_file: auth.py
    # Overwrites entire file, risky
```

## 🔒 Safety Features

### Path Validation
```python
# Blocked: Path escape attempts
read_file("../../../etc/passwd")
# Error: Path escapes workspace
```

### Command Blocking
```python
# Blocked: Dangerous commands
bash("rm -rf /")
# Error: Dangerous command blocked

bash("sudo rm file")
# Error: Dangerous command blocked
```

### Protected Directories
```python
# Warning: Deleting protected dirs
bash("rm -rf node_modules")
# Warning: About to delete node_modules. Confirm if intentional.
```

### Timeout Enforcement
```python
# All bash commands timeout after 120s
bash("long-running-command")
# Error: Command timed out after 120s
```

## 📊 Performance Tuning

### Environment Variables
```bash
# .env file
MAX_CONTEXT_TURNS=50    # Turns before suggesting compression
MAX_RETRIES=3           # API retry attempts
TIMEOUT_SECONDS=120    # Bash command timeout
```

### For Very Large Codebases (100k+ lines)
1. Increase `MAX_CONTEXT_TURNS` to 100
2. Use subagents liberally
3. Compress context after each major phase
4. Load relevant skills at task start

### For Slow Networks
1. Increase `TIMEOUT_SECONDS` to 300
2. Increase `MAX_RETRIES` to 5

## 🛠️ Creating Custom Skills

Skills are markdown files in `skills/` directory:

```markdown
# skills/my-patterns.md

## Error Handling Pattern

Always use this pattern for error handling:

\`\`\`python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise CustomError(f"Failed: {e}") from e
finally:
    cleanup()
\`\`\`

## Database Query Pattern

Use connection pooling:
\`\`\`python
from db import get_connection

with get_connection() as conn:
    # queries here
    pass
\`\`\`
```

Then load it:
```
Code> load_skill: my-patterns
  ✓ Loaded skill: my-patterns
```

## 🐛 Troubleshooting

### "API call failed after 3 retries"
- Check ANTHROPIC_API_KEY in .env
- Check network connectivity
- Check API status: status.anthropic.com

### "Context too long" errors
- Use `context_compress` tool
- Use subagents more liberally
- Break task into smaller pieces

### "Subagent timeout"
- Subagents have 50-turn limit
- Break large tasks into smaller ones

### "Dangerous command blocked"
- Review the command
- If intentional, modify command slightly
- Or use write_file for file operations

## 📈 Monitoring

### Session Logs
All tool calls are logged to `logs/session_YYYYMMDD.log`:
```
[14:32:15] read_file: {"path": "auth.py"}
[14:32:18] edit_file: {"path": "auth.py", "old_text": "..."}
[14:32:20] bash: {"command": "python -m pytest"}
```

### Session Statistics
```
Code> stats

Session Statistics
============================================================
Duration: 12.3 minutes
Tool calls: 45
Context turns: 23
Tasks: 4/6 completed
============================================================
```

## 🎯 When to Use This Agent

### ✅ Perfect For:
- Large codebases (10k+ lines)
- Complex refactoring projects
- Multi-file changes
- Architecture redesigns
- Code analysis and audits
- Long development sessions

### ❌ Overkill For:
- Single-file edits (use Level 1 agent)
- Quick bug fixes
- Simple scripts
- One-off tasks

## 📚 Level Progression

| Level | Features | Use Case |
|-------|----------|----------|
| 1 | 4 tools | Simple tasks, small files |
| 2 | +TodoWrite | Multi-step tasks |
| 3 | +Task tool | Large projects |
| 4 | +Skills | Domain-specific work |
| **5** | +Production features | **Production codebases** |

## 🔗 Resources

- [Agent Philosophy](../skills/agent-builder/references/agent-philosophy.md) - Deep dive
- [Tool Templates](../skills/agent-builder/references/tool-templates.py) - More tools
- [Subagent Pattern](../skills/agent-builder/references/subagent-pattern.py) - Context isolation

## 📝 License

MIT

---

**Built with the agent-builder philosophy: The model IS the agent. This code just provides the harness.**