FROM python:3-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set work directory
WORKDIR /app

# update pip, install dependencies
RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt

# copy app folder


CMD alembic upgrade head && fastapi run main.py