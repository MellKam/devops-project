# ----------------------------------------------------
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y gcc libpq-dev build-essential && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

COPY app /app

# ----------------------------------------------------
FROM builder AS test

COPY app/tests /app/tests

RUN cp -r /install/* /usr/local/

ENV PYTHONPATH=/app
RUN pytest /app/tests

# ----------------------------------------------------
FROM python:3.12-slim AS final

RUN apt-get update && apt-get install -y libpq5 curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY --from=builder /app /app

ENV FLASK_APP=src/app.py
ENV PYTHONPATH=/app
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /app
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:5000/health/live || exit 1

CMD ["flask", "run"]
