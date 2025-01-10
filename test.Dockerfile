FROM python:3.10-slim

WORKDIR /app

COPY . .

COPY tests/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
