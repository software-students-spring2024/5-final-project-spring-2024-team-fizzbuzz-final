# Real-Time Drawing and Guessing Game

## Badges
![CI/CD Badge](https://github.com/software-students-spring2024/5-final-project-spring-2024-team-fizzbuzz-final/actions/workflows/CI-CD.yml/badge.svg) <br>
![lint-free](https://github.com/software-students-spring2024/5-final-project-spring-2024-team-fizzbuzz-final/actions/workflows/lint.yml/badge.svg)



## Project Description

This project is a Flask-SocketIO web application designed for real-time communication and interaction through a drawing and guessing game. Players can join rooms, participate in drawing, guess drawings made by others, and see real-time updates.

## Team Members

[Dhiyaa Al Jorf](https://github.com/DoodyShark)

[Firas Darwish](https://github.com/DoodyShark)

[Shubhi Upadhyay](https://github.com/shubhiupa19)

## Deployment Link

https://fizzbuzz-draw-5d5v2.ondigitalocean.app/

## Docker Container

Link to the container image for the custom subsystem: [https://hub.docker.com/r/doodyshark/se-project-5](https://hub.docker.com/r/doodyshark/se-project-5)

## Getting Started

Follow these instructions to run a copy of the project on your local machine.

### Running the Project

1. **Clone the Repository**
   ```bash
   git clone https://github.com/software-students-spring2024/5-final-project-spring-2024-team-fizzbuzz-final.git

   cd 5-final-project-spring-2024-team-fizzbuzz-final
   ```
   
2.  **Create a .env file in the root of the directory with the following contents**
   ```bash
   MONGODB_USER=your_mongodb_user
   MONGODB_PASSWORD=your_mongodb_password
   MONGODB_HOST=your_mongodb_host
   MONGODB_NAME=your_database_name
   MONGODB_AUTHSOURCE=admin
   MONGODB_PORT=27017
   WEBAPP_FLASK_SECRET_KEY=your_secret_key
   WEBAPP_FLASK_PORT=5000
   WEBAPP_FLASK_ENV = development
   WEBAPP_FLASK_APP = app.py
   ```

3. **Running with Docker**
   To run the project, use
   ```bash
   docker-compose up --build
   ```

