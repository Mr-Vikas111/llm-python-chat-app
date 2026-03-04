"""Chat history management for conversational RAG."""

from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class Message:
    """Represents a single message in the conversation."""

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        sources: Optional[list[str]] = None,
    ):
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.sources = sources or []

    def to_dict(self) -> dict:
        """Convert message to dictionary format."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "sources": self.sources,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create message from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            sources=data.get("sources", []),
        )

    def to_langchain_message(self) -> BaseMessage:
        """Convert to LangChain message object."""
        if self.role == "user":
            return HumanMessage(content=self.content)
        elif self.role == "assistant":
            return AIMessage(content=self.content)
        elif self.role == "system":
            return SystemMessage(content=self.content)
        else:
            return HumanMessage(content=self.content)


class ChatHistory:
    """Manages conversation history for RAG system."""

    def __init__(self, max_history: int = 20):
        """
        Initialize chat history.

        Args:
            max_history: Maximum number of messages to keep in memory
        """
        self.messages: list[Message] = []
        self.max_history = max_history
        self.session_start = datetime.now()

    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        message = Message(role="user", content=content)
        self._add_message(message)

    def add_assistant_message(self, content: str, sources: Optional[list[str]] = None) -> None:
        """Add an assistant message to history."""
        message = Message(role="assistant", content=content, sources=sources)
        self._add_message(message)

    def add_system_message(self, content: str) -> None:
        """Add a system message to history."""
        message = Message(role="system", content=content)
        self._add_message(message)

    def _add_message(self, message: Message) -> None:
        """Internal method to add message and manage history size."""
        self.messages.append(message)
        
        # Remove oldest messages if we exceed max_history
        if len(self.messages) > self.max_history:
            # Keep system messages, always remove oldest user/assistant messages
            non_system = [m for m in self.messages if m.role != "system"]
            system = [m for m in self.messages if m.role == "system"]
            
            # Remove oldest non-system message
            if non_system:
                non_system.pop(0)
            
            self.messages = system + non_system

    def get_all_messages(self) -> list[Message]:
        """Get all messages in history."""
        return self.messages.copy()

    def get_last_n_messages(self, n: int) -> list[Message]:
        """Get the last n messages."""
        return self.messages[-n:] if self.messages else []

    def get_conversation_context(self, window_size: int = 6) -> list[BaseMessage]:
        """
        Get recent conversation context as LangChain messages.
        
        Args:
            window_size: Number of recent messages to include
            
        Returns:
            List of LangChain message objects
        """
        recent_messages = self.get_last_n_messages(window_size)
        return [msg.to_langchain_message() for msg in recent_messages]

    def get_summary(self, max_messages: int = 5) -> str:
        """Get a text summary of recent conversation."""
        recent = self.get_last_n_messages(max_messages)
        if not recent:
            return ""
        
        summary_lines = []
        for msg in recent:
            role = msg.role.upper()
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary_lines.append(f"{role}: {content}")
        
        return "\n".join(summary_lines)

    def clear(self) -> None:
        """Clear all messages from history."""
        self.messages.clear()
        self.session_start = datetime.now()

    def save_to_file(self, filepath: Path) -> None:
        """Save chat history to JSON file."""
        data = {
            "session_start": self.session_start.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: Path) -> None:
        """Load chat history from JSON file."""
        if not filepath.exists():
            return
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        self.session_start = datetime.fromisoformat(data.get("session_start", datetime.now().isoformat()))
        self.messages = [Message.from_dict(msg) for msg in data.get("messages", [])]

    def export_as_markdown(self) -> str:
        """Export conversation as markdown."""
        lines = ["# Chat History\n"]
        lines.append(f"**Session Started:** {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for msg in self.messages:
            role = msg.role.capitalize()
            lines.append(f"\n## {role}\n")
            lines.append(msg.content + "\n")
            
            if msg.sources:
                lines.append("\n**Sources:**\n")
                for source in msg.sources:
                    lines.append(f"- {source}\n")
        
        return "".join(lines)

    def get_stats(self) -> dict:
        """Get statistics about the conversation."""
        user_msgs = [m for m in self.messages if m.role == "user"]
        assistant_msgs = [m for m in self.messages if m.role == "assistant"]
        
        total_user_chars = sum(len(m.content) for m in user_msgs)
        total_assistant_chars = sum(len(m.content) for m in assistant_msgs)
        
        return {
            "total_messages": len(self.messages),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "user_total_chars": total_user_chars,
            "assistant_total_chars": total_assistant_chars,
            "avg_user_message_length": total_user_chars // len(user_msgs) if user_msgs else 0,
            "avg_assistant_message_length": total_assistant_chars // len(assistant_msgs) if assistant_msgs else 0,
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
        }

    def __len__(self) -> int:
        """Return number of messages in history."""
        return len(self.messages)

    def __repr__(self) -> str:
        """String representation of chat history."""
        return f"ChatHistory(messages={len(self.messages)}, max_history={self.max_history})"


class ConversationalRAG:
    """Enhanced RAG that uses conversation history for better context."""

    def __init__(self, max_history: int = 20):
        """Initialize conversational RAG with chat history."""
        self.history = ChatHistory(max_history=max_history)

    def add_to_history(
        self,
        question: str,
        answer: str,
        sources: Optional[list[str]] = None,
    ) -> None:
        """Add a Q&A pair to history."""
        self.history.add_user_message(question)
        self.history.add_assistant_message(answer, sources=sources)

    def get_history(self) -> ChatHistory:
        """Get the chat history object."""
        return self.history

    def get_context_prompt(self, include_history: bool = True, window_size: int = 4) -> str:
        """
        Build a prompt that includes conversation context.

        Args:
            include_history: Whether to include chat history
            window_size: Number of recent messages to include

        Returns:
            Formatted prompt string with history
        """
        if not include_history or len(self.history) == 0:
            return ""

        recent = self.history.get_last_n_messages(window_size)
        lines = ["## Conversation Context:\n"]
        
        for msg in recent:
            lines.append(f"**{msg.role.upper()}:** {msg.content}\n")
        
        return "".join(lines) + "\n"
