"""CRM tool definitions for agent integration.

This module provides tool definitions for CRM operations:
- Lead lookup (by ID or email)
- Lead creation
- Lead updates

Each tool is permission-gated and follows provider-neutral patterns.
"""

from __future__ import annotations

from agents.crm import (
    CreateLeadInput,
    CRMAdapter,
    LeadSource,
    LeadStatus,
    UpdateLeadInput,
)
from agents.tool_definitions import (
    Permission,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
)

_crm_adapter_instance: CRMAdapter | None = None


def _get_crm_adapter() -> CRMAdapter:
    """Get or create CRM adapter instance."""
    global _crm_adapter_instance
    if _crm_adapter_instance is None:
        _crm_adapter_instance = CRMAdapter()
    return _crm_adapter_instance


def set_crm_adapter(adapter: CRMAdapter) -> None:
    """Set the CRM adapter instance (for testing)."""
    global _crm_adapter_instance
    _crm_adapter_instance = adapter


def reset_crm_adapter() -> None:
    """Reset the CRM adapter (for testing)."""
    global _crm_adapter_instance
    _crm_adapter_instance = None


def crm_lookup_lead(
    lead_id: str | None = None, email: str | None = None
) -> dict[str, object]:
    """Look up a lead by ID or email address.

    Args:
        lead_id: The unique identifier of the lead
        email: The email address of the lead

    Returns:
        Lead data if found, or error message
    """
    adapter = _get_crm_adapter()

    if not lead_id and not email:
        return {"error": "Either lead_id or email must be provided"}

    if lead_id:
        lead = adapter.get_lead(lead_id)
    elif email:
        lead = adapter.get_lead_by_email(email)
    else:
        lead = None

    if not lead:
        return {"error": "Lead not found"}

    return {
        "id": lead.id,
        "email": lead.email,
        "name": lead.name,
        "company": lead.company,
        "phone": lead.phone,
        "status": lead.status.value,
        "source": lead.source.value,
        "notes": lead.notes,
        "created_at": lead.created_at.isoformat(),
        "updated_at": lead.updated_at.isoformat(),
    }


def crm_list_leads(
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, object]:
    """List leads with optional filtering.

    Args:
        status: Filter by lead status (new, contacted, qualified, proposal, won, lost)
        limit: Maximum number of leads to return
        offset: Number of leads to skip

    Returns:
        List of leads matching the criteria
    """
    adapter = _get_crm_adapter()

    status_enum = None
    if status:
        try:
            status_enum = LeadStatus(status)
        except ValueError:
            return {
                "error": f"Invalid status: {status}. Valid values: {[s.value for s in LeadStatus]}"
            }

    leads = adapter.list_leads(status=status_enum, limit=limit, offset=offset)

    return {
        "leads": [
            {
                "id": lead.id,
                "email": lead.email,
                "name": lead.name,
                "company": lead.company,
                "status": lead.status.value,
                "created_at": lead.created_at.isoformat(),
            }
            for lead in leads
        ],
        "total": len(leads),
    }


def crm_create_lead(
    email: str,
    name: str,
    company: str | None = None,
    phone: str | None = None,
    source: str = "other",
    notes: str | None = None,
) -> dict[str, object]:
    """Create a new lead in the CRM.

    Args:
        email: Email address of the lead (required)
        name: Full name of the lead (required)
        company: Company name
        phone: Phone number
        source: Lead source (web, referral, cold_call, event, other)
        notes: Additional notes about the lead

    Returns:
        Created lead data or error message
    """
    adapter = _get_crm_adapter()

    try:
        source_enum = LeadSource(source)
    except ValueError:
        return {
            "error": f"Invalid source: {source}. Valid values: {[s.value for s in LeadSource]}"
        }

    try:
        input_data = CreateLeadInput(
            email=email,
            name=name,
            company=company,
            phone=phone,
            source=source_enum,
            notes=notes,
        )
        lead = adapter.create_lead(input_data)

        return {
            "id": lead.id,
            "email": lead.email,
            "name": lead.name,
            "company": lead.company,
            "phone": lead.phone,
            "status": lead.status.value,
            "source": lead.source.value,
            "notes": lead.notes,
            "created_at": lead.created_at.isoformat(),
        }
    except ValueError as e:
        return {"error": str(e)}


def crm_update_lead(
    lead_id: str,
    email: str | None = None,
    name: str | None = None,
    company: str | None = None,
    phone: str | None = None,
    status: str | None = None,
    notes: str | None = None,
) -> dict[str, object]:
    """Update an existing lead in the CRM.

    Args:
        lead_id: The unique identifier of the lead to update
        email: New email address
        name: New name
        company: New company name
        phone: New phone number
        status: New status (new, contacted, qualified, proposal, won, lost)
        notes: Updated notes

    Returns:
        Updated lead data or error message
    """
    adapter = _get_crm_adapter()

    status_enum = None
    if status:
        try:
            status_enum = LeadStatus(status)
        except ValueError:
            return {
                "error": f"Invalid status: {status}. Valid values: {[s.value for s in LeadStatus]}"
            }

    input_data = UpdateLeadInput(
        email=email,
        name=name,
        company=company,
        phone=phone,
        status=status_enum,
        notes=notes,
    )

    lead = adapter.update_lead(lead_id, input_data)

    if not lead:
        return {"error": f"Lead not found: {lead_id}"}

    return {
        "id": lead.id,
        "email": lead.email,
        "name": lead.name,
        "company": lead.company,
        "phone": lead.phone,
        "status": lead.status.value,
        "notes": lead.notes,
        "updated_at": lead.updated_at.isoformat(),
    }


CRM_TOOL_DEFINITIONS: list[ToolDefinition] = [
    ToolDefinition(
        name="crm_lookup_lead",
        description="Look up a lead by ID or email address",
        parameters=[
            ToolParameter(
                name="lead_id",
                description="The unique identifier of the lead",
                required=False,
            ),
            ToolParameter(
                name="email",
                description="The email address of the lead",
                required=False,
            ),
        ],
        permission=Permission.CRM_READ,
        category=ToolCategory.CRM,
        handler=crm_lookup_lead,
    ),
    ToolDefinition(
        name="crm_list_leads",
        description="List leads with optional filtering by status",
        parameters=[
            ToolParameter(
                name="status",
                description="Filter by lead status (new, contacted, qualified, proposal, won, lost)",
                required=False,
                enum=["new", "contacted", "qualified", "proposal", "won", "lost"],
            ),
            ToolParameter(
                name="limit",
                description="Maximum number of leads to return",
                type="integer",
                required=False,
                default=100,
            ),
            ToolParameter(
                name="offset",
                description="Number of leads to skip",
                type="integer",
                required=False,
                default=0,
            ),
        ],
        permission=Permission.CRM_READ,
        category=ToolCategory.CRM,
        handler=crm_list_leads,
    ),
    ToolDefinition(
        name="crm_create_lead",
        description="Create a new lead in the CRM",
        parameters=[
            ToolParameter(
                name="email",
                description="Email address of the lead (required)",
                required=True,
            ),
            ToolParameter(
                name="name",
                description="Full name of the lead (required)",
                required=True,
            ),
            ToolParameter(
                name="company",
                description="Company name",
                required=False,
            ),
            ToolParameter(
                name="phone",
                description="Phone number",
                required=False,
            ),
            ToolParameter(
                name="source",
                description="Lead source",
                required=False,
                enum=["web", "referral", "cold_call", "event", "other"],
                default="other",
            ),
            ToolParameter(
                name="notes",
                description="Additional notes about the lead",
                required=False,
            ),
        ],
        permission=Permission.CRM_WRITE,
        category=ToolCategory.CRM,
        handler=crm_create_lead,
    ),
    ToolDefinition(
        name="crm_update_lead",
        description="Update an existing lead in the CRM",
        parameters=[
            ToolParameter(
                name="lead_id",
                description="The unique identifier of the lead to update",
                required=True,
            ),
            ToolParameter(
                name="email",
                description="New email address",
                required=False,
            ),
            ToolParameter(
                name="name",
                description="New name",
                required=False,
            ),
            ToolParameter(
                name="company",
                description="New company name",
                required=False,
            ),
            ToolParameter(
                name="phone",
                description="New phone number",
                required=False,
            ),
            ToolParameter(
                name="status",
                description="New status",
                required=False,
                enum=["new", "contacted", "qualified", "proposal", "won", "lost"],
            ),
            ToolParameter(
                name="notes",
                description="Updated notes",
                required=False,
            ),
        ],
        permission=Permission.CRM_WRITE,
        category=ToolCategory.CRM,
        handler=crm_update_lead,
    ),
]


__all__ = [
    "CRM_TOOL_DEFINITIONS",
    "crm_create_lead",
    "crm_list_leads",
    "crm_lookup_lead",
    "crm_update_lead",
    "set_crm_adapter",
]
