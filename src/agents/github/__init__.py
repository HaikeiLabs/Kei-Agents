"""GitHub tool definitions for agent integration.

This module provides tool definitions for GitHub operations:
- List issues and pull requests
- Create issues (with governance/approval workflow)
- Get workflow status

Each tool is permission-gated and can be integrated with actual
GitHub API via the provider-neutral GitHubAdapter interface.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class IssueState(str, Enum):
    """Issue state enum."""

    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


class IssuePriority(str, Enum):
    """Issue priority enum for governance."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueLabel(str, Enum):
    """Common issue labels."""

    BUG = "bug"
    ENHANCEMENT = "enhancement"
    QUESTION = "question"
    DOCUMENTATION = "documentation"
    PRIORITY_CRITICAL = "priority:critical"
    PRIORITY_HIGH = "priority:high"
    PRIORITY_MEDIUM = "priority:medium"
    PRIORITY_LOW = "priority:low"


@dataclass
class GitHubIssue:
    """GitHub issue data model."""

    id: int
    number: int
    title: str
    body: str | None
    state: IssueState
    labels: list[str] = field(default_factory=list)
    assignee: str | None = None
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    closed_at: datetime.datetime | None = None


@dataclass
class CreateIssueInput:
    """Input for creating a GitHub issue."""

    title: str
    body: str | None = None
    labels: list[str] = field(default_factory=list)
    assignee: str | None = None


@dataclass
class ApprovalInfo:
    """Governance approval information for issues."""

    approved: bool
    approver: str | None = None
    approved_at: datetime.datetime | None = None
    reason: str | None = None


class GitHubAdapterProtocol(Protocol):
    """Protocol for GitHub adapters (provider-neutral interface)."""

    def list_issues(
        self,
        state: IssueState = IssueState.OPEN,
        labels: list[str] | None = None,
        limit: int = 30,
    ) -> list[GitHubIssue]:
        """List GitHub issues."""
        ...

    def get_issue(self, issue_number: int) -> GitHubIssue | None:
        """Get a specific issue by number."""
        ...

    def create_issue(self, input: CreateIssueInput) -> GitHubIssue:
        """Create a new issue."""
        ...

    def list_pull_requests(
        self,
        state: str = "open",
        limit: int = 30,
    ) -> list[dict[str, object]]:
        """List pull requests."""
        ...

    def get_workflow_status(self, workflow_name: str) -> dict[str, object]:
        """Get workflow status."""
        ...


class MockGitHubAdapter:
    """Mock GitHub adapter with in-memory storage.

    This is a provider-neutral interface for development and testing.
    Replace with actual GitHub API adapter for production use.
    """

    def __init__(self) -> None:
        self._issues: dict[int, GitHubIssue] = {}
        self._next_id = 1
        self._next_number = 1

    def list_issues(
        self,
        state: IssueState = IssueState.OPEN,
        labels: list[str] | None = None,
        limit: int = 30,
    ) -> list[GitHubIssue]:
        issues = list(self._issues.values())
        if state != IssueState.ALL:
            issues = [i for i in issues if i.state == state]
        if labels:
            issues = [i for i in issues if any(label in i.labels for label in labels)]
        issues.sort(key=lambda x: x.created_at, reverse=True)
        return issues[:limit]

    def get_issue(self, issue_number: int) -> GitHubIssue | None:
        return self._issues.get(issue_number)

    def create_issue(self, input: CreateIssueInput) -> GitHubIssue:
        issue_id = self._next_id
        self._next_id += 1

        issue_number = self._next_number
        self._next_number += 1

        now = datetime.datetime.now(datetime.UTC)
        issue = GitHubIssue(
            id=issue_id,
            number=issue_number,
            title=input.title,
            body=input.body,
            state=IssueState.OPEN,
            labels=input.labels,
            assignee=input.assignee,
            created_at=now,
            updated_at=now,
        )

        self._issues[issue_number] = issue
        return issue

    def list_pull_requests(
        self,
        state: str = "open",
        limit: int = 30,
    ) -> list[dict[str, object]]:
        return []

    def get_workflow_status(self, workflow_name: str) -> dict[str, object]:
        return {
            "name": workflow_name,
            "status": "unknown",
            "conclusion": None,
        }

    def clear(self) -> None:
        self._issues.clear()
        self._next_id = 1
        self._next_number = 1


@dataclass
class GovernanceConfig:
    """Configuration for issue creation governance."""

    require_approval: bool = False
    auto_label_bugs: bool = True
    max_title_length: int = 256
    max_body_length: int = 65536


_github_adapter_instance: GitHubAdapterProtocol | None = None
_governance_config: GovernanceConfig = GovernanceConfig()


def _get_github_adapter() -> GitHubAdapterProtocol:
    global _github_adapter_instance
    if _github_adapter_instance is None:
        _github_adapter_instance = MockGitHubAdapter()
    return _github_adapter_instance


def set_github_adapter(adapter: GitHubAdapterProtocol) -> None:
    global _github_adapter_instance
    _github_adapter_instance = adapter


def set_governance_config(config: GovernanceConfig) -> None:
    global _governance_config
    _governance_config = config


def get_governance_config() -> GovernanceConfig:
    return _governance_config


def github_list_issues(
    state: str = "open",
    labels: str | None = None,
    limit: int = 30,
) -> dict[str, object]:
    """List GitHub issues.

    Args:
        state: Filter by issue state (open, closed, all)
        labels: Comma-separated list of labels to filter by
        limit: Maximum number of issues to return

    Returns:
        List of issues matching the criteria
    """
    adapter = _get_github_adapter()

    try:
        state_enum = IssueState(state)
    except ValueError:
        return {
            "error": f"Invalid state: {state}. Valid values: {[s.value for s in IssueState]}"
        }

    label_list = None
    if labels:
        label_list = [label.strip() for label in labels.split(",")]

    issues = adapter.list_issues(state=state_enum, labels=label_list, limit=limit)

    return {
        "issues": [
            {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state.value,
                "labels": issue.labels,
                "created_at": issue.created_at.isoformat(),
            }
            for issue in issues
        ],
        "total": len(issues),
    }


def github_create_issue(
    title: str,
    body: str | None = None,
    labels: str | None = None,
    assignee: str | None = None,
    auto_approve: bool = False,
) -> dict[str, object]:
    """Create a new GitHub issue with governance workflow.

    Args:
        title: Issue title (required)
        body: Issue body/description
        labels: Comma-separated list of labels
        assignee: Username to assign the issue to
        auto_approve: Skip approval for governance (use with caution)

    Returns:
        Created issue data or approval required response
    """
    config = get_governance_config()

    if len(title) > config.max_title_length:
        return {"error": f"Title exceeds maximum length of {config.max_title_length}"}

    if body and len(body) > config.max_body_length:
        return {"error": f"Body exceeds maximum length of {config.max_body_length}"}

    label_list = []
    if labels:
        label_list = [label.strip() for label in labels.split(",")]

    is_bug = IssueLabel.BUG.value in label_list
    if (
        is_bug
        and config.auto_label_bugs
        and IssueLabel.PRIORITY_CRITICAL.value not in label_list
    ):
        label_list.append(IssueLabel.PRIORITY_MEDIUM.value)

    if config.require_approval and not auto_approve and is_bug:
        return {
            "approval_required": True,
            "message": "Bug issues require approval before creation",
            "title": title,
            "labels": label_list,
        }

    adapter = _get_github_adapter()

    input_data = CreateIssueInput(
        title=title,
        body=body,
        labels=label_list,
        assignee=assignee,
    )

    issue = adapter.create_issue(input_data)

    return {
        "id": issue.id,
        "number": issue.number,
        "title": issue.title,
        "body": issue.body,
        "state": issue.state.value,
        "labels": issue.labels,
        "created_at": issue.created_at.isoformat(),
    }


def github_get_workflow_status(workflow_name: str) -> dict[str, object]:
    """Get CI/CD workflow status.

    Args:
        workflow_name: Name of the workflow

    Returns:
        Workflow status information
    """
    adapter = _get_github_adapter()
    return adapter.get_workflow_status(workflow_name)


def github_list_prs(
    state: str = "open",
    limit: int = 30,
) -> dict[str, object]:
    """List GitHub pull requests.

    Args:
        state: Filter by PR state (open, closed, all)
        limit: Maximum number of PRs to return

    Returns:
        List of pull requests
    """
    adapter = _get_github_adapter()
    prs = adapter.list_pull_requests(state=state, limit=limit)

    return {
        "pull_requests": prs,
        "total": len(prs),
    }


__all__ = [
    "ApprovalInfo",
    "CreateIssueInput",
    "GitHubAdapterProtocol",
    "GitHubIssue",
    "GovernanceConfig",
    "IssueLabel",
    "IssuePriority",
    "IssueState",
    "MockGitHubAdapter",
    "get_governance_config",
    "github_create_issue",
    "github_get_workflow_status",
    "github_list_issues",
    "github_list_prs",
    "set_github_adapter",
    "set_governance_config",
]
