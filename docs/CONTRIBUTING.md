# 🤝 Contributing to MarketMind AI

Thank you for your interest in contributing to MarketMind AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers and help them get started
- ✅ Provide constructive feedback
- ✅ Focus on what is best for the community
- ✅ Show empathy towards other community members

### Unacceptable Behavior

- ❌ Harassment or discriminatory language
- ❌ Personal attacks or trolling
- ❌ Publishing others' private information
- ❌ Spamming or excessive self-promotion
- ❌ Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.10+** installed
- **Git** for version control
- **Redis** running locally or accessible
- **API Keys** for development (Nebius AI, ScrapeGraph)
- Basic understanding of:
  - Python async/await
  - REST APIs
  - AI/LLM concepts

### Finding Issues to Work On

1. **Good First Issues**: Look for issues labeled `good-first-issue`
2. **Help Wanted**: Check issues labeled `help-wanted`
3. **Bug Fixes**: Issues labeled `bug` are always welcome
4. **Feature Requests**: Check `enhancement` labeled issues

**Before starting work**:
- Comment on the issue to let others know you're working on it
- Wait for maintainer confirmation if it's a significant change
- Check if there's already a PR addressing the issue

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork

git clone https://github.com/YOUR_USERNAME/marketmind-ai.git
cd marketmind-ai

# Add upstream remote
git remote add upstream https://github.com/original/marketmind-ai.git
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp api.env.example api.env

# Edit with your development keys
nano api.env
```

### 4. Start Redis

```bash
# macOS
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:latest

# Linux
sudo systemctl start redis
```


### 5. Start Development Server

```bash
python run.py
```

---

## How to Contribute

### Types of Contributions

#### 🐛 Bug Fixes

1. Create an issue describing the bug (if not exists)
2. Fork and create a branch: `git checkout -b fix/issue-number-description`
3. Fix the bug with tests
4. Submit a pull request

#### ✨ New Features

1. Discuss the feature in an issue first
2. Wait for maintainer approval
3. Fork and create a branch: `git checkout -b feature/feature-name`
4. Implement with tests and documentation
5. Submit a pull request

#### 📚 Documentation

1. Fork and create a branch: `git checkout -b docs/what-you-are-documenting`
2. Make your documentation changes
3. Ensure examples are accurate
4. Submit a pull request

#### 🧪 Tests

1. Fork and create a branch: `git checkout -b test/what-you-are-testing`
2. Add comprehensive tests
3. Ensure all tests pass
4. Submit a pull request

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with these specifics:

```python
# Line length: 100 characters (not 79)
# Indentation: 4 spaces (no tabs)
# Quotes: Double quotes for strings

# ✅ Good
def analyze_company(url: str, feature: str) -> dict:
    """
    Analyze a company website.
    
    Args:
        url: Company website URL
        feature: Analysis type
        
    Returns:
        Analysis results dictionary
    """
    result = {"status": "success", "data": {}}
    return result

# ❌ Bad
def analyzeCompany(url,feature):  # Wrong naming, no types
    result={'status':'success'}  # Wrong quotes, no spaces
    return result
```

### Code Formatting

We use **Black** for consistent formatting:

```bash
# Format all code
black app/ tests/

# Check formatting without changes
black --check app/ tests/
```

### Linting

We use **Flake8** for linting:

```bash
# Run linter
flake8 app/ tests/

# Ignore specific rules in setup.cfg if needed
```

### Type Checking

We use **MyPy** for type checking:

```bash
# Run type checker
mypy app/

# Fix type issues before submitting
```

### Import Organization

```python
# Standard library imports
import asyncio
import logging
from typing import Optional, Dict

# Third-party imports
import redis
from tenacity import retry

# Local imports
from app.config import settings
from app.services import llm_service
```

### Docstrings

Use **Google-style docstrings**:

```python
def search_competitors(self, company_url: str) -> str:
    """
    Search for competitor intelligence.
    
    Args:
        company_url: Company website URL
        
    Returns:
        Competitive intelligence report as markdown
        
    Raises:
        ValueError: If URL is invalid
        TimeoutError: If search exceeds timeout
        
    Example:
        >>> service = SearchScraperService()
        >>> result = service.search_competitors("https://stripe.com")
        >>> print(result)
        # 🏢 Competitive Intelligence Report
        ...
    """
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Warning messages for recoverable issues")
logger.error("Error messages for failures")
logger.critical("Critical errors requiring immediate attention")

# Include context in log messages
logger.info(f"✅ Parsed query - URL: {url}, Type: {feature}")

# Use exc_info=True for exceptions
try:
    process()
except Exception as e:
    logger.error(f"Processing failed: {e}", exc_info=True)
```

---

## Testing Guidelines

### Test Structure

```python
# tests/test_agent.py

import pytest
from app.agent import SmartGTMAgent

class TestSmartGTMAgent:
    """Test suite for SmartGTMAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return SmartGTMAgent()
    
    def test_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent is not None
        assert agent.handlers is None
    
    @pytest.mark.asyncio
    async def test_assist_valid_query(self, agent, mock_response_handler):
        """Test assist with valid query"""
        # Setup
        session = MockSession(user_id="test-user")
        query = MockQuery(prompt="Research stripe.com")
        
        # Execute
        await agent.assist(session, query, mock_response_handler)
        
        # Assert
        assert mock_response_handler.complete_called
        assert "Stripe" in mock_response_handler.text_blocks
```

### Test Coverage

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+
- **Critical Paths**: 100% coverage required

```bash
# Run with coverage report
pytest --cov=app --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Mocking External Services

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_smartcrawler():
    """Mock SmartCrawler service"""
    with patch('app.services.smartcrawler_service.crawl') as mock:
        mock.return_value = "Mocked crawler data"
        yield mock

def test_with_mocked_crawler(agent, mock_smartcrawler):
    """Test agent with mocked external service"""
    result = agent.process()
    mock_smartcrawler.assert_called_once()
```

### Test Naming Convention

```python
# Pattern: test_{what}_{condition}_{expected}

def test_parse_query_valid_url_returns_normalized_url():
    pass

def test_rate_limiter_exceeded_limit_returns_false():
    pass

def test_cache_miss_triggers_fresh_analysis():
    pass
```

---

## Pull Request Process

### 1. Create Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

```bash
# Make your changes
# ... edit files ...

# Run tests frequently
pytest tests/

# Format code
black app/ tests/

# Check linting
flake8 app/ tests/
```

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add natural language query parsing

- Implement QueryParser class
- Support multiple URL formats
- Add comprehensive tests
- Update documentation

Closes #123"
```

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 4. Push Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill in the PR template completely
3. Link related issues (Closes #123)
4. Request review from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings

## Related Issues
Closes #123
Relates to #456
```

### 6. Address Review Comments

```bash
# Make requested changes
# ... edit files ...

# Commit
git add .
git commit -m "refactor: address review comments

- Simplified error handling
- Added type hints
- Fixed docstring formatting"

# Push
git push origin feature/your-feature-name
```

### 7. Merge

Once approved:
- Maintainer will merge your PR
- Your branch will be deleted automatically
- Changes will be in the next release

---

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Submit query '...'
3. See error

**Expected behavior**
What you expected to happen

**Actual behavior**
What actually happened

**Environment**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.5]
- Version: [e.g., 2.0.0]

**Logs**
```
Paste relevant logs
```

**Additional context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired functionality

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Mockups, examples, or use cases

**Willing to implement?**
- [ ] Yes, I can implement this
- [ ] No, but I can help test
- [ ] No, just suggesting
```

---

## Development Workflow

### Branching Strategy

```
main (production)
  ├─ develop (integration)
  │   ├─ feature/feature-name
  │   ├─ fix/bug-description
  │   └─ docs/documentation-update
```

### Release Process

1. **Development**: Features merged to `develop`
2. **Testing**: QA on `develop` branch
3. **Release**: Create release branch from `develop`
4. **Tagging**: Tag release (e.g., `v2.1.0`)
5. **Merge**: Merge to `main` and back to `develop`

---

## Communication

### Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code review, technical discussion
- **Discord**: Real-time chat (link in README)
- **Email**: Private concerns (support@marketmind.ai)

### Response Times

- **Issues**: Within 48 hours
- **Pull Requests**: Within 3-5 days
- **Security Issues**: Within 24 hours

---

## Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **Release Notes**: Acknowledgments
- **CONTRIBUTORS.md**: Full list of contributors

---

## Questions?

If you have questions not covered here:

1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Join our Discord community

Thank you for contributing to MarketMind AI! 🚀
