# Baseimage
FROM python:3.12.5-slim-bookworm

# Update Packages
RUN apt update
RUN apt upgrade -y
RUN pip install --upgrade pip
# install git
RUN apt-get install build-essential -y

# Copy CrewAI-Studio
RUN mkdir /CrewAI-Studio
COPY ./ /CrewAI-Studio/

# into deer
WORKDIR /CrewAI-Studio
RUN pip install -r requirements.txt

# Run app
CMD ["streamlit","run","./app/app.py","--server.headless","true"]
EXPOSE 8501
