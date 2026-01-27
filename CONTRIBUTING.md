# Contributing to AUTO-blogger

Thank you for your interest in contributing to AUTO-blogger! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all backgrounds and experience levels.

## Getting Started

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AUTO-blogger.git
   cd AUTO-blogger
   ```

2. **Run the development setup:**
   ```bash
   # On macOS/Linux
   ./setup.sh --dev

   # On Windows
   setup.bat --dev
   # or
   .\setup.ps1 -Mode dev
   ```

3. **Activate the virtual environment:**
   ```bash
   # On macOS/Linux
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Using the Makefile

Common development tasks are available via Make:

```bash
make help          # Show all available commands
make dev-setup     # Set up development environment
make test          # Run tests
make lint          # Run linters
make format        # Format code
make build         # Build distribution packages
```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions/changes

### Commit Messages

We use conventional commits. Format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(gui): add dark mode toggle
fix(api): handle WordPress connection timeout
docs(readme): update installation instructions
```

### Code Style

- **Python:** We use Black for formatting and flake8 for linting
- **Line length:** 100 characters maximum
- **Imports:** Use isort for organizing imports

Run before committing:
```bash
make format
make lint
```

### Testing

All new features should include tests. Run tests with:

```bash
make test          # Run all tests
make test-cov      # Run with coverage report
make test-fast     # Skip slow tests
```

Test file structure:
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests

### Type Hints

We support type hints. Add type annotations to new code:

```python
def process_article(article: dict, config: Config) -> bool:
    """Process an article for publishing."""
    ...
```

## Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** with appropriate tests
3. **Run the full test suite:** `make test`
4. **Run linting:** `make lint`
5. **Update documentation** if needed
6. **Submit a pull request** with a clear description

### PR Checklist

- [ ] Code follows the project style guide
- [ ] Tests pass locally
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

## Project Structure

```
AUTO-blogger/
├── auto_blogger/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── automation_engine.py # Core automation logic
│   ├── gui_blogger.py      # GUI application
│   ├── cli.py              # CLI interface
│   ├── log_manager.py      # Logging utilities
│   ├── css_selector_extractor.py # CSS selector detection
│   └── configs/            # Configuration files
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── requirements/           # Dependency files
│   ├── base.txt            # Core dependencies
│   ├── dev.txt             # Development dependencies
│   └── test.txt            # Test dependencies
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── website/                # GitHub Pages site
```

## Reporting Issues

When reporting issues, please include:

1. **Description:** Clear description of the problem
2. **Steps to reproduce:** How to trigger the issue
3. **Expected behavior:** What should happen
4. **Actual behavior:** What actually happens
5. **Environment:** OS, Python version, package version
6. **Logs:** Relevant error messages or logs

## Feature Requests

For feature requests:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** - why is this needed?
3. **Propose a solution** if you have one
4. **Be open to discussion** about implementation

## Questions?

- Open an issue with the `question` label
- Check existing documentation in `/docs`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to AUTO-blogger!
