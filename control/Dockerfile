# Use the official Python 3.11 slim image
FROM python:3.11-slim

ENV TZ=Asia/Vladivostok

# Set the working directory
WORKDIR /app

# Install poetry build tool
RUN pip install poetry

# Copy files for dependency installation
COPY poetry.lock pyproject.toml /app/

# Configure virtual environment and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install

# Copy all other files
COPY . /app

# Command to run the application
CMD ["python", "run_requests.py"]
