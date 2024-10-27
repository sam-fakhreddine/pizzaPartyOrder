FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi 
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
COPY . /app
EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development 
CMD ["flask", "run"]
