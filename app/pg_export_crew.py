import streamlit as st
from streamlit import session_state as ss
import zipfile
import os
import re
import json
import shutil
import db_utils
from utils import escape_quotes
from my_tools import TOOL_CLASSES
from crewai import Process
from my_crew import MyCrew
from my_agent import MyAgent
from my_task import MyTask
from datetime import datetime

class PageExportCrew:
    def __init__(self):
        self.name = "Import/export"

    def extract_placeholders(self, text):
        return re.findall(r'\{(.*?)\}', text)

    def get_placeholders_from_crew(self, crew):
        placeholders = set()
        for task in crew.tasks:
            placeholders.update(self.extract_placeholders(task.description))
            placeholders.update(self.extract_placeholders(task.expected_output))
        return list(placeholders)

    def generate_streamlit_app(self, crew, output_dir):
        agents = crew.agents
        tasks = crew.tasks

        # Check if any custom tools are used
        custom_tools_used = any(tool.name in ["CustomApiTool", "CustomFileWriteTool", "CustomCodeInterpreterTool"] 
                                for agent in agents for tool in agent.tools)

        def json_dumps_python(obj):
            if isinstance(obj, bool):
                return str(obj)
            return json.dumps(obj)

        def format_tool_instance(tool):
            tool_class = TOOL_CLASSES.get(tool.name)
            if tool_class:
                params = ', '.join([f'{key}={json_dumps_python(value)}' for key, value in tool.parameters.items() if value is not None])
                return f'{tool.name}({params})' if params else f'{tool.name}()'
            return None

        agent_definitions = ",\n        ".join([
            f"""
Agent(
    role={json_dumps_python(agent.role)},
    backstory={json_dumps_python(agent.backstory)},
    goal={json_dumps_python(agent.goal)},
    allow_delegation={json_dumps_python(agent.allow_delegation)},
    verbose={json_dumps_python(agent.verbose)},
    tools=[{', '.join([format_tool_instance(tool) for tool in agent.tools])}],
    llm=create_llm({json_dumps_python(agent.llm_provider_model)}, {json_dumps_python(agent.temperature)})
)
            """
            for agent in agents
        ])

        task_definitions = ",\n        ".join([
            f"""
Task(
    description={json_dumps_python(task.description)},
    expected_output={json_dumps_python(task.expected_output)},
    agent=next(agent for agent in agents if agent.role == {json_dumps_python(task.agent.role)}),
    async_execution={json_dumps_python(task.async_execution)}
)
            """
            for task in tasks
        ])

        placeholders = self.get_placeholders_from_crew(crew)
        placeholder_inputs = "\n    ".join([
            f'{placeholder} = st.text_input({json_dumps_python(placeholder.capitalize())})'
            for placeholder in placeholders
        ])
        placeholders_dict = ", ".join([f'{json_dumps_python(placeholder)}: {placeholder}' for placeholder in placeholders])

        manager_llm_definition = ""
        if crew.process == Process.hierarchical and crew.manager_llm:
            manager_llm_definition = f'manager_llm=create_llm({json_dumps_python(crew.manager_llm)})'
        elif crew.process == Process.hierarchical and crew.manager_agent:
            manager_llm_definition = f'manager_agent=next(agent for agent in agents if agent.role == {json_dumps_python(crew.manager_agent.role)})'
        
        app_content = f"""
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
from crewai_tools import *
{'''from custom_tools import CustomApiTool, CustomFileWriteTool, CustomCodeInterpreterTool''' if custom_tools_used else ''}

load_dotenv()

def create_lmstudio_llm(model, temperature):
    api_base = os.getenv('LMSTUDIO_API_BASE')
    os.environ["OPENAI_API_KEY"] = "lm-studio"
    os.environ["OPENAI_API_BASE"] = api_base
    if api_base:
        return ChatOpenAI(openai_api_key='lm-studio', openai_api_base=api_base, temperature=temperature)
    else:
        raise ValueError("LM Studio API base not set in .env file")

def create_openai_llm(model, temperature):
    safe_pop_env_var('OPENAI_API_KEY')
    safe_pop_env_var('OPENAI_API_BASE')
    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1/')
    if api_key:
        return ChatOpenAI(openai_api_key=api_key, openai_api_base=api_base, model_name=model, temperature=temperature)
    else:
        raise ValueError("OpenAI API key not set in .env file")

def create_groq_llm(model, temperature):
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        return ChatGroq(groq_api_key=api_key, model_name=model, temperature=temperature)
    else:
        raise ValueError("Groq API key not set in .env file")

def create_anthropic_llm(model, temperature):
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        return ChatAnthropic(anthropic_api_key=api_key, model_name=model, temperature=temperature)
    else:
        raise ValueError("Anthropic API key not set in .env file")

def safe_pop_env_var(key):
    try:
        os.environ.pop(key)
    except KeyError:
        pass
        
LLM_CONFIG = {{
    "OpenAI": {{
        "create_llm": create_openai_llm
    }},
    "Groq": {{
        "create_llm": create_groq_llm
    }},
    "LM Studio": {{
        "create_llm": create_lmstudio_llm
    }},
    "Anthropic": {{
        "create_llm": create_anthropic_llm
    }}
}}

def create_llm(provider_and_model, temperature=0.1):
    provider, model = provider_and_model.split(": ")
    create_llm_func = LLM_CONFIG.get(provider, {{}}).get("create_llm")
    if create_llm_func:
        return create_llm_func(model, temperature)
    else:
        raise ValueError(f"LLM provider {{provider}} is not recognized or not supported")

def load_agents():
    agents = [
        {agent_definitions}
    ]
    return agents

def load_tasks(agents):
    tasks = [
        {task_definitions}
    ]
    return tasks

def main():
    st.title({json_dumps_python(crew.name)})

    agents = load_agents()
    tasks = load_tasks(agents)
    crew = Crew(
        agents=agents, 
        tasks=tasks, 
        process={json_dumps_python(crew.process)}, 
        verbose={json_dumps_python(crew.verbose)}, 
        memory={json_dumps_python(crew.memory)}, 
        cache={json_dumps_python(crew.cache)}, 
        max_rpm={json_dumps_python(crew.max_rpm)},
        {manager_llm_definition}
    )

    {placeholder_inputs}

    placeholders = {{
        {placeholders_dict}
    }}

    if st.button("Run Crew"):
        with st.spinner("Running crew..."):
            try:
                result = crew.kickoff(inputs=placeholders)
                if isinstance(result, dict):
                    with st.expander("Final output", expanded=True):                
                        st.write(result.get('final_output', 'No final output available'))
                    with st.expander("Full output", expanded=False):
                        st.write(result)
                else:
                    st.write("Result:")
                    st.write(result)
            except Exception as e:
                st.error(f"An error occurred: {{str(e)}}")

if __name__ == '__main__':
    main()
"""
        with open(os.path.join(output_dir, 'app.py'), 'w') as f:
            f.write(app_content)

        # If custom tools are used, copy the custom_tools.py file
        if custom_tools_used:
            source_path = os.path.join(os.path.dirname(__file__), 'custom_tools.py')
            dest_path = os.path.join(output_dir, 'custom_tools.py')
            shutil.copy2(source_path, dest_path)

    def create_env_file(self, output_dir):
        env_content = """
# OPENAI_API_KEY="FILL-IN-YOUR-OPENAI-API-KEY"
# OPENAI_API_BASE="OPTIONAL-FILL-IN-YOUR-OPENAI-API-BASE"
# GROQ_API_KEY="FILL-IN-YOUR-GROQ-API-KEY"
# ANTHROPIC_API_KEY="FILL-IN-YOUR-ANTHROPIC-API-KEY"
# LMSTUDIO_API_BASE="http://localhost:1234/v1"
"""
        with open(os.path.join(output_dir, '.env'), 'w') as f:
            f.write(env_content)

    def create_shell_scripts(self, output_dir):
        install_sh_content = """
#!/bin/bash

# Create a virtual environment
python -m venv venv || { echo "Failed to create venv"; exit 1; }

# Activate the virtual environment
source venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

# Install requirements
pip install -r requirements.txt || { echo "Failed to install requirements"; exit 1; }

echo "Installation completed successfully."
"""
        with open(os.path.join(output_dir, 'install.sh'), 'w') as f:
            f.write(install_sh_content)
            os.chmod(os.path.join(output_dir, 'install.sh'), 0o755)

        run_sh_content = """
#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate" || { echo "Failed to activate venv"; exit 1; }

cd "$SCRIPT_DIR"

streamlit run app.py --server.headless True
"""
        with open(os.path.join(output_dir, 'run.sh'), 'w') as f:
            f.write(run_sh_content)
            os.chmod(os.path.join(output_dir, 'run.sh'), 0o755)

        install_bat_content = """
@echo off

:: Create a virtual environment
python -m venv venv || (
    echo Failed to create venv
    exit /b 1
)

:: Activate the virtual environment
call venv\\Scripts\\activate || (
    echo Failed to activate venv
    exit /b 1
)

:: Install requirements
pip install -r requirements.txt || (
    echo Failed to install requirements
    exit /b 1
)

echo Installation completed successfully.
"""
        with open(os.path.join(output_dir, 'install.bat'), 'w') as f:
            f.write(install_bat_content)

        run_bat_content = """
@echo off

:: Activate the virtual environment
call venv\\Scripts\\activate || (
    echo Failed to activate venv
    exit /b 1
)

:: Run the Streamlit app
streamlit run app.py --server.headless true
"""
        with open(os.path.join(output_dir, 'run.bat'), 'w') as f:
            f.write(run_bat_content)

        # Copy the main project's requirements.txt
        source_requirements = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        dest_requirements = os.path.join(output_dir, 'requirements.txt')
        shutil.copy2(source_requirements, dest_requirements)

    def zip_directory(self, folder_path, output_path):
        with zipfile.ZipFile(output_path, 'w') as zip_file:
            for foldername, subfolders, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, folder_path)
                    zip_file.write(file_path, arcname)

    def create_export(self, crew_name):
        output_dir = f"{crew_name}_app"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        selected_crew = next((crew for crew in ss.crews if crew.name == crew_name), None)
        if selected_crew:
            self.generate_streamlit_app(selected_crew, output_dir)
            self.create_env_file(output_dir)
            self.create_shell_scripts(output_dir)

            zip_path = f"{crew_name}_app.zip"
            self.zip_directory(output_dir, zip_path)
            return zip_path

    def export_crew_to_json(self, crew):
        crew_data = {
            'id': crew.id,
            'name': crew.name,
            'process': crew.process,
            'verbose': crew.verbose,
            'memory': crew.memory,
            'cache': crew.cache,
            'max_rpm': crew.max_rpm,
            'manager_llm': crew.manager_llm,
            'manager_agent': crew.manager_agent.id if crew.manager_agent else None,
            'created_at': crew.created_at,
            'agents': [],
            'tasks': [],
            'tools': []
        }

        tool_ids = set()

        for agent in crew.agents:
            agent_data = {
                'id': agent.id,
                'role': agent.role,
                'backstory': agent.backstory,
                'goal': agent.goal,
                'allow_delegation': agent.allow_delegation,
                'verbose': agent.verbose,
                'cache': agent.cache,
                'llm_provider_model': agent.llm_provider_model,
                'temperature': agent.temperature,
                'max_iter': agent.max_iter,
                'tool_ids': [tool.tool_id for tool in agent.tools]
            }
            crew_data['agents'].append(agent_data)
            tool_ids.update(agent_data['tool_ids'])

        for task in crew.tasks:
            task_data = {
                'id': task.id,
                'description': task.description,
                'expected_output': task.expected_output,
                'async_execution': task.async_execution,
                'agent_id': task.agent.id if task.agent else None,
                'context_from_async_tasks_ids': task.context_from_async_tasks_ids,
                'created_at': task.created_at
            }
            crew_data['tasks'].append(task_data)

        for tool_id in tool_ids:
            tool = next((t for t in ss.tools if t.tool_id == tool_id), None)
            if tool:
                tool_data = {
                    'tool_id': tool.tool_id,
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': tool.get_parameters()
                }
                crew_data['tools'].append(tool_data)

        return json.dumps(crew_data, indent=2)
    
    def import_crew_from_json(self, crew_data):
        # Create tools
        for tool_data in crew_data['tools']:
            tool_class = TOOL_CLASSES[tool_data['name']]
            tool = tool_class(tool_id=tool_data['tool_id'])
            tool.set_parameters(**tool_data['parameters'])
            if tool not in ss.tools:
                ss.tools.append(tool)
                db_utils.save_tool(tool)

        # Create agents
        agents = []
        for agent_data in crew_data['agents']:
            agent = MyAgent(
                id=agent_data['id'],
                role=agent_data['role'],
                backstory=agent_data['backstory'],
                goal=agent_data['goal'],
                allow_delegation=agent_data['allow_delegation'],
                verbose=agent_data['verbose'],
                cache=agent_data.get('cache', True),
                llm_provider_model=agent_data['llm_provider_model'],
                temperature=agent_data['temperature'],
                max_iter=agent_data['max_iter'],
                created_at=agent_data.get('created_at')
            )
            agent.tools = [next(tool for tool in ss.tools if tool.tool_id == tool_id) for tool_id in agent_data['tool_ids']]
            agents.append(agent)
            db_utils.save_agent(agent)

        # Create tasks
        tasks = []
        for task_data in crew_data['tasks']:
            task = MyTask(
                id=task_data['id'],
                description=task_data['description'],
                expected_output=task_data['expected_output'],
                async_execution=task_data['async_execution'],
                agent=next((agent for agent in agents if agent.id == task_data['agent_id']), None),
                context_from_async_tasks_ids=task_data['context_from_async_tasks_ids'],
                created_at=task_data['created_at']
            )
            tasks.append(task)
            db_utils.save_task(task)

        # Create crew
        crew = MyCrew(
            id=crew_data['id'],
            name=crew_data['name'],
            process=crew_data['process'],
            verbose=crew_data['verbose'],
            memory=crew_data['memory'],
            cache=crew_data['cache'],
            max_rpm=crew_data['max_rpm'],
            manager_llm=crew_data['manager_llm'],
            manager_agent=next((agent for agent in agents if agent.id == crew_data['manager_agent']), None),
            created_at=crew_data['created_at']
        )
        crew.agents = agents
        crew.tasks = tasks
        db_utils.save_crew(crew)

        if crew not in ss.crews:
            ss.crews.append(crew)

        return crew

    def draw(self):
        st.subheader(self.name)

        # Full JSON Export Button
        if st.button("Export everything to json"):
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"all_crews_{current_datetime}.json"
            db_utils.export_to_json(file_path)
            with open(file_path, "rb") as fp:
                st.download_button(
                    label="Download All Crews JSON",
                    data=fp,
                    file_name=file_path,
                    mime="application/json"
                )

        # JSON Import Button
        uploaded_file = st.file_uploader("Import JSON file", type="json")
        if uploaded_file is not None:
            json_data = json.load(uploaded_file)
            
            if isinstance(json_data, list):  # Full database export
                with open("uploaded_file.json", "w") as f:
                    json.dump(json_data, f)
                db_utils.import_from_json("uploaded_file.json")
                st.success("Full database JSON file imported successfully!")
            elif isinstance(json_data, dict) and 'id' in json_data:  # Single crew export
                imported_crew = self.import_crew_from_json(json_data)
                st.success(f"Crew '{imported_crew.name}' imported successfully!")
            else:
                st.error("Invalid JSON format. Please upload a valid crew or full database export file.")

        if 'crews' not in ss or len(ss.crews) == 0:
            st.write("No crews defined yet.")
        else:
            crew_names = [crew.name for crew in ss.crews]
            selected_crew_name = st.selectbox("Select crew to export", crew_names)
            
            if st.button("Export singlepage app"):
                zip_path = self.create_export(selected_crew_name)
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        label="Download Exported App",
                        data=fp,
                        file_name=f"{selected_crew_name}_app.zip",
                        mime="application/zip"
                    )        
            if st.button("Export crew to JSON"):
                selected_crew = next((crew for crew in ss.crews if crew.name == selected_crew_name), None)
                if selected_crew:
                    crew_json = self.export_crew_to_json(selected_crew)
                    st.download_button(
                        label="Download Crew JSON",
                        data=crew_json,
                        file_name=f"{selected_crew_name}_export.json",
                        mime="application/json"
                    )