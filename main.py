import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    args = parse_arguments()
    client = setup_client()
    model_name = "gemini-2.0-flash-001"
    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]
    system_prompt = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )
    print_info(response, args)


def parse_arguments():
    argument_parser = argparse.ArgumentParser(
        description="Prompt the AI model with some text"
    )
    _ = argument_parser.add_argument("user_prompt", type=str, help="the message prompt")
    _ = argument_parser.add_argument(
        "--verbose", action="store_true", help="add debugging text output"
    )
    return argument_parser.parse_args()


def setup_client():
    _ = load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


def print_info(response: types.GenerateContentResponse, arguments: argparse.Namespace):
    print(response.text)
    usage_meta_data = response.usage_metadata
    if usage_meta_data and arguments.verbose:
        print(f"User prompt: {arguments.user_prompt}")
        print(f"Prompt tokens: {usage_meta_data.prompt_token_count}")
        print(f"Response tokens: {usage_meta_data.candidates_token_count}")


if __name__ == "__main__":
    main()
