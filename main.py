# ==========================================
# MYMFIT AI - MAIN APPLICATION
# ==========================================

from ai.anthropic_client import ask_ai, generate_summary

from memory.conversation import (
    create_conversation,
    add_user_message,
    add_ai_message,
    get_conversation_length
)

from memory.session_manager import (
    save_session,
    list_sessions,
    open_session
)


# ==========================================
# DISPLAY AI RESPONSE
# ==========================================

def display_response(response):

    print("\nMYMFIT AI:")

    print(response["message"])

    print("\nRECOMMENDATIONS:")

    for item in response["recommendations"]:

        print("\n- " + item["title"])

        print(item["details"])

    print("\nFOLLOW-UP QUESTION:")

    print(response["next_question"])

    print("\nSAFETY NOTE:")

    print(response["safety_note"])


# ==========================================
# DISPLAY PREVIOUS SESSION
# ==========================================

def display_saved_session(session):

    print("\n========== PREVIOUS SESSION ==========")

    print("DATE:", session.get("session_date"))

    print("\nCONVERSATION:")

    for message in session.get("conversation", []):

        role = message["role"].upper()

        print(f"\n{role}:")

        print(message["content"])

    print("\nSESSION SUMMARY:")

    print(session.get("summary"))

    print("\n======================================")


# ==========================================
# START NEW SESSION
# ==========================================

def start_session():

    history = create_conversation()

    print("\n=================================")

    print("       MYMFIT AI COACH")

    print("=================================")

    print("Tell me about your fitness journey.")

    print("Type 'exit' to end the session.")

    print("=================================")

    while True:

        question = input("\nYou: ").strip()

        if not question:

            print("Please enter a message.")

            continue

        if question.lower() == "exit":

            break

        add_user_message(history, question)

        print("\nMYMFIT AI is thinking...")

        response, raw_answer = ask_ai(history)

        if "error" in response:

            print("\nError:", response["error"])

            history.pop()

            continue

        add_ai_message(history, raw_answer)

        display_response(response)

        print(
            "\nTurns completed:",
            get_conversation_length(history)
        )

    # ======================================
    # END SESSION AND GENERATE SUMMARY
    # ======================================

    if not history:

        print("\nNo conversation to save.")

        return

    print("\nGenerating your session summary...")

    summary = generate_summary(history)

    filepath = save_session(history, summary)

    if filepath:

        print("\nYour session was saved successfully!")

        print("File:", filepath)

    else:

        print("\nYour session could not be saved.")


# ==========================================
# OPEN A PREVIOUS SESSION
# ==========================================

def view_previous_session():

    sessions = list_sessions()

    if not sessions:

        print("\nNo previous sessions found.")

        return

    print("\n========== SAVED SESSIONS ==========")

    for index, filename in enumerate(sessions, 1):

        print(f"{index}. {filename}")

    print("0. Return to main menu")

    choice = input("\nSelect a session: ").strip()

    if choice == "0":

        return

    try:

        index = int(choice) - 1

        if index < 0 or index >= len(sessions):

            print("Invalid selection.")

            return

        session = open_session(sessions[index])

        if session:

            display_saved_session(session)

    except ValueError:

        print("Please enter a valid number.")


# ==========================================
# MAIN MENU
# ==========================================

def main():

    while True:

        print("\n=================================")

        print("          MYMFIT AI")

        print("=================================")

        print("1. Start New Session")

        print("2. View Previous Sessions")

        print("3. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":

            start_session()

        elif choice == "2":

            view_previous_session()

        elif choice == "3":

            print("\nThank you for using MYMFIT AI!")

            break

        else:

            print("\nInvalid choice. Try again.")


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    main()
