import os
from subprocess import run


def run_python_file(working_directory: str, file_path: str, args: list[str] = []):
    absolute_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(absolute_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory\n'
    if not os.path.exists(target_file):
        return f'Error: File "{file_path}" not found.\n'
    if not target_file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.\n'

    try:
        run_result = run(
            ["python3", target_file, *args],
            timeout=5,
            capture_output=True,
            cwd=working_directory,
        )

        result = ""
        if len(run_result.stdout) == 0 and len(run_result.stderr) == 0:
            result += "No output produced."
        else:
            result += f"STDOUT: {run_result.stdout}\n"
            result += f"STDERR: {run_result.stderr}"
        if run_result.returncode != 0:
            result += f"Process exited with code {run_result.returncode}"
        return result + "\n"

    except Exception as e:
        return f"Error: executing Python file: {e}\n"
