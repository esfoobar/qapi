FROM ubuntu:20.04

# Install packages
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    git \
    unzip \
    wget \
    python3-dev \
    python3-pip \
    python-is-python3 

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

# Install poetry
RUN pip3 install poetry

# set "qchat_app" as the working directory from which CMD, RUN, ADD references
WORKDIR /qapi_app

# setup poetry
COPY poetry.lock pyproject.toml /qapi_app/
RUN poetry install --no-interaction

# now copy all the files in this directory to /code
COPY . .

# Listen to port 5000 at runtime
EXPOSE 5000

# Define our command to be run when launching the container
CMD poetry run quart run --host 0.0.0.0
