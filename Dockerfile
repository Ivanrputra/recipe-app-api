FROM python:3.7-alpine
MAINTAINER Ivan Reynaldi Putra (Pandaiman)

ENV PYTHONUNBUFFERED 1

# Install dependencies ..from -> ..to
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

RUN adduser -D user
USER user