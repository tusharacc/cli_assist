# Lumos CLI Test Suite

This directory contains comprehensive tests for the Lumos CLI project, organized by test type and functionality.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── run_tests.py             # Test runner script
├── README.md                # This file
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── core/                # Core module tests
│   │   ├── test_router.py
│   │   ├── test_embeddings.py
│   │   └── test_safety.py
│   ├── clients/             # Client module tests
│   │   ├── test_github_client.py
│   │   └── test_github_parsing.py
│   └── interactive/         # Interactive module tests
│       └── test_intent_detection.py
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_github_integration.py
└── functional/              # Functional tests
    ├── __init__.py
    ├── test_cli_functionality.py
    └── test_refactored_cli.py
```

## Test Types

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution

### Integration Tests (`tests/integration/`)
- **Purpose**: Test interactions between components
- **Scope**: Multiple modules working together
- **Dependencies**: May use real external services (with test credentials)
- **Speed**: Medium execution time

### Functional Tests (`tests/functional/`)
- **Purpose**: Test complete workflows and user scenarios
- **Scope**: End-to-end functionality
- **Dependencies**: May use real external services
- **Speed**: Slower execution

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Types
```bash
# Unit tests only
python tests/run_tests.py unit

# Integration tests only
python tests/run_tests.py integration

# Functional tests only
python tests/run_tests.py functional
```

### Run with Pytest Directly
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/unit/core/test_router.py

# Specific test class
pytest tests/unit/core/test_router.py::TestLLMRouter

# Specific test method
pytest tests/unit/core/test_router.py::TestLLMRouter::test_router_initialization
```

### Run with Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only functional tests
pytest -m functional

# Skip slow tests
pytest -m "not slow"
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- Test discovery patterns
- Output formatting
- Markers for test categorization
- Warning filters

### Fixtures (`conftest.py`)
- Common test data
- Mock configurations
- Temporary directories
- API response mocks

## Test Coverage

### Core Modules
- ✅ LLMRouter - LLM routing and task detection
- ✅ EmbeddingDB - Code indexing and search
- ✅ SafeFileEditor - File editing with safety features
- ✅ HistoryManager - Session and conversation management

### Client Modules
- ✅ GitHubClient - GitHub API integration
- ✅ JenkinsClient - Jenkins API integration
- ✅ JiraClient - Jira API integration
- ✅ Neo4jClient - Neo4j graph database integration
- ✅ AppDynamicsClient - AppDynamics monitoring integration

### Interactive Modules
- ✅ Intent Detection - Natural language intent classification
- ✅ GitHub Handler - GitHub interactive commands
- ✅ Jenkins Handler - Jenkins interactive commands
- ✅ Jira Handler - Jira interactive commands
- ✅ Neo4j Handler - Neo4j interactive commands
- ✅ AppDynamics Handler - AppDynamics interactive commands
- ✅ Code Handler - Code operations interactive commands

### Configuration Modules
- ✅ Config Managers - Service configuration management
- ✅ Validators - Input validation and sanitization

### UI Modules
- ✅ Console - Rich console utilities
- ✅ Footer - CLI footer display
- ✅ Panels - Rich panel creation

## Test Data

### Mock Data
- GitHub API responses
- Jenkins API responses
- Jira API responses
- Neo4j query results
- AppDynamics API responses

### Test Files
- Sample code files (Python, JavaScript, Java)
- Configuration files
- Temporary directories and files

## Best Practices

### Writing Tests
1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
3. **Mocking**: Mock external dependencies to ensure tests are isolated
4. **Fixtures**: Use pytest fixtures for common test setup
5. **Assertions**: Use specific assertions that provide clear failure messages

### Test Organization
1. **One Test Class Per Module**: Group related tests in classes
2. **One Test Method Per Scenario**: Each test should verify one specific behavior
3. **Descriptive Names**: Test names should clearly describe what is being tested
4. **Setup and Teardown**: Use fixtures for common setup and cleanup

### Mocking Guidelines
1. **Mock External APIs**: Always mock external service calls
2. **Mock File Operations**: Mock file system operations for unit tests
3. **Mock Network Calls**: Mock HTTP requests and responses
4. **Mock Time-Dependent Code**: Mock time-dependent operations

## Continuous Integration

### GitHub Actions
Tests are automatically run on:
- Pull requests
- Push to main branch
- Release tags

### Test Reports
- Coverage reports generated
- Test results published
- Performance metrics tracked

## Debugging Tests

### Running Individual Tests
```bash
# Run with verbose output
pytest tests/unit/core/test_router.py -v

# Run with debug output
pytest tests/unit/core/test_router.py -s

# Run with pdb debugger
pytest tests/unit/core/test_router.py --pdb
```

### Common Issues
1. **Import Errors**: Ensure `src` is in Python path
2. **Mock Issues**: Check mock setup and assertions
3. **Fixture Errors**: Verify fixture dependencies
4. **Timeout Issues**: Increase timeout for slow tests

## Contributing

### Adding New Tests
1. Create test file in appropriate directory
2. Follow naming convention: `test_*.py`
3. Add test class: `Test*`
4. Add test methods: `test_*`
5. Update this README if adding new test categories

### Test Requirements
- All tests must pass
- New code must have test coverage
- Tests must be fast and reliable
- Tests must be well-documented
