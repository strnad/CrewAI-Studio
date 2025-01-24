import os
from typing import Optional, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, model_validator

class FixedCustomFileWriteToolInputSchema(BaseModel):
    content: str = Field(..., description="The content to write or append to the file")
    mode: str = Field(..., description="Mode to open the file in, either 'w' or 'a'")

class CustomFileWriteToolInputSchema(FixedCustomFileWriteToolInputSchema):
    content: str = Field(..., description="The content to write or append to the file")
    mode: str = Field(..., description="Mode to open the file in, either 'w' or 'a'")
    filename: str = Field(..., description="The name of the file to write to or append")

class CustomFileWriteTool(BaseTool):
    name: str = "Write File"
    description: str = "Tool to write or append to files"
    args_schema = CustomFileWriteToolInputSchema
    filename: Optional[str] = None

    def __init__(self, base_folder: str, filename: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if filename is not None and len(filename) > 0:
            self.args_schema = FixedCustomFileWriteToolInputSchema
        self._base_folder = base_folder
        self.filename = filename or None
        self._ensure_base_folder_exists()
        self._generate_description()


    def _ensure_base_folder_exists(self):
        os.makedirs(self._base_folder, exist_ok=True)

    def _get_full_path(self, filename: Optional[str]) -> str:
        if filename is None and self.filename is None:
            raise ValueError("No filename specified and no default file set.")

        chosen_file = filename or self.filename
        full_path = os.path.abspath(os.path.join(self._base_folder, chosen_file))

        if not full_path.startswith(os.path.abspath(self._base_folder)):
            raise ValueError("Access outside the base directory is not allowed.")  #TODO: add validations for path traversal

        return full_path

    def _run(self, content: str, mode: str, filename: Optional[str] = None) -> Dict[str, Any]:
        full_path = self._get_full_path(filename)
        try:
            with open(full_path, 'a' if mode == 'a' else 'w') as file:
                file.write(content)
            return {
                "status": "success",
                "message": f"Content successfully {'appended to' if mode == 'a' else 'written to'} {full_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def run(self, input_data: CustomFileWriteToolInputSchema) -> Any:
        response_data = self._run(
            content=input_data.content,
            mode=input_data.mode,
            filename=input_data.filename
        )
        return response_data
