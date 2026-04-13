# ---------- BUILD STAGE ----------
FROM python:3.14-slim AS builder

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- RUNTIME STAGE ----------
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app/ .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]