"""Kei Agents - Agent definitions, tools, and prompts for Kei AI assistant platform.

This package provides:
- Tool definitions with multi-model format support (OpenAI, Anthropic, Ollama)
- Provider-neutral read schemas for governed connectors (GitHub, Linear,
  Google Drive/Docs, S3, http_api/CRM, Notion)
- CRM tools for lead management (mock adapter)
- GitHub tools for issue/PR management (with governance)
- Permission-based access control
- Harness-neutral workflow registry for discovering workflows by tool or
  connector dependency

Install: pip install kei-agents

Usage:
    from agents import TOOL_DEFINITIONS, render_tools, ModelFormat
    tools = render_tools(TOOL_DEFINITIONS, ModelFormat.OPENAI)

    from agents import WorkflowRegistry
    registry = WorkflowRegistry.get_default()
    workflows = registry.discover_by_tool("github.get_repository")
"""

from agents.crm import (
    CRMAdapter,
    Lead,
    LeadSource,
    LeadStatus,
)
from agents.github import (
    GovernanceConfig,
    MockGitHubAdapter,
)
from agents.policy import (
    AuthorizationResult,
    PermissionContext,
    PolicyDecision,
    PolicyEngine,
    check_tool_access,
    create_user_context,
    filter_accessible_tools,
)
from agents.tool_definitions import (
    ALL_TOOL_DEFINITIONS,
    TOOL_DEFINITIONS,
    ModelFormat,
    Permission,
    ToolBinding,
    ToolCategory,
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
    validate_tool_definitions,
)

__version__ = "0.1.0"

# Imported after tool_definitions so its bottom-of-module import of this
# package resolves without a circular import.
from agents.connectors import (
    CONNECTOR_READ_TOOL_DEFINITIONS,
    DRIVE_READ_TOOL_DEFINITIONS,
    GITHUB_READ_TOOL_DEFINITIONS,
    HTTP_API_READ_TOOL_DEFINITIONS,
    LINEAR_READ_TOOL_DEFINITIONS,
    NOTION_READ_TOOL_DEFINITIONS,
    S3_READ_TOOL_DEFINITIONS,
)

# Imported after connectors so the workflow registry's module-level
# _register_builtin_workflows() sees the full CONNECTOR_READ_TOOL_DEFINITIONS
# list.
from agents.workflow_registry import (
    WorkflowManifest,
    WorkflowRegistry,
)

__all__ = [
    "ALL_TOOL_DEFINITIONS",
    "CONNECTOR_READ_TOOL_DEFINITIONS",
    "DRIVE_READ_TOOL_DEFINITIONS",
    "GITHUB_READ_TOOL_DEFINITIONS",
    "HTTP_API_READ_TOOL_DEFINITIONS",
    "LINEAR_READ_TOOL_DEFINITIONS",
    "NOTION_READ_TOOL_DEFINITIONS",
    "S3_READ_TOOL_DEFINITIONS",
    "TOOL_DEFINITIONS",
    "AuthorizationResult",
    "CRMAdapter",
    "GovernanceConfig",
    "Lead",
    "LeadSource",
    "LeadStatus",
    "MockGitHubAdapter",
    "ModelFormat",
    "Permission",
    "PermissionContext",
    "PolicyDecision",
    "PolicyEngine",
    "ToolBinding",
    "ToolCategory",
    "ToolDefinition",
    "ToolParameter",
    "WorkflowManifest",
    "WorkflowRegistry",
    "check_tool_access",
    "create_user_context",
    "detect_model_format",
    "filter_accessible_tools",
    "get_tool_by_name",
    "get_tools_by_category",
    "get_tools_by_permission",
    "get_tools_for_model",
    "render_anthropic_tools",
    "render_ollama_tools",
    "render_openai_tools",
    "render_tools",
    "validate_tool_definitions",
]
