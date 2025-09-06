# Debug Logging Guide for Lumos CLI

This guide explains how to enable and use debug logging for GitHub and Jenkins integrations in Lumos CLI.

## Overview

Debug logging has been added to both GitHub and Jenkins clients to help trace function calls, URL construction, and API requests. All logs are written to disk files for detailed analysis.

## Log File Locations

### Windows
```
%APPDATA%\Lumos\Logs\
```
**Example:** `C:\Users\YourUsername\AppData\Roaming\Lumos\Logs\`

### macOS/Linux
```
~/.lumos/logs/
```
**Example:** `/home/username/.lumos/logs/`

## Log File Format

Log files are created with timestamps:
- `lumos-debug-YYYYMMDD_HHMMSS.log`

Example: `lumos-debug-20250906_143022.log`

## What Gets Logged

### GitHub Client
- Function calls with parameters
- URL construction details
- HTTP request/response information
- Authentication setup
- Error details

### Jenkins Client
- Function calls with parameters
- API path construction
- HTTP request/response information
- Authentication setup
- Error details

## Log Levels

- **DEBUG**: Detailed function call traces, URL construction, parameter details
- **INFO**: High-level operations, configuration loading
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors and exceptions

## Example Log Output

```
2025-09-06 14:30:22 - lumos_debug - INFO - GitHubClient.__init__:25 - Using config file: base_url=https://api.github.com, token=***
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient.__init__:47 - Session headers set: {'Authorization': 'token ***', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Lumos-CLI/1.0'}
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient.list_pull_requests:151 - 🔍 CALL: GitHubClient.list_pull_requests({'org': 'microsoft', 'repo': 'vscode', 'state': 'open', 'head': None, 'base': None})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._get_api_endpoint:53 - 🔍 CALL: GitHubClient._get_api_endpoint({'operation': 'list_pull_requests', 'org': 'microsoft', 'repo': 'vscode'})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._get_fallback_endpoint:63 - 🔍 CALL: GitHubClient._get_fallback_endpoint({'operation': 'list_pull_requests', 'org': 'microsoft', 'repo': 'vscode'})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._get_fallback_endpoint:69 - Constructed list_pull_requests endpoint: /repos/microsoft/vscode/pulls
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:113 - 🔍 CALL: GitHubClient._make_request({'endpoint': '/repos/microsoft/vscode/pulls', 'params': {'state': 'open'}})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:116 - 🌐 URL CONSTRUCTION:
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Base URL: https://api.github.com
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Endpoint: /repos/microsoft/vscode/pulls
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Params: {'state': 'open'}
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Full URL: https://api.github.com/repos/microsoft/vscode/pulls?state=open
```

## Testing Debug Logging

Run the test script to see debug logging in action:

```bash
python test_debug_logging.py
```

This will:
1. Show log file locations for your platform
2. Test GitHub client with debug logging
3. Test Jenkins client with debug logging
4. Create log files you can examine

## Troubleshooting URL Construction Issues

If you're experiencing URL construction problems:

1. **Check the logs** for the exact URL being constructed
2. **Look for parameter passing** issues in function calls
3. **Verify base URL** configuration
4. **Check for missing parameters** in endpoint construction

### Common Issues to Look For

- **Empty org/repo parameters**: Look for `org=''` or `repo=''` in logs
- **Malformed endpoints**: Check the constructed endpoint path
- **Missing parameters**: Verify all required parameters are passed
- **Authentication issues**: Check token and base URL configuration

## Disabling Debug Logging

To disable debug logging, you can modify the `debug_logger.py` file and change the log level:

```python
# Change this line in debug_logger.py
self.logger.setLevel(logging.INFO)  # Instead of logging.DEBUG
```

## Log Rotation

Log files are created with timestamps, so they won't overwrite each other. For production use, consider implementing log rotation to manage disk space.

## Security Note

Debug logs may contain sensitive information like API tokens (partially masked) and URLs. Ensure log files are stored securely and not shared publicly.
