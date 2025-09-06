# 🐙 GitHub Integration for Lumos CLI

## Overview
Lumos CLI now includes powerful GitHub integration for enterprise workflows, allowing you to clone repositories and manage pull requests directly from the command line.

## Setup

### 1. Configure GitHub Token
```bash
# Set your GitHub personal access token
export GITHUB_TOKEN=your_token_here

# Or add to .env file
echo 'GITHUB_TOKEN=your_token_here' >> .env
```

### 2. Verify Configuration
```bash
lumos-cli github-config
```

## Commands

### Repository Cloning
```bash
# Clone a repository
lumos-cli github-clone scimarketplace/externaldata

# Clone specific branch
lumos-cli github-clone scimarketplace/externaldata --branch RC1

# Clone to specific directory
lumos-cli github-clone scimarketplace/externaldata --target-dir ./my-repo
```

### Pull Request Management
```bash
# Check PRs for specific branch
lumos-cli github-pr scimarketplace/externaldata --branch RC1

# List all open PRs
lumos-cli github-pr scimarketplace/externaldata --list

# Get specific PR details
lumos-cli github-pr scimarketplace/externaldata --pr 123
```

## Example Workflows

### 1. Check RC1 Branch for PRs
```bash
lumos-cli github-pr scimarketplace/externaldata --branch RC1
```

### 2. Clone and Work on Repository
```bash
lumos-cli github-clone scimarketplace/externaldata --branch RC1
cd externaldata
# Now you're in the repository and can use other Lumos commands
```

### 3. Review Specific PR
```bash
lumos-cli github-pr scimarketplace/externaldata --pr 456
```

## Features
- ✅ **Repository Cloning** with branch support
- ✅ **PR Detection** by branch name
- ✅ **PR Summarization** with commits and file changes
- ✅ **Rich Console Output** with tables and panels
- ✅ **Enterprise Ready** with token authentication
- ✅ **Multiple Organizations** support
