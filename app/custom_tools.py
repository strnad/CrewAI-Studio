# app/custom_tools.py
import os
from typing import Optional, Dict, Any
from crewai_tools import BaseTool
import requests
import json
from pydantic.v1 import BaseModel, Field

class FixedCustomFileWriteToolInputSchema(BaseModel):
    content: str = Field(..., description="The content to write or append to the file")
    mode: str = Field(..., description="Mode to open the file in, either 'write' or 'append'")

class CustomFileWriteToolInputSchema(FixedCustomFileWriteToolInputSchema):
    content: str = Field(..., description="The content to write or append to the file")
    mode: str = Field(..., description="Mode to open the file in, either 'write' or 'append'")
    filename: str = Field(..., description="The name of the file to write to or append")

class CustomFileWriteTool(BaseTool):
    name: str = "FileWriteTool"
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
            with open(full_path, 'a' if mode == 'append' else 'w') as file:
                file.write(content)
            return {
                "status": "success",
                "message": f"Content successfully {'appended to' if mode == 'append' else 'written to'} {full_path}"
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

class CustomApiToolInputSchema(BaseModel):
    endpoint: str = Field(..., description="The specific endpoint for the API call")
    method: str = Field(..., description="HTTP method to use (GET, POST, PUT, DELETE)")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers to include in the request")
    query_params: Optional[Dict[str, Any]] = Field(None, description="Query parameters for the request")
    body: Optional[Dict[str, Any]] = Field(None, description="Body of the request for POST/PUT methods")


class CustomApiTool(BaseTool):
    name: str = "CustomApiTool"
    description: str = "Tool to make API calls with customizable parameters"
    args_schema = CustomApiToolInputSchema
    base_url: Optional[str] = None
    default_headers: Optional[Dict[str, str]] = None
    default_query_params: Optional[Dict[str, Any]] = None

    def __init__(self, base_url: Optional[str] = None, headers: Optional[Dict[str, str]] = None, query_params: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.default_headers = headers or {}
        self.default_query_params = query_params or {}
        self._generate_description()
        

    def _run(self, endpoint: str, method: str, headers: Optional[Dict[str, str]] = None, query_params: Optional[Dict[str, Any]] = None, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}".rstrip("/")
        headers = {**self.default_headers, **(headers or {})}
        query_params = {**self.default_query_params, **(query_params or {})}

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=query_params,
                json=body,
                verify=False #TODO: add option to disable SSL verification
            )
            return {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
            }
        except Exception as e:
            return {
                "status_code": 500,
                "response": str(e)
            }

    def run(self, input_data: CustomApiToolInputSchema) -> Any:
        response_data = self._run(
            endpoint=input_data.endpoint,
            method=input_data.method,
            headers=input_data.headers,
            query_params=input_data.query_params,
            body=input_data.body
            
        )
        return response_data