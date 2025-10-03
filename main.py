import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    if len(sys.argv) != 2:
        print("usage: uv run main.py [prompt]")
        sys.exit(1)
    user_prompt = sys.argv[1]

    _ = load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )
    print(response.text)
    usage_meta_data = response.usage_metadata
    if usage_meta_data:
        print(f"Prompt tokens: {usage_meta_data.prompt_token_count}")
        print(f"Response tokens: {usage_meta_data.candidates_token_count}")


if __name__ == "__main__":
    main()
