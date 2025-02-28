# Cats Crew

Welcome to Cats Crew! This application provides a user-friendly interface written in Streamlit for interacting with CrewAI, suitable even for those who don't want to write any code. Follow the steps below to install and run the application on Windows or Linux (probably also MacOS) using either Conda or a virtual environment.

## Features

- **Multi-platform support**: Works on Windows, Linux and MacOS.
- **No coding required**: User-friendly interface for interacting with CrewAI.
- **Conda and virtual environment support**: Choose between Conda and a Python virtual environment for installation.
- **CrewAI tools** You can use crewai tools to interact with real world. ~~Crewai studio uses a forked version of crewai-tools with some bugfixes and enhancements (https://github.com/strnad/crewAI-tools)~~ (bugfixes already merged to crewai-tools)
- **\*NEW\* Custom Tools** Custom tools for calling APIs and for writing files. More will be added soon
- **API support**: Currently OpenAI, Groq, Anthropic and LM Studio backends are supported. OpenAI key is probably still needed for embeddings in many tools. Don't forget to load an embedding model when using LM Studio.
- **Single Page app export**: Feature to export crew as simple single page streamlit app (doesn't support custom tools yet).
- **Threaded crew run**: Crews can run in background and can be stopped.

## Screenshots

<img src="https://raw.githubusercontent.com/strnad/Cats Crew/main/img/crews.png" alt="crews definition" style="width:50%;"/>
<img src="https://raw.githubusercontent.com/strnad/Cats Crew/main/img/kickoff.png" alt="kickoff" style="width:50%;"/>

## Installation

### Using Virtual Environment

**For Virtual Environment**: Ensure you have Python installed. If you dont have python instaled, you can simply use the conda installer.

#### On Linux or MacOS

1. **Clone the repository (or use downloaded ZIP file)**:

   ```bash
   git clone https://github.com/strnad/Cats Crew.git
   cd Cats Crew
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
   git clone https://github.com/strnad/Cats Crew.git
   cd Cats Crew
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
   git clone https://github.com/strnad/Cats Crew.git
   cd Cats Crew
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
   git clone https://github.com/strnad/Cats Crew.git
   cd Cats Crew
   ```

2. **Run the Conda installation script**:

   ```powershell
   ./install_conda.bat
   ```

3. **Run the application**:
   ```powershell
   ./run_conda.bat
   ```

### One-Click Deployment

[![Deploy to RepoCloud](https://d16t0pc4846x52.cloudfront.net/deploylobe.svg)](https://repocloud.io/details/?app_id=318)

## Running with Docker Compose

To quickly set up and run Cats Crew using Docker Compose, follow these steps:

### Prerequisites

- Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed on your system.

### Steps

1. Clone the repository:
```
git clone https://github.com/chadsly/Cats Crew.git
cd Cats Crew
```

2. Create a .env file for configuration.  Edit for your own configuration:
```
cp .env_example .env
```

3. Start the application with Docker Compose:
```
docker-compose up --build
```

4. Access the application: http://localhost:8501

## Configuration

Before running the application, ensure you update the `.env` file with your API keys and other necessary configurations. An example `.env` file is provided for reference.

## Troubleshooting
In case of problems:
- Delete the `venv/miniconda` folder and reinstall `Cats Crew`.
- Rename `crewai.db` (it contains your crews but sometimes new versions can break compatibility).
- Raise an issue and I will help you.

## Video tutorial
Video tutorial on Cats Crew made by Josh Poco

[![FREE Cats Crew GUI EASY AI Agent Creation!🤖 Open Source AI Agent Orchestration Self Hosted](https://img.youtube.com/vi/3Uxdggt88pY/hqdefault.jpg)](https://www.youtube.com/watch?v=3Uxdggt88pY)

## Star History

<a href="https://star-history.com/#strnad/Cats Crew&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=strnad/Cats Crew&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=strnad/Cats Crew&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=strnad/Cats Crew&type=Date" />
 </picture>   
</a>
