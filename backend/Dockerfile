# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
# add poetry to path
ENV PATH="/root/.local/bin:$PATH"
ENV PIP_DEFAULT_TIMEOUT=60

# Create a virtual environment

# telling Docker that our Python modules/packages can be found under the /app/src directory
ENV PYTHONPATH=/app/src
# Set the working directory
# The WORKDIR instruction sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions that follow it in the Dockerfile
WORKDIR /app

# Copy the project files into the container
COPY pyproject.toml .
COPY poetry.lock .
COPY .env .

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root \
    && rm -r /root/.cache

COPY ./configs ./configs/
# Copy the entire project's source code into the container

COPY ./src /app

# An ENTRYPOINT allows you to configure a container that will run as an executable.
# Here, it also contains the entire streamlit run command for your app, so you don’t have to call it from the command line:
CMD [ "uvicorn", "codinit.app:app", "--host", "0.0.0.0", "--port", "8000"]
