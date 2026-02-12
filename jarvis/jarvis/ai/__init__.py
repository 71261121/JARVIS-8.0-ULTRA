"""
JARVIS AI Module
================

Purpose: AI engine for question generation and assistance.

Components:
- llama.cpp integration for local LLM
- DeepSeek-R1:1.5B model interface
- Question generation pipeline
- Response caching

Requirements:
- llama.cpp binary compiled
- DeepSeek model downloaded (Q4_K_M, ~1GB)

Reason for local AI:
- No internet needed during study
- No API costs
- Privacy preserved
- Works on mobile with 4GB+ RAM
"""

# Module status
AI_AVAILABLE = False

try:
    # Check if dependencies are available
    import subprocess
    result = subprocess.run(["which", "llama-cli"], capture_output=True)
    if result.returncode == 0:
        AI_AVAILABLE = True
except Exception:
    pass

__all__ = [
    "AI_AVAILABLE",
    "QuestionGenerator",
    "ResponseCache",
]
