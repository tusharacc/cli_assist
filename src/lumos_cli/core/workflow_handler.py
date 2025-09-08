#!/usr/bin/env python3
"""
Workflow handler for complex multi-system operations
"""

import re
from typing import Dict, List, Optional
from ..clients.github_client import GitHubClient
from ..clients.jira_client import JiraClient
from ..clients.neo4j_client import Neo4jClient
from ..utils.debug_logger import debug_logger

class WorkflowHandler:
    """Handles complex workflows spanning multiple systems"""
    
    def __init__(self):
        self.github_client = GitHubClient()
        self.jira_client = JiraClient()
        self.neo4j_client = Neo4jClient()
    
    def execute_workflow(self, workflow_type: str, query: str, systems: List[str]) -> Dict:
        """Execute a complex workflow"""
        debug_logger.log_function_call("WorkflowHandler.execute_workflow", 
                                     kwargs={"workflow_type": workflow_type, "query": query, "systems": systems})
        
        if workflow_type == 'multi_system':
            return self._execute_multi_system_workflow(query, systems)
        
        return {
            'success': False,
            'error': f'Unknown workflow type: {workflow_type}'
        }
    
    def _execute_multi_system_workflow(self, query: str, systems: List[str]) -> Dict:
        """Execute workflows that span multiple systems"""
        results = {
            'workflow': 'multi_system',
            'systems': systems,
            'steps': [],
            'data': {},
            'success': True
        }
        
        try:
            # Step 1: Extract GitHub data (commits/PRs)
            if 'github' in systems:
                github_data = self._extract_github_data(query)
                if github_data:
                    results['steps'].append('github_data_extracted')
                    results['data']['github'] = github_data
                    
                    # Extract Jira tickets from GitHub data
                    tickets = self._extract_jira_tickets_from_github(github_data)
                    if tickets:
                        results['data']['jira_tickets'] = tickets
                        results['steps'].append('jira_tickets_extracted')
            
            # Step 2: Get Jira ticket details
            if 'jira' in systems and 'jira_tickets' in results['data']:
                jira_data = self._get_jira_ticket_details(results['data']['jira_tickets'])
                if jira_data:
                    results['data']['jira'] = jira_data
                    results['steps'].append('jira_details_retrieved')
            
            # Step 3: Analyze impact using Neo4j
            if 'neo4j' in systems:
                neo4j_data = self._analyze_impact_with_neo4j(query, results['data'])
                if neo4j_data:
                    results['data']['neo4j'] = neo4j_data
                    results['steps'].append('impact_analysis_completed')
            
            # Step 4: Generate comprehensive report
            report = self._generate_workflow_report(results['data'], results['steps'])
            results['report'] = report
            
        except Exception as e:
            debug_logger.error(f"Workflow execution failed: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        debug_logger.log_function_return("WorkflowHandler.execute_workflow", 
                                       f"Workflow completed: {len(results['steps'])} steps")
        return results
    
    def _extract_github_data(self, query: str) -> Optional[Dict]:
        """Extract GitHub data based on query"""
        # Parse query to extract org/repo and operation type
        from .github_query_parser import GitHubQueryParser
        parser = GitHubQueryParser()
        parsed = parser.parse_query(query)
        
        if not parsed or not parsed.get('org_repo'):
            return None
        
        org, repo = parsed['org_repo'].split('/', 1)
        
        # Determine operation type
        if 'commit' in query.lower():
            # Get commits
            commits = self.github_client.list_commits(org, repo, per_page=5)
            return {
                'type': 'commits',
                'org': org,
                'repo': repo,
                'data': commits
            }
        elif 'pr' in query.lower() or 'pull request' in query.lower():
            # Get PRs
            prs = self.github_client.list_pull_requests(org, repo)
            return {
                'type': 'pull_requests',
                'org': org,
                'repo': repo,
                'data': prs
            }
        
        return None
    
    def _extract_jira_tickets_from_github(self, github_data: Dict) -> List[str]:
        """Extract Jira ticket numbers from GitHub data"""
        tickets = []
        
        if github_data['type'] == 'commits':
            for commit in github_data['data']:
                message = commit.get('commit', {}).get('message', '')
                # Look for Jira ticket patterns (e.g., ABC-123, DEF-456)
                ticket_matches = re.findall(r'\b([A-Z]+-\d+)\b', message)
                tickets.extend(ticket_matches)
        
        elif github_data['type'] == 'pull_requests':
            for pr in github_data['data']:
                title = pr.get('title', '')
                body = pr.get('body', '')
                # Look for Jira ticket patterns in title and body
                ticket_matches = re.findall(r'\b([A-Z]+-\d+)\b', f"{title} {body}")
                tickets.extend(ticket_matches)
        
        return list(set(tickets))  # Remove duplicates
    
    def _get_jira_ticket_details(self, tickets: List[str]) -> Dict:
        """Get detailed information for Jira tickets"""
        ticket_details = {}
        
        for ticket in tickets:
            try:
                # Get ticket details from Jira
                ticket_info = self.jira_client.get_ticket(ticket)
                if ticket_info:
                    ticket_details[ticket] = {
                        'summary': ticket_info.get('summary', ''),
                        'description': ticket_info.get('description', ''),
                        'status': ticket_info.get('status', ''),
                        'assignee': ticket_info.get('assignee', ''),
                        'priority': ticket_info.get('priority', ''),
                        'labels': ticket_info.get('labels', [])
                    }
            except Exception as e:
                debug_logger.warning(f"Failed to get Jira ticket {ticket}: {e}")
                ticket_details[ticket] = {'error': str(e)}
        
        return ticket_details
    
    def _analyze_impact_with_neo4j(self, query: str, workflow_data: Dict) -> Dict:
        """Analyze impact using Neo4j graph database"""
        impact_analysis = {
            'affected_repositories': [],
            'affected_classes': [],
            'affected_functions': [],
            'dependency_chain': [],
            'risk_assessment': 'low'
        }
        
        try:
            # Extract changed files/classes from GitHub data
            changed_items = []
            if 'github' in workflow_data:
                github_data = workflow_data['github']
                if github_data['type'] == 'commits':
                    for commit in github_data['data']:
                        files = commit.get('files', [])
                        for file_info in files:
                            changed_items.append({
                                'file': file_info.get('filename', ''),
                                'status': file_info.get('status', ''),
                                'changes': file_info.get('additions', 0) + file_info.get('deletions', 0)
                            })
            
            # Query Neo4j for impact analysis
            if changed_items:
                # This would be implemented based on your Neo4j schema
                # For now, return a mock analysis
                impact_analysis = self.neo4j_client.analyze_impact(changed_items)
            
        except Exception as e:
            debug_logger.warning(f"Neo4j impact analysis failed: {e}")
            impact_analysis['error'] = str(e)
        
        return impact_analysis
    
    def _generate_workflow_report(self, data: Dict, steps: List[str]) -> str:
        """Generate a comprehensive workflow report"""
        report = []
        report.append("🔍 **Multi-System Workflow Analysis**")
        report.append("=" * 50)
        
        # GitHub section
        if 'github' in data:
            github_data = data['github']
            report.append(f"\n📁 **GitHub Analysis** ({github_data['org']}/{github_data['repo']})")
            if github_data['type'] == 'commits':
                report.append(f"   • Found {len(github_data['data'])} recent commits")
            elif github_data['type'] == 'pull_requests':
                report.append(f"   • Found {len(github_data['data'])} pull requests")
        
        # Jira section
        if 'jira' in data:
            jira_data = data['jira']
            report.append(f"\n🎫 **Jira Tickets** ({len(jira_data)} tickets)")
            for ticket, details in jira_data.items():
                if 'error' not in details:
                    report.append(f"   • {ticket}: {details.get('summary', 'No summary')}")
                    report.append(f"     Status: {details.get('status', 'Unknown')}")
                    report.append(f"     Priority: {details.get('priority', 'Unknown')}")
        
        # Neo4j section
        if 'neo4j' in data:
            neo4j_data = data['neo4j']
            report.append(f"\n🕸️ **Impact Analysis**")
            if 'affected_repositories' in neo4j_data:
                report.append(f"   • Affected Repositories: {len(neo4j_data['affected_repositories'])}")
            if 'affected_classes' in neo4j_data:
                report.append(f"   • Affected Classes: {len(neo4j_data['affected_classes'])}")
            if 'risk_assessment' in neo4j_data:
                report.append(f"   • Risk Level: {neo4j_data['risk_assessment'].upper()}")
        
        # Workflow steps
        report.append(f"\n⚡ **Workflow Steps Completed**")
        for i, step in enumerate(steps, 1):
            report.append(f"   {i}. {step.replace('_', ' ').title()}")
        
        return "\n".join(report)
