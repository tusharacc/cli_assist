# 🎯 Intent Consolidation Plan

## Current Problem
We have multiple overlapping intents for code-related operations:
- `/code` - Comprehensive code operations
- `/edit` - Code editing (subset of code)
- `/plan` - Planning (subset of code) 
- `/review` - Code review (subset of code)
- `/fix` - Bug fixing (subset of code)

## Proposed Solution: Unified `/code` Intent

### 1. Consolidate All Code Operations Under `/code`
```
/code <action> [options]

Actions:
  generate    - Generate new code from specifications
  edit        - Edit existing code (replaces /edit)
  plan        - Create implementation plans (replaces /plan)
  review      - Review code for improvements (replaces /review)
  fix         - Fix bugs and issues (replaces /fix)
  test        - Generate and run tests
  analyze     - Analyze code quality and complexity
  refactor    - Refactor code for better quality
  docs        - Generate documentation
  format      - Format and lint code
  validate    - Validate code syntax and style
```

### 2. Backward Compatibility
Keep existing commands but route them to `/code`:
- `/edit` → `/code edit`
- `/plan` → `/code plan`
- `/review` → `/code review`
- `/fix` → `/code fix`

### 3. Benefits
- **Single Entry Point** - All code operations in one place
- **Consistent Interface** - Same patterns and behaviors
- **Better Organization** - Logical grouping of related operations
- **Easier Maintenance** - One code path to maintain
- **Clearer Intent** - Users know exactly where to go

### 4. Migration Strategy
1. Update intent detection to route old commands to `/code`
2. Add deprecation warnings for old commands
3. Update help system to show unified approach
4. Eventually remove old commands (optional)

## Implementation Plan

### Phase 1: Update Intent Detection
- Remove separate `edit`, `plan`, `review`, `fix` intents
- Route these to `code` intent with appropriate action
- Update LLM prompt to reflect unified approach

### Phase 2: Update Command Handlers
- Modify `_interactive_edit` to call `_interactive_code` with `edit` action
- Modify `_interactive_plan` to call `_interactive_code` with `plan` action
- Modify `_interactive_review` to call `_interactive_code` with `review` action
- Modify `_interactive_fix` to call `_interactive_code` with `fix` action

### Phase 3: Update Help System
- Show unified `/code` command structure
- Add backward compatibility notes
- Update examples to use `/code` approach

### Phase 4: Testing & Validation
- Test all code operations work through `/code`
- Verify backward compatibility
- Update documentation

## Example Usage After Consolidation

### New Unified Approach:
```bash
/code generate "create a REST API" api.py python
/code edit "add error handling" app.py
/code plan "implement user authentication"
/code review app.py
/code fix "memory leak in payment processing"
/code test generate app.py unit
/code analyze app.py
/code refactor app.py performance
/code docs api.py api
/code format app.py
/code validate app.py
```

### Backward Compatibility (Still Works):
```bash
/edit "add error handling" app.py  # → /code edit "add error handling" app.py
/plan "implement user authentication"  # → /code plan "implement user authentication"
/review app.py  # → /code review app.py
/fix "memory leak"  # → /code fix "memory leak"
```

## Result
- **Single, comprehensive code management system**
- **Backward compatibility maintained**
- **Clearer, more organized interface**
- **Easier to maintain and extend**
