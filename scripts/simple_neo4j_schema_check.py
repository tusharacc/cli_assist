#!/usr/bin/env python3
"""
Simple Neo4j Schema Check
Quick schema analysis for enterprise environment
"""

import json
from datetime import datetime
from neo4j import GraphDatabase
from src.lumos_cli.neo4j_config import Neo4jConfigManager

def quick_schema_check():
    """Quick schema check for enterprise Neo4j"""
    
    config_manager = Neo4jConfigManager()
    if not config_manager.is_configured():
        print("❌ Neo4j not configured. Run 'lumos-cli neo4j config' first.")
        return
    
    config = config_manager.load_config()
    if not config:
        print("❌ Failed to load Neo4j configuration")
        return
    
    driver = GraphDatabase.driver(config.uri, auth=(config.username, config.password))
    
    try:
        with driver.session() as session:
            print("🔍 Quick Enterprise Neo4j Schema Check...")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "neo4j_uri": config.uri,
                "quick_analysis": {}
            }
            
            # 1. Node labels
            print("  📊 Getting node labels...")
            try:
                query = """
                MATCH (n)
                WITH labels(n) as nodeLabels, n
                UNWIND nodeLabels as label
                WITH label, collect(n)[0..2] as samples
                RETURN label, 
                       count(n) as count,
                       [node in samples | properties(node)] as sample_properties
                ORDER BY count DESC
                """
                result = session.run(query)
                results["quick_analysis"]["node_labels"] = [
                    {
                        "label": record["label"], 
                        "count": record["count"],
                        "sample_properties": record["sample_properties"]
                    } 
                    for record in result
                ]
                print(f"    ✅ Found {len(results['quick_analysis']['node_labels'])} node types")
            except Exception as e:
                print(f"    ❌ Failed: {e}")
                results["quick_analysis"]["node_labels"] = []
            
            # 2. Relationship types
            print("  🔗 Getting relationship types...")
            try:
                query = """
                MATCH ()-[r]->()
                RETURN type(r) as relType, count(r) as count
                ORDER BY count DESC
                """
                result = session.run(query)
                results["quick_analysis"]["relationship_types"] = [
                    {"type": record["relType"], "count": record["count"]} 
                    for record in result
                ]
                print(f"    ✅ Found {len(results['quick_analysis']['relationship_types'])} relationship types")
            except Exception as e:
                print(f"    ❌ Failed: {e}")
                results["quick_analysis"]["relationship_types"] = []
            
            # 3. Check for old vs new schema
            print("  🔍 Checking schema types...")
            try:
                # Old schema check
                old_query = """
                MATCH (n)
                WHERE n.repository IS NOT NULL OR n.organization IS NOT NULL
                RETURN labels(n) as labels, count(n) as count
                ORDER BY count DESC
                """
                old_result = session.run(old_query)
                old_schema = [{"labels": record["labels"], "count": record["count"]} for record in old_result]
                
                # New schema check
                new_query = """
                MATCH (n)
                WHERE n.namespace IS NOT NULL OR n.source IS NOT NULL
                RETURN labels(n) as labels, count(n) as count
                ORDER BY count DESC
                """
                new_result = session.run(new_query)
                new_schema = [{"labels": record["labels"], "count": record["count"]} for record in new_result]
                
                results["quick_analysis"]["old_schema"] = old_schema
                results["quick_analysis"]["new_schema"] = new_schema
                
                print(f"    ✅ Old schema nodes: {sum(r['count'] for r in old_schema)}")
                print(f"    ✅ New schema nodes: {sum(r['count'] for r in new_schema)}")
                
            except Exception as e:
                print(f"    ❌ Failed: {e}")
                results["quick_analysis"]["old_schema"] = []
                results["quick_analysis"]["new_schema"] = []
            
            # 4. Test dependency queries
            print("  🔄 Testing dependency queries...")
            try:
                # Test with a common class name
                test_queries = [
                    {
                        "name": "old_schema_deps",
                        "query": """
                        MATCH (source:Class {name: $class_name, repository: $repo, organization: $org})
                        MATCH (source)-[r:DEPENDS_ON]->(target:Class)
                        RETURN target.name as target_class, r.type as dependency_type
                        LIMIT 3
                        """
                    },
                    {
                        "name": "new_schema_deps", 
                        "query": """
                        MATCH (source:Class {name: $class_name, source: $repo})
                        MATCH (source)-[r:DEPENDS_ON]->(target:Class)
                        RETURN target.name as target_class, r.type as dependency_type
                        LIMIT 3
                        """
                    },
                    {
                        "name": "mixed_schema_deps",
                        "query": """
                        MATCH (source:Class {name: $class_name})
                        WHERE (source.repository = $repo AND source.organization = $org) 
                           OR (source.source = $repo)
                        MATCH (source)-[r:DEPENDS_ON]->(target:Class)
                        RETURN target.name as target_class, r.type as dependency_type
                        LIMIT 3
                        """
                    }
                ]
                
                dependency_tests = []
                for test in test_queries:
                    try:
                        result = session.run(test["query"], {
                            "class_name": "QuoteController",  # Adjust as needed
                            "repo": "quoteapp",
                            "org": "scimarketplace"
                        })
                        deps = [{"target_class": record["target_class"], "dependency_type": record["dependency_type"]} for record in result]
                        dependency_tests.append({
                            "name": test["name"],
                            "success": True,
                            "dependencies_found": len(deps),
                            "dependencies": deps
                        })
                        print(f"    ✅ {test['name']}: {len(deps)} dependencies")
                    except Exception as e:
                        dependency_tests.append({
                            "name": test["name"],
                            "success": False,
                            "error": str(e)
                        })
                        print(f"    ❌ {test['name']}: {e}")
                
                results["quick_analysis"]["dependency_tests"] = dependency_tests
                
            except Exception as e:
                print(f"    ❌ Dependency tests failed: {e}")
                results["quick_analysis"]["dependency_tests"] = []
            
            # Save results
            output_file = "enterprise_neo4j_quick_check.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n✅ Quick Schema Check Complete!")
            print(f"📁 Results saved to: {output_file}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    quick_schema_check()
