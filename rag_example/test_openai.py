import requests
import json

API_KEY = "sk-proj-batjcE88WHH0MаTRvbIyLFFRLWoZEXPi0W5hdUJvj4Ij8uGsjNuw8PxHZ_HyADkV-VWjRh5b1_T3BIbkFJEp6qlJ4BscapNLeISsnuVEUHuXeOXTVzHIDI8fH1Etj3As7kwI-7vYn9X@ka5mGRiMmf1tA7gAl"  # Replace with your actual API key
ENDPOINT = "https://api.openai.com/v1/chat/completions"

def test_openai():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "I like to hike. What would you recommend?"}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
    }

    try:
        print("Sending raw request to OpenAI...")
        response = requests.post(ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an error for HTTP errors
        print("OpenAI Response:")
        print(response.json()["choices"][0]["message"]["content"])
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_openai()
