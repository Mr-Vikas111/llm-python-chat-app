# Chat History Management Guide

Chat history management allows you to build conversational RAG systems where the LLM can understand context from previous messages. This guide covers all available features and usage patterns.

## Overview

The RAG system now includes comprehensive chat history management with:

- **Conversation tracking** - Store and manage all messages
- **Persistence** - Save/load conversations to/from files
- **Statistics** - Get insights about conversations
- **Export** - Convert conversations to markdown
- **Memory management** - Automatic cleanup of old messages
- **Context windows** - Extract recent messages for multi-turn conversations

## Key Classes

### `Message`
Represents a single message in a conversation.

```python
from rag_app.core.chat_history import Message

# Create a message
msg = Message(
    role="user",          # "user", "assistant", or "system"
    content="Your text",
    sources=["doc.txt"]   # Optional
)

# Convert to dict for storage
msg_dict = msg.to_dict()

# Convert to LangChain message
langchain_msg = msg.to_langchain_message()
```

### `ChatHistory`
Main class for managing conversation history.

```python
from rag_app.core.chat_history import ChatHistory

# Create history with max 50 messages
history = ChatHistory(max_history=50)

# Add messages
history.add_user_message("What is accounting?")
history.add_assistant_message("Accounting is...", sources=["doc.txt"])

# Access messages
all_msgs = history.get_all_messages()
recent_5 = history.get_last_n_messages(5)

# Get context for LLM (as LangChain messages)
context = history.get_conversation_context(window_size=4)

# Statistics
stats = history.get_stats()

# Save/Load
history.save_to_file(Path("history.json"))
history.load_from_file(Path("history.json"))

# Export as markdown
markdown = history.export_as_markdown()

# Clear
history.clear()
```

### `ConversationalRAG`
Enhanced RAG system with integrated chat history.

```python
from rag_app.core.chat_history import ConversationalRAG
from rag_app.core.retriever import retrieve
from rag_app.core.generator import generate_answer

rag = ConversationalRAG(max_history=20)

# Add Q&A pairs to history
question = "What are debits?"
chunks = retrieve(question)
answer = generate_answer(question, chunks, chat_history=rag.get_history())
rag.add_to_history(question, answer, sources=["doc.txt"])

# Access history
history = rag.get_history()
```

## Usage Patterns

### 1. Basic Single-Turn Retrieval (No History)

```python
from rag_app.core.retriever import retrieve
from rag_app.core.generator import generate_answer

# Simple query without history
question = "What is accounting?"
chunks = retrieve(question)
answer = generate_answer(question, chunks)
print(answer)
```

### 2. Multi-Turn Conversation (With History)

```python
from rag_app.core.chat_history import ChatHistory
from rag_app.core.retriever import retrieve
from rag_app.core.generator import generate_answer

history = ChatHistory(max_history=20)

# Turn 1
q1 = "What are debits?"
chunks = retrieve(q1)
a1 = generate_answer(q1, chunks, chat_history=history)
history.add_user_message(q1)
history.add_assistant_message(a1, sources=[c['source'] for c in chunks])

# Turn 2: LLM understands previous context
q2 = "What about credits?"
chunks = retrieve(q2)
a2 = generate_answer(q2, chunks, chat_history=history, use_history=True)
history.add_user_message(q2)
history.add_assistant_message(a2)

print(a2)  # Answer will reference previous discussion
```

### 3. Persistent Conversations

```python
from pathlib import Path
from rag_app.core.chat_history import ChatHistory

history_file = Path("my_conversation.json")

# Load previous conversation (or create new)
history = ChatHistory()
history.load_from_file(history_file)

# Continue conversation
history.add_user_message("Next question")
history.add_assistant_message("Next answer")

# Save updated history
history.save_to_file(history_file)
```

### 4. Streamlit Chat App (Built-in)

The chat history is fully integrated in the Streamlit app:

```bash
streamlit run scripts/streamlit_app.py
```

Features:
- ✅ Automatic message tracking
- ✅ Export conversations as markdown
- ✅ View conversation statistics
- ✅ Clear history with one click
- ✅ Toggle history usage in LLM
- ✅ Real-time summary display

### 5. Retrieve with Different Methods

```python
from rag_app.core.retriever import retrieve

# Use MMR (default)
chunks = retrieve("question", use_mmr=True, top_k=4)

# Use similarity search
chunks = retrieve("question", use_mmr=False, top_k=4)

# Use config defaults
chunks = retrieve("question")
```

## Configuration

Add to `.env` to customize chat history behavior:

```env
# Maximum messages to keep in memory (default: 50 in Streamlit, 20 in code)
# No config var - set in code: ChatHistory(max_history=50)

# MMR Retrieval (for better diversity)
USE_MMR=true
MMR_FETCH_K=20
MMR_LAMBDA_MULT=0.5

# LLM settings
USE_LLM=true
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## Chat History in LLM Prompts

When `use_history=True`, the LLM receives:

```
System Prompt: "You are a precise assistant..."

[Previous messages from history]

User Query: "Can you give me an example?"
Context: "[Retrieved chunks]"
Question: "[Current question]"
```

This allows the LLM to:
- Reference previous answers
- Ask clarifying follow-up questions
- Maintain conversation continuity
- Remember context from earlier turns

## Advanced Features

### 1. Memory Management

History automatically limits messages:

```python
# Keep only recent 10 messages
history = ChatHistory(max_history=10)

# Add 20 messages
for i in range(20):
    history.add_user_message(f"Q{i}")
    history.add_assistant_message(f"A{i}")

# Only last 10 remain
print(len(history))  # 10
```

### 2. Context Window

Get formatted LangChain messages for LLM:

```python
# Include recent 6 messages as context
context_msgs = history.get_conversation_context(window_size=6)

# Use in custom LLM calls
from langchain_openai import ChatOpenAI
chat = ChatOpenAI()
context_msgs.append(HumanMessage(content="New question"))
response = chat.invoke(context_msgs)
```

### 3. Statistics & Metrics

```python
stats = history.get_stats()

# Available metrics:
stats['total_messages']           # Total messages
stats['user_messages']            # User count
stats['assistant_messages']       # Assistant count
stats['user_total_chars']         # Total user characters
stats['assistant_total_chars']    # Total assistant characters
stats['avg_user_message_length']  # Average user message length
stats['avg_assistant_message_length']  # Average assistant length
stats['session_duration']         # Session duration in seconds
```

### 4. Export & Sharing

```python
# Export as markdown with formatting
markdown = history.export_as_markdown()

# Save to file
with open("conversation.md", "w") as f:
    f.write(markdown)

# Share or archive
```

### 5. Programmatic Message Access

```python
# Get all messages
all_messages = history.get_all_messages()

for msg in all_messages:
    print(f"{msg.role}: {msg.content}")
    print(f"  Sources: {msg.sources}")
    print(f"  Time: {msg.timestamp}")
    print()

# Filter by role
user_msgs = [m for m in all_messages if m.role == "user"]
assistant_msgs = [m for m in all_messages if m.role == "assistant"]
```

## Streamlit App Features

### Chat Interface
- Full message history display
- Source attribution for each answer
- Automatic message management

### Sidebar Controls
- **Top K Chunks**: Adjust number of retrieved documents
- **Use MMR Retrieval**: Toggle between MMR and similarity search
- **Use Chat History**: Enable/disable history in LLM context
- **Export History**: Download conversation as markdown
- **Clear Chat**: Reset conversation
- **Statistics**: View conversation metrics
- **Recent Summary**: Last few messages overview

### Statistics Dashboard
Real-time metrics:
- Total message count
- User vs Assistant message count
- Session duration
- Conversation summary

## Example Scripts

```bash
# Interactive examples
python scripts/example_chat_history.py
```

Covers:
1. Basic history management
2. Save/load conversations
3. Multi-turn RAG
4. Statistics
5. Export as markdown
6. Context windows
7. Memory management

## Best Practices

### 1. When to Use History
✅ **Use history when:**
- Building conversational assistants
- Questions reference previous answers
- User asks follow-up questions
- You want context continuity

❌ **Don't use history when:**
- Each question is independent
- Memory is limited
- Processing many documents
- Speed is critical

### 2. Memory Management
```python
# For long conversations, limit history
history = ChatHistory(max_history=20)  # Keep last 20 messages

# For short chats, allow more
history = ChatHistory(max_history=100)
```

### 3. Context Windows
```python
# Don't use too large windows
context = history.get_conversation_context(window_size=4)  # ✓ Good

context = history.get_conversation_context(window_size=50)  # ✗ Too large
```

### 4. Persistence
```python
# Auto-save after each interaction
history.save_to_file(history_file)

# Load on startup
history.load_from_file(history_file)
```

## Troubleshooting

### History Not Appearing
```python
# Make sure to use history in generator
answer = generate_answer(
    question,
    chunks,
    chat_history=history,      # ✓ Pass history
    use_history=True           # ✓ Enable it
)
```

### Messages Lost After Refresh (Streamlit)
```python
# Messages are stored in session_state, survives page refresh
# To persist across sessions, save to file:
history.save_to_file(Path("data/chat_history.json"))
```

### History Too Large
```python
# Set reasonable max_history
history = ChatHistory(max_history=50)  # Automatic cleanup

# Or manually clear
history.clear()
```

## API Reference

### ChatHistory Methods

| Method | Description |
|--------|-------------|
| `add_user_message(content)` | Add user message |
| `add_assistant_message(content, sources)` | Add assistant message |
| `add_system_message(content)` | Add system message |
| `get_all_messages()` | Get all messages |
| `get_last_n_messages(n)` | Get last n messages |
| `get_conversation_context(window_size)` | Get LangChain messages |
| `get_summary(max_messages)` | Get text summary |
| `get_stats()` | Get statistics dict |
| `save_to_file(filepath)` | Save to JSON |
| `load_from_file(filepath)` | Load from JSON |
| `export_as_markdown()` | Export as MD |
| `clear()` | Clear all messages |
| `__len__()` | Message count |

### Message Methods

| Method | Description |
|--------|-------------|
| `to_dict()` | Convert to dict |
| `from_dict(data)` | Create from dict |
| `to_langchain_message()` | Convert to LangChain |

## Next Steps

1. Run the Streamlit app: `streamlit run scripts/streamlit_app.py`
2. Experiment with the chat history features
3. Review `scripts/example_chat_history.py` for detailed examples
4. Integrate into your own RAG application
