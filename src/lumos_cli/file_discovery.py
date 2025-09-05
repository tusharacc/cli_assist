"""Smart file discovery system for natural language instructions"""

import os
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import ast
import json

@dataclass
class FileCandidate:
    """Represents a file candidate with relevance scoring"""
    path: str
    score: float
    reasons: List[str]
    content_preview: str
    file_type: str
    size_lines: int

class InstructionAnalyzer:
    """Analyzes natural language instructions to extract intent and context"""
    
    # Intent patterns and their associated file type preferences
    INTENT_PATTERNS = {
        "error_handling": {
            "patterns": [
                r"\b(add|implement|improve)\s+(error|exception)\s*handl",
                r"\btry.?catch\b",
                r"\berror\s+(handling|management)",
                r"\bexception\s+(handling|catch)",
                r"\b(handle|catch)\s+(errors|exceptions)"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs", "*.go"],
            "content_indicators": ["def ", "function ", "class ", "async ", "await", "throw", "raise"],
            "negative_indicators": ["test", "spec", "__pycache__", ".pyc"]
        },
        
        "logging": {
            "patterns": [
                r"\b(add|implement|improve)\s+log",
                r"\blogging\b",
                r"\blog\s+(messages|statements)",
                r"\b(debug|info|warn|error)\s+log"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs"],
            "content_indicators": ["def ", "function ", "class "],
            "negative_indicators": ["test", "spec", "__pycache__", ".pyc"]
        },
        
        "authentication": {
            "patterns": [
                r"\b(auth|authentication|login|signin)\b",
                r"\b(user|password|token)\s+(validation|verification)",
                r"\bsession\s+management\b",
                r"\b(jwt|oauth|saml)\b"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs"],
            "content_indicators": ["auth", "login", "user", "password", "token", "session"],
            "negative_indicators": ["test", "spec"]
        },
        
        "database": {
            "patterns": [
                r"\b(database|db|sql|query)\b",
                r"\b(crud|create|read|update|delete)\b",
                r"\b(model|schema|table|collection)\b",
                r"\b(connection|migrate|seed)\b"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs", "*.sql"],
            "content_indicators": ["db", "database", "model", "query", "sql", "table"],
            "negative_indicators": ["test", "spec", "migration"]
        },
        
        "api": {
            "patterns": [
                r"\b(api|endpoint|route|controller)\b",
                r"\b(rest|graphql|webhook)\b",
                r"\b(request|response|payload)\b",
                r"\b(get|post|put|delete|patch)\s+(route|endpoint)"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs"],
            "content_indicators": ["@app.route", "@get", "@post", "router", "controller", "endpoint"],
            "negative_indicators": ["test", "spec", "client"]
        },
        
        "testing": {
            "patterns": [
                r"\b(test|testing|unit test|integration test)\b",
                r"\b(mock|stub|fixture)\b",
                r"\b(assert|expect|should)\b",
                r"\b(test\s+case|test\s+suite)\b"
            ],
            "file_preferences": ["test_*.py", "*_test.py", "*.test.js", "*.spec.js", "*.test.ts"],
            "content_indicators": ["test_", "def test", "it(", "describe(", "assert", "expect"],
            "negative_indicators": []
        },
        
        "configuration": {
            "patterns": [
                r"\b(config|configuration|settings)\b",
                r"\b(environment|env|variables)\b",
                r"\b(setup|initialization)\b"
            ],
            "file_preferences": ["config.py", "settings.py", "*.config.js", "*.env", "*.yaml", "*.json"],
            "content_indicators": ["config", "settings", "env", "PORT", "HOST"],
            "negative_indicators": ["test", "spec"]
        },
        
        "validation": {
            "patterns": [
                r"\b(validat|sanitiz|clean)\b",
                r"\b(input\s+validation|data\s+validation)\b",
                r"\b(schema|validator)\b"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs"],
            "content_indicators": ["validate", "validator", "schema", "clean", "sanitize"],
            "negative_indicators": ["test", "spec"]
        },
        
        "security": {
            "patterns": [
                r"\b(security|secure|encryption|decrypt)\b",
                r"\b(hash|salt|crypto)\b",
                r"\b(xss|csrf|injection)\b",
                r"\b(permission|authorization|access\s+control)\b"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs"],
            "content_indicators": ["hash", "encrypt", "secure", "auth", "permission"],
            "negative_indicators": ["test", "spec"]
        },
        
        "performance": {
            "patterns": [
                r"\b(performance|optimization|optimize|cache)\b",
                r"\b(slow|fast|speed|efficiency)\b",
                r"\b(memory|cpu|resource)\b"
            ],
            "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs", "*.go"],
            "content_indicators": ["def ", "function ", "class ", "cache", "optimize"],
            "negative_indicators": ["test", "spec"]
        }
    }
    
    def analyze(self, instruction: str) -> Dict[str, any]:
        """Analyze instruction and return intent and context"""
        instruction_lower = instruction.lower()
        
        # Detect primary intent
        detected_intents = []
        for intent, config in self.INTENT_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, instruction_lower):
                    detected_intents.append((intent, config))
                    break
        
        # If no specific intent detected, use general approach
        if not detected_intents:
            detected_intents = [("general", {
                "file_preferences": ["*.py", "*.js", "*.ts", "*.java", "*.cs"],
                "content_indicators": ["def ", "function ", "class "],
                "negative_indicators": ["test", "spec", "__pycache__"]
            })]
        
        # Extract keywords from instruction
        keywords = self._extract_keywords(instruction)
        
        # Determine file type preferences
        file_preferences = []
        content_indicators = []
        negative_indicators = []
        
        for intent, config in detected_intents:
            file_preferences.extend(config.get("file_preferences", []))
            content_indicators.extend(config.get("content_indicators", []))
            negative_indicators.extend(config.get("negative_indicators", []))
        
        return {
            "intents": [intent for intent, _ in detected_intents],
            "keywords": keywords,
            "file_preferences": list(set(file_preferences)),
            "content_indicators": list(set(content_indicators)),
            "negative_indicators": list(set(negative_indicators))
        }
    
    def _extract_keywords(self, instruction: str) -> List[str]:
        """Extract relevant keywords from instruction"""
        # Remove common words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'among', 'this', 'that', 'these', 'those', 'i', 'me', 'we', 'us', 'you', 'he',
            'him', 'she', 'her', 'it', 'they', 'them', 'add', 'implement', 'improve', 'create', 'make'
        }
        
        words = re.findall(r'\b\w+\b', instruction.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords

class FileScorer:
    """Scores files based on relevance to instruction and context"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._file_contents_cache = {}
    
    def score_files(self, files: List[str], analysis: Dict[str, any]) -> List[FileCandidate]:
        """Score a list of files based on instruction analysis"""
        candidates = []
        
        for file_path in files:
            try:
                candidate = self._score_single_file(file_path, analysis)
                if candidate and candidate.score > 0:
                    candidates.append(candidate)
            except Exception as e:
                # Skip files that can't be processed
                continue
        
        # Sort by score (descending)
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        return candidates
    
    def _score_single_file(self, file_path: str, analysis: Dict[str, any]) -> Optional[FileCandidate]:
        """Score a single file"""
        full_path = os.path.join(self.repo_path, file_path)
        
        if not os.path.isfile(full_path):
            return None
        
        # Get file info
        file_ext = Path(file_path).suffix
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        
        score = 0.0
        reasons = []
        
        # Check negative indicators first (early exit)
        for neg_indicator in analysis["negative_indicators"]:
            if neg_indicator in file_path.lower():
                return None
        
        # Skip certain file types
        if file_ext in ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe']:
            return None
        
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        if any(skip_dir in file_path for skip_dir in skip_dirs):
            return None
        
        # File extension/pattern matching
        for preference in analysis["file_preferences"]:
            if self._matches_pattern(file_name, preference):
                score += 2.0
                reasons.append(f"Matches file pattern {preference}")
                break
        
        # Read file content for analysis
        try:
            content = self._get_file_content(full_path)
            if not content:
                return None
                
            content_lower = content.lower()
            line_count = len(content.split('\n'))
            
            # Content indicators scoring
            for indicator in analysis["content_indicators"]:
                if indicator.lower() in content_lower:
                    score += 1.5
                    reasons.append(f"Contains '{indicator}'")
            
            # Keywords scoring
            keyword_matches = 0
            for keyword in analysis["keywords"]:
                if keyword in content_lower:
                    keyword_matches += 1
                    score += 1.0
            
            if keyword_matches > 0:
                reasons.append(f"Contains {keyword_matches} relevant keywords")
            
            # File structure scoring
            if self._is_main_implementation_file(file_path, content):
                score += 3.0
                reasons.append("Main implementation file")
            
            # Recency/modification scoring (files modified recently might be more relevant)
            try:
                mod_time = os.path.getmtime(full_path)
                import time
                hours_since_mod = (time.time() - mod_time) / 3600
                if hours_since_mod < 24:  # Modified in last 24 hours
                    score += 1.0
                    reasons.append("Recently modified")
            except:
                pass
            
            # Size scoring (prefer reasonably sized files)
            if 10 <= line_count <= 500:
                score += 0.5
                reasons.append("Good file size")
            elif line_count > 500:
                score -= 0.2  # Slightly penalize very large files
            
            # Generate preview
            preview = self._generate_preview(content, analysis)
            
            return FileCandidate(
                path=file_path,
                score=score,
                reasons=reasons,
                content_preview=preview,
                file_type=file_ext,
                size_lines=line_count
            )
            
        except Exception as e:
            return None
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a glob-like pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _get_file_content(self, file_path: str) -> str:
        """Get file content with caching"""
        if file_path in self._file_contents_cache:
            return self._file_contents_cache[file_path]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Cache only if reasonable size
                if len(content) < 100000:  # 100KB limit
                    self._file_contents_cache[file_path] = content
                return content
        except (UnicodeDecodeError, IOError):
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except:
                return ""
    
    def _is_main_implementation_file(self, file_path: str, content: str) -> bool:
        """Determine if this is a main implementation file"""
        file_name = os.path.basename(file_path).lower()
        
        # Common main file names
        main_names = {
            'main.py', 'app.py', 'server.py', 'index.py', 'api.py',
            'main.js', 'app.js', 'server.js', 'index.js', 'api.js',
            'main.ts', 'app.ts', 'server.ts', 'index.ts', 'api.ts',
            'application.java', 'main.java', 'app.java',
            'program.cs', 'startup.cs', 'application.cs'
        }
        
        if file_name in main_names:
            return True
        
        # Check for main-like content
        content_lower = content.lower()
        main_indicators = [
            'if __name__ == "__main__"',
            'app.run(',
            'express(',
            'public static void main',
            'static void Main',
            'func main('
        ]
        
        return any(indicator in content_lower for indicator in main_indicators)
    
    def _generate_preview(self, content: str, analysis: Dict[str, any]) -> str:
        """Generate a relevant preview of the file content"""
        lines = content.split('\n')
        preview_lines = []
        
        # Look for relevant lines
        keywords = [kw.lower() for kw in analysis["keywords"]]
        content_indicators = [ci.lower() for ci in analysis["content_indicators"]]
        
        relevant_lines = []
        for i, line in enumerate(lines[:50]):  # Check first 50 lines
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in keywords + content_indicators):
                relevant_lines.append(f"{i+1}: {line.strip()}")
        
        if relevant_lines:
            return "\n".join(relevant_lines[:3])  # Show top 3 relevant lines
        else:
            # Show first few non-empty lines
            for line in lines[:10]:
                if line.strip():
                    preview_lines.append(line.strip())
                if len(preview_lines) >= 3:
                    break
            return "\n".join(preview_lines)

class SmartFileDiscovery:
    """Main class for smart file discovery system"""
    
    def __init__(self, repo_path: str = ".", console=None):
        self.repo_path = os.path.abspath(repo_path)
        self.analyzer = InstructionAnalyzer()
        self.scorer = FileScorer(self.repo_path)
        self.console = console
    
    def discover_files(self, instruction: str, max_candidates: int = 10) -> List[FileCandidate]:
        """Discover relevant files for the given instruction"""
        
        # Analyze the instruction
        analysis = self.analyzer.analyze(instruction)
        
        # Get all relevant files from the repository
        all_files = self._get_repository_files(analysis)
        
        # Score and rank the files
        candidates = self.scorer.score_files(all_files, analysis)
        
        # Return top candidates
        return candidates[:max_candidates]
    
    def _get_repository_files(self, analysis: Dict[str, any]) -> List[str]:
        """Get all files from repository that could be relevant"""
        relevant_files = []
        
        # Walk through repository
        for root, dirs, files in os.walk(self.repo_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', 'build', 'dist'}]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                # Basic file filtering
                if self._should_consider_file(rel_path, analysis):
                    relevant_files.append(rel_path)
        
        return relevant_files
    
    def _should_consider_file(self, file_path: str, analysis: Dict[str, any]) -> bool:
        """Quick filter to determine if file should be considered"""
        file_ext = Path(file_path).suffix.lower()
        
        # Skip binary and irrelevant files
        skip_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', 
                          '.img', '.jpg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz'}
        
        if file_ext in skip_extensions:
            return False
        
        # Check if file matches any preferred patterns
        file_name = os.path.basename(file_path)
        for preference in analysis["file_preferences"]:
            if self.scorer._matches_pattern(file_name, preference):
                return True
        
        # Include common text files that might be relevant
        include_extensions = {'.py', '.js', '.ts', '.java', '.cs', '.go', '.rs', 
                            '.cpp', '.c', '.h', '.php', '.rb', '.swift', '.kt'}
        
        return file_ext in include_extensions
    
    def interactive_file_selection(self, candidates: List[FileCandidate], instruction: str) -> Optional[List[str]]:
        """Interactive file selection interface"""
        if not self.console:
            # Fallback for non-interactive usage
            return [candidates[0].path] if candidates else None
        
        from rich.table import Table
        from rich.prompt import Prompt, Confirm
        from rich.text import Text
        
        self.console.print("\n[bold cyan]Smart File Discovery Results[/bold cyan]")
        self.console.print(f"[dim]Looking for files to: {instruction}[/dim]\n")
        
        if not candidates:
            self.console.print("[yellow]No relevant files found for your instruction.[/yellow]")
            return None
        
        # Auto-select if only one high-confidence candidate
        if len(candidates) == 1 and candidates[0].score >= 5.0:
            self.console.print(f"[green]✓[/green] Auto-selected: [bold]{candidates[0].path}[/bold] (confidence: {candidates[0].score:.1f})")
            self.console.print(f"[dim]Reasons: {', '.join(candidates[0].reasons)}[/dim]\n")
            return [candidates[0].path]
        
        # Show candidates table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("File", style="cyan", min_width=20)
        table.add_column("Score", justify="right", style="green", width=8)
        table.add_column("Type", style="blue", width=8)
        table.add_column("Lines", justify="right", style="yellow", width=8)
        table.add_column("Reasons", style="dim", no_wrap=False)
        
        for i, candidate in enumerate(candidates[:10], 1):
            score_color = "green" if candidate.score >= 3.0 else "yellow" if candidate.score >= 1.0 else "red"
            table.add_row(
                str(i),
                candidate.path,
                f"[{score_color}]{candidate.score:.1f}[/{score_color}]",
                candidate.file_type or "txt",
                str(candidate.size_lines),
                ", ".join(candidate.reasons[:3])  # Show only first 3 reasons
            )
        
        self.console.print(table)
        
        # Show previews for top candidates
        if candidates and Confirm.ask("\nShow file previews?", default=True):
            for i, candidate in enumerate(candidates[:3], 1):
                if candidate.content_preview:
                    self.console.print(f"\n[bold]{i}. {candidate.path}[/bold]")
                    self.console.print(f"[dim]{candidate.content_preview}[/dim]")
        
        # Selection options
        self.console.print("\n[bold]Selection Options:[/bold]")
        self.console.print("• Enter numbers (e.g., '1,3,5' for multiple files)")
        self.console.print("• Enter 'all' to select all candidates")
        self.console.print("• Enter 'none' or 'q' to cancel")
        
        while True:
            try:
                choice = Prompt.ask("\nSelect files", default="1").strip().lower()
                
                if choice in ['none', 'q', 'quit', 'cancel']:
                    return None
                
                if choice == 'all':
                    return [c.path for c in candidates]
                
                # Parse number selection
                selected_indices = []
                for part in choice.split(','):
                    part = part.strip()
                    if '-' in part:
                        # Handle ranges like "1-3"
                        start, end = part.split('-', 1)
                        selected_indices.extend(range(int(start), int(end) + 1))
                    else:
                        selected_indices.append(int(part))
                
                # Validate indices and convert to paths
                selected_paths = []
                for idx in selected_indices:
                    if 1 <= idx <= len(candidates):
                        selected_paths.append(candidates[idx - 1].path)
                    else:
                        self.console.print(f"[red]Invalid selection: {idx}[/red]")
                        break
                else:
                    if selected_paths:
                        return selected_paths
                        
            except (ValueError, IndexError):
                self.console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")
            except KeyboardInterrupt:
                return None
    
    def suggest_files_for_instruction(self, instruction: str, auto_select_threshold: float = 5.0) -> Optional[List[str]]:
        """Main interface - discover and optionally select files for instruction"""
        candidates = self.discover_files(instruction)
        
        if not candidates:
            return None
        
        # Auto-select high confidence single candidate
        if len(candidates) == 1 and candidates[0].score >= auto_select_threshold:
            return [candidates[0].path]
        
        # Use interactive selection
        return self.interactive_file_selection(candidates, instruction)