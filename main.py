import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    argument_parser = argparse.ArgumentParser(
        description="Prompt the AI model with some text"
    )
    _ = argument_parser.add_argument("user_prompt", type=str, help="the message prompt")
    _ = argument_parser.add_argument(
        "--verbose", action="store_true", help="add debugging text output"
    )
    args = argument_parser.parse_args()

    _ = load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )
    print(response.text)
    usage_meta_data = response.usage_metadata
    if usage_meta_data and args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {usage_meta_data.prompt_token_count}")
        print(f"Response tokens: {usage_meta_data.candidates_token_count}")


if __name__ == "__main__":
    main()
