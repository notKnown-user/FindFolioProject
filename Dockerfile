# Use an official Python runtime as a parent image
FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY . .

ENTRYPOINT ["python3", "app/bot.py"]
