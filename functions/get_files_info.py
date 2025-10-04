import os


def get_files_info(working_directory: str, directory: str = "."):
    try:
        absolute_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.abspath(os.path.join(working_directory, directory))
        if not target_dir.startswith(absolute_working_dir):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory\n'
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory\n'

        result = ""
        for item in os.listdir(target_dir):
            result += f"- {item}: file_size={os.path.getsize(target_dir + os.path.sep + item)} bytes, is_dir={os.path.isdir(target_dir + os.path.sep + item)}\n"
        return result

    except Exception as e:
        return f"Error: {e}\n"
