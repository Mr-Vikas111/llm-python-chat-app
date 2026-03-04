"""
Python Buddy - RAG-based Chat Application with Streamlit
Refactored with Object-Oriented Programming (OOP) Design Pattern
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid
from pathlib import Path
import sys
import os

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _load_streamlit_secrets_into_env() -> None:
    """Populate os.environ from Streamlit secrets when running on Streamlit Cloud."""
    try:
        for key in st.secrets:
            value = st.secrets[key]
            if isinstance(value, (str, int, float, bool)) and key not in os.environ:
                os.environ[key] = str(value)
    except Exception:
        # No secrets configured (or local run without secrets.toml)
        pass


_load_streamlit_secrets_into_env()

from rag_app.core.chat_history import ChatHistory
from rag_app.core.generator import generate_answer_stream
from rag_app.core.retriever import retrieve
from rag_app.core.config import get_settings


@dataclass
class AppConfig:
    """
    Application configuration settings.
    
    Retrieval settings (top_k, use_mmr, use_history) are loaded from environment variables:
    - TOP_K: Number of chunks to retrieve (default: 4)
    - USE_MMR: Enable MMR retrieval for diversity (default: true)
    - USE_HISTORY: Use chat history for context (default: true)
    
    Set these in .env file to customize without changing code.
    """
    title: str = "Python Buddy"
    icon: str = "💬"
    layout: str = "wide"
    max_history: int = 50
    default_top_k: int = None  # Will be set from Settings
    default_use_mmr: bool = None  # Will be set from Settings
    default_use_history: bool = None  # Will be set from Settings
    
    def __post_init__(self):
        """Initialize defaults from Settings if not provided."""
        settings = get_settings()
        if self.default_top_k is None:
            self.default_top_k = settings.top_k
        if self.default_use_mmr is None:
            self.default_use_mmr = settings.use_mmr
        if self.default_use_history is None:
            self.default_use_history = settings.use_history


class ChatSession:
    """Represents a single chat session with its metadata."""
    
    def __init__(self, session_id: str = None, max_history: int = 50):
        """
        Initialize a chat session.
        
        Args:
            session_id: Unique identifier for the session
            max_history: Maximum number of messages to keep in history
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.history = ChatHistory(max_history=max_history)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_title(self, max_length: int = 50) -> str:
        """
        Generate a title from the first user message.
        
        Args:
            max_length: Maximum length of the title
            
        Returns:
            Generated title or "New Chat" if no messages
        """
        messages = self.history.get_all_messages()
        for msg in messages:
            if msg.role == "user":
                title = msg.content[:max_length]
                if len(msg.content) > max_length:
                    title += "..."
                return title
        return "New Chat"
    
    def get_message_count(self) -> int:
        """Get the total number of messages in this session."""
        return len(self.history.get_all_messages())
    
    def is_empty(self) -> bool:
        """Check if the session has no messages."""
        return self.get_message_count() == 0
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for storage.
        
        Returns:
            Dictionary containing session data
        """
        return {
            "title": self.get_title(),
            "history": self.history,
            "timestamp": self.updated_at,
            "message_count": self.get_message_count(),
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, session_id: str, data: Dict[str, Any]) -> 'ChatSession':
        """
        Create a ChatSession from dictionary data.
        
        Args:
            session_id: Session identifier
            data: Dictionary containing session data
            
        Returns:
            ChatSession instance
        """
        session = cls(session_id=session_id)
        session.history = data["history"]
        session.updated_at = data["timestamp"]
        session.created_at = data.get("created_at", data["timestamp"])
        return session
    
    def clone(self) -> 'ChatSession':
        """
        Create a deep copy of this session.
        
        Returns:
            New ChatSession instance with copied data
        """
        new_session = ChatSession(session_id=self.session_id)
        for msg in self.history.get_all_messages():
            if msg.role == "user":
                new_session.history.add_user_message(msg.content)
            elif msg.role == "assistant":
                new_session.history.add_assistant_message(msg.content, msg.sources)
        new_session.created_at = self.created_at
        new_session.updated_at = self.updated_at
        return new_session


class SessionManager:
    """Manages multiple chat sessions (CRUD operations)."""
    
    def __init__(self, state_key: str = "saved_chats"):
        """
        Initialize the session manager.
        
        Args:
            state_key: Key to store sessions in Streamlit session state
        """
        self.state_key = state_key
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize session state if not already present."""
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = {}
    
    def save_session(self, session: ChatSession) -> bool:
        """
        Save a chat session to storage.
        
        Args:
            session: ChatSession to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not session.is_empty():
            st.session_state[self.state_key][session.session_id] = session.to_dict()
            return True
        return False
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Load a chat session from storage.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            ChatSession if found, None otherwise
        """
        if session_id in st.session_state[self.state_key]:
            data = st.session_state[self.state_key][session_id]
            return ChatSession.from_dict(session_id, data)
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session from storage.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in st.session_state[self.state_key]:
            del st.session_state[self.state_key][session_id]
            return True
        return False
    
    def get_all_sessions(self, sort_by: str = "timestamp") -> List[tuple]:
        """
        Get all saved sessions sorted by specified field.
        
        Args:
            sort_by: Field to sort by (timestamp, message_count, title)
            
        Returns:
            List of (session_id, session_data) tuples
        """
        sessions = st.session_state[self.state_key].items()
        if sort_by == "timestamp":
            return sorted(sessions, key=lambda x: x[1]["timestamp"], reverse=True)
        return list(sessions)
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in storage.
        
        Args:
            session_id: ID to check
            
        Returns:
            True if exists, False otherwise
        """
        return session_id in st.session_state[self.state_key]


class ChatEngine:
    """Handles RAG operations including retrieval and answer generation."""
    
    def __init__(self, top_k: int = 4, use_mmr: bool = True, use_history: bool = True):
        """
        Initialize the chat engine.
        
        Args:
            top_k: Number of chunks to retrieve
            use_mmr: Whether to use MMR retrieval
            use_history: Whether to use chat history
        """
        self.top_k = top_k
        self.use_mmr = use_mmr
        self.use_history = use_history
    
    def update_settings(self, top_k: int = None, use_mmr: bool = None, use_history: bool = None):
        """
        Update engine settings.
        
        Args:
            top_k: Number of chunks to retrieve
            use_mmr: Whether to use MMR retrieval
            use_history: Whether to use chat history
        """
        if top_k is not None:
            self.top_k = top_k
        if use_mmr is not None:
            self.use_mmr = use_mmr
        if use_history is not None:
            self.use_history = use_history
    
    def retrieve_context(
        self,
        question: str,
        chat_history: Optional[ChatHistory] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context chunks for a question.
        
        Args:
            question: User's question
            chat_history: Optional chat history for context
            
        Returns:
            List of retrieved chunks with metadata
        """
        # Extract previous query for follow-up handling
        previous_query = None
        if chat_history and self.use_history:
            messages = chat_history.get_all_messages()
            if len(messages) >= 3:
                for i in range(len(messages) - 2, -1, -1):
                    if messages[i].role == "user":
                        previous_query = messages[i].content
                        break
        
        return retrieve(
            query=question,
            top_k=self.top_k,
            use_mmr=self.use_mmr,
            previous_query=previous_query,
            chat_history=chat_history if self.use_history else None,
        )
    
    def generate_answer(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
        chat_history: Optional[ChatHistory] = None
    ):
        """
        Generate streaming answer for a question.
        
        Args:
            question: User's question
            chunks: Retrieved context chunks
            chat_history: Optional chat history
            
        Returns:
            Generator yielding answer chunks
        """
        return generate_answer_stream(
            question=question,
            chunks=chunks,
            chat_history=chat_history if self.use_history else None,
            use_history=self.use_history,
        )
    
    @staticmethod
    def format_sources(chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Format chunk sources for display.
        
        Args:
            chunks: Retrieved chunks with metadata
            
        Returns:
            List of formatted source strings
        """
        return [f"{chunk['source']} (chunk {chunk['chunk_index']})" for chunk in chunks]


class StreamlitUI:
    """Handles all UI rendering for the Streamlit application."""
    
    def __init__(self, config: AppConfig, session_manager: SessionManager, engine: ChatEngine):
        """
        Initialize the UI handler.
        
        Args:
            config: Application configuration
            session_manager: Session manager instance
            engine: Chat engine instance
        """
        self.config = config
        self.session_manager = session_manager
        self.engine = engine
    
    def configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=self.config.title,
            page_icon=self.config.icon,
            layout=self.config.layout
        )
        st.title(f"{self.config.title} {self.config.icon}")
    
    def render_sidebar(self, current_session: ChatSession) -> tuple:
        """
        Render sidebar with settings and controls.
        
        Args:
            current_session: Current chat session
            
        Returns:
            Tuple of (action) where action is one of:
            None, "new_chat", "export", "clear", ("load", session_id), ("delete", session_id)
        """
        action = None
        
        with st.sidebar:
            st.header("Settings")
            
            # History management
            st.subheader("History Management")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🆕 New Chat"):
                    action = "new_chat"
            
            with col2:
                if st.button("📥 Export"):
                    action = "export"
            
            with col3:
                if st.button("🗑️ Clear"):
                    action = "clear"
            
            # Display saved chats
            load_delete_action = self._render_saved_chats()
            if load_delete_action:
                action = load_delete_action
            
            st.divider()
            
            # Statistics
            # self._render_statistics(current_session)
            
            # Conversation summary
            if not current_session.is_empty():
                self._render_summary(current_session)
        
        return action
    
    def _render_saved_chats(self) -> Optional[tuple]:
        """
        Render saved chats section.
        
        Returns:
            Action tuple if any button clicked, None otherwise
        """
        saved_chats = self.session_manager.get_all_sessions()
        if not saved_chats:
            return None
        
        st.divider()
        st.subheader("💾 Saved Chats")
        
        for session_id, chat_data in saved_chats:
            with st.expander(f"📝 {chat_data['title']}", expanded=False):
                st.caption(f"🕒 {chat_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.caption(f"💬 {chat_data['message_count']} messages")
                
                col_load, col_del = st.columns(2)
                with col_load:
                    if st.button("📂 Load", key=f"load_{session_id}"):
                        return ("load", session_id)
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_{session_id}"):
                        return ("delete", session_id)
        
        return None
    
    def _render_statistics(self, session: ChatSession):
        """
        Render statistics section.
        
        Args:
            session: Current chat session
        """
        st.subheader("Statistics")
        stats = session.history.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", stats["total_messages"])
            st.metric("User Messages", stats["user_messages"])
        with col2:
            st.metric("Assistant Messages", stats["assistant_messages"])
            st.metric("Session Duration (s)", f"{stats['session_duration']:.0f}")
    
    def _render_summary(self, session: ChatSession):
        """
        Render conversation summary.
        
        Args:
            session: Current chat session
        """
        st.divider()
        st.subheader("Recent Conversation")
        summary = session.history.get_summary(max_messages=3)
        st.text_area("Summary", value=summary, height=150, disabled=True)
    
    def render_chat_header(self, session: ChatSession, is_saved: bool):
        """
        Render chat header with title and status.
        
        Args:
            session: Current chat session
            is_saved: Whether the session is saved
        """
        current_title = session.get_title() if not session.is_empty() else "New Chat"
        
        col_title, col_status = st.columns([4, 1])
        with col_title:
            st.subheader(f"💬 {current_title}")
        with col_status:
            if is_saved:
                st.caption("💾 Saved")
            elif not session.is_empty():
                st.caption("📝 Unsaved")
        
        st.divider()
    
    def render_chat_messages(self, session: ChatSession):
        """
        Render all chat messages.
        
        Args:
            session: Current chat session
        """
        for message in session.history.get_all_messages():
            if message.role == "user":
                with st.chat_message("user"):
                    st.markdown(message.content)
            elif message.role == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(message.content)
                    if message.sources:
                        with st.expander("📚 Sources"):
                            for source in message.sources:
                                st.markdown(f"- {source}")
    
    def handle_chat_input(self, session: ChatSession) -> bool:
        """
        Handle user input and generate response.
        
        Args:
            session: Current chat session
            
        Returns:
            True if a message was processed, False otherwise
        """
        question = st.chat_input("Ask a question about your documents...")
        if not question:
            return False
        
        # Display user message
        session.history.add_user_message(question)
        with st.chat_message("user"):
            st.markdown(question)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chunks = self.engine.retrieve_context(question, session.history)
            
            # Display streaming response word-by-word
            answer = st.write_stream(
                self.engine.generate_answer(question, chunks, session.history)
            )
            
            # Format sources
            sources = self.engine.format_sources(chunks)
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.markdown(f"- {source}")
        
        # Add assistant message to history
        session.history.add_assistant_message(answer)
        session.update_timestamp()
        return True
    
    def export_chat(self, session: ChatSession):
        """
        Show export download button.
        
        Args:
            session: Session to export
        """
        markdown_export = session.history.export_as_markdown()
        st.download_button(
            label="Download",
            data=markdown_export,
            file_name=f"chat_{session.session_id[:8]}.md",
            mime="text/markdown"
        )


class ChatApp:
    """Main application class coordinating all components."""
    
    def __init__(self, config: AppConfig = None):
        """
        Initialize the chat application.
        
        Args:
            config: Application configuration (uses defaults if None)
        """
        self.config = config or AppConfig()
        self.session_manager = SessionManager()
        self.engine = ChatEngine(
            top_k=self.config.default_top_k,
            use_mmr=self.config.default_use_mmr,
            use_history=self.config.default_use_history
        )
        self.ui = StreamlitUI(self.config, self.session_manager, self.engine)
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state."""
        if "current_session_id" not in st.session_state:
            st.session_state.current_session_id = str(uuid.uuid4())
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = ChatHistory(max_history=self.config.max_history)
    
    def get_current_session(self) -> ChatSession:
        """
        Get the current active session.
        
        Returns:
            Current ChatSession
        """
        session = ChatSession(
            session_id=st.session_state.current_session_id,
            max_history=self.config.max_history
        )
        session.history = st.session_state.chat_history
        return session
    
    def create_new_session(self):
        """Create a new chat session and save the current one."""
        current = self.get_current_session()
        self.session_manager.save_session(current)
        
        # Create new session
        st.session_state.current_session_id = str(uuid.uuid4())
        st.session_state.chat_history = ChatHistory(max_history=self.config.max_history)
    
    def load_session(self, session_id: str):
        """
        Load a saved session.
        
        Args:
            session_id: ID of session to load
        """
        loaded_session = self.session_manager.load_session(session_id)
        if loaded_session:
            st.session_state.chat_history = loaded_session.history
            st.session_state.current_session_id = session_id
    
    def clear_current_session(self):
        """Clear all messages from current session."""
        st.session_state.chat_history.clear()
    
    def handle_action(self, action, current_session: ChatSession):
        """
        Handle UI actions.
        
        Args:
            action: Action to perform
            current_session: Current session
        """
        if action == "new_chat":
            self.create_new_session()
            st.rerun()
        elif action == "export":
            self.ui.export_chat(current_session)
        elif action == "clear":
            self.clear_current_session()
            st.rerun()
        elif isinstance(action, tuple):
            action_type, session_id = action
            if action_type == "load":
                self.load_session(session_id)
                st.rerun()
            elif action_type == "delete":
                self.session_manager.delete_session(session_id)
                st.rerun()
    
    def run(self):
        """Main application loop."""
        # Configure page
        self.ui.configure_page()
        
        # Get current session
        current_session = self.get_current_session()
        
        # Render sidebar and get action
        action = self.ui.render_sidebar(current_session)
        
        # Engine settings are now fixed from config (no UI changes)
        
        # Handle actions
        if action:
            self.handle_action(action, current_session)
        
        # Render chat header
        is_saved = self.session_manager.session_exists(current_session.session_id)
        self.ui.render_chat_header(current_session, is_saved)
        
        # Render chat messages
        self.ui.render_chat_messages(current_session)
        
        # Handle chat input
        if self.ui.handle_chat_input(current_session):
            # Auto-save after message exchange
            self.session_manager.save_session(current_session)


def main():
    """Application entry point."""
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
