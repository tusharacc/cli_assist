// Neo4j Schema Analysis Queries
// Run these queries in Neo4j Browser (http://localhost:7474) to understand your actual schema

// 1. Get all node labels and their counts
CALL db.labels() YIELD label
CALL apoc.cypher.run("MATCH (n:" + label + ") RETURN count(n) as count", {}) YIELD value
RETURN label, value.count as node_count
ORDER BY value.count DESC;

// 2. Get all relationship types and their counts
CALL db.relationshipTypes() YIELD relationshipType
CALL apoc.cypher.run("MATCH ()-[r:" + relationshipType + "]->() RETURN count(r) as count", {}) YIELD value
RETURN relationshipType, value.count as relationship_count
ORDER BY value.count DESC;

// 3. Get all properties used across all nodes
CALL apoc.meta.data() YIELD label, property, type
WHERE label IS NOT NULL
RETURN label, property, type, count(*) as frequency
ORDER BY label, frequency DESC;

// 4. Get sample nodes for each label (to see actual structure)
MATCH (n)
WITH labels(n) as nodeLabels, n
UNWIND nodeLabels as label
WITH label, collect(n)[0..3] as sampleNodes
RETURN label, 
       [node in sampleNodes | properties(node)] as sample_properties
ORDER BY label;

// 5. Get relationship patterns (what connects to what)
MATCH (a)-[r]->(b)
WITH labels(a) as fromLabels, type(r) as relType, labels(b) as toLabels
RETURN fromLabels, relType, toLabels, count(*) as frequency
ORDER BY frequency DESC;

// 6. Get specific node structure for Repository nodes
MATCH (r:Repository)
RETURN properties(r) as repository_properties
LIMIT 5;

// 7. Get specific node structure for Class nodes
MATCH (c:Class)
RETURN properties(c) as class_properties
LIMIT 5;

// 8. Get specific node structure for Method nodes
MATCH (m:Method)
RETURN properties(m) as method_properties
LIMIT 5;

// 9. Get all unique property keys used in the database
CALL apoc.meta.data() YIELD property
RETURN DISTINCT property
ORDER BY property;

// 10. Get the actual schema constraints and indexes
CALL db.constraints() YIELD description
RETURN description;

CALL db.indexes() YIELD description
RETURN description;

// 11. Get a sample of actual data to understand the structure
MATCH (r:Repository)-[rel1]->(c:Class)-[rel2]->(m:Method)
RETURN r, rel1, c, rel2, m
LIMIT 10;

// 12. If you have .NET specific nodes, check for them
MATCH (n)
WHERE 'Controller' IN labels(n) OR 'StoredProcedure' IN labels(n) OR 'Table' IN labels(n) OR 'Constant' IN labels(n) OR 'Enum' IN labels(n)
RETURN labels(n) as node_labels, properties(n) as node_properties
LIMIT 10;

// 13. Check for any nodes with 'repository' or 'organization' properties
MATCH (n)
WHERE n.repository IS NOT NULL OR n.organization IS NOT NULL
RETURN labels(n) as node_labels, 
       n.repository as repository_prop, 
       n.organization as organization_prop,
       properties(n) as all_properties
LIMIT 10;

// 14. Get the actual relationship structure in a readable format
MATCH (a)-[r]->(b)
WITH labels(a)[0] as from_label, type(r) as relationship, labels(b)[0] as to_label, count(*) as count
RETURN from_label + " -[" + relationship + "]-> " + to_label as pattern, count
ORDER BY count DESC;
