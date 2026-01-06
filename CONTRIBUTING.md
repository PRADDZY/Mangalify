# Contributing to Mangalify

Thank you for considering contributing to Mangalify! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Report unacceptable behavior to project maintainers

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Mangalify.git
   cd Mangalify
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/PRADDZY/Mangalify.git
   ```

## Development Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install flake8 pytest pytest-asyncio
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

4. **Set up MongoDB**:
   - Install MongoDB locally or use Docker:
     ```bash
     docker run -d -p 27017:27017 --name test-mongo mongo:7.0
     ```

## Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the existing code structure
   - Add docstrings to new functions/classes
   - Update type hints where applicable

3. **Keep commits focused**:
   - Each commit should represent a single logical change
   - Write clear commit messages (see [Commit Guidelines](#commit-guidelines))

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_wishes_flows.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_<feature>_<scenario>`
- Mock external dependencies (Discord API, databases, external APIs)
- Use `pytest.mark.asyncio` for async tests

**Example test structure**:
```python
@pytest.mark.asyncio
async def test_birthday_announcement_success():
    """Test successful birthday announcement with all mocks."""
    # Arrange
    mock_bot = AsyncMock()
    # ... setup mocks
    
    # Act
    result = await cog._check_for_birthdays(today)
    
    # Assert
    assert result == 1
    mock_channel.send.assert_called_once()
```

## Code Style

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Maximum line length: **120 characters**
- Use **4 spaces** for indentation (no tabs)
- Use **snake_case** for functions/variables
- Use **PascalCase** for classes

### Linting

```bash
# Run flake8
python -m flake8 .

# Fix common issues automatically (optional)
autopep8 --in-place --aggressive --aggressive <file>
```

### Type Hints

Use type hints for function signatures:

```python
async def get_birthdays_for_date(day: int, month: int) -> AsyncGenerator:
    """Fetch birthdays for specific date."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
async def send_wish(channel: discord.TextChannel, message: str) -> bool:
    """Send a wish message to a Discord channel.
    
    Args:
        channel: The Discord text channel to send to
        message: The wish message content
        
    Returns:
        True if message sent successfully, False otherwise
        
    Raises:
        discord.HTTPException: If message sending fails
    """
    ...
```

## Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat: Add holiday approval mode with /holiday_post command

- Implemented HOLIDAY_APPROVAL_MODE environment variable
- Added /holiday_post slash command for manual posting
- Updated wishes cog to skip auto-posting when approval enabled

Closes #42
```

```
fix: Prevent duplicate birthday role assignments

- Check role_log before assigning birthday role
- Add user to role_log after successful assignment
- Handle edge case where role already assigned manually

Fixes #38
```

## Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests and linting**:
   ```bash
   pytest tests/ -v
   python -m flake8 .
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**:
   - Go to the [Mangalify repository](https://github.com/PRADDZY/Mangalify)
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template

5. **PR Description should include**:
   - Clear description of changes
   - Motivation/context
   - Testing performed
   - Screenshots (if UI changes)
   - Related issues (use "Closes #123")

6. **Review process**:
   - Wait for maintainer review
   - Address feedback promptly
   - Make requested changes in new commits
   - Once approved, maintainer will merge

## Development Tips

### Debugging

- Use `LOG_LEVEL=DEBUG` in `.env` for verbose logging
- Use `LOG_FORMAT=json` for structured logs
- Check logs with: `tail -f logs/bot.log`

### Testing Against Live Discord

1. Create a test Discord server
2. Use separate test bot token
3. Configure test channel IDs in `.env`
4. Test commands manually before submitting PR

### Database Testing

- Use separate test database: `MONGO_URI=mongodb://localhost:27017/mangalify_test`
- Clear test data between runs
- Use Docker for consistent test environment

## Questions?

- Open a [GitHub Issue](https://github.com/PRADDZY/Mangalify/issues)
- Check existing issues and discussions
- Reach out to maintainers

Thank you for contributing! 🎉
