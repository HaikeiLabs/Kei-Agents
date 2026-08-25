# Contributing to Kei Agents

We welcome contributions! Please follow these guidelines.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/kei-agents.git`
3. Install dev dependencies: `pip install -e ".[dev]"`

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run linter
ruff check .

# Run type checker
mypy src/agents

# Run tests
pytest
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass and code passes linting/type checking
4. Update documentation if needed
5. Submit a Pull Request
6. Wait for review from a maintainer

## Code Style

- Use Python 3.11+ features
- Follow PEP 8 (enforced by ruff)
- Use type hints
- Write docstrings for public functions

## Commit Messages

Use conventional commits:
- `feat: add new tool definition`
- `fix: correct parameter type`
- `docs: update README`
- `chore: update dependencies`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.