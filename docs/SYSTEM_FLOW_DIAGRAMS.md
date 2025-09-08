# 🔄 Lumos CLI System Flow Diagrams

## 📋 Table of Contents
- [System Architecture](#system-architecture)
- [Data Flow](#data-flow)
- [Module Dependencies](#module-dependencies)
- [Interactive Mode Flow](#interactive-mode-flow)
- [Configuration Flow](#configuration-flow)
- [Error Handling Flow](#error-handling-flow)
- [Testing Flow](#testing-flow)

## 🏛️ System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface  │  Interactive Mode  │  UI Components          │
│  (typer)        │  (mode.py)         │  (Rich)                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core Processing Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  LLM Router     │  Intent Detector  │  Workflow Handler        │
│  (router.py)    │  (intent_detector)│  (workflow_handler)      │
│                 │                   │                          │
│  Code Manager   │  Persona Manager  │  History Manager         │
│  (code_manager) │  (persona_manager)│  (history.py)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Integration Layer                    │
├─────────────────────────────────────────────────────────────────┤
│  GitHub Client  │  Jenkins Client  │  Jira Client             │
│  (github_client)│  (jenkins_client)│  (jira_client)           │
│                 │                  │                          │
│  Neo4j Client   │  AppDynamics     │  Enterprise LLM          │
│  (neo4j_client) │  (appdynamics)   │  (enterprise_llm)        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data & Storage Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  Configuration  │  History Storage │  Embeddings DB            │
│  (config/)      │  (JSON files)    │  (SQLite + vectors)       │
│                 │                  │                          │
│  Safe File      │  Debug Logs      │  Backup Storage           │
│  Editor         │  (platform_utils)│  (safety.py)              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        External Services                        │
├─────────────────────────────────────────────────────────────────┤
│  GitHub API     │  Jenkins API     │  Jira API                │
│  (REST v4)      │  (REST)          │  (REST latest)           │
│                 │                  │                          │
│  Neo4j DB       │  AppDynamics     │  OpenAI/Ollama           │
│  (Bolt)         │  (Events API v2) │  (GPT-4/Devstral)        │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Command Processing Flow
```
User Input
    │
    ▼
┌─────────────────┐
│  CLI Interface  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Intent Detector│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  LLM Router     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Command Handler│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Service Client │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  External API   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Response       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  UI Display     │
└─────────────────┘
```

### Interactive Mode Flow
```
Interactive Mode Start
    │
    ▼
┌─────────────────┐
│  Show Prompt    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  User Input     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Intent Detect  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Route Command  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Execute Handler│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Display Result │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Update History │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Continue Loop  │
└─────────────────┘
```

## 🔗 Module Dependencies

### Core Module Dependencies
```
┌─────────────────┐
│  CLI Entry      │
│  (cli_refactored_v2.py) │
└─────────────────┘
    │
    ├───► ┌─────────────────┐
    │     │  Core Router    │
    │     │  (router.py)    │
    │     └─────────────────┘
    │              │
    │              ├───► ┌─────────────────┐
    │              │     │  LLM Backends   │
    │              │     │  (OpenAI, Ollama)│
    │              │     └─────────────────┘
    │              │
    │              └───► ┌─────────────────┐
    │                    │  Service Clients│
    │                    │  (GitHub, etc.) │
    │                    └─────────────────┘
    │
    ├───► ┌─────────────────┐
    │     │  Intent Detector│
    │     │  (intent_detector)│
    │     └─────────────────┘
    │
    ├───► ┌─────────────────┐
    │     │  Interactive    │
    │     │  Mode           │
    │     └─────────────────┘
    │
    └───► ┌─────────────────┐
          │  UI Components  │
          │  (Rich)         │
          └─────────────────┘
```

### Service Client Dependencies
```
┌─────────────────┐
│  GitHub Client  │
└─────────────────┘
    │
    ├───► ┌─────────────────┐
    │     │  GitHub Config  │
    │     │  Manager        │
    │     └─────────────────┘
    │
    └───► ┌─────────────────┐
          │  GitHub API     │
          └─────────────────┘

┌─────────────────┐
│  Jenkins Client │
└─────────────────┘
    │
    ├───► ┌─────────────────┐
    │     │  Jenkins Config │
    │     │  Manager        │
    │     └─────────────────┘
    │
    └───► ┌─────────────────┐
          │  Jenkins API    │
          └─────────────────┘

┌─────────────────┐
│  Jira Client    │
└─────────────────┘
    │
    ├───► ┌─────────────────┐
    │     │  Jira Config    │
    │     │  Manager        │
    │     └─────────────────┘
    │
    └───► ┌─────────────────┐
          │  Jira API       │
          └─────────────────┘
```

## 💬 Interactive Mode Flow

### Intent Detection Flow
```
User Input
    │
    ▼
┌─────────────────┐
│  Preprocess     │
│  Input          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  LLM Intent     │
│  Detection      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Confidence     │
│  Check          │
└─────────────────┘
    │
    ├───► High Confidence ──► ┌─────────────────┐
    │                         │  Route to       │
    │                         │  Handler        │
    │                         └─────────────────┘
    │
    └───► Low Confidence ──► ┌─────────────────┐
                             │  Regex Fallback │
                             └─────────────────┘
                                     │
                                     ▼
                             ┌─────────────────┐
                             │  Route to       │
                             │  Handler        │
                             └─────────────────┘
```

### Command Handler Flow
```
Command Handler
    │
    ▼
┌─────────────────┐
│  Parse          │
│  Parameters     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Validate       │
│  Input          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Execute        │
│  Service Call   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Process        │
│  Response       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Format         │
│  Output         │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Return         │
│  Result         │
└─────────────────┘
```

## ⚙️ Configuration Flow

### Configuration Loading Flow
```
Application Start
    │
    ▼
┌─────────────────┐
│  Load Config    │
│  Files          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Validate       │
│  Configuration  │
└─────────────────┘
    │
    ├───► Valid ──► ┌─────────────────┐
    │               │  Initialize     │
    │               │  Services       │
    │               └─────────────────┘
    │
    └───► Invalid ──► ┌─────────────────┐
                      │  Show Error     │
                      │  & Setup Wizard │
                      └─────────────────┘
                              │
                              ▼
                      ┌─────────────────┐
                      │  User Input     │
                      │  Configuration │
                      └─────────────────┘
                              │
                              ▼
                      ┌─────────────────┐
                      │  Save Config    │
                      └─────────────────┘
```

### Service Configuration Flow
```
Service Config Command
    │
    ▼
┌─────────────────┐
│  Check Existing │
│  Configuration  │
└─────────────────┘
    │
    ├───► Exists ──► ┌─────────────────┐
    │                │  Show Current   │
    │                │  Configuration  │
    │                └─────────────────┘
    │
    └───► Not Exists ──► ┌─────────────────┐
                         │  Interactive    │
                         │  Setup          │
                         └─────────────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │  Validate       │
                         │  Input          │
                         └─────────────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │  Save           │
                         │  Configuration  │
                         └─────────────────┘
```

## 🚨 Error Handling Flow

### Error Processing Flow
```
Error Occurs
    │
    ▼
┌─────────────────┐
│  Error Handler  │
│  (error_handler)│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Categorize     │
│  Error          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Log Error      │
│  Details        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Generate       │
│  Suggestions    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Display        │
│  Error Message  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Continue       │
│  or Exit        │
└─────────────────┘
```

### Failure Analysis Flow
```
Build/Process Failure
    │
    ▼
┌─────────────────┐
│  Failure        │
│  Analyzer       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Parse Logs     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Identify       │
│  Error Patterns │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Categorize     │
│  Failure        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Generate       │
│  Solutions      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Display        │
│  Analysis       │
└─────────────────┘
```

## 🧪 Testing Flow

### Test Execution Flow
```
Test Command
    │
    ▼
┌─────────────────┐
│  Test Runner    │
│  (test_runner)  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Load Test      │
│  Configuration  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Execute Tests  │
│  (pytest)       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Collect        │
│  Results        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Generate       │
│  Report         │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Display        │
│  Results        │
└─────────────────┘
```

### Quick Test Flow
```
Quick Test Command
    │
    ▼
┌─────────────────┐
│  Import Tests   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Module Import  │
│  Tests          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  CLI Function   │
│  Tests          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Config Manager │
│  Tests          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Interactive    │
│  Component      │
│  Tests          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Utility        │
│  Function       │
│  Tests          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Display        │
│  Results        │
└─────────────────┘
```

## 🔄 State Management

### Application State Flow
```
Application Start
    │
    ▼
┌─────────────────┐
│  Initialize     │
│  Global State   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Load           │
│  Configuration  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Initialize     │
│  Services       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Ready for      │
│  Commands       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Process        │
│  Commands       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Update State   │
│  as Needed      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Continue       │
│  Processing     │
└─────────────────┘
```

### Session State Flow
```
Session Start
    │
    ▼
┌─────────────────┐
│  Initialize     │
│  Session State  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Load User      │
│  Context        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Process        │
│  Commands       │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Update         │
│  Context        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Save Session   │
│  State          │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Continue or    │
│  End Session    │
└─────────────────┘
```

---

**Last Updated**: September 2024  
**Version**: 2.0.0  
**Maintainer**: Lumos CLI Team
