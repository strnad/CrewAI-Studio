import os
from typing import Optional, Type
from crewai.tools import BaseTool
import importlib.util
#from pydantic.v1 import BaseModel, Field,root_validator
from pydantic import BaseModel, Field
import docker
import base64

class CustomCodeInterpreterSchema(BaseModel):
    """Input for CustomCodeInterpreterTool."""
    code: Optional[str] = Field(
        None,
        description="Python3 code used to be interpreted in the Docker container. ALWAYS PRINT the final result and the output of the code",
    )

    run_script: Optional[str] = Field(
        None,
        description="Relative path to the script to run in the Docker container. The script should contain the code to be executed.",
    )

    libraries_used: str = Field(
        ...,
        description="List of libraries used in the code with proper installing names separated by commas. Example: numpy,pandas,beautifulsoup4",
    )

    def check_code_or_run_script(cls, values):
        code = values.get('code')
        run_script = values.get('run_script')
        if not code and not run_script:
            raise ValueError('Either code or run_script must be provided')
        if code and run_script:
            raise ValueError('Only one of code or run_script should be provided')
        return values

class CustomCodeInterpreterTool(BaseTool):
    name: str = "Code Interpreter"
    description: str = "Interprets Python3 code strings with a final print statement. Requires eighter code or run_script to be provided."
    args_schema: Type[BaseModel] = CustomCodeInterpreterSchema
    code: Optional[str] = None
    run_script: Optional[str] = None
    workspace_dir: Optional[str] = None

    def __init__(self, workspace_dir: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if workspace_dir is not None and len(workspace_dir) > 0:
            self.workspace_dir = os.path.abspath(workspace_dir)
            os.makedirs(self.workspace_dir, exist_ok=True)
        self._generate_description()

    @staticmethod
    def _get_installed_package_path():
        spec = importlib.util.find_spec('crewai_tools')
        return os.path.dirname(spec.origin)

    def _verify_docker_image(self) -> None:
        """
        Verify if the Docker image is available
        """
        image_tag = "code-interpreter:latest"
        client = docker.from_env()

        try:
            client.images.get(image_tag)

        except docker.errors.ImageNotFound:
            package_path = self._get_installed_package_path()
            dockerfile_path = os.path.join(package_path, "tools/code_interpreter_tool")
            if not os.path.exists(dockerfile_path):
                raise FileNotFoundError(f"Dockerfile not found in {dockerfile_path}")

            client.images.build(
                path=dockerfile_path,
                tag=image_tag,
                rm=True,
            )

    def _install_libraries(
        self, container: docker.models.containers.Container, libraries: str
    ) -> None:
        """
        Install missing libraries in the Docker container
        """
        if libraries and len(libraries) > 0:
            for library in libraries.split(","):
                print(f"Installing library: {library}")
                install_result = container.exec_run(f"pip install {library}")
                if install_result.exit_code != 0:
                    print(f"Something went wrong while installing the library: {library}")
                    print(install_result.output.decode("utf-8"))
            

    def _get_existing_container(self, container_name: str) -> Optional[docker.models.containers.Container]:
        client = docker.from_env()
        try:
            existing_container = client.containers.get(container_name)
            if existing_container.status == 'running':
                return existing_container
            if existing_container.status == 'exited':
                existing_container.remove()
        except docker.errors.NotFound:
            pass
        return None

    def _init_docker_container(self) -> docker.models.containers.Container:
        client = docker.from_env()
        volumes = {}
        if self.workspace_dir:
            volumes[self.workspace_dir] = {"bind": "/workspace", "mode": "rw"}
        container_name = "custom-code-interpreter"
        existing_container = self._get_existing_container(container_name)
        if existing_container:
            return existing_container
        return client.containers.run(
            "code-interpreter", detach=True, tty=True, working_dir="/workspace", name=container_name, volumes=volumes
        )

    def run_code_in_docker(self, code: str, libraries_used: str) -> str:
        self._verify_docker_image()
        container = self._init_docker_container()
        self._install_libraries(container, libraries_used)
        
        # Encode the code to base64
        encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
        
        # Create a command to decode the base64 string and run the Python code
        cmd_to_run = f'python3 -c "import base64; exec(base64.b64decode(\'{encoded_code}\').decode(\'utf-8\'))"'
        
        print(f"Running code in container: \n{code}")
        
        exec_result = container.exec_run(cmd_to_run)

        if exec_result.exit_code != 0:
            print(f"Something went wrong while running the code: \n{exec_result.output.decode('utf-8')}")
            return f"Something went wrong while running the code: \n{exec_result.output.decode('utf-8')}"
        print(f"Code run output: \n{exec_result.output.decode('utf-8')}")
        return exec_result.output.decode("utf-8")
    
    def _run_script(self, run_script: str,libraries_used: str) -> str:
        with open(f"{self.workspace_dir}/{run_script}", "r") as file:
            code = file.read()
            return self.run_code_in_docker(code, libraries_used)

    def _run(self, **kwargs) -> str:
        code = kwargs.get("code", self.code)
        run_script = kwargs.get("run_script", self.run_script)
        libraries_used = kwargs.get("libraries_used", [])
        if run_script:
            return self._run_script(run_script, libraries_used)
        return self.run_code_in_docker(code, libraries_used)
