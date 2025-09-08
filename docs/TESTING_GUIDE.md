# 🧪 Lumos CLI Testing Guide

This guide explains how to test Lumos CLI functionality using the comprehensive testing system.

## 🚀 Quick Start

### Fastest Way to Test
```bash
# Quick functionality test (recommended for development)
make test-quick

# Or using Python directly
python test_lumos.py --quick
```

### Test All Functionality
```bash
# Comprehensive test suite
make test-all

# Or using Python directly
python test_lumos.py --all
```

## 📋 Available Test Commands

### Using Makefile (Recommended)
```bash
make help                    # Show all available commands
make test-quick             # Quick functionality test
make test-smoke             # Smoke test (basic functionality)
make test-unit              # Unit tests only
make test-integration       # Integration tests
make test-all               # Comprehensive test suite
make test-feature FEATURE=github  # Test specific feature
make cli-test               # Test CLI basic functionality
make cli-help               # Show CLI help
```

### Using Python Scripts
```bash
# Quick test
python test_lumos.py --quick

# All tests
python test_lumos.py --all

# Specific feature
python test_lumos.py --feature github

# List available tests
python test_lumos.py --list

# Interactive test selection
python tests/test_runner.py --interactive
```

## 🎯 Test Categories

### Core Tests (Critical)
- **Core Functionality**: Router, embeddings, safety, history
- **Client Modules**: GitHub, Jenkins, Jira, Neo4j, AppDynamics clients
- **Interactive Mode**: Intent detection and command handling
- **Shell Execution**: Command execution and automation
- **Configuration**: Config management and validation

### Integration Tests (Optional)
- **GitHub Integration**: PR management, commit analysis
- **Jenkins Integration**: Build monitoring, failure analysis
- **Jira Integration**: Ticket management
- **Neo4j Integration**: Graph database operations
- **AppDynamics Integration**: Application monitoring

## 🔧 Test Configuration

### Test Suites
- **smoke**: Quick smoke test - basic functionality only
- **unit**: Unit tests only - fast and reliable
- **integration**: Integration tests - requires external services
- **full**: Full test suite - everything
- **ci**: CI/CD pipeline tests - critical tests only
- **development**: Development tests - fast feedback loop

### Test Environments
- **local**: Local development environment
- **ci**: CI/CD environment
- **enterprise**: Enterprise environment with all services

## 📊 Test Results

### Quick Test Results
The quick test checks:
- ✅ Module imports (all critical modules)
- ✅ CLI help command
- ✅ Configuration managers
- ✅ Interactive components
- ✅ Utility functions

### Comprehensive Test Results
The comprehensive test includes:
- All unit tests
- Integration tests (if services available)
- End-to-end functionality tests
- Performance tests
- Error handling tests

## 🛠️ Customizing Tests

### Test Configuration
Edit `tests/test_config.py` to customize:
- Test categories and their dependencies
- Test timeouts and retry settings
- Required services for integration tests
- Test markers and filters

### Adding New Tests
1. Create test files in appropriate directories:
   - `tests/unit/` - Unit tests
   - `tests/integration/` - Integration tests
   - `tests/functional/` - Functional tests

2. Follow naming convention: `test_*.py`

3. Use appropriate pytest markers:
   - `@pytest.mark.unit` - Unit tests
   - `@pytest.mark.integration` - Integration tests
   - `@pytest.mark.slow` - Slow tests
   - `@pytest.mark.requires_config` - Tests requiring configuration

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check if modules can be imported
python -c "from src.lumos_cli.core import LLMRouter; print('Import OK')"
```

#### CLI Not Working
```bash
# Test CLI basic functionality
make cli-test

# Check CLI help
make cli-help
```

#### Test Failures
```bash
# Run specific test with verbose output
python -m pytest tests/unit/core/test_router.py -v

# Run with debug output
python -m pytest tests/unit/core/test_router.py -v -s
```

### Debug Mode
```bash
# Run tests with debug logging
PYTHONPATH=src python -m pytest tests/ -v -s --log-cli-level=DEBUG
```

## 📈 Performance Testing

### Test Execution Times
- **Quick Test**: ~5-10 seconds
- **Unit Tests**: ~30-60 seconds
- **Integration Tests**: ~2-5 minutes
- **Full Test Suite**: ~5-10 minutes

### Optimizing Test Performance
1. Use `make test-unit` for fast feedback during development
2. Use `make test-quick` for immediate functionality verification
3. Use `make test-integration` only when testing with external services
4. Use parallel execution where possible (configured in test suites)

## 🔄 Continuous Integration

### CI/CD Pipeline
The test system is designed to work in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    make test-ci
    make test-coverage
```

### Test Reports
- HTML coverage reports: `htmlcov/index.html`
- JUnit XML reports: `junit.xml`
- Coverage reports: `coverage.xml`

## 📚 Additional Resources

- [Comprehensive Debugging Guide](COMPREHENSIVE_DEBUGGING_GUIDE.md)
- [Essential Features](ESSENTIAL_FEATURES.md)
- [GitHub Integration](GITHUB_INTEGRATION.md)
- [Jenkins Integration](JENKINS_INTEGRATION.md)

## 🆘 Getting Help

If you encounter issues with testing:

1. Check the [Comprehensive Debugging Guide](COMPREHENSIVE_DEBUGGING_GUIDE.md)
2. Run `make cli-test` to verify basic functionality
3. Check test logs for specific error messages
4. Ensure all dependencies are installed: `make dev-setup`

---

**Happy Testing! 🧪✨**
