# Kei Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/HaikeiLabs/kei-agents/actions/workflows/tests.yaml/badge.svg)](https://github.com/HaikeiLabs/kei-agents/actions/workflows/tests.yaml)
[![Dependency Review](https://github.com/HaikeiLabs/kei-agents/actions/workflows/security.yaml/badge.svg)](https://github.com/HaikeiLabs/kei-agents/actions/workflows/security.yaml)

Agent definitions, tools, and prompts for the Kei AI assistant platform.

## Installation

```bash
pip install kei-agents
```

> **Note**: PyPI publication is planned. See the [PyPI Distribution Plan](docs/pypi-distribution-plan.md) for the release timeline.

## Quick Start

```python
from agents import TOOL_DEFINITIONS, render_tools, ModelFormat

# Get tools in OpenAI format
tools = render_tools(TOOL_DEFINITIONS, ModelFormat.OPENAI)

# Or detect automatically from model name
tools = render_tools(TOOL_DEFINITIONS, "gpt-4")
```

## Features

- **Multi-model support**: OpenAI, Anthropic, Ollama, Llama, vLLM
- **Tool definitions**: Pre-built tool schemas for common operations
- **Permission-based access**: Tools gated by permissions
- **Category organization**: Tools organized by category

## Available Tools

| Tool | Description | Permission |
|------|-------------|------------|
| search_wiki | Search conversation history | search_wiki |
| web_search | Search the web for current info | web_search |
| schedule_meeting | Schedule calendar meetings | schedule_meetings |
| list_prs | List GitHub pull requests | github_read |
| list_issues | List GitHub issues | github_read |
| create_issue | Create GitHub issues | github_write |
| get_workflow_status | Get CI/CD workflow status | github_read |
| create_pull_request | Create PRs | github_write |
| start_game | Start interactive games | search_wiki |

See `src/agents/tool_definitions.py` for full list.

## Development

```bash
# Clone repository
git clone https://github.com/HaikeiLabs/kei-agents.git
cd kei-agents

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Type check
mypy src/agents
```

## Security

- Dependency vulnerabilities scanned weekly via `pip-audit`
- Dependency review on all PRs
- See [Security Policy](SECURITY.md)

## Distribution

For details on PyPI distribution, release process, and container registry strategy, see the [PyPI Distribution Plan](docs/pypi-distribution-plan.md).

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

All contributors must be approved by existing maintainers. See [CONTRIBUTORS](CONTRIBUTORS).

### Design Documents

- [npm Distribution Strategy](docs/npm-distribution-strategy.md) - proposal for publishing a JS/TypeScript consumable, plus Go distribution as a separate workstream (not approved)

## License

MIT License - see [LICENSE](LICENSE).

## Links

- [GitHub](https://github.com/HaikeiLabs/kei-agents)
- [Issues](https://github.com/HaikeiLabs/kei-agents/issues)