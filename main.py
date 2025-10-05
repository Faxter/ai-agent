import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file


def main():
    args = parse_arguments()
    client = setup_client()
    model_name = "gemini-2.0-flash-001"
    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]
    config = create_config()
    MAX_CALLS = 10
    call_counter = 0
    while call_counter < MAX_CALLS:
        call_counter += 1
        response = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=config,
        )
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)

        if response.function_calls:
            execute_function_calls(response.function_calls, messages, args.verbose)
        else:
            if response.text:
                print(response.text)
                break
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


def execute_function_calls(
    function_calls: list[types.FunctionCall],
    conversation: list[types.Content],
    verbose: bool,
):
    try:
        for function_call in function_calls:
            result = call_function(function_call, verbose)
            if not result.parts:
                raise Exception("Error: content of response is missing its parts!")
            if not result.parts[0].function_response:
                raise Exception(
                    "Error: content of response is missing the function_response!"
                )
            if not result.parts[0].function_response.response:
                raise Exception("Error: content of response is missing the reponse!")
            if verbose:
                print(f"-> {result.parts[0].function_response.response}")

            conversation.append(result)
    except Exception as e:
        print(e)


def print_meta_data(
    meta: types.GenerateContentResponseUsageMetadata | None, verbose: bool
):
    if meta and verbose:
        print(f"Prompt tokens: {meta.prompt_token_count}")
        print(f"Response tokens: {meta.candidates_token_count}")


def call_function(function_call_part: types.FunctionCall, verbose: bool = False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    working_dir = "./calculator"
    function_name = function_call_part.name if function_call_part.name else ""
    function_result: str = ""
    response: dict[str, str] = {}
    match function_name:
        case "get_files_info":
            function_result = get_files_info(working_dir)
        case "get_file_content":
            function_result = get_file_content(working_dir, **function_call_part.args)
        case "run_python_file":
            function_result = run_python_file(working_dir, **function_call_part.args)
        case "write_file":
            function_result = write_file(working_dir, **function_call_part.args)
        case _:
            response = {"error": f"Unknown function: {function_name}"}
    response = {"result": function_result}
    return types.Content(
        role="user",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response=response,
            )
        ],
    )


if __name__ == "__main__":
    main()
