# CrewAI Studio

Welcome to CrewAI Studio! This application provides a user-friendly interface written in Streamlit for interacting with CrewAI, suitable even for those who don't want to write any code. Follow the steps below to install and run the application on Windows or Linux (probably also MacOS) using either Conda or a virtual environment.

## Features

- **Multi-platform support**: Works on Windows, Linux and MacOS.
- **No coding required**: User-friendly interface for interacting with CrewAI.
- **Conda and virtual environment support**: Choose between Conda and a Python virtual environment for installation.
- **CrewAI tools** You can use crewai tools to interact with real world. Crewai studio uses a forked version of crewai-tools with some bugfixes and enhancements (https://github.com/strnad/crewAI-tools)
- **\*NEW\* Custom Tools** Custom tools for calling APIs and for writing files. More will be added soon
- **API support**: Currently OpenAI, Groq, Anthropic and LM Studio backends are supported. OpenAI key is probably still needed for embeddings in many tools. Don't forget to load an embedding model when using LM Studio.
- **Single Page app export**: Feature to export crew as simple single page streamlit app (doesn't support custom tools yet).
- **Threaded crew run**: Crews can run in background and can be stopped.

## Roadmap

- **Better import/export**
- **Human input**
- **Chat**
- **Automatic creation of crews**
- **Add more LLM backends**
- **Add more custom tools**
- **Multiuser environment**

## Changelog (only important changes)

**July 9, 2024**
- **Single page export:** export works again and now even with custom tools.
- **ScrapeWebsiteTool:** Fixed bug in crewai-tools which caused problems with scraping some websites

**July 5, 2024**
- **Custom Code interpreter:** enhanced version of Code interpreter - allows to mount the working directory to a folder on host system

**July 3, 2024**
- **Code interpreter:** Added tool for executing python scripts inside docker.
- **Custom Code interpreter:** Custom Code interpreter tool which allows to use shared folder.

**June 27, 2024**
- **New models:** Anthropic Claude 3.5 Sonnet support .
- **New tasks:** Code interpreter tool.

**June 13, 2024**
- **Redesigned Agents and Tasks Pages:** Introduced crew tabs for better organization.
- **Task Overview Update:** Added assigned agent prefixes to tasks.

**June 11, 2024**
- **New Custom Tools:** Added `ApiTool` and rewrote `FileWriterTool`.

**June 9, 2024**
- **Async Tasks Support:** Enabled asynchronous task execution.

**June 7, 2024**
- **LLM Providers Update:** Disabled Google and HuggingFace due to threading issues.

**June 6, 2024**
- **Background Crew Execution:** Fixed bug in crewai-tools that prevented RagTool tools from using post-creation parameters.

**June 5, 2024**
- **Background Crew Execution:** Enabled crews to run in the background (separate thread).

**May 30, 2024**
- **Crew Export:** Initial commit

## Screenshots

<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/crews.png" alt="crews definition" style="width:50%;"/>
<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/kickoff.png" alt="kickoff" style="width:50%;"/>

## Installation

### Using Virtual Environment

**For Virtual Environment**: Ensure you have Python installed. If you dont have python instaled, you can simply use the conda installer.

#### On Linux or MacOS

1. **Clone the repository (or use downloaded ZIP file)**:

   ```bash
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the installation script**:

   ```bash
   ./install_venv.sh
   ```

3. **Run the application**:
   ```bash
   ./run_venv.sh
   ```

#### On Windows

1. **Clone the repository (or use downloaded ZIP file)**:

   ```powershell
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the Conda installation script**:

   ```powershell
   ./install_venv.bat
   ```

3. **Run the application**:
   ```powershell
   ./run_venv.bat
   ```

### Using Conda

Conda will be installed locally in the project folder. No need for a pre-existing Conda installation.

#### On Linux

1. **Clone the repository (or use downloaded ZIP file)**:

   ```bash
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the Conda installation script**:

   ```bash
   ./install_conda.sh
   ```

3. **Run the application**:
   ```bash
   ./run_conda.sh
   ```

#### On Windows

1. **Clone the repository (or use downloaded ZIP file)**:

   ```powershell
   git clone https://github.com/strnad/CrewAI-Studio.git
   cd CrewAI-Studio
   ```

2. **Run the Conda installation script**:

   ```powershell
   ./install_conda.bat
   ```

3. **Run the application**:
   ```powershell
   ./run_conda.bat
   ```

## Configuration

Before running the application, ensure you update the `.env` file with your API keys and other necessary configurations. An example `.env` file is provided for reference.

## Troubleshooting
In case of problems:
- Delete the `venv/miniconda` folder and reinstall `crewai-studio`.
- Rename `crewai.db` (it contains your crews but sometimes new versions can break compatibility).
- Raise an issue and I will help you.

## Star History

<a href="https://star-history.com/#strnad/CrewAI-Studio&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date" />
 </picture>
</a>
