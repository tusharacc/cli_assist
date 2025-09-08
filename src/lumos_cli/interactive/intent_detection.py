"""
Intent detection for Lumos CLI interactive mode
"""

import re
from typing import Dict, Any

def detect_intent(user_input: str) -> Dict[str, Any]:
    """
    Detect user intent from natural language input
    
    Args:
        user_input: User's natural language input
        
    Returns:
        Dictionary containing intent type, confidence, and extracted data
    """
    user_lower = user_input.lower()
    
    # GitHub patterns
    github_patterns = [
        r'\b(github|git|repo|repository|pull request|pr|commit|clone|fetch|pull)\b',
        r'\b(org|organization|scimarketplace|tusharacc)\b',
        r'\b(rc1|rc2|rc3|rc4|main|master|develop|dev)\b',
        r'\b(latest|last|recent)\s+(pr|pull request|commit|commits)\b'
    ]
    
    # Jenkins patterns
    jenkins_patterns = [
        r'\b(jenkins|build|job|pipeline|ci|cd)\b',
        r'\b(failed|success|running|pending|aborted)\s+(build|job)\b',
        r'\b(deploy-all|addresssearch|scimarketplace)\b',
        r'\b(build number|job number|build \d+|job \d+)\b'
    ]
    
    # Jira patterns
    jira_patterns = [
        r'\b(jira|ticket|issue|bug|story|task)\b',
        r'\b([A-Z]+-\d+)\b',  # JIRA ticket key pattern
        r'\b(comment|comments|extract comment)\b',
        r'\b(assignee|reporter|status|priority)\b'
    ]
    
    # Neo4j patterns
    neo4j_patterns = [
        r'\b(neo4j|graph|database|dependencies|depend|impact|affected)\b',
        r'\b(class|method|function)\s+([A-Z][a-zA-Z0-9]+)\b',
        r'\b(dependency analysis|impact analysis)\b'
    ]
    
    # AppDynamics patterns
    appdynamics_patterns = [
        r'\b(appdynamics|appd|monitoring|metrics|performance)\b',
        r'\b(resource utilization|business transaction|alert|alerts)\b',
        r'\b(cpu|memory|disk|network)\s+(usage|utilization)\b'
    ]
    
    # Code patterns
    code_patterns = [
        r'\b(code|programming|program|develop|development)\b',
        r'\b(edit|modify|change|update|fix|debug|refactor)\b',
        r'\b(generate|create|write|implement)\s+(code|function|class|method)\b',
        r'\b(test|testing|unit test|integration test)\b',
        r'\b(analyze|review|inspect|examine)\s+(code|file|function)\b'
    ]
    
    # Legacy patterns (for backward compatibility)
    edit_patterns = [
        r'\b(edit|modify|change|update|fix)\b',
        r'\b(add|remove|delete|insert|replace)\b',
        r'\b(error handling|logging|validation|authentication)\b'
    ]
    
    plan_patterns = [
        r'\b(plan|planning|design|architecture|structure)\b',
        r'\b(how to|how do i|what should|what would)\b',
        r'\b(implement|create|build|develop)\s+(a|an|the)\b'
    ]
    
    review_patterns = [
        r'\b(review|analyze|inspect|examine|check)\b',
        r'\b(code quality|best practices|improvements)\b',
        r'\b(security|performance|maintainability)\b'
    ]
    
    start_patterns = [
        r'\b(start|begin|launch|run|execute)\b',
        r'\b(application|app|server|service|process)\b'
    ]
    
    fix_patterns = [
        r'\b(fix|repair|resolve|solve|debug)\b',
        r'\b(error|bug|issue|problem|fault)\b',
        r'\b(not working|broken|failing|crashing)\b'
    ]
    
    shell_patterns = [
        r'\b(run|execute|command|shell|terminal)\b',
        r'\b(ls|cd|mkdir|rm|cp|mv|grep|find)\b',
        r'\b(python|node|npm|pip|git)\b'
    ]
    
    # Check patterns and calculate confidence
    intent_scores = {}
    
    # GitHub
    github_score = sum(1 for pattern in github_patterns if re.search(pattern, user_lower))
    if github_score > 0:
        intent_scores['github'] = github_score / len(github_patterns)
    
    # Jenkins
    jenkins_score = sum(1 for pattern in jenkins_patterns if re.search(pattern, user_lower))
    if jenkins_score > 0:
        intent_scores['jenkins'] = jenkins_score / len(jenkins_patterns)
    
    # Jira
    jira_score = sum(1 for pattern in jira_patterns if re.search(pattern, user_lower))
    if jira_score > 0:
        intent_scores['jira'] = jira_score / len(jira_patterns)
    
    # Neo4j
    neo4j_score = sum(1 for pattern in neo4j_patterns if re.search(pattern, user_lower))
    if neo4j_score > 0:
        intent_scores['neo4j'] = neo4j_score / len(neo4j_patterns)
    
    # AppDynamics
    appdynamics_score = sum(1 for pattern in appdynamics_patterns if re.search(pattern, user_lower))
    if appdynamics_score > 0:
        intent_scores['appdynamics'] = appdynamics_score / len(appdynamics_patterns)
    
    # Code
    code_score = sum(1 for pattern in code_patterns if re.search(pattern, user_lower))
    if code_score > 0:
        intent_scores['code'] = code_score / len(code_patterns)
    
    # Legacy patterns
    edit_score = sum(1 for pattern in edit_patterns if re.search(pattern, user_lower))
    if edit_score > 0:
        intent_scores['edit'] = edit_score / len(edit_patterns)
    
    plan_score = sum(1 for pattern in plan_patterns if re.search(pattern, user_lower))
    if plan_score > 0:
        intent_scores['plan'] = plan_score / len(plan_patterns)
    
    review_score = sum(1 for pattern in review_patterns if re.search(pattern, user_lower))
    if review_score > 0:
        intent_scores['review'] = review_score / len(review_patterns)
    
    start_score = sum(1 for pattern in start_patterns if re.search(pattern, user_lower))
    if start_score > 0:
        intent_scores['start'] = start_score / len(start_patterns)
    
    fix_score = sum(1 for pattern in fix_patterns if re.search(pattern, user_lower))
    if fix_score > 0:
        intent_scores['fix'] = fix_score / len(fix_patterns)
    
    shell_score = sum(1 for pattern in shell_patterns if re.search(pattern, user_lower))
    if shell_score > 0:
        intent_scores['shell'] = shell_score / len(shell_patterns)
    
    # Determine the best intent
    if intent_scores:
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent]
        
        # Extract additional data based on intent
        extracted_data = {}
        
        if best_intent == 'github':
            # Extract org/repo
            org_repo_match = re.search(r'\b([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)\b', user_input)
            if org_repo_match:
                extracted_data['org_repo'] = org_repo_match.group(1)
            
            # Extract branch
            branch_match = re.search(r'\b(rc1|rc2|rc3|rc4|main|master|develop|dev)\b', user_lower)
            if branch_match:
                extracted_data['branch'] = branch_match.group(1)
            
            # Extract commit SHA
            sha_match = re.search(r'\b([a-f0-9]{7,40})\b', user_input)
            if sha_match:
                extracted_data['commit_sha'] = sha_match.group(1)
        
        elif best_intent == 'jenkins':
            # Extract folder/job names
            folder_match = re.search(r'\b(deploy-all|addresssearch|scimarketplace)\b', user_lower)
            if folder_match:
                extracted_data['folder'] = folder_match.group(1)
            
            # Extract build number
            build_match = re.search(r'\b(build|job)\s+(\d+)\b', user_lower)
            if build_match:
                extracted_data['build_number'] = int(build_match.group(2))
        
        elif best_intent == 'jira':
            # Extract ticket key
            ticket_match = re.search(r'\b([A-Z]+-\d+)\b', user_input)
            if ticket_match:
                extracted_data['ticket_key'] = ticket_match.group(1)
        
        elif best_intent == 'neo4j':
            # Extract class/method names
            class_match = re.search(r'\bclass\s+([A-Z][a-zA-Z0-9]+)\b', user_input)
            if class_match:
                extracted_data['class_name'] = class_match.group(1)
            
            method_match = re.search(r'\bmethod\s+([a-zA-Z][a-zA-Z0-9]*)\b', user_input)
            if method_match:
                extracted_data['method_name'] = method_match.group(1)
        
        elif best_intent in ['edit', 'plan', 'review', 'fix']:
            # Extract instruction
            extracted_data['instruction'] = user_input
        
        elif best_intent == 'start':
            # Extract command
            extracted_data['instruction'] = user_input
        
        elif best_intent == 'shell':
            # Extract command
            extracted_data['command'] = user_input
        
        return {
            'type': best_intent,
            'confidence': confidence,
            'query': user_input,
            **extracted_data
        }
    
    # Default to chat if no intent detected
    return {
        'type': 'chat',
        'confidence': 0.0,
        'query': user_input
    }