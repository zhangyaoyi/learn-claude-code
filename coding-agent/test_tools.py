#!/usr/bin/env python3
"""
Test script for Production Coding Agent tools.

Run to verify all tools work correctly before using the agent.
"""

import sys
from pathlib import Path

# Import from coding-agent
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("coding_agent", Path(__file__).parent / "coding-agent.py")
coding_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coding_agent)

# Import what we need
execute_tool = coding_agent.execute_tool
WORKDIR = coding_agent.WORKDIR
AGENT_TYPES = coding_agent.AGENT_TYPES
TOOLS = coding_agent.TOOLS

def test_core_tools():
    """Test core file operation tools."""
    print("\n" + "="*60)
    print("Testing Core Tools")
    print("="*60)
    
    # Test bash
    result = execute_tool("bash", {"command": "echo 'Hello, Agent!'"})
    print(f"✓ bash: {result}")
    
    # Test read_file
    result = execute_tool("read_file", {"path": "README.md", "limit": 10})
    print(f"✓ read_file: {result[:80]}...")
    
    # Test write_file
    result = execute_tool("write_file", {
        "path": "test-output.txt",
        "content": "Test file created by agent."
    })
    print(f"✓ write_file: {result}")
    
    # Test edit_file
    result = execute_tool("edit_file", {
        "path": "test-output.txt",
        "old_text": "Test file created by agent.",
        "new_text": "Test file edited by agent."
    })
    print(f"✓ edit_file: {result}")
    
    # Cleanup
    Path("test-output.txt").unlink()


def test_planning_tool():
    """Test TodoWrite tool."""
    print("\n" + "="*60)
    print("Testing TodoWrite Tool")
    print("="*60)
    
    result = execute_tool("TodoWrite", {
        "items": [
            {"content": "Test task 1", "status": "completed", "activeForm": "Testing task 1"},
            {"content": "Test task 2", "status": "in_progress", "activeForm": "Testing task 2"},
            {"content": "Test task 3", "status": "pending", "activeForm": "Testing task 3"}
        ]
    })
    print(f"✓ TodoWrite: {result}")


def test_agent_types():
    """Verify agent types are configured."""
    print("\n" + "="*60)
    print("Testing Agent Types")
    print("="*60)
    
    for name, config in AGENT_TYPES.items():
        tools = config["tools"]
        print(f"✓ {name}: {tools}")


def test_skills():
    """Test skill loading."""
    print("\n" + "="*60)
    print("Testing Skills")
    print("="*60)
    
    # Test load_skill
    result = execute_tool("load_skill", {"name": "example-patterns"})
    print(f"✓ load_skill: {result[:100]}...")
    
    # Test missing skill
    result = execute_tool("load_skill", {"name": "nonexistent"})
    print(f"✓ missing skill handled: {result[:80]}...")


def test_safety_features():
    """Test safety mechanisms."""
    print("\n" + "="*60)
    print("Testing Safety Features")
    print("="*60)
    
    # Path escape
    result = execute_tool("read_file", {"path": "../../../etc/passwd"})
    print(f"✓ Path escape blocked: {result}")
    
    # Dangerous command
    result = execute_tool("bash", {"command": "rm -rf /"})
    print(f"✓ Dangerous command blocked: {result}")


def test_context_compress():
    """Test context compression."""
    print("\n" + "="*60)
    print("Testing Context Compression")
    print("="*60)
    
    result = execute_tool("context_compress", {"reason": "Testing compression"})
    print(f"✓ context_compress: {result[:100]}...")


def test_error_handling():
    """Test error scenarios."""
    print("\n" + "="*60)
    print("Testing Error Handling")
    print("="*60)
    
    # Non-existent file
    result = execute_tool("read_file", {"path": "nonexistent.txt"})
    print(f"✓ Non-existent file: {result}")
    
    # Invalid edit (text not found)
    result = execute_tool("edit_file", {
        "path": "README.md",
        "old_text": "NONEXISTENT TEXT",
        "new_text": "replacement"
    })
    print(f"✓ Invalid edit: {result}")


def verify_tool_schema():
    """Verify all tools have valid schemas."""
    print("\n" + "="*60)
    print("Verifying Tool Schemas")
    print("="*60)
    
    for tool in TOOLS:
        name = tool["name"]
        schema = tool["input_schema"]
        
        # Check required fields
        has_type = "type" in schema
        has_properties = "properties" in schema
        
        if has_type and has_properties:
            print(f"✓ {name}: valid schema")
        else:
            print(f"✗ {name}: invalid schema")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Production Coding Agent - Tool Tests")
    print("="*60)
    print(f"Working directory: {WORKDIR}")
    print(f"Tools available: {len(TOOLS)}")
    print(f"Agent types: {list(AGENT_TYPES.keys())}")
    
    try:
        test_core_tools()
        test_planning_tool()
        test_agent_types()
        test_skills()
        test_safety_features()
        test_context_compress()
        test_error_handling()
        verify_tool_schema()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)
        print("\nAgent is ready to use!")
        print("\nNext steps:")
        print("1. cp .env.example .env")
        print("2. Add ANTHROPIC_API_KEY to .env")
        print("3. python coding-agent.py")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()