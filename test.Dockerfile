FROM python:3.10-slim

WORKDIR /app


COPY tests/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
