import os


def write_file(working_directory: str, file_path: str, content: str):
    absolute_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(absolute_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory\n'

    try:
        target_dir_name = os.path.dirname(target_file)
        if not os.path.exists(target_dir_name):
            os.makedirs(target_dir_name)

        with open(target_file, "w") as f:
            chars_written = f.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({chars_written} characters written)'
        )
    except Exception as e:
        return f"Error: {e}"
