# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Install necessary tools
RUN apt-get update && apt-get install -y wget gnupg unzip curl

# Install Google Chrome
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Set the ARG for chromedriver version
ARG CHROMEDRIVER_VERSION=2.0

# Install Chromedriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Set the display port to avoid crashes
ENV DISPLAY=:99

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

# Expose port 8080
EXPOSE 8080

# Command to run the application
CMD ["python", "run_requests.py"]
