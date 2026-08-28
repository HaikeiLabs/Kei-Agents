"""Kei Agents - Agent definitions, tools, and prompts for Kei AI assistant platform.

This package provides:
- Tool definitions with multi-model format support (OpenAI, Anthropic, Ollama)
- System prompts and instructions
- Agent schemas for integration

Install: pip install kei-agents

Usage:
    from agents import TOOL_DEFINITIONS, render_tools, ModelFormat

    # Get tools for your model
    tools = render_tools(TOOL_DEFINITIONS, ModelFormat.OPENAI)
"""

from agents.tool_definitions import (
    TOOL_DEFINITIONS,
    ModelFormat,
    ToolDefinition,
    ToolParameter,
    detect_model_format,
    get_tool_by_name,
    get_tools_by_category,
    get_tools_by_permission,
    get_tools_for_model,
    render_anthropic_tools,
    render_ollama_tools,
    render_openai_tools,
    render_tools,
)

__version__ = "0.1.0"

__all__ = [
    "TOOL_DEFINITIONS",
    "ModelFormat",
    "ToolDefinition",
    "ToolParameter",
    "detect_model_format",
    "get_tool_by_name",
    "get_tools_by_category",
    "get_tools_by_permission",
    "get_tools_for_model",
    "render_anthropic_tools",
    "render_ollama_tools",
    "render_openai_tools",
    "render_tools",
]
