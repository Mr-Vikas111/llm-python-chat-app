from functools import lru_cache
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from rag_app.core.config import get_settings
from rag_app.core.chat_history import ChatHistory


SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer questions based on the provided context. "
    "You have access to conversation history - use it to understand references and follow-up questions. "
    "If the answer is not in the provided context but you have relevant information from the chat history, "
    "you can reference that. If truly no information is available, say you do not know."
)

SYSTEM_PROMPT_WITH_HISTORY = (
    "You are a helpful assistant. Answer questions based on the provided context and conversation history. "
    "The user may ask follow-up questions or request more details about previous topics. "
    "When you see brief questions like 'In detail', 'More', 'Tell me more', understand they reference "
    "the previous question in the conversation history. "
    "Use the conversation history to understand the context of the current question. "
    "Provide detailed answers based on both the context provided and the conversation history. "
    "If the answer is not in context, say you do not know."
)


def is_followup_question(question: str) -> bool:
    """
    Detect if a question is likely a follow-up to the previous one.
    
    Examples of follow-up questions:
    - "In detail"
    - "More"
    - "Tell me more"
    - "Explain further"
    - "Can you elaborate?"
    """
    followup_keywords = [
        "in detail",
        "more",
        "tell me more",
        "explain",
        "elaborate",
        "expand",
        "further",
        "deeper",
        "clearer",
        "example",
        "specifically",
        "clarify",
        "what do you mean",
        "can you",
    ]
    
    question_lower = question.lower().strip()
    
    # Check for very short questions (usually follow-ups)
    if len(question_lower) < 30:
        return any(keyword in question_lower for keyword in followup_keywords)
    
    return False


def get_previous_question(chat_history: Optional[ChatHistory]) -> Optional[str]:
    """Extract the previous user question from chat history."""
    if not chat_history or len(chat_history) == 0:
        return None
    
    # Get all messages and find the last user message before current one
    all_messages = chat_history.get_all_messages()
    
    # Find the second-to-last user message (last is the current question being processed)
    user_messages = [msg for msg in all_messages if msg.role == "user"]
    
    if len(user_messages) >= 2:
        return user_messages[-2].content  # Return second-to-last user message
    elif len(user_messages) == 1:
        return user_messages[0].content
    
    return None


def build_context(chunks: list[dict]) -> str:
    """Build context string from retrieved chunks."""
    sections = []
    for idx, chunk in enumerate(chunks, start=1):
        sections.append(f"[{idx}] Source: {chunk['source']}\n{chunk['text']}")
    return "\n\n".join(sections)


@lru_cache(maxsize=1)
def get_chat_model():
    """Get or create the LLM chat model based on configuration."""
    settings = get_settings()

    try:
        from langchain_community.chat_models import ChatOllama
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        from langchain_openai import ChatOpenAI
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "LangChain dependencies are missing. Install with: pip install -e .[dev]"
        )

    provider = settings.llm_provider.lower()
    print(f"LLM Provider: {provider}")
    if provider == "huggingface":
        print(f"Using HuggingFace Inference API: {settings.hf_model_id}")
        
        try:
            if not settings.hf_token:
                raise ValueError(
                    "HF_TOKEN is required for HuggingFace Inference API. "
                    "Get your token from: https://huggingface.co/settings/tokens"
                )
            
            # Use HuggingFace Inference API (recommended for Streamlit)
            # Note: temperature and max_new_tokens must be direct parameters, not in model_kwargs
            endpoint_llm = HuggingFaceEndpoint(
                repo_id=settings.hf_model_id,
                task=settings.hf_task,
                huggingfacehub_api_token=settings.hf_token,
                temperature=settings.hf_temperature,
                max_new_tokens=settings.hf_max_new_tokens,
            )
            return ChatHuggingFace(llm=endpoint_llm)
        except Exception as e:
            print(f"Error loading HuggingFace Inference API: {e}")
            raise

    if provider == "ollama":
        print("Using Ollama model for LLM provider.")
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
        )

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

    print("Using OpenAI model for LLM provider.")
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0.2,
    )


def _build_messages(
    question: str,
    chunks: list[dict],
    chat_history: Optional[ChatHistory] = None,
    use_history: bool = True,
) -> list:
    """Build message list for LLM invocation."""
    settings = get_settings()
    context = build_context(chunks)
    
    # Choose system prompt based on whether history will be used
    system_prompt = SYSTEM_PROMPT_WITH_HISTORY if (chat_history and use_history) else SYSTEM_PROMPT
    
    # Build messages list
    messages = [SystemMessage(content=system_prompt)]
    
    # Add conversation history if available and enabled
    if chat_history and use_history and len(chat_history) > 0:
        # Check if this is a follow-up question
        is_followup = is_followup_question(question)
        
        # Get recent conversation context (last 6 messages for follow-ups, 4 for regular questions)
        window_size = 6 if is_followup else 4
        history_messages = chat_history.get_last_n_messages(window_size)
        
        for hist_msg in history_messages:
            messages.append(hist_msg.to_langchain_message())
    
    # Build the content for the current question
    current_content = f"Question: {question}\n"
    
    # If we have context, add it
    if context.strip():
        current_content = f"Context:\n{context}\n\n{current_content}"
    
    # Add helpful info if this seems to be a follow-up with no good context
    if is_followup_question(question) and (not context.strip() or len(chunks) == 0):
        current_content += "\nNote: This appears to be a follow-up question. Please refer to the previous messages in our conversation to provide a detailed answer about the topic we were discussing."
    else:
        current_content += "\nAnswer based on the context provided."
    
    messages.append(HumanMessage(content=current_content))
    
    return messages


def generate_answer_stream(
    question: str,
    chunks: list[dict],
    chat_history: Optional[ChatHistory] = None,
    use_history: bool = True,
):
    """
    Generate an answer using the LLM with word-by-word streaming output.
    
    Yields individual words of the response as they are generated, similar to ChatGPT.
    
    Args:
        question: The user's question
        chunks: Retrieved context chunks
        chat_history: Optional chat history for multi-turn conversations
        use_history: Whether to include chat history in the prompt
    
    Yields:
        Individual words (or spaces) of the generated answer
    """
    settings = get_settings()
    context = build_context(chunks)

    if not settings.use_llm:
        text = "LLM disabled (USE_LLM=false). Retrieved context:\n\n"
        text += context if context else "No relevant context found."
        for word in _split_into_words(text):
            yield word
        return

    try:
        chat_model = get_chat_model()
        messages = _build_messages(question, chunks, chat_history, use_history)
        
        # Stream the response word by word
        buffer = ""
        for chunk in chat_model.stream(messages):
            content = getattr(chunk, "content", "")
            if content:
                buffer += content
                # Yield complete words and spaces
                while True:
                    # Find complete words
                    space_idx = buffer.find(" ")
                    newline_idx = buffer.find("\n")
                    
                    if space_idx == -1 and newline_idx == -1:
                        # No space or newline, keep buffering
                        break
                    
                    # Find the nearest separator
                    next_sep = space_idx if space_idx != -1 else newline_idx
                    if newline_idx != -1 and newline_idx < space_idx:
                        next_sep = newline_idx
                    
                    # Yield word with separator
                    word = buffer[:next_sep]
                    separator = buffer[next_sep]
                    buffer = buffer[next_sep + 1:]
                    
                    yield word + separator
        
        # Yield remaining buffer
        if buffer:
            yield buffer

    except Exception as e:
        yield f"Error generating answer: {str(e)}"


def _split_into_words(text: str):
    """
    Split text into words and preserve spaces/newlines.
    
    Args:
        text: Text to split
        
    Yields:
        Individual words with their trailing spaces/newlines
    """
    buffer = ""
    for char in text:
        buffer += char
        if char in (" ", "\n", "\t"):
            yield buffer
            buffer = ""
    if buffer:
        yield buffer


def generate_answer(
    question: str,
    chunks: list[dict],
    chat_history: Optional[ChatHistory] = None,
    use_history: bool = True,
) -> str:
    """
    Generate an answer using the LLM based on retrieved chunks.
    
    Handles both direct questions and follow-up questions by using conversation history.
    
    Args:
        question: The user's question
        chunks: Retrieved context chunks
        chat_history: Optional chat history for multi-turn conversations
        use_history: Whether to include chat history in the prompt
    
    Returns:
        Generated answer string
    """
    settings = get_settings()
    context = build_context(chunks)

    if not settings.use_llm:
        return (
            "LLM disabled (USE_LLM=false). Retrieved context:\n\n"
            f"{context if context else 'No relevant context found.'}"
        )

    try:
        chat_model = get_chat_model()
        messages = _build_messages(question, chunks, chat_history, use_history)
        
        result = chat_model.invoke(messages)
        content = getattr(result, "content", result)
        return str(content).strip()

    except Exception as e:
        return f"Error generating answer: {str(e)}"
