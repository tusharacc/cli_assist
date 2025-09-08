# CLI Refactoring Plan

## Current Structure (cli.py - 2346 lines)
- All commands in single file
- Mixed concerns
- Hard to maintain

## Proposed Structure

### 1. Core CLI (cli.py - ~200 lines)
- Main app initialization
- Command routing
- Global managers
- Entry points

### 2. Command Modules

#### src/lumos_cli/commands/
- `__init__.py` - Command registry
- `edit.py` - Edit command and related functions
- `review.py` - Review command and related functions
- `plan.py` - Plan command and related functions
- `debug.py` - Debug command and related functions
- `chat.py` - Chat and interactive mode
- `github.py` - GitHub integration commands
- `jira.py` - JIRA integration commands
- `scaffold.py` - Project scaffolding commands
- `backups.py` - Backup and restore commands
- `config.py` - Configuration commands
- `utils.py` - Utility commands (platform, logs, etc.)

#### src/lumos_cli/interactive/
- `__init__.py` - Interactive mode exports
- `mode.py` - Main interactive mode logic
- `intent_detection.py` - Intent detection logic
- `handlers.py` - Command handlers for interactive mode
- `github_handler.py` - GitHub interactive handlers
- `jira_handler.py` - JIRA interactive handlers

#### src/lumos_cli/utils/
- `__init__.py` - Utility exports
- `managers.py` - Global manager functions
- `helpers.py` - Common helper functions
- `validators.py` - Input validation functions

## Benefits
1. **Modularity** - Each command in its own file
2. **Maintainability** - Easy to find and modify specific functionality
3. **Testability** - Individual modules can be tested separately
4. **Reusability** - Commands can be imported and used elsewhere
5. **Scalability** - Easy to add new commands without cluttering main file

## Migration Strategy
1. Create new directory structure
2. Move commands one by one
3. Update imports
4. Test each migration
5. Remove old code
6. Update documentation
