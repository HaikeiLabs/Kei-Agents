"""Provider-neutral read tool schemas for the governed Google Drive/Docs connector.

Read capabilities are scoped to the Drive bound in the governed connection
preset (delegated context); agents can never target arbitrary drives or supply
URLs/credentials. Execution is delegated to the tenant-side distributed proxy
- these schemas declare no handlers.
"""

from __future__ import annotations

from agents.tool_definitions import (
    Permission,
    ToolBinding,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
)

DRIVE_READ_TOOL_DEFINITIONS: list[ToolDefinition] = [
    ToolDefinition(
        name="drive.list_files",
        description="List files in the governed Drive",
        parameters=[
            ToolParameter(
                name="query",
                description="Search query applied within the governed Drive",
                required=False,
            ),
            ToolParameter(
                name="mime_type",
                description="Filter by MIME type (e.g. text/plain)",
                required=False,
            ),
            ToolParameter(
                name="limit",
                description="Maximum number of files to return",
                type="integer",
                required=False,
                default=50,
            ),
        ],
        permission=Permission.DRIVE_READ,
        category=ToolCategory.DRIVE,
        service="drive",
        tags=["drive-read", "governed-connector"],
        binding=ToolBinding(
            connector_id="conn_drive_1",
            config={"resource": "files"},
            delegated_context=["tenant_id", "drive_id"],
        ),
    ),
    ToolDefinition(
        name="drive.get_file",
        description="Read metadata for a single file in the governed Drive",
        parameters=[
            ToolParameter(
                name="file_id",
                description="File identifier within the governed Drive",
                required=True,
            ),
        ],
        permission=Permission.DRIVE_READ,
        category=ToolCategory.DRIVE,
        service="drive",
        tags=["drive-read", "governed-connector"],
        binding=ToolBinding(
            connector_id="conn_drive_1",
            config={"resource": "files"},
            delegated_context=["tenant_id", "drive_id"],
        ),
    ),
    ToolDefinition(
        name="docs.get_document",
        description="Read a document's content from the governed Docs workspace",
        parameters=[
            ToolParameter(
                name="document_id",
                description="Document identifier within the governed Docs workspace",
                required=True,
            ),
            ToolParameter(
                name="plain_text",
                description="Return plain text instead of structured content",
                type="boolean",
                required=False,
                default=True,
            ),
        ],
        permission=Permission.DRIVE_READ,
        category=ToolCategory.DRIVE,
        service="drive",
        tags=["drive-read", "governed-connector"],
        binding=ToolBinding(
            connector_id="conn_drive_1",
            config={"resource": "documents"},
            delegated_context=["tenant_id", "drive_id"],
        ),
    ),
]

__all__ = ["DRIVE_READ_TOOL_DEFINITIONS"]
