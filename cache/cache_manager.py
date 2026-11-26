# ==========================================
# MYMFIT AI - CACHE AND ANALYTICS MANAGER
# ==========================================

import sqlite3
import json
import hashlib
import os

from datetime import datetime, timedelta


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE = "data/cache.db"


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_cache():

    os.makedirs("data", exist_ok=True)

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        # MAIN RESPONSE CACHE TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_cache (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                cache_key TEXT UNIQUE,

                question TEXT,

                response TEXT,

                input_tokens INTEGER DEFAULT 0,

                output_tokens INTEGER DEFAULT 0,

                created_at TEXT

            )
        """)

        # NEW ANALYTICS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_events (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                event_type TEXT,

                input_tokens INTEGER DEFAULT 0,

                output_tokens INTEGER DEFAULT 0,

                tokens_saved INTEGER DEFAULT 0,

                created_at TEXT

            )
        """)

        connection.commit()


# ==========================================
# GENERATE UNIQUE REQUEST FINGERPRINT
# ==========================================

def generate_cache_key(question, history, system_prompt, model):

    cache_data = {

        "question": question.strip().lower(),

        "history": history,

        "system_prompt": system_prompt,

        "model": model

    }

    encoded_data = json.dumps(

        cache_data,

        sort_keys=True,

        ensure_ascii=False

    )

    return hashlib.sha256(

        encoded_data.encode("utf-8")

    ).hexdigest()


# ==========================================
# CHECK WHETHER RESPONSE EXISTS
# ==========================================

def get_cached_response(cache_key, expiry_days=30):

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT response, created_at
            FROM response_cache
            WHERE cache_key = ?
        """, (cache_key,))

        result = cursor.fetchone()

    if result is None:

        return None

    response, created_at = result

    created_date = datetime.fromisoformat(created_at)

    if datetime.now() - created_date > timedelta(days=expiry_days):

        return None

    return json.loads(response)


# ==========================================
# SAVE NEW RESPONSE
# ==========================================

def save_cached_response(

    cache_key,

    question,

    response,

    input_tokens=0,

    output_tokens=0

):

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO response_cache
            (
                cache_key,
                question,
                response,
                input_tokens,
                output_tokens,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?)

        """, (

            cache_key,

            question,

            json.dumps(response, ensure_ascii=False),

            input_tokens,

            output_tokens,

            datetime.now().isoformat()

        ))

        connection.commit()


# ==========================================
# RECORD CACHE HIT
# ==========================================

def record_cache_hit(cache_key):

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        # Retrieve original token usage
        cursor.execute("""
            SELECT input_tokens, output_tokens
            FROM response_cache
            WHERE cache_key = ?
        """, (cache_key,))

        result = cursor.fetchone()

        tokens_saved = 0

        if result:

            tokens_saved = result[0] + result[1]

        # Record cache event
        cursor.execute("""
            INSERT INTO usage_events
            (
                event_type,
                tokens_saved,
                created_at
            )

            VALUES (?, ?, ?)

        """, (

            "cache_hit",

            tokens_saved,

            datetime.now().isoformat()

        ))

        connection.commit()


# ==========================================
# RECORD SUCCESSFUL API REQUEST
# ==========================================

def record_api_usage(input_tokens, output_tokens):

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO usage_events
            (
                event_type,
                input_tokens,
                output_tokens,
                created_at
            )

            VALUES (?, ?, ?, ?)

        """, (

            "api_success",

            input_tokens,

            output_tokens,

            datetime.now().isoformat()

        ))

        connection.commit()


# ==========================================
# RECORD FAILED API REQUEST
# ==========================================

def record_api_error():

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO usage_events
            (
                event_type,
                created_at
            )

            VALUES (?, ?)

        """, (

            "api_error",

            datetime.now().isoformat()

        ))

        connection.commit()


# ==========================================
# GET ANALYTICS
# ==========================================

def get_cache_analytics():

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT

                COUNT(*),

                SUM(CASE
                    WHEN event_type = 'cache_hit'
                    THEN 1 ELSE 0
                END),

                SUM(CASE
                    WHEN event_type = 'api_success'
                    THEN 1 ELSE 0
                END),

                SUM(CASE
                    WHEN event_type = 'api_error'
                    THEN 1 ELSE 0
                END),

                SUM(input_tokens),

                SUM(output_tokens),

                SUM(tokens_saved)

            FROM usage_events
        """)

        result = cursor.fetchone()

    (
        total_events,
        cache_hits,
        api_successes,
        api_errors,
        input_tokens,
        output_tokens,
        tokens_saved

    ) = result

    cache_hits = cache_hits or 0
    api_successes = api_successes or 0
    api_errors = api_errors or 0

    input_tokens = input_tokens or 0
    output_tokens = output_tokens or 0
    tokens_saved = tokens_saved or 0

    total_requests = cache_hits + api_successes + api_errors

    cache_misses = api_successes + api_errors

    if total_requests > 0:

        cache_hit_rate = (
            cache_hits / total_requests
        ) * 100

    else:

        cache_hit_rate = 0

    return {

        "total_requests": total_requests,

        "api_requests": api_successes + api_errors,

        "api_successes": api_successes,

        "api_errors": api_errors,

        "cache_hits": cache_hits,

        "cache_misses": cache_misses,

        "cache_hit_rate": round(cache_hit_rate, 2),

        "input_tokens": input_tokens,

        "output_tokens": output_tokens,

        "total_tokens": input_tokens + output_tokens,

        "estimated_tokens_saved": tokens_saved

    }


# ==========================================
# END OF CACHE MANAGER
# ==========================================
