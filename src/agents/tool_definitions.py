from enum import Enum
from typing import Any


class ModelFormat(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class ToolDefinition:
    def __init__(
        self, name: str, description: str, parameters: dict[str, Any] | None = None
    ):
        self.name = name
        self.description = description
        self.parameters = parameters or {}


class ToolParameter:
    def __init__(self, name: str, type: str, description: str, required: bool = False):
        self.name = name
        self.type = type
        self.description = description
        self.required = required


TOOL_DEFINITIONS: list[ToolDefinition] = []


def detect_model_format(model: str) -> ModelFormat:
    if "claude" in model.lower():
        return ModelFormat.ANTHROPIC
    if "ollama" in model.lower():
        return ModelFormat.OLLAMA
    return ModelFormat.OPENAI


def get_tool_by_name(name: str) -> ToolDefinition | None:
    for tool in TOOL_DEFINITIONS:
        if tool.name == name:
            return tool
    return None


def get_tools_by_category(category: str) -> list[ToolDefinition]:
    return []


def get_tools_by_permission(permission: str) -> list[ToolDefinition]:
    return []


def get_tools_for_model(model: str) -> list[ToolDefinition]:
    return TOOL_DEFINITIONS


def render_tools(
    tools: list[ToolDefinition], format: ModelFormat
) -> list[dict[str, Any]]:
    return [{"name": t.name, "description": t.description} for t in tools]


def render_anthropic_tools(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
    return render_tools(tools, ModelFormat.ANTHROPIC)


def render_openai_tools(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
    return render_tools(tools, ModelFormat.OPENAI)


def render_ollama_tools(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
    return render_tools(tools, ModelFormat.OLLAMA)
