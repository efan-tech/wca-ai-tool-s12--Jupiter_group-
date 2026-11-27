# ==========================================
# MYMFIT AI - ANTHROPIC API CLIENT
# ==========================================

import os
import json

from dotenv import load_dotenv
from anthropic import Anthropic

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

API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise ValueError("Anthropic API key not found! Set ANTHROPIC_API_KEY in your .env file.")

client = Anthropic(api_key=API_KEY)

MODEL = "claude-sonnet-5-5"


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
        SESSION_USAGE["input_tokens"] += usage.input_tokens
        SESSION_USAGE["output_tokens"] += usage.output_tokens


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

def ask_ai(conversation_history, client_profile_text=None):
    try:
        if not conversation_history:
            return {"error": "No question provided."}, None

        latest_question = conversation_history[-1]["content"]
        previous_history = conversation_history[:-1]

        # Build system prompt (with or without client profile)
        system_content = build_system_prompt(client_profile_text)

        cache_key = generate_cache_key(
            latest_question,
            previous_history,
            system_content,   # use the actual system prompt being sent
            MODEL
        )

        # CHECK LOCAL CACHE
        cached_response = get_cached_response(cache_key)

        if cached_response is not None:
            SESSION_USAGE["cache_hits"] += 1
            print("\n[CACHE HIT] Retrieved answer locally.")
            return cached_response, json.dumps(cached_response)

        SESSION_USAGE["cache_misses"] += 1
        print("\n[CACHE MISS] Contacting Anthropic API...")

        # Anthropic expects only "user" and "assistant" roles in messages
        messages = conversation_history.copy()

        # ALLOW ONE RETRY
        for attempt in range(2):
            response = client.messages.create(
                model=MODEL,
                max_tokens=1000,
                system=system_content,          # system prompt goes here
                messages=messages
            )

            SESSION_USAGE["api_requests"] += 1
            record_token_usage(response)

            # Extract text content
            answer = ""
            
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    answer += block.text
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
                    usage.input_tokens if usage else 0,
                    usage.output_tokens if usage else 0
                )

                print("[NEW RESPONSE] Answer saved in local cache.")
                return parsed_answer, answer

            print("\n[VALIDATION FAILED] Invalid AI response.")

            if attempt == 0:
                print("[RETRY] Asking AI to correct its response.")

                # Append the failed assistant response + correction instruction
                messages.append({
                    "role": "assistant",
                    "content": answer or ""
                })
                messages.append({
                    "role": "user",
                    "content": (
                        "Correct your previous response. Return ONLY valid JSON "
                        "with exactly these fields: message, recommendations, "
                        "next_question and safety_note. "
                        "Recommendations may be an empty list when unnecessary. "
                        "Use an empty string for an unnecessary next_question "
                        "or safety_note. Do not include any markdown or extra text."
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
        response = client.messages.create(
            model=MODEL,
            max_tokens=1200,
            system=SUMMARY_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(
                        conversation_history,
                        ensure_ascii=False
                    )
                }
            ]
        )

        SESSION_USAGE["api_requests"] += 1
        record_token_usage(response)

        answer = ""
        
        for block in response.content:
            if getattr(block, "type", None) == "text":
                answer += block.text
                answer += block.text

        return json.loads(answer)

    except Exception as error:
        print("\nSummary generation failed:", error)
        return {
            "error": "Summary could not be generated."
        }
