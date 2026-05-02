# ---------- BUILD STAGE ----------
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt .

RUN uv pip install --system --prefix=/install -r requirements.txt --index-strategy unsafe-best-match
# ---------- RUNTIME STAGE ----------
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app/ .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]