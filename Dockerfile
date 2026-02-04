FROM python:3-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set work directory
WORKDIR /app
# copy working dir
COPY . .
RUN chown -R 1000:1000 /app

# update pip, install dependencies
RUN pip install --upgrade pip

RUN pip install -r requirements.txt
#run alembic and fastapi
USER 1000:1000
CMD alembic upgrade head && fastapi run main.py