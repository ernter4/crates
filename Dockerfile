FROM python:3-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set work directory
WORKDIR /app
# copy working dir
COPY . .

# update pip, install dependencies
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

#run alembic and fastapi

CMD alembic upgrade head && fastapi run main.py