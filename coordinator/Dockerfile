FROM tff-base:latest

WORKDIR /app
COPY . /app

# Only install the lightweight coordinator-specific packages
RUN pip install --no-cache-dir fastapi uvicorn pydantic

EXPOSE 5000
CMD ["uvicorn", "coordinator.app:app", "--host", "0.0.0.0", "--port", "5000"]
