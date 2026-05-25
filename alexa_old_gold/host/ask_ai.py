from ollama import chat
from ollama import ChatResponse
import json

def ask_ai(msg="", model="openchat"):

    if msg == "":
        return "No question asked"

    print("[*] Asking openchat")

    response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': msg
        }
    ])

    return response['message']['content']

