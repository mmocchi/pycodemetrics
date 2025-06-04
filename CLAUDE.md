# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- Run tests: `uv run pytest`
- Run tests with coverage: `uv run task test` (includes coverage reporting)

### Code Quality
- Lint code: `uv run task lint` or `uv run ruff check .`
- Format code: `uv run task format` or `uv run ruff format .`
- Type check: `uv run task mypy` or `uv run mypy src`
- Type check tests: `uv run mypy tests`

### Development Setup
- Install dependencies: `uv sync`
- Run the CLI: `uv run pycodemetrics --help`

## Architecture Overview

PyCodeMetrics is a Python code analysis tool with a modular CLI architecture:

### Core Structure
- **CLI Layer** (`src/pycodemetrics/cli/`): Click-based command interface with four main commands:
  - `analyze`: Python code metrics analysis (file-level)
  - `coupling`: Module coupling analysis (project-level)
  - `hotspot`: Git-based hotspot analysis (change frequency + complexity)
  - `committer`: Developer contribution analysis
- **Services Layer** (`src/pycodemetrics/services/`): Business logic for each analysis type
- **Metrics Layer** (`src/pycodemetrics/metrics/`): Core metric calculation engines
- **Git Client** (`src/pycodemetrics/gitclient/`): Git repository interaction and log parsing

### Key Components
- **Python Metrics**: Uses `radon` and `cognitive-complexity` for code quality metrics
- **Coupling Analysis**: Analyzes module dependencies and calculates coupling metrics (Ca, Ce, I)
- **Import Analysis**: Analyzes Python import relationships and dependencies
- **Git Integration**: Parses git logs to analyze code change patterns and developer activity
- **Parallel Processing**: Supports concurrent analysis with configurable worker counts
- **Multiple Output Formats**: TABLE, JSON, CSV with optional file export

### Data Flow
1. CLI commands parse arguments and delegate to service layer
2. Services coordinate between git client, file utilities, and metric calculators
3. Metrics engines process files/git data and return structured results
4. Results are formatted and exported via display utilities

### Configuration
- Uses `pydantic` models for data validation throughout
- Configuration managed via `config/config_manager.py`
- File filtering and path resolution in `util/file_util.py`

## Coupling Analysis

The `coupling` command analyzes project-wide module coupling metrics:

### Coupling Metrics
- **Ca (Afferent Coupling)**: Number of modules that depend on this module
- **Ce (Efferent Coupling)**: Number of modules this module depends on
- **I (Instability)**: Ce / (Ca + Ce) - measures susceptibility to change
- **A (Abstractness)**: Currently not implemented
- **D (Distance)**: |A + I - 1| - distance from main sequence

### Module Categories
- **stable**: Low instability, concrete implementation (ideal utilities)
- **unstable**: High instability, abstract interface (ideal interfaces)
- **painful**: Low instability, high abstractness (hard to change)
- **useless**: High instability, low abstractness (low value)

### Usage Examples
```bash
# Basic coupling analysis
uv run pycodemetrics coupling /path/to/project

# With filtering and export
uv run pycodemetrics coupling . --filter unstable --export coupling.csv

# Show project summary
uv run pycodemetrics coupling . --summary --limit 20
```
