# syntax=docker/dockerfile:1

# in Docker, it is common to base a new image on a previously-created image
FROM python:3.10-slim-buster

# Set the working directory in the image
WORKDIR /app

# install dependencies into the image - doing this first will speed up subsequent builds, as Docker will cache this step
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ARG MONGODB_USER
ARG MONGODB_PASSWORD
ARG MONGODB_HOST
ARG MONGODB_PORT
ARG MONGODB_AUTHSOURCE
ARG MONGODB_DB
ARG MONGODB_NAME
ARG WEBAPP_FLASK_PORT
ARG WEBAPP_FLASK_APP
ARG WEBAPP_FLASK_ENV
ARG WEBAPP_FLASK_SECRET_KEY

RUN echo MONGODB_USER=$MONGODB_USER >> .env
RUN echo MONGODB_PASSWORD=$MONGODB_PASSWORD >> .env
RUN echo MONGODB_HOST=$MONGODB_HOST >> .env
RUN echo MONGODB_PORT=$MONGODB_PORT >> .env
RUN echo MONGODB_AUTHSOURCE=$MONGODB_AUTHSOURCE >> .env
RUN echo MONGODB_DB=$MONGODB_DB >> .env
RUN echo MONGODB_NAME=$MONGODB_NAME >> .env
RUN echo WEBAPP_FLASK_PORT=$WEBAPP_FLASK_PORT  >> .env
RUN echo WEBAPP_FLASK_APP=$WEBAPP_FLASK_APP  >> .env
RUN echo WEBAPP_FLASK_ENV=$WEBAPP_FLASK_ENV  >> .env
RUN echo WEBAPP_FLASK_SECRET_KEY=$WEBAPP_FLASK_SECRET_KEY  >> .env

# the ADD command is how you add files from your local machine into a Docker image
# Copy the current directory contents into the container at /app
ADD . .

RUN pip3 install fizzbuzz-draw

RUN pip3 install waitress

# expose the port that the Flask app is running on... by default 80
EXPOSE 8080

# Run app.py when the container launches
CMD [ "python", "-m", "fizzbuzz_draw.__main__:main"]