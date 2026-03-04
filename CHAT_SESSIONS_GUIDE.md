# Chat Session Management - User Guide

## Overview

The RAG Chat application now supports multiple chat sessions with automatic saving and loading. You can create new chats, save your conversations, and switch between different chat sessions seamlessly.

## Features

### 🆕 New Chat
Create a fresh chat session while automatically saving your current conversation.

**How to use:**
1. Click "🆕 New Chat" button in the sidebar
2. Your current chat (if it has messages) is automatically saved
3. A new empty chat session starts
4. You can return to the saved chat anytime

### 💾 Saved Chats
All your chat sessions are automatically saved in memory during your browser session.

**Auto-save:**
- Chats are automatically saved after each question-answer exchange
- No manual save action needed
- Session storage persists until you close the browser

**What's saved:**
- Full conversation history
- Message timestamps
- Source references
- Chat title (based on first question)

### 📂 Load Previous Chats
Access and continue any of your previous conversations.

**Saved chat information:**
- 📝 Chat title (first 50 characters of your first question)
- 🕒 Timestamp (when the chat was last updated)
- 💬 Message count

**How to load:**
1. Find the chat in "💾 Saved Chats" section in sidebar
2. Click on the chat title to expand details
3. Click "📂 Load" button
4. The chat's full history is restored

### 🗑️ Delete Chats
Remove saved chats you no longer need.

**How to delete:**
1. Expand the saved chat entry
2. Click "🗑️ Delete" button
3. Chat is permanently removed from session storage

### 📥 Export Chat
Download individual chat sessions as markdown files.

**File naming:**
- Format: `chat_<session_id>.md`
- Example: `chat_a1b2c3d4.md`

### 🗑️ Clear Current Chat
Clear the current conversation without saving (messages will be lost).

## Interface Layout

```
Sidebar:
├── Settings
│   ├── Top K Chunks
│   ├── Use MMR Retrieval
│   └── Use Chat History
├── History Management
│   ├── 🆕 New Chat (save current + create new)
│   ├── 📥 Export (download current as .md)
│   └── 🗑️ Clear (delete current without saving)
├── 💾 Saved Chats (if any exist)
│   ├── 📝 Chat Title 1
│   │   ├── 🕒 2026-03-04 14:30:15
│   │   ├── 💬 8 messages
│   │   ├── 📂 Load
│   │   └── 🗑️ Delete
│   └── 📝 Chat Title 2
│       └── ...
├── Statistics
│   ├── Messages, User Messages
│   └── Assistant Messages, Duration
└── Recent Conversation (summary)

Main Area:
├── 💬 [Chat Title]  [💾 Saved / 📝 Unsaved]
├── Conversation messages...
└── Chat input box
```

## Status Indicators

In the main chat area, you'll see status indicators:

- **💾 Saved** - Current chat is saved in session storage
- **📝 Unsaved** - Current chat has messages but hasn't been saved yet (will auto-save on next exchange)
- **New Chat** - No messages in current chat

## Example Workflow

### Starting Multiple Conversations

```
1. Start first chat:
   Q: "What is Python?"
   A: [Answer about Python]
   → Auto-saved after response

2. Create new chat:
   Click "🆕 New Chat"
   → First chat is saved
   → New empty chat starts

3. Start second topic:
   Q: "What is accounting?"
   A: [Answer about accounting]
   → Auto-saved after response

4. Switch back to first chat:
   Sidebar → 💾 Saved Chats → "What is Python?" → 📂 Load
   → Full Python conversation restored
```

### Managing Multiple Projects

```
Session 1: Python Learning
├── Q: What is OOP?
├── A: [OOP explanation]
├── Q: In detail
└── A: [Detailed OOP explanation]

Session 2: Accounting Notes
├── Q: What is a debit note?
├── A: [Debit note explanation]
├── Q: Give me an example
└── A: [Example provided]

Session 3: Research Notes
├── Q: What is machine learning?
└── A: [ML explanation]

All sessions accessible via sidebar!
```

## Technical Details

### Session Storage
- **Storage:** Streamlit session state (browser memory)
- **Persistence:** Active during browser session only
- **Capacity:** Limited by browser memory (typically handles 50+ chats)
- **Data structure:** Dictionary with session IDs as keys

### Chat Titles
- Generated from first user message
- Maximum 50 characters
- Adds "..." if truncated
- Default: "New Chat" if no messages

### Auto-Save Triggers
- After each complete question-answer exchange
- Before creating a new chat
- Manual via "🆕 New Chat" button

### Session IDs
- Format: UUID v4 (e.g., `a1b2c3d4-e5f6-7890-1234-567890abcdef`)
- Unique per chat session
- Used for internal tracking and export filenames

## Limitations & Considerations

### Session Persistence
- ⚠️ Chats are stored in browser session state only
- ⚠️ Closing the browser tab will lose all saved chats
- ⚠️ Not saved to disk (use Export to preserve permanently)
- ✅ Solution: Export important chats as markdown files

### Memory Management
- Each chat stores full conversation history
- Large numbers of chats (100+) may impact performance
- Recommend exporting and deleting old chats periodically

### Best Practices
1. **Export important chats** - Use 📥 Export to save permanently
2. **Delete unused chats** - Keep session storage clean
3. **Use descriptive first questions** - Makes chat titles more useful
4. **Create new chats for different topics** - Better organization

## Troubleshooting

### Chat not appearing in saved list
**Cause:** Chat has no messages  
**Solution:** Send at least one question to trigger auto-save

### Lost all saved chats
**Cause:** Browser tab/session closed  
**Solution:** Export important chats before closing browser

### Can't load a saved chat
**Cause:** Session storage corrupted  
**Solution:** Refresh the page (will reset all chats)

### Chat title shows "New Chat"
**Cause:** No user messages in chat yet  
**Solution:** Ask a question - title updates automatically

## Keyboard Shortcuts

- **Enter** - Send message
- **Shift+Enter** - New line in message (if input supports it)

## Tips & Tricks

### Organizing Chats
- Start each chat with a clear, descriptive question
- Example: "Python OOP concepts" instead of "Tell me about this"

### Quick Switching
- Keep frequently used chats at top by loading them recently
- Delete old chats to reduce clutter

### Backup Strategy
1. Export chats at end of work session
2. Save markdown files to your documents folder
3. Can import context by copying text back if needed

### Performance
- Keep total saved chats under 20 for best performance
- Each chat with 50 messages ≈ 10-20 KB memory
- Monitor if app becomes slow, delete old chats

## API Reference

### Functions

**`get_chat_title(chat_history: ChatHistory) -> str`**
- Generates title from first user message
- Returns "New Chat" if no messages

**`save_current_chat()`**
- Saves current chat to session storage
- Only saves if chat has messages
- Updates existing save if session ID exists

**`create_new_chat()`**
- Saves current chat (if has messages)
- Creates new session with unique ID
- Initializes empty ChatHistory

**`load_chat(session_id: str)`**
- Loads chat from session storage
- Copies all messages to current history
- Sets current session ID to loaded chat

**`delete_chat(session_id: str)`**
- Removes chat from session storage
- Permanent deletion (can't undo)

## Future Enhancements (Not Yet Implemented)

- Persistent storage to database/file system
- Search across saved chats
- Tags/categories for chats
- Bulk export of all chats
- Import chats from markdown
- Share chats with others
- Cloud sync across devices

## Related Documentation

- [FOLLOWUP_QUICK_REFERENCE.md](FOLLOWUP_QUICK_REFERENCE.md) - Follow-up questions
- [CHAT_HISTORY_GUIDE.md](CHAT_HISTORY_GUIDE.md) - Chat history management
- [LANGCHAIN_QUICKSTART.md](LANGCHAIN_QUICKSTART.md) - System setup

---

**Feature Version:** 1.0  
**Implementation Date:** Latest Session  
**Status:** ✅ Fully Functional  
**Tested:** Yes  
**Backward Compatible:** Yes
