# 🤖 Enhanced Agentic Architecture for Lumos CLI

## Overview
This document describes the enhanced agentic pattern implemented in Lumos CLI, demonstrating how AI agents can work together to provide intelligent, context-aware responses.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY                                   │
│  "Get me the last 5 builds from jenkins for scimarketplace"    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                MASTER INTENT AGENT                             │
│  • Analyzes user intent using LLM                              │
│  • Determines primary service (GitHub, Jenkins, Jira, etc.)   │
│  • Provides confidence scoring and reasoning                   │
│  • Routes to appropriate specialized agent                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                SPECIALIZED SERVICE AGENTS                      │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ GITHUB      │  │ JENKINS     │  │ JIRA        │  │ NEO4J   │ │
│  │ AGENT       │  │ AGENT       │  │ AGENT       │  │ AGENT   │ │
│  │             │  │             │  │             │  │         │ │
│  │ • PR Ops    │  │ • Build     │  │ • Tickets   │  │ • Deps  │ │
│  │ • Commits   │  │   Status    │  │ • Comments  │  │ • Impact│ │
│  │ • Repos     │  │ • Console   │  │ • Sprints   │  │ • Graph │ │
│  │ • Branches  │  │   Analysis  │  │ • Issues    │  │ • Query │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ APPDYNAMICS │  │ CODE        │  │ WORKFLOW    │             │
│  │ AGENT       │  │ ANALYSIS    │  │ AGENT       │             │
│  │             │  │ AGENT       │  │             │             │
│  │ • Resources │  │ • Review    │  │ • Multi-    │             │
│  │ • Alerts    │  │ • Debug     │  │   Service   │             │
│  │ • Transact  │  │ • Analysis  │  │   Ops       │             │
│  │ • Health    │  │ • Security  │  │ • Orchestr. │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                SUB-AGENT FUNCTIONALITY                         │
│                                                                 │
│  Each specialized agent determines specific functionality:     │
│                                                                 │
│  JENKINS AGENT:                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Input: "Get me the last 5 builds from jenkins..."          │ │
│  │                                                             │ │
│  │ Sub-Functions:                                              │ │
│  │ • build_status → get_build_status()                        │ │
│  │ • console_analysis → analyze_console()                     │ │
│  │ • build_parameters → get_parameters()                      │ │
│  │ • general_jenkins → general_operations()                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                EXECUTION & RESPONSE                            │
│                                                                 │
│  • Agent executes specific functionality                       │
│  • Returns structured response with parameters                 │
│  • Can chain to other agents for complex workflows             │
│  • Provides reasoning and confidence scores                    │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Responsibilities

### 1. Master Intent Agent
- **Purpose**: High-level intent classification
- **Input**: Natural language query
- **Output**: Service routing decision with confidence
- **Methods**: LLM-based analysis with regex fallback

### 2. Specialized Service Agents

#### GitHub Agent
- **Purpose**: Git and repository operations
- **Sub-functions**:
  - Pull Request Operations
  - Commit Analysis
  - Repository Management
  - Branch Operations

#### Jenkins Agent
- **Purpose**: CI/CD and build operations
- **Sub-functions**:
  - Build Status Monitoring
  - Console Log Analysis
  - Job Parameter Management
  - Pipeline Operations

#### Jira Agent
- **Purpose**: Project management and ticketing
- **Sub-functions**:
  - Ticket Operations
  - Comment Management
  - Sprint Planning
  - Issue Tracking

#### Neo4j Agent
- **Purpose**: Graph database and dependency analysis
- **Sub-functions**:
  - Dependency Analysis
  - Impact Assessment
  - Graph Queries
  - Relationship Mapping

#### AppDynamics Agent
- **Purpose**: Application performance monitoring
- **Sub-functions**:
  - Resource Utilization
  - Alert Management
  - Transaction Monitoring
  - Health Assessment

#### Code Analysis Agent
- **Purpose**: Code review and analysis
- **Sub-functions**:
  - Code Review
  - Debugging
  - Security Analysis
  - Performance Analysis

#### Workflow Agent
- **Purpose**: Complex multi-service operations
- **Sub-functions**:
  - Multi-service Orchestration
  - Complex Workflow Management
  - Cross-service Data Flow

## Benefits of Agentic Pattern

### 1. 🧠 **Intelligent Routing**
- Master agent understands context and intent
- Routes to most appropriate specialized agent
- Handles complex, multi-domain queries

### 2. 🔧 **Specialized Expertise**
- Each agent is an expert in its domain
- Deep understanding of specific service capabilities
- Optimized for particular types of operations

### 3. 🎯 **Granular Functionality**
- Agents can determine specific sub-functions needed
- Precise parameter extraction and validation
- Context-aware operation selection

### 4. 🔄 **Workflow Support**
- Support for complex multi-service operations
- Agent chaining for sophisticated workflows
- Cross-service data flow and analysis

### 5. 📊 **Confidence & Reasoning**
- Each agent provides confidence scores
- Reasoning explanations for decisions
- Transparency in decision-making process

### 6. 🔧 **Structured Responses**
- Standardized response format across all agents
- Consistent parameter structure
- Easy integration with downstream processing

### 7. 🚀 **Scalability**
- Easy to add new specialized agents
- Modular architecture for independent development
- Clear separation of concerns

## Example Workflows

### Simple Workflow
```
User: "Get me the last 5 builds from jenkins"
Master Agent → Jenkins Agent → Build Status Function → Response
```

### Complex Workflow
```
User: "Get me the last 5 builds from jenkins, then check dependencies of changed classes"
Master Agent → Workflow Agent → [Jenkins Agent → Neo4j Agent] → Combined Response
```

### Multi-Service Workflow
```
User: "Show me failed builds, get the PR details, and check impact in neo4j"
Master Agent → Workflow Agent → [Jenkins Agent → GitHub Agent → Neo4j Agent] → Orchestrated Response
```

## Implementation Status

- ✅ **Current**: Unified LLM-based keyword detection system implemented
- ✅ **Enhanced**: Specialized agent architecture with integration-specific detectors
- ✅ **Completed**: GitHub, Jenkins, Jira, Neo4j, AppDynamics agents
- ✅ **Advanced**: Neo4j LLM-generated Cypher queries
- ✅ **Production**: Console clearing, detailed commit analysis, rich formatting
- 🔄 **Future**: Advanced workflow orchestration and multi-agent chaining

This agentic pattern provides a robust, scalable foundation for building intelligent CLI tools that can understand complex user intents and route them to appropriate specialized agents for execution.
