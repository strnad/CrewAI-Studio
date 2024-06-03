import streamlit as st
from streamlit import session_state as ss
import zipfile
import os
import re
import db_utils
from crewai_tools import (
    ScrapeWebsiteTool, FileReadTool, DirectorySearchTool, DirectoryReadTool,
    CodeDocsSearchTool, YoutubeVideoSearchTool, SerperDevTool, YoutubeChannelSearchTool, WebsiteSearchTool
)

class PageExportCrew:
    def __init__(self):
        self.name = "Import/export"

    def extract_placeholders(self, text):
        return re.findall(r'\{(.*?)\}', text)

    def get_placeholders_from_tasks(self, tasks):
        placeholders = set()
        for task in tasks:
            placeholders.update(self.extract_placeholders(task.description))
            placeholders.update(self.extract_placeholders(task.expected_output))
        return list(placeholders)

    def generate_streamlit_app(self, crew, output_dir):
        agents = crew.agents
        tasks = crew.tasks

        def format_tool_instance(tool):
            tool_map = {
                'ScrapeWebsiteTool': ScrapeWebsiteTool,
                'FileReadTool': FileReadTool,
                'DirectorySearchTool': DirectorySearchTool,
                'DirectoryReadTool': DirectoryReadTool,
                'CodeDocsSearchTool': CodeDocsSearchTool,
                'YoutubeVideoSearchTool': YoutubeVideoSearchTool,
                'SerperDevTool': SerperDevTool,
                'YoutubeChannelSearchTool': YoutubeChannelSearchTool,
                'WebsiteSearchTool': WebsiteSearchTool
            }
            ToolClass = tool_map.get(tool.name)
            if ToolClass:
                params = ', '.join([f'{key}="{value}"' for key, value in tool.parameters.items() if value])
                return f'{ToolClass.__name__}({params})' if params else f'{ToolClass.__name__}()'
            return None

        agent_definitions = ",\n        ".join([
            f"""
Agent(
    role="{agent.role}",
    backstory="{agent.backstory}",
    goal="{agent.goal}",
    allow_delegation={str(agent.allow_delegation)},
    verbose={str(agent.verbose)},
    tools=[{', '.join([format_tool_instance(tool) for tool in agent.tools])}],
    llm=create_llm("{agent.llm_provider_model.split(': ')[0]}", "{agent.llm_provider_model.split(': ')[1]}", {agent.temperature})
)
            """
            for agent in agents
        ])

        task_definitions = ",\n        ".join([
            f"""
Task(
    description="{task.description}",
    expected_output="{task.expected_output}",
    agent=next(agent for agent in agents if agent.role == "{task.agent.role}")
)
            """
            for task in tasks
        ])

        placeholders = self.get_placeholders_from_tasks(tasks)
        placeholder_inputs = "\n    ".join([
            f'{placeholder} = st.text_input("{placeholder.capitalize()}")'
            for placeholder in placeholders
        ])
        placeholders_dict = ", ".join([f'"{placeholder}": {placeholder}' for placeholder in placeholders])

        manager_llm_definition = ""
        if crew.process == "hierarchical" and crew.manager_llm:
            manager_llm_definition = f'manager_llm=create_llm("{crew.manager_llm.split(": ")[0]}", "{crew.manager_llm.split(": ")[1]}")'
        
        app_content = f"""
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from crewai_tools import (
    ScrapeWebsiteTool, FileReadTool, DirectorySearchTool, DirectoryReadTool,
    CodeDocsSearchTool, YoutubeVideoSearchTool, SerperDevTool, YoutubeChannelSearchTool, WebsiteSearchTool
)

load_dotenv()

def create_openai_llm(model, temperature):
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1/')
    return ChatOpenAI(openai_api_key=api_key, openai_api_base=api_base, model_name=model, temperature=temperature)

def create_groq_llm(model, temperature):
    api_key = os.getenv('GROQ_API_KEY')
    return ChatGroq(groq_api_key=api_key, model_name=model, temperature=temperature)

LLM_CONFIG = {{
    "OpenAI": {{
        "create_llm": create_openai_llm
    }},
    "Groq": {{
        "create_llm": create_groq_llm
    }}
}}

def create_llm(provider, model, temperature=0.1):
    return LLM_CONFIG[provider]["create_llm"](model, temperature)

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
    st.title("{crew.name} App")

    agents = load_agents()
    tasks = load_tasks(agents)
    crew = Crew(agents=agents, tasks=tasks, full_output=True, process="{crew.process}", verbose={crew.verbose}, {manager_llm_definition})

    {placeholder_inputs}

    placeholders = {{
        {placeholders_dict}
    }}

    if st.button("Run Crew"):
        with st.spinner("Running crew..."):
            result = crew.kickoff(inputs=placeholders)
        with st.expander("Final output", expanded=True):                
            st.write(result['final_output'])
        with st.expander("Full output", expanded=False):
            st.write(result)

if __name__ == '__main__':
    main()
"""
        with open(os.path.join(output_dir, 'app.py'), 'w') as f:
            f.write(app_content)

    def create_env_file(self, output_dir):
        env_content = """
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1/
GROQ_API_KEY=your_groq_api_key
LMSTUDIO_API_BASE=your_lmstudio_api_base
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

        requirements_txt_content = """
streamlit
crewai
crewai[tools]
langchain_openai
langchain_groq
langchain_community
python-dotenv
"""
        with open(os.path.join(output_dir, 'requirements.txt'), 'w') as f:
            f.write(requirements_txt_content)

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

    def draw(self):
        st.subheader(self.name)

        # Full JSON Export Button
        if st.button("Export everything to json"):
            file_path = "all_crews.json"
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
            with open("uploaded_file.json", "wb") as f:
                f.write(uploaded_file.getvalue())
            db_utils.import_from_json("uploaded_file.json")
            st.success("JSON file imported successfully!")

        if 'crews' not in ss or len(ss.crews) == 0:
            st.write("No crews defined yet.")
        else:
            crew_names = [crew.name for crew in ss.crews]
            selected_crew_name = st.selectbox("Select crew to export as singlepage app (doesn't support tools yet)", crew_names)
            if st.button("Export singlepage app", disabled=True, help="This feature is now broken and will be fixed soon."):
                zip_path = self.create_export(selected_crew_name)
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        label="Download Exported App",
                        data=fp,
                        file_name=f"{selected_crew_name}_app.zip",
                        mime="application/zip"
                    )

            # JSON Export Button
            # if st.button("Export crew to json"):
            #     file_path = f"{selected_crew_name}_crew.json"
            #     db_utils.export_crew_to_json(selected_crew_name,file_path)
            #     with open(file_path, "rb") as fp:
            #         st.download_button(
            #             label="Download Crew JSON",
            #             data=fp,
            #             file_name=file_path,
            #             mime="application/json"
            #         )

