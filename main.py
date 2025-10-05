import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file


def main():
    args = parse_arguments()
    client = setup_client()
    model_name = "gemini-2.0-flash-001"
    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]
    config = create_config()
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=config,
    )
    print_response(response)
    print_meta_data(response.usage_metadata, args.verbose)


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


def create_config():
    return types.GenerateContentConfig(
        tools=[get_available_functions()], system_instruction=get_system_prompt()
    )


def get_available_functions():
    return types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )


def get_system_prompt():
    return """
    You are a helpful AI coding agent.
    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:
        - List files and directories
        - Read file contents
        - Execute Python files with optional arguments
        - Write or overwrite files
    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """


def print_response(response: types.GenerateContentResponse):
    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(response.text)


def print_meta_data(
    meta: types.GenerateContentResponseUsageMetadata | None, verbose: bool
):
    if meta and verbose:
        print(f"Prompt tokens: {meta.prompt_token_count}")
        print(f"Response tokens: {meta.candidates_token_count}")


if __name__ == "__main__":
    main()
