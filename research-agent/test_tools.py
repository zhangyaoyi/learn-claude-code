#!/usr/bin/env python3
"""
Test script for Research Agent tools.

Run this to verify the agent's tools work correctly.
"""

from pathlib import Path
import tempfile
import shutil
import sys

# Import from research-agent
sys.path.insert(0, str(Path(__file__).parent))
# Import the module with hyphen in name
import importlib.util
spec = importlib.util.spec_from_file_location("research_agent", Path(__file__).parent / "research-agent.py")
research_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research_agent)
execute_tool = research_agent.execute_tool
WORKDIR = research_agent.WORKDIR


def test_bash_tool():
    """Test bash command execution."""
    print("\n" + "="*60)
    print("Testing bash tool...")
    print("="*60)
    
    # Test simple command
    result = execute_tool("bash", {"command": "echo 'Hello, Research!'"})
    print(f"✓ Echo test: {result}")
    
    # Test file listing
    result = execute_tool("bash", {"command": "ls -la"})
    print(f"✓ List files: {result[:80]}...")
    
    # Test find command
    result = execute_tool("bash", {"command": "find . -name '*.py' | head -5"})
    print(f"✓ Find Python files: {result[:80]}...")
    
    # Test safety (dangerous command)
    result = execute_tool("bash", {"command": "rm -rf /"})
    print(f"✓ Safety test: {result}")


def test_read_file_tool():
    """Test file reading."""
    print("\n" + "="*60)
    print("Testing read_file tool...")
    print("="*60)
    
    # Test reading existing file
    result = execute_tool("read_file", {"path": "README.md", "limit": 5})
    print(f"✓ Read README (first 5 lines):\n{result}\n")
    
    # Test reading non-existent file
    result = execute_tool("read_file", {"path": "nonexistent.txt"})
    print(f"✓ Non-existent file: {result}")


def test_write_and_list_notes():
    """Test note writing and listing."""
    print("\n" + "="*60)
    print("Testing write_note and list_notes tools...")
    print("="*60)
    
    # Write a test note
    result = execute_tool("write_note", {
        "filename": "test-note.md",
        "content": "# Test Note\n\nThis is a test research note.\n\n## Findings\n- Point 1\n- Point 2\n\n## Conclusion\nEverything works!"
    })
    print(f"✓ Write note: {result}")
    
    # List notes
    result = execute_tool("list_notes", {})
    print(f"✓ List notes:\n{result}")
    
    # Read the note back
    result = execute_tool("read_file", {"path": "notes/test-note.md"})
    print(f"\n✓ Read note back:\n{result[:200]}...")


def test_safety():
    """Test security measures."""
    print("\n" + "="*60)
    print("Testing security measures...")
    print("="*60)
    
    # Test path escape attempt
    result = execute_tool("read_file", {"path": "../../../etc/passwd"})
    print(f"✓ Path escape blocked: {result}")
    
    # Test dangerous command
    result = execute_tool("bash", {"command": "sudo rm -rf /"})
    print(f"✓ Dangerous command blocked: {result}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Research Agent Tool Tests")
    print("="*60)
    print(f"Working directory: {WORKDIR}")
    
    try:
        test_bash_tool()
        test_read_file_tool()
        test_write_and_list_notes()
        test_safety()
        
        print("\n" + "="*60)
        print("✓ All tests completed!")
        print("="*60)
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your ANTHROPIC_API_KEY to .env")
        print("3. Run: python research-agent.py")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()