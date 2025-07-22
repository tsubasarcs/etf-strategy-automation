# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ETF策略自動化系統 - An automated ETF dividend investment strategy system that analyzes Taiwan ETFs (0056, 00878, 00713, 00919) for optimal entry points based on historical dividend patterns.

### Key Features:
- Daily automated analysis via GitHub Actions
- Firebase integration for data storage
- Technical analysis with RSI, Bollinger Bands, and Volume indicators
- Risk assessment and opportunity scoring
- Configuration-based dividend schedule management

## Development Commands

### Environment Management
- `python3 -m venv etf-env` - Create virtual environment
- `source etf-env/bin/activate` (Linux/Mac) or `etf-env\Scripts\activate` (Windows) - Activate virtual environment
- `deactivate` - Deactivate virtual environment
- `./setup.sh` - Complete environment setup with dependencies
- `pip install -r requirements.txt` - Install dependencies
- `pip install -r requirements-dev.txt` - Install development dependencies

### Package Management
- `pip install <package>` - Install a package
- `pip install -e .` - Install project in development mode
- `pip freeze > requirements.txt` - Generate requirements file
- `pip-tools compile requirements.in` - Compile requirements with pip-tools

### Project-Specific Commands
- `./start_analysis.sh` - Run ETF analysis
- `./test_system.sh` - Test configuration and dependencies
- `cd scripts && python main_analyzer.py` - Manual analysis execution
- `cd scripts && python test_config_system.py` - Test configuration system
- `cd scripts && python check_dependencies.py` - Check all dependencies

### Code Quality Commands
- `black .` - Format code with Black
- `black --check .` - Check code formatting without changes
- `isort .` - Sort imports
- `isort --check-only .` - Check import sorting
- `flake8` - Run linting with Flake8
- `pylint src/` - Run linting with Pylint
- `mypy src/` - Run type checking with MyPy

### Development Tools
- `python -m pip install --upgrade pip` - Upgrade pip
- `python -c "import sys; print(sys.version)"` - Check Python version
- `python -m site` - Show Python site information
- `python -m pdb script.py` - Debug with pdb

## Technology Stack

### Core Technologies
- **Python** - Primary programming language (3.8+)
- **pip** - Package management
- **venv** - Virtual environment management

### Core Dependencies
- **requests** - HTTP requests for ETF data fetching
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing for technical indicators
- **lxml** - XML/HTML parsing
- **beautifulsoup4** - Web scraping capabilities

### Project Components
- **Firebase Client** - Data storage and retrieval
- **Configuration Manager** - Dynamic dividend schedule management
- **Technical Analyzer** - RSI, Bollinger Bands, Volume analysis
- **Risk Analyzer** - Position sizing and risk assessment
- **Signal Generator** - Buy/sell signal generation

### Testing Frameworks
- **pytest** - Testing framework
- **unittest** - Built-in testing framework
- **pytest-cov** - Coverage plugin for pytest
- **factory-boy** - Test fixtures
- **responses** - Mock HTTP requests

### Code Quality Tools
- **Black** - Code formatter
- **isort** - Import sorter
- **flake8** - Style guide enforcement
- **pylint** - Code analysis
- **mypy** - Static type checker
- **pre-commit** - Git hooks framework

## Project Structure

```
├── scripts/
│   ├── main_analyzer.py      # Main entry point
│   ├── core/
│   │   ├── config_manager.py # Configuration management
│   │   ├── data_collector.py # ETF data collection
│   │   ├── firebase_client.py # Firebase integration
│   │   └── etf_data_parser.py # Data parsing utilities
│   ├── analysis/
│   │   ├── basic_analyzer.py  # Basic price analysis
│   │   ├── technical_analyzer.py # Technical indicators
│   │   └── risk_analyzer.py   # Risk assessment
│   ├── strategy/
│   │   ├── signal_generator.py # Trading signals
│   │   └── opportunity_finder.py # Opportunity scoring
│   └── config/
│       ├── etf_config.py      # ETF configurations
│       ├── base_dividend.py   # Base dividend data
│       └── dynamic_dividend.json # Dynamic updates
├── .github/workflows/
│   └── etf-daily.yml         # GitHub Actions workflow
├── etf-env/                  # Virtual environment
└── requirements.txt          # Python dependencies
```

### Naming Conventions
- **Files/Modules**: Use snake_case (`user_profile.py`)
- **Classes**: Use PascalCase (`UserProfile`)
- **Functions/Variables**: Use snake_case (`get_user_data`)
- **Constants**: Use UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Private methods**: Prefix with underscore (`_private_method`)

## Python Guidelines

### Type Hints
- Use type hints for function parameters and return values
- Import types from `typing` module when needed
- Use `Optional` for nullable values
- Use `Union` for multiple possible types
- Document complex types with comments

### Code Style
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Use docstrings for modules, classes, and functions
- Limit line length to 88 characters (Black default)

### Best Practices
- Use list comprehensions for simple transformations
- Prefer `pathlib` over `os.path` for file operations
- Use context managers (`with` statements) for resource management
- Handle exceptions appropriately with try/except blocks
- Use `logging` module instead of print statements

## Testing Standards

### Test Structure
- Organize tests to mirror source code structure
- Use descriptive test names that explain the behavior
- Follow AAA pattern (Arrange, Act, Assert)
- Use fixtures for common test data
- Group related tests in classes

### Coverage Goals
- Aim for 90%+ test coverage
- Write unit tests for business logic
- Use integration tests for external dependencies
- Mock external services in tests
- Test error conditions and edge cases

### pytest Configuration
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=term-missing"
```

## Virtual Environment Setup

### Creation and Activation
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Requirements Management
- Use `requirements.txt` for production dependencies
- Use `requirements-dev.txt` for development dependencies
- Consider using `pip-tools` for dependency resolution
- Pin versions for reproducible builds

## ETF Configuration System

### Configuration Files
- `config/etf_config.py` - Static ETF information
- `config/base_dividend.py` - Historical dividend data
- `config/dynamic_dividend.json` - Runtime updates
- `config/strategy_config.py` - Strategy parameters

### Key ETF Information
```python
ETF_LIST = ['0056', '00878', '00713', '00919']

# Dividend frequencies
- 0056: Quarterly (除息月份: 3, 6, 9, 12)
- 00878: Quarterly (除息月份: 2, 5, 8, 11)
- 00713: Biannual (除息月份: 7, 12)
- 00919: Quarterly (除息月份: 3, 6, 9, 12)
```

### Analysis Parameters
- RSI Period: 14 days
- Bollinger Bands: 20-day SMA, 2 std dev
- Volume Analysis: 20-day average
- Historical data: 180 days minimum

## Security Guidelines

### Dependencies
- Regularly update dependencies with `pip list --outdated`
- Use `safety` package to check for known vulnerabilities
- Pin dependency versions in requirements files
- Use virtual environments to isolate dependencies

### Code Security
- Validate input data with Pydantic or similar
- Use environment variables for sensitive configuration
- Implement proper authentication and authorization
- Sanitize data before database operations
- Use HTTPS for production deployments

## Development Workflow

### Initial Setup
1. Run `./setup.sh` to create environment and install dependencies
2. Verify setup with `./test_system.sh`
3. Check Firebase credentials if needed

### Daily Operations
1. GitHub Actions runs automatically at 15:30 Taiwan time
2. Manual execution: `./start_analysis.sh`
3. Update dividend dates in `dynamic_dividend.json` as needed

### Key Functions
- `get_dividend_schedule()` - Get current dividend configuration
- `collect_etf_data()` - Fetch latest ETF prices
- `analyze_etf()` - Run complete analysis pipeline
- `generate_signals()` - Create buy/sell signals

### Testing
1. Configuration test: `python scripts/test_config_system.py`
2. Dependency check: `python scripts/check_dependencies.py`
3. Manual analysis: `cd scripts && python main_analyzer.py`