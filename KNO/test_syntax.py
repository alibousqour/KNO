#!/usr/bin/env python3
"""Test syntax of agent.py"""
import ast
try:
    with open('agent.py', 'r', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)
    print("[OK] agent.py syntax is valid")
    exit(0)
except SyntaxError as e:
    print(f"[SYNTAX_ERROR] Line {e.lineno}: {e.msg}")
    print(f"  {e.text}")
    exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)
