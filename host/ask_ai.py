from ollama import chat
from ollama import ChatResponse
import json

from read_config import get_from_config as config

def ask_ai(msg="", model=""):

    if msg == "":
        return "No question asked"

    if model == "":
        return "No model selected"

    print(f"[*] Asking {model}")

    response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'system',
            'content': 'Jesteś domową asystentką o imieniu Alexa Odpowiadasz wyłącznie w języku Polskim Nie używasz interpunkcji ani żadnych emotek sam tekst'
        },
        {
            'role': 'user',
            'content': msg
        }
    ])

    return response['message']['content']

if __name__ == "__main__":
    question = input("Input question: ")
    model = input("Input model: ")

    if model:
        print(ask_ai(msg=question, model=model))
    else:
        model = config(parameter="DEF_MODEL")
        print(f"Using default model {model}")
        print(ask_ai(msg=question, model=model))     
    