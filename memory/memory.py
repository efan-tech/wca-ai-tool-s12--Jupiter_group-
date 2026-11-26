# ==========================================
# MYMFIT AI - CONVERSATION MEMORY
# ==========================================

# This file manages conversation history.


def create_conversation():

    """
    Creates a new conversation history.
    """

    return []


def add_user_message(history, message):

    """
    Adds a user's message to conversation history.
    """

    history.append({
        "role": "user",
        "content": message
    })


def add_ai_message(history, message):

    """
    Adds MYMFIT AI's response to conversation history.
    """

    history.append({
        "role": "assistant",
        "content": message
    })


def get_conversation_length(history):

    """
    Counts the number of user turns.
    """

    return sum(
        1 for message in history
        if message["role"] == "user"
    )