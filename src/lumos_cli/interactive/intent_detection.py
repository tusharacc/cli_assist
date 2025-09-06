"""
Intent detection for interactive mode
"""

import re
from typing import Dict

def detect_command_intent(user_input: str) -> Dict[str, any]:
    """Detect command intent from natural language"""
    lower_input = user_input.lower()
    
    # GitHub patterns (high priority)
    github_patterns = [
        r'(github|git hub)\s+(.+)',
        r'(clone|pull|fetch)\s+(.+)',
        r'(pr|pull request|pullrequest)\s+(.+)',
        r'(repository|repo)\s+(.+)',
        r'(branch|commit|push|merge)\s+(.+)',
        r'(tusharacc|scimarketplace|microsoft|github\.com)\s+(.+)',
        r'(.+)/(.+)\s+(pr|pull request|clone|branch)',
        r'(check|show|list|get)\s+(pr|pull request|repository|repo)\s+(.+)',
        r'(is there|are there|any)\s+(pr|pull request)\s+(.+)',
        r'(latest|recent)\s+(commit|pr|pull request)\s+(.+)'
    ]
    
    for pattern in github_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'github',
                'query': user_input,
                'confidence': 0.9
            }

    # Jenkins patterns (high priority)
    jenkins_patterns = [
        r'(jenkins|ci|cd|build|pipeline)\s+(.+)',
        r'(failed|failure|broken|error).*(job|build|pipeline)',
        r'(running|executing|building|in progress).*(job|build|pipeline)',
        r'(repository|repo).*(branch|rc1|rc2|rc3|rc4)',
        r'(build parameters|params).*(job|build)',
        r'(console|log|analyze|why).*(failed|failure)',
        r'(deploy-all|scimarketplace).*(job|build)',
        r'(last|past)\s+(\d+)\s*(hours?|minutes?)\s*(failed|running|jobs?)',
        r'(job|build)\s+(\d+)\s*(parameters|console|failed|why)',
        r'(externaldata|addresssearch).*(rc1|rc2|rc3|rc4)'
    ]
    
    for pattern in jenkins_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'jenkins',
                'query': user_input,
                'confidence': 0.9
            }

    # JIRA patterns (high priority)
    jira_ticket_pattern = r'\b([A-Z]+-\d+)\b'
    if re.search(jira_ticket_pattern, user_input, re.IGNORECASE):
        return {
            'type': 'jira',
            'query': user_input,
            'confidence': 0.9
        }

    if 'jira' in lower_input:
        jira_keywords = ['ticket', 'sprint', 'issue', 'board', 'project']
        if any(keyword in lower_input for keyword in jira_keywords):
            return {
                'type': 'jira',
                'query': user_input,
                'confidence': 0.9
            }
    
    # Edit patterns
    edit_patterns = [
        r'^(edit|modify|update|change|fix)\s+(.+)',
        r'^add\s+(.+)\s+to\s+(.+)',
        r'^(.+)\s+(add|implement|improve)\s+(.+)'
    ]
    
    # Plan patterns  
    plan_patterns = [
        r'^(plan|design|architect|create plan for)\s+(.+)',
        r'^how (do i|to|can i)\s+(.+)',
        r'^(steps|approach|strategy)\s+(for|to)\s+(.+)'
    ]
    
    # Review patterns
    review_patterns = [
        r'^(review|check|analyze|inspect)\s+(.+)',
        r'^look at\s+(.+)',
        r'^what.*wrong.*(with|in)\s+(.+)'
    ]
    
    # Start patterns
    start_patterns = [
        r'^(start|run|launch)\s+(.*)',
        r'^start\s*(the\s*)?(app|server|application)',
        r'^(npm|python|node|flask)\s+.*'
    ]
    
    # Shell/Command patterns - detect shell commands
    shell_patterns = [
        r'^(run|execute|shell)\s+(.+)',
        r'^(ls|dir|cd|pwd|mkdir|rmdir|cp|mv|rm|del)(\s+.*)?$',
        r'^(git|npm|pip|python|node|java|gcc|make|cmake|docker|kubectl)\s+.*',
        r'^(curl|wget|ssh|scp|rsync)\s+.*',
        r'^(ps|top|htop|kill|killall|chmod|chown|sudo)\s*.*',
        r'^(cat|grep|find|sort|wc|head|tail|less|more)\s+.*',
        r'^(echo|printf|which|whereis|whoami|date|uptime)\s*.*'
    ]
    
    # Error/Fix patterns - enhanced to catch more debugging requests
    fix_patterns = [
        r'^(fix|debug|solve|resolve)\s+(.+)',
        r'^(error|exception|traceback|failed).*',
        r'.*not working.*',
        r'.*broken.*',
        r'.*(error|exception).*',
        r'^(why|what).*(wrong|issue|problem|error).*',
        r'^(help|assistance).*(bug|issue|problem|error|debug).*',
        r'.*(bug|issue|problem).*(in|with|on).*',
        r'^(there is|i have|having).*(issue|problem|error|bug).*',
        r'.*(doesnt work|doesn\'t work|not functioning|failing).*',
        r'^(my|the).*(app|code|program|function).*(bug|issue|problem|error|broken|not working).*'
    ]
    
    # Check for edit intent
    for pattern in edit_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'edit',
                'instruction': user_input,
                'confidence': 0.8
            }
    
    # Check for plan intent
    for pattern in plan_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'plan', 
                'instruction': match.group(2) if len(match.groups()) >= 2 else user_input,
                'confidence': 0.8
            }
    
    # Check for review intent
    for pattern in review_patterns:
        match = re.search(pattern, lower_input)
        if match:
            file_part = match.group(2) if len(match.groups()) >= 2 else ''
            return {
                'type': 'review',
                'file': file_part,
                'instruction': user_input,
                'confidence': 0.7
            }
    
    # Check for start intent
    for pattern in start_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'start',
                'instruction': user_input,
                'confidence': 0.8
            }
    
    # Check for shell/command intent
    for pattern in shell_patterns:
        match = re.search(pattern, lower_input)
        if match:
            # Extract the actual command (remove "run", "execute", "shell" prefixes)
            if pattern.startswith(r'^(run|execute|shell)'):
                command = match.group(2) if len(match.groups()) >= 2 else user_input
            else:
                command = user_input
            
            # Fix: Add python prefix for .py files that don't already have it
            command = command.strip()
            if '.py' in command and not command.startswith('python '):
                # Extract Python filename from command using regex
                py_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', command)
                if py_match:
                    py_filename = py_match.group(1)
                    command = f"python {py_filename}"
            
            return {
                'type': 'shell',
                'command': command,
                'instruction': user_input,
                'confidence': 0.9
            }
    
    # Check for fix/error intent
    for pattern in fix_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'fix',
                'instruction': user_input,
                'confidence': 0.8
            }
    
    return {'type': 'chat', 'instruction': user_input}
