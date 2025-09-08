# 🔗 Neo4j Integration for Lumos CLI

## Overview

Lumos CLI includes powerful Neo4j integration with LLM-generated Cypher queries, enabling complex graph database operations through natural language. This integration supports dependency analysis, impact assessment, and advanced graph queries using enterprise LLM.

## 🚀 Key Features

- **🧠 LLM-Generated Queries**: Natural language to Cypher query conversion
- **📊 Schema Analysis**: Automatic extraction of database schema
- **🔍 Complex Graph Operations**: Multi-level dependencies, path analysis, centrality
- **📈 Rich Visualization**: Beautiful tables and formatted results
- **⚡ Real-time Execution**: Direct query execution with error handling
- **🔒 Secure Authentication**: Username/password and LDAP support

## Setup

### 1. Configure Neo4j Connection

```bash
# Set environment variables
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=your_password

# Or add to .env file
echo 'NEO4J_URI=bolt://localhost:7687' >> .env
echo 'NEO4J_USERNAME=neo4j' >> .env
echo 'NEO4J_PASSWORD=your_password' >> .env
```

### 2. Verify Configuration

```bash
lumos-cli neo4j config
```

## 🎯 Commands

### Interactive Mode (Recommended)

```bash
lumos-cli
# Then use natural language queries:
```

#### Repository Operations
- `"list all repositories"`
- `"show repository statistics"`
- `"what repositories are in the graph"`

#### Dependency Analysis
- `"find all classes that depend on UserService"`
- `"show dependencies of PaymentController through 2 levels"`
- `"what classes depend on DatabaseService"`

#### Impact Analysis
- `"what classes are affected by changes to UserService"`
- `"show impact analysis for PaymentController"`
- `"find classes that will be impacted by UserService changes"`

#### Graph Analysis
- `"what classes are most connected in the graph"`
- `"find orphaned classes with no dependencies"`
- `"show me the relationship path between PaymentService and UserService"`
- `"which classes have the most incoming dependencies"`

#### Custom Queries
- `"MATCH (n) RETURN n LIMIT 10"`
- `"MATCH (c:Class)-[:DEPENDS_ON]->(d:Class) RETURN c.name, d.name"`

### Command Line Mode

```bash
# List repositories
lumos-cli neo4j list-repositories

# Show statistics
lumos-cli neo4j stats

# Dependency analysis
lumos-cli neo4j dependencies UserService

# Impact analysis
lumos-cli neo4j impact PaymentController

# Custom query
lumos-cli neo4j query "MATCH (n) RETURN n LIMIT 10"
```

## 🧠 LLM Query Generation

### How It Works

1. **Schema Extraction**: Automatically extracts Neo4j schema (labels, relationships, properties)
2. **LLM Processing**: Sends schema + user intent to enterprise LLM
3. **Query Generation**: LLM generates appropriate Cypher query
4. **Execution**: Query is executed with error handling
5. **Results Display**: Rich formatting of results with query transparency

### Schema Context Sent to LLM

```
Node Labels:
  - Class
  - Method
  - Repository
  - File

Relationship Types:
  - DEPENDS_ON
  - CONTAINS
  - IMPLEMENTS

Node Properties:
  Class: name (count: 100), repository (count: 100)
  Method: name (count: 500), parameters (count: 300)

Constraints:
  - Class name unique constraint
  - Method signature unique constraint
```

### Example LLM Prompts

#### Dependency Analysis
```
User Intent: "find all classes that depend on UserService through 2 levels"

Generated Query: 
MATCH (c:Class {name: 'UserService'})-[:DEPENDS_ON*1..2]->(dep:Class)
RETURN dep.name as dependency, dep.repository as repository
ORDER BY dep.name
```

#### Path Analysis
```
User Intent: "show me the relationship path between PaymentService and UserService"

Generated Query:
MATCH path = shortestPath((p:Class {name: 'PaymentService'})-[:DEPENDS_ON*]-(u:Class {name: 'UserService'}))
RETURN path
```

#### Centrality Analysis
```
User Intent: "what classes are most connected in the graph"

Generated Query:
MATCH (c:Class)-[r]-()
RETURN c.name as class_name, count(r) as connection_count
ORDER BY connection_count DESC
LIMIT 10
```

## 📊 Rich Output Features

### Query Display
- Shows the generated Cypher query for transparency
- Displays schema context used by the LLM
- Provides confidence scores and reasoning

### Result Formatting
- Rich tables with color-coded columns
- Truncated long values for readability
- Pagination for large result sets
- Error handling with helpful messages

### Example Output

```
🤖 Generating Cypher query using Enterprise LLM...
Intent: find all classes that depend on UserService through 2 levels

🔍 Generated Cypher Query:
MATCH (c:Class {name: 'UserService'})-[:DEPENDS_ON*1..2]->(dep:Class)
RETURN dep.name as dependency, dep.repository as repository
ORDER BY dep.name

📊 Schema Context:
Labels: Class, Method, Repository, File
Relationships: DEPENDS_ON, CONTAINS, IMPLEMENTS

✅ Query executed successfully. Found 15 records.

┌─────────────────────────────────────────────────────────────────┐
│                    Query Results (15)                          │
├─────────────────┬─────────────────────────────────────────────┤
│ dependency      │ repository                                  │
├─────────────────┼─────────────────────────────────────────────┤
│ AuthService     │ scimarketplace/user-management             │
│ DatabaseService │ scimarketplace/core                        │
│ EmailService    │ scimarketplace/notifications               │
│ ...             │ ...                                         │
└─────────────────┴─────────────────────────────────────────────┘
```

## 🔧 Advanced Features

### Schema Introspection

The integration automatically extracts:
- **Node Labels**: All node types in the graph
- **Relationship Types**: All relationship types
- **Properties**: Node properties with usage counts
- **Constraints**: Database constraints and indexes
- **Indexes**: Performance indexes

### Error Handling

- **Connection Issues**: Clear error messages for connection problems
- **Query Failures**: Graceful handling of malformed queries
- **LLM Failures**: Fallback to basic operations when LLM is unavailable
- **Schema Issues**: Helpful messages for schema-related problems

### Performance Optimization

- **Query Limits**: Automatic LIMIT clauses to prevent large result sets
- **Efficient Patterns**: LLM generates optimized Cypher queries
- **Caching**: Schema information is cached for performance
- **Connection Pooling**: Efficient database connection management

## 🎯 Use Cases

### 1. Dependency Analysis
```bash
# Find direct dependencies
/neo4j find all classes that depend on UserService

# Find multi-level dependencies
/neo4j show dependencies of PaymentController through 2 levels

# Find reverse dependencies
/neo4j what classes depend on DatabaseService
```

### 2. Impact Assessment
```bash
# Assess impact of changes
/neo4j what classes are affected by changes to UserService

# Find breaking change risks
/neo4j show impact analysis for PaymentController

# Identify critical classes
/neo4j which classes have the most incoming dependencies
```

### 3. Graph Analysis
```bash
# Find central classes
/neo4j what classes are most connected in the graph

# Find orphaned code
/neo4j find orphaned classes with no dependencies

# Analyze relationships
/neo4j show me the relationship path between PaymentService and UserService
```

### 4. Repository Management
```bash
# List all repositories
/neo4j list all repositories

# Get statistics
/neo4j show repository statistics

# Analyze repository structure
/neo4j what repositories are in the graph
```

## 🔒 Security Features

### Authentication
- **Username/Password**: Standard Neo4j authentication
- **LDAP Integration**: Enterprise LDAP support
- **Token-based**: API token authentication (future)

### Data Protection
- **Encrypted Storage**: Credentials stored securely
- **Query Validation**: Input validation for custom queries
- **Access Control**: Respects Neo4j user permissions

## 🛠️ Troubleshooting

### Connection Issues
```bash
# Test connection
lumos-cli neo4j config

# Check environment variables
echo $NEO4J_URI
echo $NEO4J_USERNAME
echo $NEO4J_PASSWORD
```

### Common Issues

1. **Connection Refused**: Check NEO4J_URI and ensure Neo4j is running
2. **Authentication Failed**: Verify NEO4J_USERNAME and NEO4J_PASSWORD
3. **Query Timeout**: Large queries may timeout; try adding LIMIT clauses
4. **Schema Empty**: Ensure your Neo4j database has data and proper schema

### Getting Help

```bash
# Show all Neo4j commands
lumos-cli --help | grep neo4j

# Get help for specific command
lumos-cli neo4j --help
```

## 🔮 Future Enhancements

- **Query Optimization**: Advanced query optimization suggestions
- **Visualization**: Graph visualization capabilities
- **Batch Operations**: Bulk operations for large datasets
- **Real-time Updates**: Live graph updates and notifications
- **Advanced Analytics**: Machine learning-based graph analysis
- **Custom Functions**: User-defined Cypher functions

## 📚 Related Documentation

- [Technical Architecture](TECHNICAL_ARCHITECTURE.md) - System architecture details
- [Agentic Architecture](AGENTIC_ARCHITECTURE.md) - AI agent patterns
- [Essential Features](ESSENTIAL_FEATURES.md) - Core functionality overview
- [Testing Guide](TESTING_GUIDE.md) - Testing Neo4j integration

---

**🌟 The Neo4j integration brings the power of graph databases to natural language, making complex graph operations accessible through simple conversations!**
