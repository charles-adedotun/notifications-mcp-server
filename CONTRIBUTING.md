# Contributing to Claude Notification Server

Thank you for your interest in contributing to this project! This document outlines the process for contributing and guidelines to follow.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a new branch** for your contribution
4. **Make your changes**
5. **Test your changes**
6. **Submit a pull request**

## Development Environment Setup

1. Ensure you have Python 3.8 or higher installed
2. Install development dependencies:
   ```bash
   uv pip install fastmcp pytest pytest-cov
   ```
   
3. Run the server locally:
   ```bash
   python server.py
   ```

## Code Style and Guidelines

- Follow PEP 8 guidelines for Python code
- Include docstrings for all functions, classes, and modules
- Use type hints where applicable
- Keep functions focused and modular
- Add appropriate logging for debugging
- Add tests for new functionality

## Pull Request Guidelines

1. **Create focused PRs**: Each PR should address a single issue or feature
2. **Include tests**: Add tests for new features or bug fixes
3. **Update documentation**: If your changes affect how users interact with the project, update the README
4. **Describe your changes**: Provide a clear description of what your PR accomplishes
5. **Link related issues**: Reference any issues your PR addresses

## Testing

Before submitting a PR, make sure all tests pass:

```bash
pytest
```

## Feature Requests and Bug Reports

Please use GitHub Issues to report bugs or request features. When reporting a bug, include:

1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. System information (macOS version, Python version)
5. Any relevant logs or error messages

## Cross-Platform Considerations

This project currently only supports macOS. If you're interested in adding support for other platforms:

1. Create a platform-specific sound management class
2. Ensure platform detection and appropriate fallbacks
3. Update documentation to reflect multi-platform support

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
