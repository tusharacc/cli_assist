"""Persistent, repository-aware chat history system"""

import os
import json
import sqlite3
import hashlib
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from .client import LLMRouter

@dataclass
class ChatMessage:
    """Single chat message"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    command: Optional[str] = None  # Which command generated this
    file_path: Optional[str] = None  # Associated file if any
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "command": self.command,
            "file_path": self.file_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

@dataclass
class ChatSession:
    """A conversation session within a repository"""
    session_id: str
    repository_path: str
    created_at: datetime
    last_updated: datetime
    title: str
    message_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "repository_path": self.repository_path,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "title": self.title,
            "message_count": self.message_count
        }

class HistoryManager:
    """Repository-aware persistent chat history manager"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("LUMOS_HISTORY_DB", ".lumos_history.db")
        self.current_repo_path = self._get_repository_root()
        self.current_repo_id = self._get_repository_id(self.current_repo_path)
        self.current_session_id = None
        self._init_db()
    
    def _get_repository_root(self) -> str:
        """Get the root path of the current repository"""
        try:
            # Try Git first
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to current directory
            return os.getcwd()
    
    def _get_repository_id(self, repo_path: str) -> str:
        """Generate a unique ID for a repository"""
        # Use absolute path hash for consistent repo identification
        abs_path = os.path.abspath(repo_path)
        return hashlib.sha256(abs_path.encode()).hexdigest()[:12]
    
    def _init_db(self):
        """Initialize the history database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS repositories (
            repo_id TEXT PRIMARY KEY,
            repo_path TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            last_accessed TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            repo_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            title TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            FOREIGN KEY (repo_id) REFERENCES repositories (repo_id)
        );
        
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            command TEXT,
            file_path TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
        CREATE INDEX IF NOT EXISTS idx_sessions_repo ON sessions(repo_id);
        ''')
        
        # Register current repository
        self._register_repository()
        self.conn.commit()
    
    def _register_repository(self):
        """Register current repository in database"""
        now = datetime.now().isoformat()
        self.conn.execute('''
        INSERT OR REPLACE INTO repositories (repo_id, repo_path, created_at, last_accessed)
        VALUES (?, ?, COALESCE((SELECT created_at FROM repositories WHERE repo_id = ?), ?), ?)
        ''', (self.current_repo_id, self.current_repo_path, self.current_repo_id, now, now))
    
    def start_session(self, title: str = None) -> str:
        """Start a new chat session"""
        session_id = f"{self.current_repo_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not title:
            title = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        now = datetime.now().isoformat()
        self.conn.execute('''
        INSERT INTO sessions (session_id, repo_id, created_at, last_updated, title, message_count)
        VALUES (?, ?, ?, ?, ?, 0)
        ''', (session_id, self.current_repo_id, now, now, title))
        
        self.current_session_id = session_id
        self.conn.commit()
        return session_id
    
    def get_or_create_session(self, command: str = None) -> str:
        """Get current session or create new one"""
        if not self.current_session_id:
            # Try to get the most recent session for this repo
            cursor = self.conn.execute('''
            SELECT session_id FROM sessions 
            WHERE repo_id = ? 
            ORDER BY last_updated DESC 
            LIMIT 1
            ''', (self.current_repo_id,))
            
            row = cursor.fetchone()
            if row:
                self.current_session_id = row[0]
            else:
                # Create new session
                title = f"Auto-session ({command or 'chat'})"
                self.current_session_id = self.start_session(title)
        
        return self.current_session_id
    
    def add_message(self, role: str, content: str, command: str = None, 
                   file_path: str = None) -> ChatMessage:
        """Add a message to current session"""
        session_id = self.get_or_create_session(command)
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            command=command,
            file_path=file_path
        )
        
        # Insert message
        self.conn.execute('''
        INSERT INTO messages (session_id, role, content, timestamp, command, file_path)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, message.role, message.content, 
              message.timestamp.isoformat(), message.command, message.file_path))
        
        # Update session
        self.conn.execute('''
        UPDATE sessions 
        SET last_updated = ?, message_count = message_count + 1
        WHERE session_id = ?
        ''', (message.timestamp.isoformat(), session_id))
        
        self.conn.commit()
        return message
    
    def get_session_messages(self, session_id: str = None, limit: int = None) -> List[ChatMessage]:
        """Get messages from a session"""
        session_id = session_id or self.current_session_id
        if not session_id:
            return []
        
        query = '''
        SELECT role, content, timestamp, command, file_path
        FROM messages 
        WHERE session_id = ?
        ORDER BY timestamp ASC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor = self.conn.execute(query, (session_id,))
        messages = []
        
        for row in cursor:
            messages.append(ChatMessage(
                role=row[0],
                content=row[1], 
                timestamp=datetime.fromisoformat(row[2]),
                command=row[3],
                file_path=row[4]
            ))
        
        return messages
    
    def get_recent_context(self, max_tokens: int = 4000, session_id: str = None) -> List[Dict[str, str]]:
        """Get recent messages formatted for LLM, with smart truncation"""
        messages = self.get_session_messages(session_id)
        
        if not messages:
            return []
        
        # Convert to LLM format
        formatted_messages = []
        total_tokens = 0
        
        # Add messages from most recent backwards until we hit token limit
        for message in reversed(messages):
            content_tokens = len(message.content)
            
            if total_tokens + content_tokens > max_tokens and formatted_messages:
                break
                
            formatted_messages.insert(0, {
                "role": message.role,
                "content": message.content
            })
            total_tokens += content_tokens
        
        # If we're still over limit, summarize older messages
        if total_tokens > max_tokens and len(formatted_messages) > 2:
            return self._summarize_context(formatted_messages, max_tokens)
        
        return formatted_messages
    
    def _summarize_context(self, messages: List[Dict[str, str]], max_tokens: int) -> List[Dict[str, str]]:
        """Summarize older messages to fit within token limit"""
        if len(messages) <= 3:
            return messages
        
        # Keep first message, summarize middle, keep last few
        first_message = messages[0]
        last_messages = messages[-2:]  # Keep last 2 messages
        middle_messages = messages[1:-2]  # Messages to summarize
        
        if not middle_messages:
            return messages
        
        # Create summary prompt
        middle_content = "\n".join([f"{m['role']}: {m['content']}" for m in middle_messages])
        
        try:
            # Use a simple router to summarize (without infinite recursion)
            from .client import LLMRouter
            router = LLMRouter("auto")  # Use smart routing
            
            summary_prompt = [{
                "role": "system", 
                "content": "Summarize this conversation briefly, preserving key technical details and context."
            }, {
                "role": "user",
                "content": middle_content
            }]
            
            summary = router.chat(summary_prompt)
            
            # Build result with summary
            result = [first_message]
            result.append({"role": "system", "content": f"[Previous conversation summary: {summary}]"})
            result.extend(last_messages)
            
            return result
            
        except Exception as e:
            # Fallback: just truncate
            print(f"Warning: Failed to summarize context: {e}")
            return [first_message] + last_messages
    
    def list_sessions(self, repo_id: str = None) -> List[ChatSession]:
        """List sessions for current or specified repository"""
        repo_id = repo_id or self.current_repo_id
        
        cursor = self.conn.execute('''
        SELECT session_id, repo_id, created_at, last_updated, title, message_count
        FROM sessions 
        WHERE repo_id = ?
        ORDER BY last_updated DESC
        ''', (repo_id,))
        
        sessions = []
        for row in cursor:
            sessions.append(ChatSession(
                session_id=row[0],
                repository_path=self.current_repo_path,
                created_at=datetime.fromisoformat(row[2]),
                last_updated=datetime.fromisoformat(row[3]),
                title=row[4],
                message_count=row[5]
            ))
        
        return sessions
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """List all known repositories"""
        cursor = self.conn.execute('''
        SELECT repo_id, repo_path, created_at, last_accessed,
               (SELECT COUNT(*) FROM sessions WHERE repo_id = repositories.repo_id) as session_count
        FROM repositories
        ORDER BY last_accessed DESC
        ''')
        
        repos = []
        for row in cursor:
            repos.append({
                "repo_id": row[0],
                "repo_path": row[1],
                "created_at": datetime.fromisoformat(row[2]),
                "last_accessed": datetime.fromisoformat(row[3]),
                "session_count": row[4]
            })
        
        return repos
    
    def search_messages(self, query: str, repo_id: str = None, limit: int = 20) -> List[Tuple[ChatMessage, str]]:
        """Search messages across sessions"""
        repo_id = repo_id or self.current_repo_id
        
        cursor = self.conn.execute('''
        SELECT m.role, m.content, m.timestamp, m.command, m.file_path, s.title
        FROM messages m
        JOIN sessions s ON m.session_id = s.session_id
        WHERE s.repo_id = ? AND m.content LIKE ?
        ORDER BY m.timestamp DESC
        LIMIT ?
        ''', (repo_id, f'%{query}%', limit))
        
        results = []
        for row in cursor:
            message = ChatMessage(
                role=row[0],
                content=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                command=row[3],
                file_path=row[4]
            )
            session_title = row[5]
            results.append((message, session_title))
        
        return results
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        cursor = self.conn.execute('''
        SELECT session_id FROM sessions 
        WHERE session_id = ? AND repo_id = ?
        ''', (session_id, self.current_repo_id))
        
        if cursor.fetchone():
            self.current_session_id = session_id
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        cursor = self.conn.execute('''
        SELECT session_id FROM sessions 
        WHERE session_id = ? AND repo_id = ?
        ''', (session_id, self.current_repo_id))
        
        if not cursor.fetchone():
            return False
        
        # Delete messages first (foreign key constraint)
        self.conn.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        self.conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        
        # If this was current session, clear it
        if self.current_session_id == session_id:
            self.current_session_id = None
        
        self.conn.commit()
        return True
    
    def get_repository_stats(self, repo_id: str = None) -> Dict[str, Any]:
        """Get statistics for a repository"""
        repo_id = repo_id or self.current_repo_id
        
        cursor = self.conn.execute('''
        SELECT 
            COUNT(DISTINCT s.session_id) as session_count,
            COUNT(m.id) as message_count,
            MIN(s.created_at) as first_session,
            MAX(s.last_updated) as last_activity
        FROM sessions s
        LEFT JOIN messages m ON s.session_id = m.session_id
        WHERE s.repo_id = ?
        ''', (repo_id,))
        
        row = cursor.fetchone()
        
        return {
            "repo_id": repo_id,
            "repo_path": self.current_repo_path,
            "session_count": row[0] or 0,
            "message_count": row[1] or 0,
            "first_session": datetime.fromisoformat(row[2]) if row[2] else None,
            "last_activity": datetime.fromisoformat(row[3]) if row[3] else None
        }
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Delete sessions older than specified days"""
        cutoff_date = datetime.now().replace(days=days_old)
        
        cursor = self.conn.execute('''
        SELECT session_id FROM sessions 
        WHERE repo_id = ? AND last_updated < ?
        ''', (self.current_repo_id, cutoff_date.isoformat()))
        
        old_sessions = [row[0] for row in cursor]
        
        for session_id in old_sessions:
            self.delete_session(session_id)
        
        return len(old_sessions)
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()