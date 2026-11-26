# ==========================================
# MYMFIT AI - SESSION MANAGER
# ==========================================

import os
import json
from datetime import datetime


# Directory for storing conversations
SESSION_DIR = "data/sessions"


# Ensure directory exists
os.makedirs(SESSION_DIR, exist_ok=True)


# ==========================================
# SAVE SESSION
# ==========================================

def save_session(history, summary, client_id=None, client_name=None):
    """
    Saves a conversation session.
    Optionally links it to a client.
    """

    try:
        timestamp = datetime.now()

        filename = timestamp.strftime(
            "%Y-%m-%d_session_%H%M%S.json"
        )

        filepath = os.path.join(SESSION_DIR, filename)

        session_data = {
            "session_date": timestamp.isoformat(),
            "client_id": client_id,
            "client_name": client_name,
            "conversation": history,
            "summary": summary
        }

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(
                session_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        return filepath

    except (OSError, TypeError, ValueError) as error:
        print("Could not save session:", error)
        return None


# ==========================================
# LIST ALL SESSIONS
# ==========================================

def list_sessions():
    """
    Returns a list of all session filenames (newest first).
    """

    try:
        files = os.listdir(SESSION_DIR)

        sessions = [
            file for file in files
            if file.endswith(".json")
        ]

        return sorted(sessions, reverse=True)

    except OSError as error:
        print("Could not access sessions:", error)
        return []


# ==========================================
# LIST SESSIONS FOR A SPECIFIC CLIENT
# ==========================================

def list_sessions_for_client(client_id):
    """
    Returns session filenames that belong to a specific client.
    """

    if not client_id:
        return []

    matching = []

    try:
        for filename in list_sessions():
            session = open_session(filename)
            if session and session.get("client_id") == client_id:
                matching.append(filename)

        return matching

    except Exception as error:
        print("Could not filter sessions:", error)
        return []


# ==========================================
# OPEN PREVIOUS SESSION
# ==========================================

def open_session(filename):
    """
    Loads a session by filename.
    Works with both old and new session formats.
    """

    filepath = os.path.join(SESSION_DIR, filename)

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print("Session file not found.")
        return None

    except (OSError, json.JSONDecodeError) as error:
        print("Could not open session:", error)
        return None
