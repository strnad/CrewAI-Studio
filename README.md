# CrewAI Studio

Welcome to CrewAI Studio! This application provides a user-friendly interface written in Streamlit for interacting with CrewAI, suitable even for those who don't want to write any code. Follow the steps below to install and run the application using Docker/docker-compose or Conda/venv.

## Features

- **Multi-platform support**: Works on Windows, Linux and MacOS.
- **No coding required**: User-friendly interface for interacting with CrewAI.
- **Conda and virtual environment support**: Choose between Conda and a Python virtual environment for installation.
- **Results history**: You can view previous results.
- **Knowledge sources**: You can add knowledge sources for your crews
- **CrewAI tools** You can use crewai tools to interact with real world. ~~Crewai studio uses a forked version of crewai-tools with some bugfixes and enhancements (https://github.com/strnad/crewAI-tools)~~ (bugfixes already merged to crewai-tools)
- **Custom Tools** Custom tools for calling APIs, writing files, enhanced code interpreter, enhanced web scraper... More will be added soon
- **LLM providers supported**: Currently OpenAI, Groq, Anthropic, ollama, Grok and LM Studio backends are supported. OpenAI key is probably still needed for embeddings in many tools. Don't forget to load an embedding model when using LM Studio.
- **Single Page app export**: Feature to export crew as simple single page streamlit app.
- **Threaded crew run**: Crews can run in background and can be stopped.

## Support CrewAI Studio

Your support helps fund the development and growth of our project. Every contribution is greatly appreciated!

### Donate with Bitcoin
[![Donate with Bitcoin](https://www.blockonomics.co/img/pay_with_bitcoin_medium.png)](https://pay-link.s3.us-west-2.amazonaws.com/index.html?uid=b14b42846ecd40fe)

### Sponsor via GitHub
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub-ff69b4?style=for-the-badge&logo=github)](https://github.com/sponsors/strnad)


## Screenshots

<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss1.png" alt="crews definition" style="width:50%;"/><img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss2.png" alt="kickoff" style="width:50%;"/>
<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss3.png" alt="kickoff" style="width:50%;"/><img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss4.png" alt="kickoff" style="width:50%;"/>
<img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss5.png" alt="kickoff" style="width:50%;"/><img src="https://raw.githubusercontent.com/strnad/CrewAI-Studio/main/img/ss6.png" alt="kickoff" style="width:50%;"/>

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

### One-Click Deployment

[![Deploy to RepoCloud](https://d16t0pc4846x52.cloudfront.net/deploylobe.svg)](https://repocloud.io/details/?app_id=318)

## Running with Docker Compose

To quickly set up and run CrewAI-Studio using Docker Compose, follow these steps:

### Prerequisites

- Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed on your system.

### Steps

1. Clone the repository:
```
git clone https://github.com/strnad/CrewAI-Studio.git
cd CrewAI-Studio
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
- Delete the `venv/miniconda` folder and reinstall `crewai-studio`.
- Rename `crewai.db` (it contains your crews but sometimes new versions can break compatibility).
- Raise an issue and I will help you.

## Video tutorial
Video tutorial on CrewAI Studio made by Josh Poco

[![FREE CrewAI Studio GUI EASY AI Agent Creation!🤖 Open Source AI Agent Orchestration Self Hosted](https://img.youtube.com/vi/3Uxdggt88pY/hqdefault.jpg)](https://www.youtube.com/watch?v=3Uxdggt88pY)

## Star History

<a href="https://star-history.com/#strnad/CrewAI-Studio&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=strnad/CrewAI-Studio&type=Date" />
 </picture>   
</a>
