#!/usr/bin/env python3
"""
Neo4j Schema Analysis Script with APOC
Executes schema analysis queries and saves results to JSON file
"""

import json
import sys
from datetime import datetime
from neo4j import GraphDatabase
from src.lumos_cli.neo4j_config import Neo4jConfigManager

def analyze_schema():
    """Analyze Neo4j schema and save results to JSON"""
    
    # Load Neo4j configuration
    config_manager = Neo4jConfigManager()
    if not config_manager.is_configured():
        print("❌ Neo4j not configured. Run 'lumos-cli neo4j config' first.")
        return
    
    config = config_manager.load_config()
    if not config:
        print("❌ Failed to load Neo4j configuration")
        return
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(config.uri, auth=(config.username, config.password))
    
    try:
        with driver.session() as session:
            print("🔍 Analyzing Neo4j schema with APOC...")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "neo4j_uri": config.uri,
                "analysis": {}
            }
            
            # 1. Get all node labels and counts using APOC
            print("  📊 Getting node labels and counts...")
            try:
                node_labels_query = """
                CALL apoc.meta.stats() YIELD labels
                UNWIND keys(labels) as label
                WITH label, labels[label] as count
                RETURN label, count
                ORDER BY count DESC
                """
                node_result = session.run(node_labels_query)
                results["analysis"]["node_labels"] = [{"label": record["label"], "count": record["count"]} for record in node_result]
            except Exception as e:
                print(f"    ⚠️ Node labels query failed: {e}")
                # Fallback without APOC
                try:
                    fallback_query = """
                    MATCH (n)
                    RETURN DISTINCT labels(n) as node_labels, count(n) as count
                    ORDER BY count DESC
                    """
                    fallback_result = session.run(fallback_query)
                    results["analysis"]["node_labels"] = [{"label": labels[0] if labels else "Unknown", "count": record["count"]} for record in fallback_result for labels in [record["node_labels"]]]
                except Exception as e2:
                    print(f"    ⚠️ Fallback also failed: {e2}")
                    results["analysis"]["node_labels"] = []
            
            # 2. Get all relationship types and counts using APOC
            print("  🔗 Getting relationship types and counts...")
            try:
                rel_types_query = """
                CALL apoc.meta.stats() YIELD relTypes
                UNWIND keys(relTypes) as relType
                WITH relType, relTypes[relType] as count
                RETURN relType, count
                ORDER BY count DESC
                """
                rel_result = session.run(rel_types_query)
                results["analysis"]["relationship_types"] = [{"type": record["relType"], "count": record["count"]} for record in rel_result]
            except Exception as e:
                print(f"    ⚠️ Relationship types query failed: {e}")
                # Fallback without APOC
                try:
                    fallback_query = """
                    MATCH ()-[r]->()
                    RETURN DISTINCT type(r) as relType, count(r) as count
                    ORDER BY count DESC
                    """
                    fallback_result = session.run(fallback_query)
                    results["analysis"]["relationship_types"] = [{"type": record["relType"], "count": record["count"]} for record in fallback_result]
                except Exception as e2:
                    print(f"    ⚠️ Fallback also failed: {e2}")
                    results["analysis"]["relationship_types"] = []
            
            # 3. Get all properties used across nodes using APOC
            print("  🏷️ Getting property analysis...")
            try:
                properties_query = """
                CALL apoc.meta.data() YIELD label, property, type
                WHERE label IS NOT NULL
                RETURN label, property, type, count(*) as frequency
                ORDER BY label, frequency DESC
                """
                prop_result = session.run(properties_query)
                results["analysis"]["properties"] = [{"label": record["label"], "property": record["property"], "type": record["type"], "frequency": record["frequency"]} for record in prop_result]
            except Exception as e:
                print(f"    ⚠️ Properties query failed: {e}")
                results["analysis"]["properties"] = []
            
            # 4. Get sample nodes for each label
            print("  📝 Getting sample nodes...")
            try:
                sample_nodes_query = """
                MATCH (n)
                WITH labels(n) as nodeLabels, n
                UNWIND nodeLabels as label
                WITH label, collect(n)[0..3] as sampleNodes
                RETURN label, 
                       [node in sampleNodes | properties(node)] as sample_properties
                ORDER BY label
                """
                sample_result = session.run(sample_nodes_query)
                results["analysis"]["sample_nodes"] = [{"label": record["label"], "sample_properties": record["sample_properties"]} for record in sample_result]
            except Exception as e:
                print(f"    ⚠️ Sample nodes query failed: {e}")
                results["analysis"]["sample_nodes"] = []
            
            # 5. Get relationship patterns
            print("  🔄 Getting relationship patterns...")
            try:
                patterns_query = """
                MATCH (a)-[r]->(b)
                WITH labels(a) as fromLabels, type(r) as relType, labels(b) as toLabels
                RETURN fromLabels, relType, toLabels, count(*) as frequency
                ORDER BY frequency DESC
                """
                pattern_result = session.run(patterns_query)
                results["analysis"]["relationship_patterns"] = [{"from_labels": record["fromLabels"], "relationship": record["relType"], "to_labels": record["toLabels"], "frequency": record["frequency"]} for record in pattern_result]
            except Exception as e:
                print(f"    ⚠️ Relationship patterns query failed: {e}")
                results["analysis"]["relationship_patterns"] = []
            
            # 6. Get specific node structures
            print("  🏗️ Getting specific node structures...")
            specific_nodes = {}
            
            for node_type in ["Repository", "Class", "Method", "Controller", "StoredProcedure", "Table", "Constant", "Enum"]:
                try:
                    query = f"MATCH (n:{node_type}) RETURN properties(n) as {node_type.lower()}_properties LIMIT 5"
                    result = session.run(query)
                    specific_nodes[f"{node_type.lower()}_nodes"] = [record[f"{node_type.lower()}_properties"] for record in result]
                except Exception as e:
                    print(f"    ⚠️ {node_type} nodes query failed: {e}")
                    specific_nodes[f"{node_type.lower()}_nodes"] = []
            
            results["analysis"]["specific_nodes"] = specific_nodes
            
            # 7. Get all unique property keys using APOC
            print("  🔑 Getting unique property keys...")
            try:
                unique_keys_query = """
                CALL apoc.meta.data() YIELD property
                RETURN DISTINCT property
                ORDER BY property
                """
                keys_result = session.run(unique_keys_query)
                results["analysis"]["unique_properties"] = [record["property"] for record in keys_result]
            except Exception as e:
                print(f"    ⚠️ Unique properties query failed: {e}")
                results["analysis"]["unique_properties"] = []
            
            # 8. Get constraints and indexes
            print("  📋 Getting constraints and indexes...")
            try:
                constraints_query = "CALL db.constraints() YIELD description RETURN description"
                constraints_result = session.run(constraints_query)
                results["analysis"]["constraints"] = [record["description"] for record in constraints_result]
            except Exception as e:
                print(f"    ⚠️ Constraints query failed: {e}")
                results["analysis"]["constraints"] = []
            
            try:
                indexes_query = "CALL db.indexes() YIELD description RETURN description"
                indexes_result = session.run(indexes_query)
                results["analysis"]["indexes"] = [record["description"] for record in indexes_result]
            except Exception as e:
                print(f"    ⚠️ Indexes query failed: {e}")
                results["analysis"]["indexes"] = []
            
            # 9. Check for repository/organization properties
            print("  🔍 Checking for repository/organization properties...")
            try:
                repo_org_query = """
                MATCH (n)
                WHERE n.repository IS NOT NULL OR n.organization IS NOT NULL
                RETURN labels(n) as node_labels, 
                       n.repository as repository_prop, 
                       n.organization as organization_prop,
                       properties(n) as all_properties
                LIMIT 10
                """
                repo_org_result = session.run(repo_org_query)
                results["analysis"]["repository_organization_props"] = [{"node_labels": record["node_labels"], "repository_prop": record["repository_prop"], "organization_prop": record["organization_prop"], "all_properties": record["all_properties"]} for record in repo_org_result]
            except Exception as e:
                print(f"    ⚠️ Repository/Organization properties query failed: {e}")
                results["analysis"]["repository_organization_props"] = []
            
            # 10. Check for namespace/source properties (new schema)
            print("  🔍 Checking for namespace/source properties...")
            try:
                namespace_source_query = """
                MATCH (n)
                WHERE n.namespace IS NOT NULL OR n.source IS NOT NULL
                RETURN labels(n) as node_labels, 
                       n.namespace as namespace_prop, 
                       n.source as source_prop,
                       properties(n) as all_properties
                LIMIT 10
                """
                namespace_result = session.run(namespace_source_query)
                results["analysis"]["namespace_source_props"] = [{"node_labels": record["node_labels"], "namespace_prop": record["namespace_prop"], "source_prop": record["source_prop"], "all_properties": record["all_properties"]} for record in namespace_result]
            except Exception as e:
                print(f"    ⚠️ Namespace/Source properties query failed: {e}")
                results["analysis"]["namespace_source_props"] = []
            
            # 11. Get actual data samples
            print("  📊 Getting actual data samples...")
            try:
                data_sample_query = """
                MATCH (r:Repository)-[rel1]->(c:Class)-[rel2]->(m:Method)
                RETURN r, rel1, c, rel2, m
                LIMIT 5
                """
                data_result = session.run(data_sample_query)
                data_samples = []
                for record in data_result:
                    data_samples.append({
                        "repository": dict(record["r"]),
                        "rel1": dict(record["rel1"]),
                        "class": dict(record["c"]),
                        "rel2": dict(record["rel2"]),
                        "method": dict(record["m"])
                    })
                results["analysis"]["data_samples"] = data_samples
            except Exception as e:
                print(f"    ⚠️ Data samples query failed: {e}")
                results["analysis"]["data_samples"] = []
            
            # Save results to JSON file
            output_file = "neo4j_schema_analysis_apoc.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"✅ Schema analysis complete! Results saved to {output_file}")
            print(f"📊 Found {len(results['analysis']['node_labels'])} node types")
            print(f"🔗 Found {len(results['analysis']['relationship_types'])} relationship types")
            print(f"🏷️ Found {len(results['analysis']['unique_properties'])} unique properties")
            
    except Exception as e:
        print(f"❌ Error analyzing schema: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    analyze_schema()
