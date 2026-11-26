# ==========================================
# MYMFIT AI - GROQ API CLIENT
# ==========================================

import os
import json

from dotenv import load_dotenv
from groq import Groq

from ai.prompts import SYSTEM_PROMPT, SUMMARY_PROMPT, build_system_prompt

from cache.cache_manager import (
    initialize_cache,
    generate_cache_key,
    get_cached_response,
    save_cached_response
)


# ==========================================
# ENVIRONMENT CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("Groq API key not found!")

client = Groq(api_key=API_KEY)

MODEL = "openai/gpt-oss-20b"


# ==========================================
# SESSION TOKEN TRACKER
# ==========================================

SESSION_USAGE = {
    "input_tokens": 0,
    "output_tokens": 0,
    "api_requests": 0,
    "cache_hits": 0,
    "cache_misses": 0
}


def reset_session_usage():

    for key in SESSION_USAGE:
        SESSION_USAGE[key] = 0


def get_session_usage():

    return SESSION_USAGE.copy()


def record_token_usage(response):

    usage = response.usage

    if usage:

        SESSION_USAGE["input_tokens"] += usage.prompt_tokens

        SESSION_USAGE["output_tokens"] += usage.completion_tokens


# ==========================================
# INITIALIZE CACHE
# ==========================================

initialize_cache()


# ==========================================
# VALIDATE AI RESPONSE
# ==========================================

def validate_response(data):

    if not isinstance(data, dict):
        return False

    if not isinstance(data.get("message"), str):
        return False

    if not data["message"].strip():
        return False

    if not isinstance(data.get("recommendations"), list):
        return False

    if not isinstance(data.get("next_question"), str):
        return False

    if not isinstance(data.get("safety_note"), str):
        return False

    for item in data["recommendations"]:

        if not isinstance(item, dict):
            return False

        if not isinstance(item.get("title"), str):
            return False

        if not isinstance(item.get("details"), str):
            return False

        if not item["title"].strip():
            return False

        if not item["details"].strip():
            return False

    return True


# ==========================================
# ASK AI WITH AUTOMATIC CACHING
# ==========================================

def ask_ai(conversation_history , client_profile_text=None):

    try:

        if not conversation_history:
            return {"error": "No question provided."}, None

        latest_question = conversation_history[-1]["content"]

        previous_history = conversation_history[:-1]

        cache_key = generate_cache_key(
            latest_question,
            previous_history,
            SYSTEM_PROMPT,
            MODEL
        )

        # CHECK LOCAL CACHE

        cached_response = get_cached_response(cache_key)

        if cached_response is not None:

            SESSION_USAGE["cache_hits"] += 1

            print("\n[CACHE HIT] Retrieved answer locally.")

            return cached_response, json.dumps(cached_response)

        SESSION_USAGE["cache_misses"] += 1

        print("\n[CACHE MISS] Contacting Groq API...")
# Build system prompt (with or without client profile)
        system_content = build_system_prompt(client_profile_text)

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend(conversation_history)

        # ALLOW ONE RETRY

        for attempt in range(2):

            response = client.chat.completions.create(

                model=MODEL,

                messages=messages,

                temperature=0.7,

                max_completion_tokens=1000,

                response_format={"type": "json_object"}

            )

            SESSION_USAGE["api_requests"] += 1

            record_token_usage(response)

            answer = response.choices[0].message.content

            try:

                parsed_answer = json.loads(answer)

            except (json.JSONDecodeError, TypeError):

                parsed_answer = None

            if parsed_answer is not None and validate_response(parsed_answer):

                print("\n[VALIDATION SUCCESS] Response is valid.")

                usage = response.usage

                save_cached_response(

                    cache_key,

                    latest_question,

                    parsed_answer,

                    usage.prompt_tokens if usage else 0,

                    usage.completion_tokens if usage else 0

                )

                print("[NEW RESPONSE] Answer saved in local cache.")

                return parsed_answer, answer

            print("\n[VALIDATION FAILED] Invalid AI response.")

            if attempt == 0:

                print("[RETRY] Asking AI to correct its response.")

                messages.append({
                    "role": "assistant",
                    "content": answer or ""
                })

                messages.append({
                    "role": "user",
                    "content": (
                        "Correct your previous response. Return valid JSON "
                        "with exactly these fields: message, recommendations, "
                        "next_question and safety_note. "
                        "Recommendations may be an empty list when unnecessary. "
                        "Use an empty string for an unnecessary next_question "
                        "or safety_note."
                    )
                })

        return {
            "error": (
                "MYMFIT AI could not produce a valid response. "
                "Please try again."
            )
        }, None

    except Exception as error:

        return {
            "error": str(error)
        }, None


# ==========================================
# GENERATE SESSION SUMMARY
# ==========================================

def generate_summary(conversation_history):

    try:

        messages = [

            {
                "role": "system",
                "content": SUMMARY_PROMPT
            },

            {
                "role": "user",
                "content": json.dumps(
                    conversation_history,
                    ensure_ascii=False
                )
            }

        ]

        response = client.chat.completions.create(

            model=MODEL,

            messages=messages,

            temperature=0.3,

            max_completion_tokens=1200,

            response_format={"type": "json_object"}

        )

        SESSION_USAGE["api_requests"] += 1

        record_token_usage(response)

        answer = response.choices[0].message.content

        return json.loads(answer)

    except Exception as error:

        print("\nSummary generation failed:", error)

        return {
            "error": "Summary could not be generated."
        }
        
