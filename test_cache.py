from cache.cache_manager import (
    initialize_cache,
    generate_cache_key,
    get_cached_response,
    save_cached_response
)




initialize_cache()

question = "What are the benefits of walking?"

history = [
    {
        "role": "user",
        "content": question
    }
]

system_prompt = "You are MYMFIT AI."

model = "openai/gpt-oss-20b"


# Generate fingerprint
key = generate_cache_key(
    question,
    history,
    system_prompt,
    model
)


# Check existing cache
cached = get_cached_response(key)


if cached:

    print("CACHE HIT!")

    print(cached)

else:

    print("CACHE MISS!")

    example_response = {
        "message": "Walking supports general fitness.",
        "recommendations": [],
        "next_question": "How often do you walk?",
        "safety_note": "Start at a comfortable pace."
    }

    save_cached_response(
        key,
        question,
        example_response,
        100,
        50
    )

    print("Example response saved successfully!")