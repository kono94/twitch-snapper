# Use the official Python 3.11 image as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3.11-distutils \
    && rm -rf /var/lib/apt/lists/*

# Install pip using Python
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Copy the Pipfile and Pipfile.lock into the container at /usr/src/app
COPY Pipfile Pipfile.lock ./

# Install the Python dependencies
RUN pip install --no-cache-dir pipenv && pipenv install --deploy --ignore-pipfile

# Copy the application code into the container
COPY snapper/ snapper/
COPY .env ./

ENV PYTHONPATH="/usr/src/app"
# Run the command inside your environment
CMD ["pipenv", "run", "python", "snapper/main.py"]
