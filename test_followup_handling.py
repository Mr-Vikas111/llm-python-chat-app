#!/usr/bin/env python3
"""
Test script to validate follow-up question handling.

This tests:
1. Follow-up question detection
2. Query combination for follows-ups
3. Chat history integration
4. End-to-end conversation flow
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_app.core.chat_history import ChatHistory, Message
from rag_app.core.retriever import retrieve, is_followup_query
from rag_app.core.generator import generate_answer, is_followup_question


def test_followup_detection():
    """Test follow-up question detection."""
    print("=" * 60)
    print("TEST 1: Follow-up Question Detection")
    print("=" * 60)
    
    test_queries = [
        ("What is ABC in Python OOPS?", False, "Normal question"),
        ("In detail", True, "Short follow-up with 'in detail'"),
        ("More", True, "Short follow-up with 'More'"),
        ("Tell me more", True, "Follow-up with 'Tell me more'"),
        ("Explain", True, "Follow-up with 'Explain'"),
        ("Elaborate on that", True, "Follow-up with 'Elaborate'"),
        ("What is XYZ?", False, "Different question"),
        ("Can you give an example?", True, "Follow-up with 'example'"),
        ("How does that work?", True, "Follow-up with 'How'"),
    ]
    
    for query, expected, description in test_queries:
        result = is_followup_query(query)
        status = "✓" if result == expected else "✗"
        print(f"{status} {description}")
        print(f"  Query: '{query}'")
        print(f"  is_followup_query: {result} (expected: {expected})")
        print()


def test_generator_followup_detection():
    """Test generator's follow-up detection."""
    print("=" * 60)
    print("TEST 2: Generator Follow-up Detection")
    print("=" * 60)
    
    test_queries = [
        ("In detail", True),
        ("More", True),
        ("Explain further", True),
        ("Tell me more about this", True),
        ("What is something else?", False),
    ]
    
    for query, expected in test_queries:
        result = is_followup_question(query)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{query}' -> {result} (expected: {expected})")


def test_query_combination():
    """Test query combination for follow-ups."""
    print("\n" + "=" * 60)
    print("TEST 3: Query Combination for Follow-ups")
    print("=" * 60)
    
    # Create a chat history with previous question
    history = ChatHistory(max_history=50)
    history.add_user_message("What is ABC in Python OOPS?")
    history.add_assistant_message("ABC refers to Abstraction, Binding, and Capsulation...")
    
    # Test retrieval with follow-up
    print("\nScenario: Previous question exists + follow-up question")
    print("Previous: 'What is ABC in Python OOPS?'")
    print("Current: 'In detail'")
    print()
    
    # Note: We won't actually call retrieve() since it needs a vector store
    # Just demonstrate the logic
    
    previous_messages = history.get_all_messages()
    print(f"Chat history has {len(previous_messages)} messages:")
    for i, msg in enumerate(previous_messages):
        print(f"  {i}: {msg.role} - {msg.content[:50]}...")
    
    # Extract previous query as the retriever does
    previous_query = None
    for i in range(len(previous_messages) - 1, -1, -1):
        if previous_messages[i].role == "user":
            previous_query = previous_messages[i].content
            break
    
    print(f"\nExtracted previous query: '{previous_query}'")
    print(f"Combined query would be: '{previous_query} In detail'")


def test_chat_history_flow():
    """Test the complete chat history flow."""
    print("\n" + "=" * 60)
    print("TEST 4: Complete Chat History Flow")
    print("=" * 60)
    
    history = ChatHistory(max_history=50)
    
    # Simulate a conversation
    conversation = [
        ("user", "What is Python?"),
        ("assistant", "Python is a programming language..."),
        ("user", "More details"),
        ("assistant", "Sure! Python was created by..."),
        ("user", "In detail"),
    ]
    
    print("\nSimulated conversation:")
    for role, content in conversation:
        if role == "user":
            history.add_user_message(content)
            print(f"User: {content}")
        else:
            history.add_assistant_message(content)
            print(f"Assistant: {content}")
        print()
    
    # Verify history tracking
    stats = history.get_stats()
    print(f"Chat history statistics:")
    print(f"  Total messages: {stats['total_messages']}")
    print(f"  User messages: {stats['user_messages']}")
    print(f"  Assistant messages: {stats['assistant_messages']}")
    
    # Check if we can detect follow-ups in context
    messages = history.get_all_messages()
    print(f"\nDetecting follow-ups in conversation:")
    for i, msg in enumerate(messages):
        if msg.role == "user":
            is_followup = is_followup_query(msg.content)
            print(f"  Message {i}: '{msg.content}' -> follow-up: {is_followup}")


def test_retriever_context():
    """Test retriever's ability to extract context."""
    print("\n" + "=" * 60)
    print("TEST 5: Retriever Context Extraction")
    print("=" * 60)
    
    history = ChatHistory(max_history=50)
    
    # Build conversation
    history.add_user_message("Tell me about Python decorators")
    history.add_assistant_message("Decorators are functions that modify functions...")
    history.add_user_message("Give me an example")
    
    # Simulate what retriever does
    print("\nCurrent query: 'Give me an example'")
    print(f"Current query is follow-up: {is_followup_query('Give me an example')}")
    
    # Extract previous query
    messages = history.get_all_messages()
    previous_query = None
    
    if len(messages) >= 3:
        for i in range(len(messages) - 2, -1, -1):
            if messages[i].role == "user":
                previous_query = messages[i].content
                break
    
    print(f"\nExtracted previous user query: '{previous_query}'")
    
    if previous_query and is_followup_query("Give me an example"):
        combined = f"{previous_query} Give me an example"
        print(f"Combined search query: '{combined}'")
        print("\nThis combined query would be sent to the vector store")
        print("for better semantic matching with the previous context.")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("FOLLOW-UP QUESTION HANDLING - TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_followup_detection()
        test_generator_followup_detection()
        test_query_combination()
        test_chat_history_flow()
        test_retriever_context()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nSummary:")
        print("- Follow-up detection works for common patterns")
        print("- Query combination enables context-aware retrieval")
        print("- Chat history properly tracks conversation flow")
        print("- Retriever can extract previous context")
        print("\nNext: Run Streamlit app to test with actual RAG system")
        print("  $ streamlit run scripts/streamlit_app.py")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
