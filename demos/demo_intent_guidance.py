#!/usr/bin/env python3
"""
Demo of Enhanced Intent Guidance for Lumos CLI
Shows what happens when users forget explicit intent prefixes
"""

import sys
import os
sys.path.append('src')

def demo_intent_guidance():
    """Demonstrate the enhanced intent guidance system"""
    
    print("🎯 Enhanced Intent Guidance Demo for Lumos CLI")
    print("=" * 60)
    
    print("\n📋 What happens when you forget explicit intent prefixes?")
    print("-" * 60)
    
    # Simulate different scenarios
    scenarios = [
        {
            "query": "get me the latest PR from scimarketplace/externaldata",
            "detected_intent": "github",
            "confidence": 0.6,
            "method": "regex"
        },
        {
            "query": "show me the last 5 builds from jenkins folder deploy-all", 
            "detected_intent": "jenkins",
            "confidence": 0.5,
            "method": "llm"
        },
        {
            "query": "what are the dependencies of class UserService",
            "detected_intent": "neo4j", 
            "confidence": 0.4,
            "method": "llm"
        },
        {
            "query": "show me resource utilization for SCI Market Place",
            "detected_intent": "appdynamics",
            "confidence": 0.3,
            "method": "llm"
        },
        {
            "query": "get me ticket ABC-123 details",
            "detected_intent": "jira",
            "confidence": 0.8,
            "method": "regex"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Query: \"{scenario['query']}\"")
        print(f"   Detected Intent: {scenario['detected_intent']}")
        print(f"   Confidence: {scenario['confidence']:.1%}")
        print(f"   Method: {scenario['method']}")
        
        # Show what happens based on confidence
        if scenario['confidence'] < 0.7:
            print(f"   🎯 Action: SUGGEST EXPLICIT INTENT")
            print(f"   💡 Tip: For faster routing, you can use:")
            print(f"   [bright_cyan]/{scenario['detected_intent']} {scenario['query']}[/bright_cyan]")
            print(f"   [dim]Confidence: {scenario['confidence']:.1%} | Method: {scenario['method']}[/dim]")
        else:
            print(f"   ✅ Action: PROCEED WITH NATURAL LANGUAGE")
            print(f"   [green]High confidence detected, proceeding normally[/green]")
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced Behavior Flow:")
    print("=" * 60)
    
    flow = """
    1. User Input: "get me the latest PR from scimarketplace/externaldata"
       │
       ├─ Explicit Intent? (/github, /jenkins, etc.)
       │  └─ YES → Direct routing to service agent
       │
       └─ NO → Natural Language Detection
          │
          ├─ High Confidence (≥70%) → Proceed with detected intent
          │
          └─ Low Confidence (<70%) → Show helpful guidance:
             │
             ├─ 💡 Tip: "For faster routing, you can use:"
             ├─ 🔧 Suggestion: "/github get me the latest PR from scimarketplace/externaldata"
             ├─ 📊 Info: "Confidence: 60% | Method: regex"
             └─ ✅ Proceed with natural language anyway
    """
    
    print(flow)
    
    print("\n" + "=" * 60)
    print("🚀 Benefits of Enhanced Guidance:")
    print("=" * 60)
    
    benefits = [
        ("🎓 Learning", "Users learn about explicit prefixes through helpful tips"),
        ("⚡ Performance", "Suggests faster routing when confidence is low"),
        ("🔧 Control", "Users can choose between speed and natural language"),
        ("📊 Transparency", "Shows confidence levels and detection methods"),
        ("🔄 Flexibility", "Still works with natural language, just with guidance"),
        ("💡 Discoverability", "Users discover explicit prefixes organically"),
        ("🎯 Precision", "Reduces ambiguity by suggesting explicit routing")
    ]
    
    for benefit, description in benefits:
        print(f"\n{benefit}")
        print(f"   {description}")
    
    print("\n" + "=" * 60)
    print("🔧 Implementation Details:")
    print("=" * 60)
    
    implementation = """
    # Check confidence before processing
    if detected_command.get('confidence', 0) < 0.7 and detected_command['type'] in ['github', 'jenkins', 'jira', 'neo4j', 'appdynamics']:
        _suggest_explicit_intent(user_input, detected_command)
    
    # Then proceed with normal routing
    if detected_command['type'] == 'github':
        _interactive_github(detected_command['query'])
    # ... etc
    """
    
    print(implementation)
    
    print("\n🎯 This enhanced approach provides:")
    print("   • Helpful guidance when confidence is low")
    print("   • Learning opportunities for users")
    print("   • Better performance suggestions")
    print("   • Transparency about detection methods")
    print("   • Still maintains full natural language support")

if __name__ == "__main__":
    demo_intent_guidance()
