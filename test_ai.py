 import json

from ai.groq_client import ask_ai


print("\n===================================")
print("          MYMFIT AI")
print("     Your Personal Fitness Coach")
print("===================================")


question = input("\nYou: ")

print("\nMYMFIT AI is thinking...\n")

response = ask_ai(question)


if "error" in response:

    print("Error:", response["error"])

else:

    print("MYMFIT AI:")

    print(response["message"])

    print("\nRECOMMENDATIONS:")

    for item in response["recommendations"]:

        print("\n-", item["title"])
        print(item["details"])

    print("\nFOLLOW-UP QUESTION:")

    print(response["next_question"])

    print("\nSAFETY NOTE:")

    print(response["safety_note"])