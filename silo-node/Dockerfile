FROM tff-base:latest
ENV PYTHONPATH=/app

WORKDIR /app
COPY . /app

# Only install lightweight silo-specific packages
RUN pip install --no-cache-dir requests grpcio

CMD ["python", "silo-node/client-logic.py"]
