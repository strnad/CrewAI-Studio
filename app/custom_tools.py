# app/custom_tools.py
import os
from pydantic import BaseModel
from crewai_tools import BaseTool

class CustomFileWriteTool(BaseTool, BaseModel):
    name: str = "CustomFileWriteTool"
    description: str = """
        This tool writes or appends the provided text content to a specified file.

        Parameters:
        - filename (str): The name of the file to write or append to. Can be an absolute or relative path.
        - append (bool): If True, appends the content to the file. If False, overwrites the file.
        - content (str): The text content to write or append to the file.

        Example usage:
        tool._run("example.txt", append=False, content="This is a test.")
    """

    allowed_directory: str = os.getcwd()  # Defaults to the current working directory

    def _run(self, filename: str, append: bool, content: str) -> str:
        # Translate relative path to absolute path within the allowed directory
        if not os.path.isabs(filename):
            file_path = os.path.join(self.allowed_directory, filename)
        else:
            file_path = filename

        try:
            # Ensure the file_path is within the allowed_directory
            if not os.path.abspath(file_path).startswith(os.path.abspath(self.allowed_directory)):
                raise ValueError("The specified file path is not within the allowed directory.")
            
            # Write the content to the file
            mode = 'a' if append else 'w'
            with open(file_path, mode) as file:
                file.write(content)
            return f"Content successfully written to {file_path}"
        except Exception as e:
            return f"Failed to write content to {file_path}: {str(e)}"