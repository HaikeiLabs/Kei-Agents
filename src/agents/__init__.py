"""Kei Agents - Agent definitions, tools, and prompts for Kei AI assistant platform.

This package provides:
- Tool definitions with multi-model format support (OpenAI, Anthropic, Ollama)
- CRM tools for lead management (mock adapter)
- GitHub tools for issue/PR management (with governance)
- Permission-based access control

Install: pip install kei-agents

Usage:
    from agents import TOOL_DEFINITIONS, render_tools, ModelFormat
    tools = render_tools(TOOL_DEFINITIONS, ModelFormat.OPENAI)
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

__all__ = [
    "ALL_TOOL_DEFINITIONS",
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
