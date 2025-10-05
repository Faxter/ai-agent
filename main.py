import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info


def main():
    args = parse_arguments()
    client = setup_client()
    model_name = "gemini-2.0-flash-001"
    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
        ]
    )
    system_prompt = """
    You are a helpful AI coding agent.
    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:
    - List files and directories
    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """
    config = types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt
    )
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config,
    )
    print_response(response)
    print_meta_data(response.usage_metadata, args.verbose, args.user_prompt)


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


def print_response(response: types.GenerateContentResponse):
    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(response.text)


def print_meta_data(
    meta: types.GenerateContentResponseUsageMetadata | None,
    verbose: bool,
    user_prompt: str,
):
    if meta and verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {meta.prompt_token_count}")
        print(f"Response tokens: {meta.candidates_token_count}")


if __name__ == "__main__":
    main()
