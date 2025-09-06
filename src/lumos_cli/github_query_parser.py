#!/usr/bin/env python3
"""
Hybrid GitHub query parsing using both text patterns and LLM-based extraction
"""

import re
import json
from typing import Dict, Optional, Tuple, List
from .client import LLMRouter
from .debug_logger import debug_logger

class GitHubQueryParser:
    """Hybrid GitHub query parser using text patterns and LLM extraction"""
    
    def __init__(self):
        self.llm_router = LLMRouter()
        self.debug_logger = debug_logger
        
    def parse_query(self, query: str) -> Dict[str, any]:
        """
        Parse GitHub query using hybrid approach:
        1. Text pattern matching (fast, reliable for simple cases)
        2. LLM extraction (robust for complex queries)
        3. Fallback logic with confidence scoring
        """
        self.debug_logger.info(f"Starting hybrid parsing for query: {query}")
        
        # Step 1: Try text pattern matching first
        text_result = self._parse_with_text_patterns(query)
        text_confidence = self._calculate_text_confidence(text_result, query)
        
        self.debug_logger.info(f"Text parsing result: {text_result}, confidence: {text_confidence}")
        
        # Step 2: Try LLM extraction
        llm_result = self._parse_with_llm(query)
        llm_confidence = self._calculate_llm_confidence(llm_result, query)
        
        self.debug_logger.info(f"LLM parsing result: {llm_result}, confidence: {llm_confidence}")
        
        # Step 3: Decision logic
        final_result = self._decide_parsing_result(
            text_result, text_confidence,
            llm_result, llm_confidence,
            query
        )
        
        self.debug_logger.info(f"Final parsing result: {final_result}")
        return final_result
    
    def _parse_with_text_patterns(self, query: str) -> Optional[Dict[str, str]]:
        """Parse using text patterns (existing logic)"""
        lower_query = query.lower()
        org_repo = None
        
        # Pattern 1: Direct format "org/repo"
        org_repo_pattern = r'([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)'
        match = re.search(org_repo_pattern, query)
        if match:
            org_repo = f"{match.group(1)}/{match.group(2)}"
        
        # Pattern 2: "repository X in organization Y"
        if not org_repo:
            repo_org_pattern = r'repository\s+([a-zA-Z0-9_-]+)\s+in\s+organization\s+([a-zA-Z0-9_-]+)'
            match = re.search(repo_org_pattern, lower_query)
            if match:
                repo_name = match.group(1)
                org_name = match.group(2)
                org_repo = f"{org_name}/{repo_name}"
        
        # Pattern 3: "for repository X in organization Y"
        if not org_repo:
            for_repo_org_pattern = r'for\s+repository\s+([a-zA-Z0-9_-]+)\s+in\s+organization\s+([a-zA-Z0-9_-]+)'
            match = re.search(for_repo_org_pattern, lower_query)
            if match:
                repo_name = match.group(1)
                org_name = match.group(2)
                org_repo = f"{org_name}/{repo_name}"
        
        # Pattern 4: "organization X repository Y"
        if not org_repo:
            org_repo_pattern2 = r'organization\s+([a-zA-Z0-9_-]+)\s+repository\s+([a-zA-Z0-9_-]+)'
            match = re.search(org_repo_pattern2, lower_query)
            if match:
                org_name = match.group(1)
                repo_name = match.group(2)
                org_repo = f"{org_name}/{repo_name}"
        
        # Pattern 5: Simple format "github org repo"
        if not org_repo:
            words = query.split()
            if len(words) >= 3:
                for i, word in enumerate(words):
                    if word.lower() in ['github', 'repository', 'repo'] and i + 2 < len(words):
                        next_words = words[i+1:i+3]
                        if not any(w.lower() in ['in', 'organization', 'org'] for w in next_words):
                            org_repo = f"{words[i+1]}/{words[i+2]}"
                            break
        
        # Pattern 6: "for X in Y"
        if not org_repo:
            simple_pattern = r'for\s+([a-zA-Z0-9_-]+)\s+in\s+([a-zA-Z0-9_-]+)'
            match = re.search(simple_pattern, lower_query)
            if match:
                repo_name = match.group(1)
                org_name = match.group(2)
                org_repo = f"{org_name}/{repo_name}"
        
        # Pattern 7: "X repo in Y org"
        if not org_repo:
            repo_org_simple = r'([a-zA-Z0-9_-]+)\s+repo\s+in\s+([a-zA-Z0-9_-]+)\s+org'
            match = re.search(repo_org_simple, lower_query)
            if match:
                repo_name = match.group(1)
                org_name = match.group(2)
                org_repo = f"{org_name}/{repo_name}"
        
        # Pattern 8: "X in Y"
        if not org_repo:
            simple_in_pattern = r'([a-zA-Z0-9_-]+)\s+in\s+([a-zA-Z0-9_-]+)'
            match = re.search(simple_in_pattern, lower_query)
            if match:
                repo_name = match.group(1)
                org_name = match.group(2)
                org_repo = f"{org_name}/{repo_name}"
        
        if org_repo:
            parts = org_repo.split('/')
            return {
                'organization': parts[0],
                'repository': parts[1],
                'org_repo': org_repo,
                'method': 'text_pattern'
            }
        
        return None
    
    def _parse_with_llm(self, query: str) -> Optional[Dict[str, str]]:
        """Parse using LLM extraction"""
        try:
            # Try reasoning model first if available
            models_to_try = ["llama3.2:latest", "devstral", "llama3.1:latest"]
            
            for model in models_to_try:
                try:
                    prompt = f"""
You are a GitHub query parser. Extract the organization and repository from this query: "{query}"

Think step by step:
1. Look for organization name (usually comes before repository)
2. Look for repository name (usually comes after organization)
3. Consider context clues like "in organization", "repository", "org"
4. Make your best guess if unclear

Return ONLY a JSON object with this exact format:
{{
    "organization": "org_name",
    "repository": "repo_name",
    "confidence": 0.95
}}

Rules:
- Extract the organization name and repository name
- If unclear, make your best guess
- Confidence should be 0.0 to 1.0
- Return only the JSON, no other text
- If you cannot extract both, return null
"""
                    
                    messages = [{"role": "user", "content": prompt}]
                    response = self.llm_router.chat(messages)
                    
                    if response:
                        # Try to parse JSON response
                        try:
                            result = json.loads(response.strip())
                            if result and 'organization' in result and 'repository' in result:
                                result['org_repo'] = f"{result['organization']}/{result['repository']}"
                                result['method'] = f'llm_{model.replace(":", "_")}'
                                return result
                        except json.JSONDecodeError:
                            self.debug_logger.warning(f"Failed to parse LLM JSON response from {model}: {response}")
                            continue
                    
                except Exception as e:
                    self.debug_logger.warning(f"Model {model} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.debug_logger.error(f"LLM parsing failed: {e}")
            return None
    
    def _calculate_text_confidence(self, result: Optional[Dict], query: str) -> float:
        """Calculate confidence score for text pattern result"""
        if not result:
            return 0.0
        
        # Base confidence for text patterns
        confidence = 0.8
        
        # Boost confidence for direct format
        if '/' in query and not any(word in query.lower() for word in ['repository', 'organization', 'org']):
            confidence = 0.95
        
        # Reduce confidence for ambiguous patterns
        if any(word in query.lower() for word in ['in', 'for', 'from']):
            confidence = 0.7
        
        return confidence
    
    def _calculate_llm_confidence(self, result: Optional[Dict], query: str) -> float:
        """Calculate confidence score for LLM result"""
        if not result:
            return 0.0
        
        # Use LLM's own confidence if available
        if 'confidence' in result:
            return float(result['confidence'])
        
        # Default confidence for LLM results
        return 0.6
    
    def _decide_parsing_result(self, text_result: Optional[Dict], text_confidence: float,
                             llm_result: Optional[Dict], llm_confidence: float,
                             query: str) -> Dict[str, any]:
        """Decide which parsing result to use based on confidence and agreement"""
        
        # If both methods agree, use the higher confidence one
        if (text_result and llm_result and 
            text_result.get('org_repo') == llm_result.get('org_repo')):
            if text_confidence >= llm_confidence:
                return {**text_result, 'confidence': text_confidence, 'agreement': True}
            else:
                return {**llm_result, 'confidence': llm_confidence, 'agreement': True}
        
        # If only one method succeeded, use it
        if text_result and not llm_result:
            return {**text_result, 'confidence': text_confidence, 'agreement': False}
        
        if llm_result and not text_result:
            return {**llm_result, 'confidence': llm_confidence, 'agreement': False}
        
        # If both failed, try enterprise LLM or OpenAI as tiebreaker
        if not text_result and not llm_result:
            return self._try_fallback_llm(query)
        
        # If they disagree, use the higher confidence one
        if text_confidence > llm_confidence:
            return {**text_result, 'confidence': text_confidence, 'agreement': False}
        else:
            return {**llm_result, 'confidence': llm_confidence, 'agreement': False}
    
    def _try_fallback_llm(self, query: str) -> Dict[str, any]:
        """Try enterprise LLM or OpenAI as fallback"""
        try:
            # Try enterprise LLM first
            try:
                result = self._parse_with_enterprise_llm(query)
                if result:
                    return {**result, 'method': 'llm_enterprise', 'confidence': 0.5}
            except:
                pass
            
            # Try OpenAI as final fallback
            try:
                result = self._parse_with_openai(query)
                if result:
                    return {**result, 'method': 'llm_openai', 'confidence': 0.4}
            except:
                pass
            
        except Exception as e:
            self.debug_logger.error(f"Fallback LLM parsing failed: {e}")
        
        # Return failure result
        return {
            'organization': None,
            'repository': None,
            'org_repo': None,
            'method': 'failed',
            'confidence': 0.0,
            'error': 'All parsing methods failed'
        }
    
    def _parse_with_enterprise_llm(self, query: str) -> Optional[Dict[str, str]]:
        """Parse using enterprise LLM"""
        # Implementation for enterprise LLM
        # This would use the enterprise LLM provider
        return None
    
    def _parse_with_openai(self, query: str) -> Optional[Dict[str, str]]:
        """Parse using OpenAI"""
        try:
            prompt = f"""
Extract GitHub organization and repository from this query: "{query}"

Return ONLY a JSON object with this exact format:
{{
    "organization": "org_name",
    "repository": "repo_name"
}}

Rules:
- Extract the organization name and repository name
- If unclear, make your best guess
- Return only the JSON, no other text
- If you cannot extract both, return null
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_router.chat(messages)
            
            if response:
                result = json.loads(response.strip())
                if result and 'organization' in result and 'repository' in result:
                    result['org_repo'] = f"{result['organization']}/{result['repository']}"
                    return result
            
            return None
            
        except Exception as e:
            self.debug_logger.error(f"OpenAI parsing failed: {e}")
            return None
