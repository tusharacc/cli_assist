#!/usr/bin/env python3
"""
Enterprise Neo4j Schema Analyzer
Executes comprehensive schema analysis queries and generates structured output
"""

import json
import sys
from datetime import datetime
from neo4j import GraphDatabase
from src.lumos_cli.neo4j_config import Neo4jConfigManager

def analyze_enterprise_schema():
    """Analyze enterprise Neo4j schema comprehensively"""
    
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
            print("🔍 Analyzing Enterprise Neo4j Schema...")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "neo4j_uri": config.uri,
                "enterprise_analysis": {}
            }
            
            # 1. Basic Schema Discovery
            print("  📊 1. Basic Schema Discovery...")
            try:
                # Node labels and counts
                node_labels_query = """
                MATCH (n)
                WITH labels(n) as nodeLabels, n
                UNWIND nodeLabels as label
                WITH label, collect(n)[0..1] as sampleNodes
                RETURN label, 
                       count(n) as count,
                       [node in sampleNodes | properties(node)] as sample_properties
                ORDER BY count DESC
                """
                node_result = session.run(node_labels_query)
                results["enterprise_analysis"]["node_labels"] = [
                    {
                        "label": record["label"], 
                        "count": record["count"],
                        "sample_properties": record["sample_properties"]
                    } 
                    for record in node_result
                ]
                print(f"    ✅ Found {len(results['enterprise_analysis']['node_labels'])} node types")
            except Exception as e:
                print(f"    ❌ Node labels query failed: {e}")
                results["enterprise_analysis"]["node_labels"] = []
            
            # 2. Relationship Types and Patterns
            print("  🔗 2. Relationship Analysis...")
            try:
                # Relationship types and counts
                rel_types_query = """
                MATCH ()-[r]->()
                WITH type(r) as relType, r
                RETURN relType, count(r) as count
                ORDER BY count DESC
                """
                rel_result = session.run(rel_types_query)
                results["enterprise_analysis"]["relationship_types"] = [
                    {"type": record["relType"], "count": record["count"]} 
                    for record in rel_result
                ]
                
                # Relationship patterns (what connects to what)
                patterns_query = """
                MATCH (a)-[r]->(b)
                WITH labels(a) as fromLabels, type(r) as relType, labels(b) as toLabels
                RETURN fromLabels, relType, toLabels, count(*) as frequency
                ORDER BY frequency DESC
                """
                pattern_result = session.run(patterns_query)
                results["enterprise_analysis"]["relationship_patterns"] = [
                    {
                        "from_labels": record["fromLabels"], 
                        "relationship": record["relType"], 
                        "to_labels": record["toLabels"], 
                        "frequency": record["frequency"]
                    } 
                    for record in pattern_result
                ]
                print(f"    ✅ Found {len(results['enterprise_analysis']['relationship_types'])} relationship types")
            except Exception as e:
                print(f"    ❌ Relationship analysis failed: {e}")
                results["enterprise_analysis"]["relationship_types"] = []
                results["enterprise_analysis"]["relationship_patterns"] = []
            
            # 3. Property Analysis
            print("  🏷️ 3. Property Analysis...")
            try:
                # Get all unique properties across all nodes
                properties_query = """
                MATCH (n)
                UNWIND keys(n) as property
                WITH property, collect(DISTINCT labels(n)) as used_in_labels
                RETURN property, 
                       size(used_in_labels) as label_count,
                       used_in_labels as labels_using_property
                ORDER BY label_count DESC, property
                """
                prop_result = session.run(properties_query)
                results["enterprise_analysis"]["properties"] = [
                    {
                        "property": record["property"], 
                        "label_count": record["label_count"],
                        "labels_using_property": record["labels_using_property"]
                    } 
                    for record in prop_result
                ]
                print(f"    ✅ Found {len(results['enterprise_analysis']['properties'])} unique properties")
            except Exception as e:
                print(f"    ❌ Property analysis failed: {e}")
                results["enterprise_analysis"]["properties"] = []
            
            # 4. Schema Compatibility Analysis
            print("  🔍 4. Schema Compatibility Analysis...")
            try:
                # Check for old schema properties (repository, organization)
                old_schema_query = """
                MATCH (n)
                WHERE n.repository IS NOT NULL OR n.organization IS NOT NULL
                RETURN labels(n) as node_labels, 
                       n.repository as repository_prop, 
                       n.organization as organization_prop,
                       properties(n) as all_properties
                LIMIT 20
                """
                old_result = session.run(old_schema_query)
                results["enterprise_analysis"]["old_schema_nodes"] = [
                    {
                        "node_labels": record["node_labels"], 
                        "repository_prop": record["repository_prop"], 
                        "organization_prop": record["organization_prop"], 
                        "all_properties": record["all_properties"]
                    } 
                    for record in old_result
                ]
                
                # Check for new schema properties (namespace, source)
                new_schema_query = """
                MATCH (n)
                WHERE n.namespace IS NOT NULL OR n.source IS NOT NULL
                RETURN labels(n) as node_labels, 
                       n.namespace as namespace_prop, 
                       n.source as source_prop,
                       properties(n) as all_properties
                LIMIT 20
                """
                new_result = session.run(new_schema_query)
                results["enterprise_analysis"]["new_schema_nodes"] = [
                    {
                        "node_labels": record["node_labels"], 
                        "namespace_prop": record["namespace_prop"], 
                        "source_prop": record["source_prop"], 
                        "all_properties": record["all_properties"]
                    } 
                    for record in new_result
                ]
                
                print(f"    ✅ Old schema nodes: {len(results['enterprise_analysis']['old_schema_nodes'])}")
                print(f"    ✅ New schema nodes: {len(results['enterprise_analysis']['new_schema_nodes'])}")
            except Exception as e:
                print(f"    ❌ Schema compatibility analysis failed: {e}")
                results["enterprise_analysis"]["old_schema_nodes"] = []
                results["enterprise_analysis"]["new_schema_nodes"] = []
            
            # 5. Specific Node Type Analysis
            print("  🏗️ 5. Specific Node Type Analysis...")
            specific_nodes = {}
            
            node_types = ["Repository", "Class", "Method", "Controller", "StoredProcedure", "Table", "Constant", "Enum", "File"]
            for node_type in node_types:
                try:
                    query = f"""
                    MATCH (n:{node_type})
                    RETURN properties(n) as properties
                    LIMIT 10
                    """
                    result = session.run(query)
                    specific_nodes[f"{node_type.lower()}_nodes"] = [record["properties"] for record in result]
                    print(f"    ✅ {node_type}: {len(specific_nodes[f'{node_type.lower()}_nodes'])} samples")
                except Exception as e:
                    print(f"    ⚠️ {node_type}: Query failed - {e}")
                    specific_nodes[f"{node_type.lower()}_nodes"] = []
            
            results["enterprise_analysis"]["specific_nodes"] = specific_nodes
            
            # 6. Dependency Analysis Queries
            print("  🔄 6. Dependency Analysis Queries...")
            try:
                # Test dependency queries with different schemas
                dependency_tests = []
                
                # Test 1: Old schema dependency query
                old_dep_query = """
                MATCH (source:Class {name: $class_name, repository: $repo, organization: $org})
                MATCH (source)-[r:DEPENDS_ON]->(target:Class)
                RETURN target.name as target_class, r.type as dependency_type
                LIMIT 5
                """
                
                # Test 2: New schema dependency query
                new_dep_query = """
                MATCH (source:Class {name: $class_name, source: $repo})
                MATCH (source)-[r:DEPENDS_ON]->(target:Class)
                RETURN target.name as target_class, r.type as dependency_type
                LIMIT 5
                """
                
                # Test 3: Mixed schema dependency query
                mixed_dep_query = """
                MATCH (source:Class {name: $class_name})
                WHERE (source.repository = $repo AND source.organization = $org) 
                   OR (source.source = $repo)
                MATCH (source)-[r:DEPENDS_ON]->(target:Class)
                RETURN target.name as target_class, r.type as dependency_type
                LIMIT 5
                """
                
                # Test with a sample class name
                test_class = "QuoteController"  # Adjust based on your data
                test_repo = "quoteapp"
                test_org = "scimarketplace"
                
                for query_name, query in [("old_schema", old_dep_query), ("new_schema", new_dep_query), ("mixed_schema", mixed_dep_query)]:
                    try:
                        result = session.run(query, {
                            "class_name": test_class,
                            "repo": test_repo,
                            "org": test_org
                        })
                        dependencies = [{"target_class": record["target_class"], "dependency_type": record["dependency_type"]} for record in result]
                        dependency_tests.append({
                            "query_type": query_name,
                            "query": query,
                            "results": dependencies,
                            "success": True
                        })
                        print(f"    ✅ {query_name}: {len(dependencies)} dependencies found")
                    except Exception as e:
                        dependency_tests.append({
                            "query_type": query_name,
                            "query": query,
                            "error": str(e),
                            "success": False
                        })
                        print(f"    ❌ {query_name}: {e}")
                
                results["enterprise_analysis"]["dependency_tests"] = dependency_tests
                
            except Exception as e:
                print(f"    ❌ Dependency analysis failed: {e}")
                results["enterprise_analysis"]["dependency_tests"] = []
            
            # 7. Data Sample Analysis
            print("  📊 7. Data Sample Analysis...")
            try:
                # Get sample data showing actual relationships
                data_sample_query = """
                MATCH (r:Repository)-[rel1]->(c:Class)-[rel2]->(m:Method)
                RETURN r, rel1, c, rel2, m
                LIMIT 3
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
                results["enterprise_analysis"]["data_samples"] = data_samples
                print(f"    ✅ Found {len(data_samples)} data samples")
            except Exception as e:
                print(f"    ❌ Data sample analysis failed: {e}")
                results["enterprise_analysis"]["data_samples"] = []
            
            # 8. Generate Schema Summary
            print("  📋 8. Generating Schema Summary...")
            schema_summary = {
                "total_node_types": len(results["enterprise_analysis"]["node_labels"]),
                "total_relationship_types": len(results["enterprise_analysis"]["relationship_types"]),
                "total_properties": len(results["enterprise_analysis"]["properties"]),
                "has_old_schema": len(results["enterprise_analysis"]["old_schema_nodes"]) > 0,
                "has_new_schema": len(results["enterprise_analysis"]["new_schema_nodes"]) > 0,
                "is_mixed_schema": len(results["enterprise_analysis"]["old_schema_nodes"]) > 0 and len(results["enterprise_analysis"]["new_schema_nodes"]) > 0,
                "recommended_approach": "mixed_schema" if len(results["enterprise_analysis"]["old_schema_nodes"]) > 0 and len(results["enterprise_analysis"]["new_schema_nodes"]) > 0 else "new_schema" if len(results["enterprise_analysis"]["new_schema_nodes"]) > 0 else "old_schema"
            }
            results["enterprise_analysis"]["schema_summary"] = schema_summary
            
            # Save results to JSON file
            output_file = "enterprise_neo4j_schema_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n✅ Enterprise Schema Analysis Complete!")
            print(f"📁 Results saved to: {output_file}")
            print(f"📊 Schema Summary:")
            print(f"   • Node Types: {schema_summary['total_node_types']}")
            print(f"   • Relationship Types: {schema_summary['total_relationship_types']}")
            print(f"   • Properties: {schema_summary['total_properties']}")
            print(f"   • Old Schema: {'Yes' if schema_summary['has_old_schema'] else 'No'}")
            print(f"   • New Schema: {'Yes' if schema_summary['has_new_schema'] else 'No'}")
            print(f"   • Mixed Schema: {'Yes' if schema_summary['is_mixed_schema'] else 'No'}")
            print(f"   • Recommended Approach: {schema_summary['recommended_approach']}")
            
    except Exception as e:
        print(f"❌ Error analyzing enterprise schema: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    analyze_enterprise_schema()
