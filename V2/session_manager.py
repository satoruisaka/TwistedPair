"""
Session management for multi-turn chat conversations in TwistedPair V2.

Handles session storage, conversation history tracking, and session lifecycle.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

# Import parent directory types
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from twistedtypes import Mode, Tone, Knobs


@dataclass
class ChatMessage:
    """Single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    
    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatMessage':
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data["timestamp"]
        )


@dataclass
class ChatSession:
    """A chat session with conversation history and settings."""
    session_id: str
    knobs: Knobs  # Mode, Tone, Gain settings for this session
    messages: List[ChatMessage] = field(default_factory=list)
    parent_signal_id: Optional[str] = None  # Link to original Signal if from distortion
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_active: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model_name: str = "ministral-3:14b"
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        msg = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat()
        )
        self.messages.append(msg)
        self.last_active = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Serialize session to dict for JSON storage."""
        return {
            "session_id": self.session_id,
            "knobs": {
                "mode": self.knobs.mode.value,
                "tone": self.knobs.tone.value,
                "gain": self.knobs.gain
            },
            "messages": [msg.to_dict() for msg in self.messages],
            "parent_signal_id": self.parent_signal_id,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "model_name": self.model_name
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatSession':
        """Deserialize session from dict."""
        knobs = Knobs(
            mode=Mode(data["knobs"]["mode"]),
            tone=Tone(data["knobs"]["tone"]),
            gain=data["knobs"]["gain"]
        )
        messages = [ChatMessage.from_dict(msg) for msg in data["messages"]]
        
        return cls(
            session_id=data["session_id"],
            knobs=knobs,
            messages=messages,
            parent_signal_id=data.get("parent_signal_id"),
            created_at=data["created_at"],
            last_active=data["last_active"],
            model_name=data.get("model_name", "mistral:latest")
        )


class SessionStore:
    """
    Manages chat sessions with hybrid storage:
    - In-memory dict for fast access during active use
    - File-based persistence for recovery after restart
    """
    
    def __init__(self, storage_dir: str = "./V2/sessions"):
        self.sessions: Dict[str, ChatSession] = {}
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.session_timeout = timedelta(hours=2)  # 2 hour idle timeout
        
        # Load existing sessions from disk
        self._load_sessions()
    
    def create_session(
        self,
        knobs: Knobs,
        model_name: str = "mistral:latest",
        parent_signal_id: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            knobs=knobs,
            parent_signal_id=parent_signal_id,
            model_name=model_name
        )
        self.sessions[session_id] = session
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a session by ID."""
        session = self.sessions.get(session_id)
        
        if session:
            # Check if session has expired
            last_active = datetime.fromisoformat(session.last_active)
            # Make both datetimes timezone-aware for comparison
            if last_active.tzinfo is None:
                last_active = last_active.replace(tzinfo=None)
                now = datetime.utcnow()
            else:
                now = datetime.now(last_active.tzinfo)
            
            if now - last_active > self.session_timeout:
                self.delete_session(session_id)
                return None
        
        return session
    
    def update_session(self, session: ChatSession) -> None:
        """Update a session in memory and on disk."""
        self.sessions[session.session_id] = session
        self._save_session(session)
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session from memory and disk."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
    
    def cleanup_expired_sessions(self) -> int:
        """Remove sessions that have exceeded the timeout. Returns count of removed sessions."""
        now = datetime.utcnow()
        expired = []
        
        for session_id, session in self.sessions.items():
            last_active = datetime.fromisoformat(session.last_active)
            # Handle timezone awareness
            if last_active.tzinfo is None:
                check_now = now
            else:
                check_now = datetime.now(last_active.tzinfo)
            
            if check_now - last_active > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            self.delete_session(session_id)
        
        return len(expired)
    
    def _save_session(self, session: ChatSession) -> None:
        """Persist session to disk."""
        session_file = self.storage_dir / f"{session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def _load_sessions(self) -> None:
        """Load all sessions from disk on startup."""
        if not self.storage_dir.exists():
            return
        
        for session_file in self.storage_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = ChatSession.from_dict(data)
                    
                    # Only load non-expired sessions
                    last_active = datetime.fromisoformat(session.last_active)
                    # Handle timezone awareness
                    if last_active.tzinfo is None:
                        now = datetime.utcnow()
                    else:
                        now = datetime.now(last_active.tzinfo)
                    
                    if now - last_active <= self.session_timeout:
                        self.sessions[session.session_id] = session
                    else:
                        # Clean up expired session file
                        session_file.unlink()
            except Exception as e:
                print(f"Warning: Failed to load session {session_file}: {e}")


# Global session store instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get or create the global session store singleton."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store
