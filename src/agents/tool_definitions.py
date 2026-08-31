"""Tool definitions, rendering, and access metadata for Kei agents.

The lookup helpers retain the original module-global calling convention while
also accepting an explicit tool collection for CRM, GitHub, and policy use.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from typing import Any


class ModelFormat(str, Enum):
    """Supported model tool formats."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LLAMA = "llama"
    VLLM = "vllm"


class Permission(str, Enum):
    """Available permission scopes for tools."""

    SEARCH_WIKI = "search_wiki"
    WEB_SEARCH = "web_search"
    SCHEDULE_MEETINGS = "schedule_meetings"
    GITHUB_READ = "github_read"
    GITHUB_WRITE = "github_write"
    CRM_READ = "crm_read"
    CRM_WRITE = "crm_write"


class ToolCategory(str, Enum):
    """Tool categories for organization."""

    SEARCH = "search"
    PRODUCTIVITY = "productivity"
    GITHUB = "github"
    CRM = "crm"
    ENTERTAINMENT = "entertainment"


@dataclass
class ToolParameter:
    """A parameter in a tool schema."""

    name: str
    type: str = "string"
    description: str = ""
    required: bool = False
    enum: list[str] | None = None
    default: Any = None


@dataclass
class ToolDefinition:
    """Tool definition with optional policy and handler metadata."""

    name: str
    description: str
    parameters: list[ToolParameter] | dict[str, Any] | None = None
    permission: Permission = Permission.WEB_SEARCH
    category: ToolCategory = ToolCategory.SEARCH
    handler: Callable[..., Any] | None = None

    def __post_init__(self) -> None:
        if self.parameters is None:
            self.parameters = []


TOOL_DEFINITIONS: list[ToolDefinition] = []


def detect_model_format(model_name: str) -> ModelFormat:
    """Detect a rendering format from a model name."""
    name_lower = model_name.lower()
    if "claude" in name_lower:
        return ModelFormat.ANTHROPIC
    if "ollama" in name_lower:
        return ModelFormat.OLLAMA
    if "llama" in name_lower:
        return ModelFormat.LLAMA
    if "vllm" in name_lower:
        return ModelFormat.VLLM
    return ModelFormat.OPENAI


def _tool_parameters(tool: ToolDefinition) -> list[ToolParameter]:
    if isinstance(tool.parameters, dict):
        return [
            ToolParameter(
                name=name,
                type=value.get("type", "string"),
                description=value.get("description", ""),
                required=name in value.get("required", []),
            )
            for name, value in tool.parameters.get("properties", {}).items()
        ]
    return tool.parameters or []


def _render_openai_parameter(param: ToolParameter) -> dict[str, Any]:
    result: dict[str, Any] = {"type": param.type, "description": param.description}
    if param.enum:
        result["enum"] = param.enum
    return result


def render_openai_tools(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Render tools in OpenAI function-calling format."""
    result = []
    for tool in tools:
        schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        for param in _tool_parameters(tool):
            schema["properties"][param.name] = _render_openai_parameter(param)
            if param.required:
                schema["required"].append(param.name)
        result.append({"type": "function", "function": {
            "name": tool.name, "description": tool.description, "parameters": schema,
        }})
    return result


def render_anthropic_tools(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Render tools in Anthropic tool-use format."""
    result = []
    for tool in tools:
        schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        for param in _tool_parameters(tool):
            schema["properties"][param.name] = _render_openai_parameter(param)
            if param.required:
                schema["required"].append(param.name)
        result.append({"name": tool.name, "description": tool.description, "input_schema": schema})
    return result


def render_ollama_tools(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Render tools in Ollama's OpenAI-compatible format."""
    return render_openai_tools(tools)


def render_tools(tools: list[ToolDefinition], model: str | ModelFormat) -> list[dict[str, Any]]:
    """Render tools in the format selected by a model name or enum."""
    format_type = detect_model_format(model) if isinstance(model, str) else model
    if format_type == ModelFormat.ANTHROPIC:
        return render_anthropic_tools(tools)
    if format_type == ModelFormat.OLLAMA:
        return render_ollama_tools(tools)
    return render_openai_tools(tools)


def get_tool_by_name(
    tools_or_name: list[ToolDefinition] | str, name: str | None = None
) -> ToolDefinition | None:
    tools = ALL_TOOL_DEFINITIONS if isinstance(tools_or_name, str) else tools_or_name
    wanted = tools_or_name if isinstance(tools_or_name, str) else name
    return next((tool for tool in tools if tool.name == wanted), None)


def get_tools_by_category(
    category_or_tools: str | ToolCategory | list[ToolDefinition],
    category: str | ToolCategory | None = None,
) -> list[ToolDefinition]:
    tools = ALL_TOOL_DEFINITIONS if not isinstance(category_or_tools, list) else category_or_tools
    wanted = category_or_tools if not isinstance(category_or_tools, list) else category
    return [tool for tool in tools if tool.category == wanted or tool.category.value == wanted]


def get_tools_by_permission(
    permission_or_tools: str | Permission | list[ToolDefinition],
    permission: str | Permission | None = None,
) -> list[ToolDefinition]:
    tools = ALL_TOOL_DEFINITIONS if not isinstance(permission_or_tools, list) else permission_or_tools
    wanted = permission_or_tools if not isinstance(permission_or_tools, list) else permission
    return [tool for tool in tools if tool.permission == wanted or tool.permission.value == wanted]


def get_tools_for_model(
    tools_or_model: list[ToolDefinition] | str | ModelFormat,
    model: str | ModelFormat | None = None,
) -> list[ToolDefinition] | list[dict[str, Any]]:
    if isinstance(tools_or_model, list):
        return render_tools(tools_or_model, model or ModelFormat.OPENAI)
    return TOOL_DEFINITIONS


CRM_TOOL_DEFINITIONS = import_module("agents.crm.tools").CRM_TOOL_DEFINITIONS
GITHUB_TOOL_DEFINITIONS = import_module("agents.github.tools").GITHUB_TOOL_DEFINITIONS

ALL_TOOL_DEFINITIONS = TOOL_DEFINITIONS + CRM_TOOL_DEFINITIONS + GITHUB_TOOL_DEFINITIONS
