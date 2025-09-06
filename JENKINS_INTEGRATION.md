# Jenkins Integration for Lumos CLI

## Overview

Lumos CLI now includes comprehensive Jenkins integration for enterprise CI/CD workflows. This integration supports the complex folder structure used by your organization and provides natural language querying capabilities.

## Folder Structure Support

The Jenkins integration understands your specific folder hierarchy:

```
scimarketplace/
├── deploy-all/                    # Special folder for all jobs
│   ├── job1/
│   ├── job2/
│   └── ...
├── externaldata_multi/            # Repository folders (suffix: _multi)
│   ├── RC1/                      # Branch folders
│   │   ├── build-job/
│   │   └── test-job/
│   ├── RC2/
│   ├── RC3/
│   └── RC4/
├── addresssearch_multi/
│   ├── RC1/
│   ├── RC2/
│   ├── RC3/
│   └── RC4/
└── ...
```

## Configuration

### Environment Variables

Set the following environment variables:

```bash
export JENKINS_URL=https://your-jenkins.com
export JENKINS_TOKEN=your_api_token
export JENKINS_USERNAME=your_username  # Optional, defaults to 'api'
```

Or add to your `.env` file:

```bash
echo 'JENKINS_URL=https://your-jenkins.com' >> .env
echo 'JENKINS_TOKEN=your_token_here' >> .env
echo 'JENKINS_USERNAME=your_username' >> .env
```

### Getting Jenkins API Token

1. Go to Jenkins → User → Configure
2. Click "Add new Token" in the API Token section
3. Give it a name and click "Generate"
4. Copy the token (you won't see it again)

## CLI Commands

### 1. Find Failed Jobs

```bash
# Find failed jobs in deploy-all folder (last 4 hours)
lumos-cli jenkins-failed-jobs

# Find failed jobs in specific folder
lumos-cli jenkins-failed-jobs --folder scimarketplace/deploy-all --hours 8

# Find failed jobs in repository branch
lumos-cli jenkins-failed-jobs --folder scimarketplace/externaldata_multi/RC1
```

### 2. Find Running Jobs

```bash
# Find running jobs in deploy-all folder
lumos-cli jenkins-running-jobs

# Find running jobs in specific folder
lumos-cli jenkins-running-jobs --folder scimarketplace/addresssearch_multi/RC2
```

### 3. Repository and Branch Jobs

```bash
# Find jobs for externaldata repository in RC1 branch
lumos-cli jenkins-repo-jobs externaldata RC1

# Find jobs for addresssearch repository in RC2 branch
lumos-cli jenkins-repo-jobs addresssearch RC2
```

### 4. Build Parameters

```bash
# Get build parameters for specific job and build number
lumos-cli jenkins-build-params scimarketplace/deploy-all/my-job 123

# Get build parameters for repository job
lumos-cli jenkins-build-params scimarketplace/externaldata_multi/RC1/build-job 456
```

### 5. Failure Analysis

```bash
# Analyze why a build failed
lumos-cli jenkins-analyze-failure scimarketplace/deploy-all/my-job 123

# Analyze failure with console output
lumos-cli jenkins-analyze-failure scimarketplace/externaldata_multi/RC1/build-job 456
```

### 6. Configuration

```bash
# Check Jenkins configuration and test connection
lumos-cli jenkins-config
```

## Interactive Mode

Use natural language queries in interactive mode:

```bash
lumos-cli chat
```

### Example Queries

#### Failed Jobs
- "Are there failed jobs in last 4 hours in folder deploy-all?"
- "Show me failed jobs in scimarketplace/deploy-all in the last 8 hours"
- "Any broken builds in externaldata RC1 branch?"

#### Running Jobs
- "Is there any job running for repository externaldata in branch RC1?"
- "What jobs are currently running in deploy-all folder?"
- "Show me running builds in addresssearch RC2"

#### Build Information
- "Give me the build parameters of job number 123 under folder deploy-all"
- "What are the parameters for build 456 in externaldata RC1?"

#### Failure Analysis
- "Check console text and let me know why job 123 failed"
- "Analyze the failure for build 789 in deploy-all"
- "Why did the externaldata build fail?"

## Features

### Smart Folder Navigation
- Automatically handles the `_multi` suffix for repository folders
- Supports all branch names (RC1, RC2, RC3, RC4)
- Handles the special `deploy-all` folder

### Intelligent Query Parsing
- Extracts repository names, branch names, and time periods
- Understands natural language patterns
- Provides helpful suggestions for unclear queries

### Rich Output Formatting
- Beautiful tables for job listings
- Color-coded status indicators
- Detailed failure analysis with console output
- Context-aware error messages

### Error Handling
- Graceful handling of network issues
- Clear error messages for authentication problems
- Helpful suggestions for configuration issues

## Use Cases

### Daily Monitoring
```bash
# Check for overnight failures
lumos-cli jenkins-failed-jobs --hours 12

# See what's currently running
lumos-cli jenkins-running-jobs
```

### Release Management
```bash
# Check RC1 branch status
lumos-cli jenkins-repo-jobs externaldata RC1

# Analyze a specific failure
lumos-cli jenkins-analyze-failure scimarketplace/externaldata_multi/RC1/build-job 123
```

### Debugging
```bash
# Get build parameters for investigation
lumos-cli jenkins-build-params scimarketplace/deploy-all/debug-job 456

# Analyze failure with full console output
lumos-cli jenkins-analyze-failure scimarketplace/deploy-all/debug-job 456
```

## Troubleshooting

### Connection Issues
```bash
# Test connection
lumos-cli jenkins-config

# Check environment variables
echo $JENKINS_URL
echo $JENKINS_TOKEN
```

### Common Issues

1. **401 Unauthorized**: Check your JENKINS_TOKEN
2. **404 Not Found**: Verify the job path exists
3. **Connection Refused**: Check JENKINS_URL

### Getting Help

```bash
# Show all Jenkins commands
lumos-cli --help | grep jenkins

# Get help for specific command
lumos-cli jenkins-failed-jobs --help
```

## Integration with Other Tools

The Jenkins integration works seamlessly with:

- **GitHub Integration**: Query Jenkins after GitHub operations
- **JIRA Integration**: Link build failures to JIRA tickets
- **Interactive Mode**: Natural language queries across all tools

## Security Notes

- Store Jenkins credentials securely
- Use environment variables, not hardcoded values
- Regularly rotate API tokens
- Follow your organization's security policies

## Future Enhancements

- Build triggering capabilities
- Job configuration management
- Pipeline visualization
- Integration with other CI/CD tools
- Advanced analytics and reporting
