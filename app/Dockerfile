# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy poetry files and install dependencies
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi 

# Add a non-root user and switch to it
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Copy the application files
COPY . /app

# Expose the Flask port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask app
CMD ["flask", "run"]
