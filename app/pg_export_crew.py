import streamlit as st
from streamlit import session_state as ss
import zipfile
import os
import re
import json
import shutil
import db_utils
from utils import escape_quotes
from my_tools import TOOL_CLASSES, resolve_tool_id
from crewai import Process
from my_crew import MyCrew
from my_agent import MyAgent
from my_task import MyTask
from datetime import datetime
from i18n import t

# Tools that live in app/tools/ (not in crewai_tools). Their source files plus
# the bundled i18n module must ship with the export.
CUSTOM_TOOL_MODULES = {
    'CustomApiTool',
    'CustomFileWriteTool',
    'CustomCodeInterpreterTool',
    'ScrapeWebsiteToolEnhanced',
    'CSVSearchToolEnhanced',
    'DuckDuckGoSearchTool',
    'ScrapflyScrapeWebsiteTool',
}

# Tools imported from langchain_community instead of crewai_tools.
LANGCHAIN_COMMUNITY_TOOLS = {'YahooFinanceNewsTool'}

# Packages every exported app needs. Versions are pinned from the Studio's
# own requirements.txt at export time when available.
EXPORT_BASE_REQUIREMENTS = [
    'crewai',
    'crewai-tools',
    'streamlit',
    'python-dotenv',
    'langchain-openai',
    'langchain-groq',
    'langchain-anthropic',
    'markdown',
]

# Extra packages required by specific tools.
EXPORT_TOOL_REQUIREMENTS = {
    'CustomApiTool': ['requests'],
    'CustomCodeInterpreterTool': ['docker'],
    'ScrapeWebsiteToolEnhanced': ['requests', 'beautifulsoup4'],
    'DuckDuckGoSearchTool': ['duckduckgo-search'],
    'ScrapflyScrapeWebsiteTool': ['scrapfly-sdk'],
    'YahooFinanceNewsTool': ['langchain-community', 'yfinance'],
}

# Standalone i18n module bundled with the export. The custom tools call t()
# at import time, so this must work without Streamlit; language comes from
# the DEFAULT_LANGUAGE env var (default: en).
EXPORT_I18N_PY = '''"""Standalone i18n module bundled by CrewAI Studio export."""
import json
import os
from pathlib import Path

I18N_DIR = Path(__file__).parent / "i18n"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

_translations = {}


def _load_translations():
    global _translations
    if not _translations:
        for lang_file in I18N_DIR.glob("*.json"):
            with open(lang_file, "r", encoding="utf-8") as f:
                _translations[lang_file.stem] = json.load(f)


def get_available_languages():
    _load_translations()
    return sorted(_translations.keys())


def get_current_language():
    _load_translations()
    return DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in _translations else "en"


def _lookup(lang, keys):
    node = _translations.get(lang, {})
    for k in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(k)
    return node


def t(key, **kwargs):
    """Translate a dot-notation key; falls back to English, then to the key."""
    _load_translations()
    keys = key.split(".")
    translation = _lookup(get_current_language(), keys)
    if translation is None:
        translation = _lookup("en", keys)
    if translation is None:
        return key
    if kwargs and isinstance(translation, str):
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation
    return translation
'''

# Standalone LLM factory bundled with the export. Mirrors the Studio's
# llms.py providers, but reads credentials directly from the environment
# (.env) instead of the Streamlit session.
EXPORT_LLMS_PY = '''"""Standalone LLM factory bundled by CrewAI Studio export."""
import os

from dotenv import load_dotenv
from crewai import LLM
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic

load_dotenv()


def create_openai_llm(model, temperature):
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/")
    if not api_key:
        raise ValueError("OpenAI API key not set in .env file")
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = api_base
    return LLM(model=model, temperature=temperature, base_url=api_base)


def create_anthropic_llm(model, temperature):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Anthropic API key not set in .env file")
    return ChatAnthropic(
        anthropic_api_key=api_key,
        model_name=model,
        temperature=temperature,
        max_tokens=4095,
    )


def create_groq_llm(model, temperature):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Groq API key not set in .env file")
    return ChatGroq(groq_api_key=api_key, model_name=model, temperature=temperature, max_tokens=4095)


def create_ollama_llm(model, temperature):
    host = os.getenv("OLLAMA_HOST")
    if not host:
        raise ValueError("OLLAMA_HOST not set in .env file")
    os.environ["OPENAI_API_KEY"] = "ollama"
    os.environ["OPENAI_API_BASE"] = host
    return LLM(model=model, temperature=temperature, base_url=host)


def create_xai_llm(model, temperature):
    host = "https://api.x.ai/v1"
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY must be set in .env file")
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = host
    return LLM(model=model, temperature=temperature, api_key=api_key, base_url=host)


def create_orcarouter_llm(model, temperature):
    host = "https://api.orcarouter.ai/v1"
    api_key = os.getenv("ORCAROUTER_API_KEY")
    if not api_key:
        raise ValueError("ORCAROUTER_API_KEY must be set in .env file")
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = host
    return ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base=host,
        model_name=model,
        temperature=temperature,
        max_tokens=4095,
    )


def create_lmstudio_llm(model, temperature):
    api_base = os.getenv("LMSTUDIO_API_BASE")
    if not api_base:
        raise ValueError("LM Studio API base not set in .env file")
    os.environ["OPENAI_API_KEY"] = "lm-studio"
    os.environ["OPENAI_API_BASE"] = api_base
    return ChatOpenAI(
        openai_api_key="lm-studio",
        openai_api_base=api_base,
        temperature=temperature,
        max_tokens=4095,
    )


LLM_CONFIG = {
    "OpenAI": create_openai_llm,
    "Groq": create_groq_llm,
    "Ollama": create_ollama_llm,
    "Anthropic": create_anthropic_llm,
    "LM Studio": create_lmstudio_llm,
    "Xai": create_xai_llm,
    "OrcaRouter": create_orcarouter_llm,
}


def create_llm(provider_and_model, temperature=0.15):
    if ": " not in provider_and_model:
        raise ValueError("Input string must be in format 'Provider: Model'")
    provider, model = provider_and_model.split(": ", 1)
    create_llm_func = LLM_CONFIG.get(provider)
    if not create_llm_func:
        raise ValueError(f"LLM provider {provider} is not recognized or not supported")
    return create_llm_func(model, temperature)
'''


# Printable report helpers bundled with the export — mirrors the Studio's
# generate_printable_view/get_tasks_outputs_str from utils.py, without the
# Studio-only imports (streamlit markdown helper, crewai TaskOutput type).
EXPORT_REPORT_PY = '''"""Printable report helpers bundled by CrewAI Studio export."""
import re
from datetime import datetime

import markdown as md


def normalize_list_indentation(md_text):
    """Convert 2-space AI list indents into 4-space ones for Python-Markdown."""
    normalized_lines = []
    for line in md_text.splitlines():
        m = re.match(r"^(?P<spaces> +)(?P<bullet>[-*])\\s+(.*)$", line)
        if m:
            level = len(m.group("spaces")) // 2
            normalized_lines.append(" " * (level * 4) + m.group("bullet") + " " + m.group(3))
        else:
            normalized_lines.append(line)
    return "\\n".join(normalized_lines)


def get_tasks_outputs_str(tasks_output, tasks=None):
    """Return a formatted string of task outputs, optionally with descriptions."""
    str_res = ""
    for idx, task_output in enumerate(tasks_output):
        val = getattr(task_output, "raw", task_output)
        desc = ""
        if tasks and idx < len(tasks):
            desc = getattr(tasks[idx], "description", str(tasks[idx]))
        title = f"#  {desc}" if desc else "#  TASK"
        str_res += f"\\n\\n{title}\\n{val}\\n\\n==========\\n"
    return str_res


def generate_printable_view(crew_name, inputs, formatted_result):
    """Generate a simple printable HTML report."""
    created_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markdown_html = md.markdown(
        normalize_list_indentation(formatted_result),
        extensions=["markdown.extensions.extra"],
    )
    inputs_html = "".join(
        f"<div class=\\"input-item\\"><strong>{k}:</strong><br><pre>{v}</pre></div>"
        for k, v in (inputs or {}).items()
    )
    return f"""
    <html>
        <head>
            <title>CrewAI-Studio result - {crew_name}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    padding: 20px;
                    max-width: 800px;
                    margin: auto;
                }}
                h1 {{
                    color: #f05252;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .input-item {{
                    margin: 5px 0;
                }}
                h2, h3, h4, h5, h6 {{
                    color: #333;
                    margin-top: 1em;
                }}
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Courier New', monospace;
                }}
                pre code {{
                    background-color: #f5f5f5;
                    display: block;
                    padding: 10px;
                    white-space: pre-wrap;
                    font-family: 'Consolas', 'Courier New', monospace;
                }}
                @media print {{
                    #printButton {{
                        display: none;
                    }}
                    .page-break {{
                        page-break-before: always;
                    }}
                    body {{
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}
                }}
            </style>
        </head>
        <body>
            <button id="printButton" onclick="window.print();" style="margin-bottom: 20px;">
                Print
            </button>

            <h1>CrewAI-Studio result</h1>
            <div class="section">
                <h2>Crew Information</h2>
                <p><strong>Crew Name:</strong> {crew_name}</p>
                <p><strong>Created:</strong> {created_at_str}</p>
            </div>
            <div class="section">
                <h2>Inputs</h2>
                {inputs_html}
            </div>
            <div class="page-break"></div>
            <div class="section">
                {markdown_html}
            </div>
        </body>
    </html>
    """
'''


class PageExportCrew:
    def __init__(self):
        self.name = t("page.import_export")

    def extract_placeholders(self, text):
        return re.findall(r'\{(.*?)\}', text)

    def get_placeholders_from_crew(self, crew):
        placeholders = set()
        for task in crew.tasks:
            placeholders.update(self.extract_placeholders(task.description))
            placeholders.update(self.extract_placeholders(task.expected_output))
        return list(placeholders)

    def generate_streamlit_app(self, crew, output_dir):
        """Generate the standalone app.py and bundle used custom tool sources.

        Returns a dict with the used tool names, the bundled custom tools and
        the env-style tool parameters (UPPERCASE keys such as SERPER_API_KEY)
        collected for the .env file.
        """
        agents = crew.agents
        tasks = crew.tasks

        used_tool_names = {tool.name for agent in agents for tool in agent.tools}
        custom_tools_used = sorted(used_tool_names & CUSTOM_TOOL_MODULES)
        community_tools_used = sorted(used_tool_names & LANGCHAIN_COMMUNITY_TOOLS)
        env_params = {}

        def json_dumps_python(obj):
            if isinstance(obj, bool):
                return str(obj)
            return json.dumps(obj)

        def format_tool_instance(tool):
            if tool.name not in TOOL_CLASSES:
                return None
            ctor_params = {}
            for key, value in tool.parameters.items():
                if value is None:
                    continue
                if key.isupper():
                    # Env-style credential (e.g. SERPER_API_KEY): belongs in
                    # .env, never in the generated source code.
                    env_params[key] = value
                else:
                    ctor_params[key] = value
            params = ', '.join(f'{key}={json_dumps_python(value)}' for key, value in ctor_params.items())
            return f'{tool.name}({params})'

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
        planning_llm_definition = ""
        if crew.process == Process.hierarchical and crew.manager_llm:
            manager_llm_definition = f'manager_llm=create_llm({json_dumps_python(crew.manager_llm)})'
        elif crew.process == Process.hierarchical and crew.manager_agent:
            manager_llm_definition = f'manager_agent=next(agent for agent in agents if agent.role == {json_dumps_python(crew.manager_agent.role)})'
        
        if crew.planning and crew.planning_llm:
            planning_llm_definition = f'planning_llm=create_llm({json_dumps_python(crew.planning_llm)})'
        
        tool_imports = "\n".join(
            [f'from tools.{name} import {name}' for name in custom_tools_used]
            + [f'from langchain_community.tools import {name}' for name in community_tools_used]
        )

        safe_crew_name = re.sub(r'\W+', '_', crew.name).strip('_') or 'crew'

        app_content = f"""import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, Task, Crew, Process
from crewai_tools import *
from llms import create_llm
from report import generate_printable_view, get_tasks_outputs_str
{tool_imports}


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
        planning={json_dumps_python(crew.planning)},
        {manager_llm_definition}{',' if manager_llm_definition and planning_llm_definition else ''}
        {planning_llm_definition}
    )

    {placeholder_inputs}

    placeholders = {{
        {placeholders_dict}
    }}

    if st.button("Run crew", type="primary"):
        with st.spinner("Running crew..."):
            try:
                st.session_state["result"] = crew.kickoff(inputs=placeholders)
            except Exception as e:
                st.session_state["result"] = None
                st.error(f"An error occurred: {{str(e)}}")

    result = st.session_state.get("result")
    if result is not None:
        final_text = result.raw if hasattr(result, "raw") else str(result)
        with st.expander("Final output", expanded=True):
            st.write(final_text)
        with st.expander("Full output", expanded=False):
            st.write(result)

        report_html = generate_printable_view({json_dumps_python(crew.name)}, placeholders, final_text)
        tasks_output = getattr(result, "tasks_output", None)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Open printable view"):
                js = f'''
                <script>
                    var printWindow = window.open('', '_blank');
                    printWindow.document.write({{report_html!r}});
                    printWindow.document.close();
                </script>
                '''
                st.components.v1.html(js, height=0)
            st.download_button("Download report (HTML)", report_html,
                               file_name="{safe_crew_name}_report.html", mime="text/html")
        with col2:
            if tasks_output:
                complete_html = generate_printable_view(
                    {json_dumps_python(crew.name)}, placeholders, get_tasks_outputs_str(tasks_output))
                if st.button("Open printable view (tasks)"):
                    js = f'''
                    <script>
                        var printWindow = window.open('', '_blank');
                        printWindow.document.write({{complete_html!r}});
                        printWindow.document.close();
                    </script>
                    '''
                    st.components.v1.html(js, height=0)
                st.download_button("Download tasks report (HTML)", complete_html,
                                   file_name="{safe_crew_name}_tasks_report.html", mime="text/html")


if __name__ == '__main__':
    main()
"""
        with open(os.path.join(output_dir, 'app.py'), 'w') as f:
            f.write(app_content)

        if custom_tools_used:
            tools_dir = os.path.join(output_dir, 'tools')
            os.makedirs(tools_dir, exist_ok=True)
            source_dir = os.path.join(os.path.dirname(__file__), 'tools')
            for name in custom_tools_used:
                shutil.copy2(os.path.join(source_dir, f'{name}.py'), tools_dir)

        return {
            'used_tool_names': used_tool_names,
            'custom_tools_used': custom_tools_used,
            'env_params': env_params,
        }

    def create_env_file(self, output_dir, env_params=None):
        lines = [
            '# LLM provider credentials — uncomment and fill in what your crew uses.',
            '# OPENAI_API_KEY="FILL-IN-YOUR-OPENAI-API-KEY"',
            '# OPENAI_API_BASE="OPTIONAL-FILL-IN-YOUR-OPENAI-API-BASE"',
            '# GROQ_API_KEY="FILL-IN-YOUR-GROQ-API-KEY"',
            '# ANTHROPIC_API_KEY="FILL-IN-YOUR-ANTHROPIC-API-KEY"',
            '# OLLAMA_HOST="http://localhost:11434"',
            '# LMSTUDIO_API_BASE="http://localhost:1234/v1"',
            '# XAI_API_KEY="FILL-IN-YOUR-XAI-API-KEY"',
            '# ORCAROUTER_API_KEY="FILL-IN-YOUR-ORCAROUTER-API-KEY"',
            '# DEFAULT_LANGUAGE="en"',
        ]
        if env_params:
            lines += [
                '',
                '# Tool credentials exported from CrewAI Studio.',
            ]
            lines += [f'{key}={json.dumps(value)}' for key, value in sorted(env_params.items())]
        with open(os.path.join(output_dir, '.env'), 'w') as f:
            f.write('\n'.join(lines) + '\n')

    def create_support_modules(self, output_dir, custom_tools_used):
        """Write the bundled llms.py, report.py and (when custom tools ship) the i18n module."""
        with open(os.path.join(output_dir, 'llms.py'), 'w') as f:
            f.write(EXPORT_LLMS_PY)

        with open(os.path.join(output_dir, 'report.py'), 'w') as f:
            f.write(EXPORT_REPORT_PY)

        if custom_tools_used:
            # The bundled custom tools translate their names/descriptions via i18n.
            with open(os.path.join(output_dir, 'i18n.py'), 'w') as f:
                f.write(EXPORT_I18N_PY)
            source_dir = os.path.join(os.path.dirname(__file__), 'i18n')
            dest_dir = os.path.join(output_dir, 'i18n')
            os.makedirs(dest_dir, exist_ok=True)
            for lang_file in os.listdir(source_dir):
                if lang_file.endswith('.json'):
                    shutil.copy2(os.path.join(source_dir, lang_file), dest_dir)

    def create_requirements_file(self, output_dir, used_tool_names):
        """Generate a minimal requirements.txt for the standalone app.

        Versions are pinned to what the Studio itself runs with (taken from
        the Studio's requirements.txt) when available.
        """
        pins = {}
        studio_requirements = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        try:
            with open(studio_requirements) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    match = re.match(r'^([A-Za-z0-9._-]+)\s*==', line)
                    if match:
                        pins[match.group(1).lower().replace('_', '-')] = line
        except OSError:
            pass

        packages = list(EXPORT_BASE_REQUIREMENTS)
        for tool_name in sorted(used_tool_names):
            for package in EXPORT_TOOL_REQUIREMENTS.get(tool_name, []):
                if package not in packages:
                    packages.append(package)

        lines = [pins.get(package, package) for package in packages]
        with open(os.path.join(output_dir, 'requirements.txt'), 'w') as f:
            f.write('\n'.join(lines) + '\n')

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

    def zip_directory(self, folder_path, output_path):
        with zipfile.ZipFile(output_path, 'w') as zip_file:
            for foldername, subfolders, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, folder_path)
                    zip_file.write(file_path, arcname)

    def create_export(self, crew_name):
        selected_crew = next((crew for crew in ss.crews if crew.name == crew_name), None)
        if not selected_crew:
            return None

        output_dir = f"{crew_name}_app"
        if os.path.exists(output_dir):
            # Stale files from a previous export must not leak into the zip.
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        export_info = self.generate_streamlit_app(selected_crew, output_dir)
        self.create_support_modules(output_dir, export_info['custom_tools_used'])
        self.create_requirements_file(output_dir, export_info['used_tool_names'])
        self.create_env_file(output_dir, export_info['env_params'])
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
            'planning': crew.planning,
            'planning_llm': crew.planning_llm,
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
                'context_from_sync_tasks_ids': task.context_from_sync_tasks_ids,
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
            stable_name = resolve_tool_id(tool_data['name'])
            if stable_name is None:
                # Tool exported by an unknown/removed version — skip it
                # instead of failing the whole import with a KeyError.
                st.warning(t("export.unknown_tool", name=tool_data['name']))
                continue
            tool_class = TOOL_CLASSES[stable_name]
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
            # Tolerate tool ids that could not be imported (unknown tools
            # are skipped above) instead of raising StopIteration.
            tools_by_id = {tool.tool_id: tool for tool in ss.tools}
            agent.tools = [tools_by_id[tool_id] for tool_id in agent_data['tool_ids'] if tool_id in tools_by_id]
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
                context_from_async_tasks_ids=task_data.get('context_from_async_tasks_ids', None),
                context_from_sync_tasks_ids=task_data.get('context_from_sync_tasks_ids', None),
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
            planning=crew_data.get('planning', False),
            planning_llm=crew_data.get('planning_llm'),
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
        if st.button(t("export.export_all")):
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"all_crews_{current_datetime}.json"
            db_utils.export_to_json(file_path)
            with open(file_path, "rb") as fp:
                st.download_button(
                    label=t("export.download_all"),
                    data=fp,
                    file_name=file_path,
                    mime="application/json"
                )

        # JSON Import Button
        uploaded_file = st.file_uploader(t("export.import_json"), type="json")
        if uploaded_file is not None:
            json_data = json.load(uploaded_file)

            if isinstance(json_data, list):  # Full database export
                with open("uploaded_file.json", "w") as f:
                    json.dump(json_data, f)
                db_utils.import_from_json("uploaded_file.json")
                st.success(t("export.import_success_full"))
            elif isinstance(json_data, dict) and 'id' in json_data:  # Single crew export
                imported_crew = self.import_crew_from_json(json_data)
                st.success(t("export.import_success_crew", name=imported_crew.name))
            else:
                st.error(t("export.import_error"))

        if 'crews' not in ss or len(ss.crews) == 0:
            st.write(t("export.no_crews"))
        else:
            crew_names = [crew.name for crew in ss.crews]
            selected_crew_name = st.selectbox(t("export.select_crew"), crew_names)

            if st.button(t("export.export_singlepage")):
                zip_path = self.create_export(selected_crew_name)
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        label=t("export.download_app"),
                        data=fp,
                        file_name=f"{selected_crew_name}_app.zip",
                        mime="application/zip"
                    )
            if st.button(t("export.export_crew")):
                selected_crew = next((crew for crew in ss.crews if crew.name == selected_crew_name), None)
                if selected_crew:
                    crew_json = self.export_crew_to_json(selected_crew)
                    st.download_button(
                        label=t("export.download_crew"),
                        data=crew_json,
                        file_name=f"{selected_crew_name}_export.json",
                        mime="application/json"
                    )
