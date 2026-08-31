"""CRM module for lead management.

This module provides:
- Mock CRM database adapter with in-memory storage
- Lead data models and operations
- Provider-neutral interfaces for CRM operations

Usage:
    from agents.crm import CRMAdapter, Lead, LeadStatus

    adapter = CRMAdapter()
    leads = adapter.list_leads()
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class LeadStatus(str, Enum):
    """Lead status enum."""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    WON = "won"
    LOST = "lost"


class LeadSource(str, Enum):
    """Lead source enum."""

    WEB = "web"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    EVENT = "event"
    OTHER = "other"


@dataclass
class Lead:
    """Lead data model."""

    id: str
    email: str
    name: str
    company: str | None = None
    phone: str | None = None
    status: LeadStatus = LeadStatus.NEW
    source: LeadSource = LeadSource.OTHER
    notes: str | None = None
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


@dataclass
class CreateLeadInput:
    """Input for creating a lead."""

    email: str
    name: str
    company: str | None = None
    phone: str | None = None
    source: LeadSource = LeadSource.OTHER
    notes: str | None = None


@dataclass
class UpdateLeadInput:
    """Input for updating a lead."""

    email: str | None = None
    name: str | None = None
    company: str | None = None
    phone: str | None = None
    status: LeadStatus | None = None
    notes: str | None = None


class CRMAdapterProtocol(Protocol):
    """Protocol for CRM adapters (provider-neutral interface)."""

    def get_lead(self, lead_id: str) -> Lead | None:
        """Get a lead by ID."""
        ...

    def get_lead_by_email(self, email: str) -> Lead | None:
        """Get a lead by email address."""
        ...

    def list_leads(
        self,
        status: LeadStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        """List leads with optional filtering."""
        ...

    def create_lead(self, input: CreateLeadInput) -> Lead:
        """Create a new lead."""
        ...

    def update_lead(self, lead_id: str, input: UpdateLeadInput) -> Lead | None:
        """Update an existing lead."""
        ...

    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead by ID."""
        ...


class CRMAdapter:
    """Mock CRM database adapter with in-memory storage.

    This is a provider-neutral interface that can be replaced with
    actual CRM integrations (Salesforce, HubSpot, etc.) by implementing
    the CRMAdapterProtocol.
    """

    def __init__(self) -> None:
        """Initialize the mock CRM adapter."""
        self._leads: dict[str, Lead] = {}
        self._email_index: dict[str, str] = {}
        self._next_id = 1

    def get_lead(self, lead_id: str) -> Lead | None:
        """Get a lead by ID."""
        return self._leads.get(lead_id)

    def get_lead_by_email(self, email: str) -> Lead | None:
        """Get a lead by email address."""
        lead_id = self._email_index.get(email.lower())
        if lead_id:
            return self._leads.get(lead_id)
        return None

    def list_leads(
        self,
        status: LeadStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        """List leads with optional filtering."""
        leads = list(self._leads.values())
        if status:
            leads = [lead for lead in leads if lead.status == status]
        leads.sort(key=lambda x: x.created_at, reverse=True)
        return leads[offset : offset + limit]

    def create_lead(self, input: CreateLeadInput) -> Lead:
        """Create a new lead."""
        if self.get_lead_by_email(input.email):
            raise ValueError(f"Lead with email {input.email} already exists")

        lead_id = f"lead_{self._next_id}"
        self._next_id += 1

        now = datetime.datetime.now(datetime.UTC)
        lead = Lead(
            id=lead_id,
            email=input.email,
            name=input.name,
            company=input.company,
            phone=input.phone,
            status=LeadStatus.NEW,
            source=input.source,
            notes=input.notes,
            created_at=now,
            updated_at=now,
        )

        self._leads[lead_id] = lead
        self._email_index[input.email.lower()] = lead_id

        return lead

    def update_lead(self, lead_id: str, input: UpdateLeadInput) -> Lead | None:
        """Update an existing lead."""
        lead = self._leads.get(lead_id)
        if not lead:
            return None

        if input.email and input.email.lower() != lead.email.lower():
            old_email = lead.email.lower()
            if self._email_index.get(old_email) == lead_id:
                del self._email_index[old_email]
            self._email_index[input.email.lower()] = lead_id
            lead.email = input.email

        if input.name is not None:
            lead.name = input.name
        if input.company is not None:
            lead.company = input.company
        if input.phone is not None:
            lead.phone = input.phone
        if input.status is not None:
            lead.status = input.status
        if input.notes is not None:
            lead.notes = input.notes

        lead.updated_at = datetime.datetime.now(datetime.UTC)

        return lead

    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead by ID."""
        lead = self._leads.pop(lead_id, None)
        if lead:
            self._email_index.pop(lead.email.lower(), None)
            return True
        return False

    def clear(self) -> None:
        """Clear all leads (for testing)."""
        self._leads.clear()
        self._email_index.clear()
        self._next_id = 1


__all__ = [
    "CRMAdapter",
    "CRMAdapterProtocol",
    "CreateLeadInput",
    "Lead",
    "LeadSource",
    "LeadStatus",
    "UpdateLeadInput",
]
