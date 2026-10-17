FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY static ./static
COPY data ./data
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /srv
USER appuser
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
