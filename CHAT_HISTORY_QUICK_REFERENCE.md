# Chat History - Quick Reference

## 30-Second Quick Start

```python
from rag_app.core.chat_history import ChatHistory
from rag_app.core.retriever import retrieve
from rag_app.core.generator import generate_answer

# Create history
history = ChatHistory(max_history=50)

# Multi-turn conversation
for turn in range(3):
    question = input("Q: ")
    chunks = retrieve(question)
    answer = generate_answer(
        question, 
        chunks, 
        chat_history=history,  # Pass history
        use_history=True       # Enable it
    )
    print(f"A: {answer}")
    
    # Save to history
    history.add_user_message(question)
    history.add_assistant_message(answer)

# Save conversation
history.save_to_file(Path("my_chat.json"))
```

## Most Common Tasks

### 1. Create Chat History
```python
history = ChatHistory(max_history=50)
```

### 2. Add Messages
```python
history.add_user_message("What is X?")
history.add_assistant_message("X is...", sources=["doc.txt"])
```

### 3. Use in LLM
```python
answer = generate_answer(query, chunks, chat_history=history, use_history=True)
```

### 4. Save & Load
```python
history.save_to_file(Path("chat.json"))
history.load_from_file(Path("chat.json"))
```

### 5. Export as Markdown
```python
md = history.export_as_markdown()
```

### 6. Get Statistics
```python
stats = history.get_stats()
print(stats['total_messages'])
```

### 7. Clear History
```python
history.clear()
```

## Streamlit UI
```bash
streamlit run scripts/streamlit_app.py
```
- Auto-saves history in session state
- Export with button
- View stats in sidebar
- Toggle history usage

## Examples
```bash
python scripts/example_chat_history.py
# Shows 7 complete examples
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_history` | 50 | Max messages to keep |
| `window_size` | 4 | Context messages for LLM |
| `use_history` | True | Include history in LLM |
| `use_mmr` | True | Use MMR for retrieval |

## Statistics Available

```python
stats = history.get_stats()

# Returns dict with:
- total_messages
- user_messages
- assistant_messages
- user_total_chars
- assistant_total_chars
- avg_user_message_length
- avg_assistant_message_length
- session_duration
```

## API Cheat Sheet

```python
# Create
history = ChatHistory(max_history=50)

# Add
history.add_user_message(content)
history.add_assistant_message(content, sources=[...])
history.add_system_message(content)

# Access
history.get_all_messages()
history.get_last_n_messages(5)
history.get_conversation_context(window_size=4)

# Info
history.get_summary(max_messages=5)
history.get_stats()
len(history)

# File
history.save_to_file(Path(...))
history.load_from_file(Path(...))
history.export_as_markdown()

# Manage
history.clear()
```

## When to Use

✅ **Use History When:**
- Multi-turn conversations
- Questions reference previous answers
- You want context continuity
- Building chatbots

❌ **Skip History When:**
- Single questions only
- Memory is critical
- Processing many documents
- Speed is essential

## Tips & Tricks

### 1. Limited Memory
```python
# Keep only recent 20 messages
history = ChatHistory(max_history=20)
```

### 2. Large Context
```python
# Use last 10 messages as context
context = history.get_conversation_context(window_size=10)
```

### 3. Persistent Chats
```python
# Load on start
history = ChatHistory()
history.load_from_file(Path("chat.json"))

# Save after each message
history.save_to_file(Path("chat.json"))
```

### 4. Batch Processing
```python
# Process messages without saving all
for q in questions:
    answer = generate_answer(q, chunks, use_history=False)
```

### 5. Export for Sharing
```python
md = history.export_as_markdown()
with open("conversation.md") as f:
    f.write(md)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| History not used | Set `use_history=True` in `generate_answer()` |
| Messages lost | Use `save_to_file()` for persistence |
| Too much memory | Reduce `max_history` parameter |
| History too short | Increase `window_size` or `max_history` |
| Export not working | Check file permissions |

## Common Patterns

### Pattern 1: Basic Streaming
```python
history = ChatHistory()
for user_input in stream():
    answer = generate_answer(user_input, chunks, chat_history=history)
    history.add_user_message(user_input)
    history.add_assistant_message(answer)
```

### Pattern 2: Persistent Bot
```python
history = ChatHistory()
history.load_from_file(history_file)

answer = generate_answer(q, chunks, chat_history=history, use_history=True)
history.add_user_message(q)
history.add_assistant_message(answer)

history.save_to_file(history_file)
```

### Pattern 3: Streamlit App
```python
# In session_state
st.session_state.history = ChatHistory()

# After LLM call
st.session_state.history.add_assistant_message(answer)
```

### Pattern 4: Batch Analysis
```python
rag = ConversationalRAG(max_history=50)

for qa_pair in qa_list:
    rag.add_to_history(qa_pair['q'], qa_pair['a'])

stats = rag.get_history().get_stats()
```

## Next Steps

1. Try: `python scripts/example_chat_history.py`
2. Read: [CHAT_HISTORY_GUIDE.md](CHAT_HISTORY_GUIDE.md)
3. Run: `streamlit run scripts/streamlit_app.py`
4. Explore: `src/rag_app/core/chat_history.py`

---

**Need more details?** → [CHAT_HISTORY_GUIDE.md](CHAT_HISTORY_GUIDE.md)
**Want to see examples?** → [scripts/example_chat_history.py](scripts/example_chat_history.py)
**Using Streamlit?** → `streamlit run scripts/streamlit_app.py`
