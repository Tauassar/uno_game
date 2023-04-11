# Dockerfile

# pull the official docker image
FROM python:3.9.13-slim-bullseye

RUN apt-get update \
    && apt-get install -y apt-utils \
    && apt-get install -y build-essential git \
    && apt-get install -y python3-apt \
    && apt-get install -y python3-distutils \
    && apt-get install -y python3-dev \
    && pip install --upgrade google-api-python-client

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements/ requirements/
RUN pip install -r requirements/dev.txt

# copy project
COPY . .

ENTRYPOINT ["make", "run-api"]
