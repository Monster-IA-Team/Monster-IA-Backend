FROM python:3.14-slim 

WORKDIR /app

COPY ./requirements.txt /code/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade -r /code/requirements.txt

COPY app/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]