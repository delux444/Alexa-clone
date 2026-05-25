
def main():

    import requests

    filename = "command.wav"

    print("[*] Starting speech to text")

    files = {
        "file": open(filename, "rb"),
        "temperature": (None, "0.0"),
        "temperature_inc": (None, "0.2"),
        "response_format": (None, "json"),
    }

    response = requests.post(
        "http://192.168.0.102:8080/inference",
        files=files
    )

    if response.status_code == 200:

        data = response.json()

        text = data.get('text', 'no text in answer')

        return text

    else:
        text = f"[!] Server error: {response.status_code}"

        return text

if __name__ == "__main__":
   print( main())
