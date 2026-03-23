# GTS Platform - Testing Guide

## 🧪 Test Suite Overview

GTS includes a comprehensive pytest-based test suite covering:
- Authentication & Authorization
- AI Bots System
- Database Connectivity
- API Health & Endpoints

## 📦 Installation

```bash
# Install testing dependencies
pip install -r requirements-test.txt

# Or install individually
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite
```

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
pytest tests/test_bots.py
pytest tests/test_database.py
```

### Run Specific Test
```bash
pytest tests/test_auth.py::TestAuthentication::test_login_success
```

### Run with Verbose Output
```bash
pytest -v
```

### Run in Parallel (faster)
```bash
pip install pytest-xdist
pytest -n auto
```

## 📊 Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures and configuration
├── test_auth.py          # Authentication tests
├── test_bots.py          # AI Bots tests
├── test_database.py      # Database tests
└── test_api_health.py    # API health tests
```

## 🔧 Configuration

### pytest.ini
```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### pyproject.toml
Contains pytest configuration and asyncio settings.

## 📝 Writing Tests

### Example Test
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_example(client: AsyncClient, auth_headers: dict):
    """Test description"""
    response = await client.get("/api/v1/endpoint", headers=auth_headers)
    assert response.status_code == 200
```

### Available Fixtures
- `client`: AsyncClient for API testing
- `db_session`: Database session
- `test_user`: Regular user
- `admin_user`: Admin user
- `user_token`: JWT token for test user
- `admin_token`: JWT token for admin user
- `auth_headers`: Authorization headers for test user
- `admin_headers`: Authorization headers for admin user

## 🎯 Test Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| Authentication | 90%+ |
| AI Bots | 85%+ |
| Database | 90%+ |
| API Endpoints | 80%+ |

## 🔍 Continuous Integration

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=backend --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Testing](https://www.python-httpx.org/async/)

## 🐛 Troubleshooting

### Tests Failing with Database Errors
```bash
# Ensure test database can be created
rm -f test_gts.db
pytest
```

### AsyncIO Event Loop Errors
```bash
# Install latest pytest-asyncio
pip install --upgrade pytest-asyncio
```

### Import Errors
```bash
# Ensure backend is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

## ✅ Test Status

Current test coverage: **85%+**

All tests passing: ✅
