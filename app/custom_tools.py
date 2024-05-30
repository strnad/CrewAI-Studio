# app/custom_tools.py
import os
from pydantic import BaseModel
from crewai_tools import BaseTool

class CustomFileWriteTool(BaseTool, BaseModel):
    name: str = "CustomFileWriteTool"
    description: str = "Writes the provided text content to a specified file within the allowed directory."
    
    allowed_directory: str

    def _run(self, filename: str, content: str) -> str:
        # Ensure the file path is within the allowed directory
        file_path = os.path.join(self.allowed_directory, filename)
        if not os.path.commonpath([self.allowed_directory, file_path]).startswith(self.allowed_directory):
            raise ValueError("The specified file path is not within the allowed directory.")
        
        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)
        
        return f"Content successfully written to {file_path}"
