Big Data Final Project:
A flask application that is used for several movie services like submitting reviews for movies & getting custom recommendations based on these reviews.

Project component: 
- Docker containers
-Configuration files
-App code
-Html code

Docker is used to run four containers :
- Zookeeper (running)
- Kafka (running)
- redis (running)
- python app (work in progress)

Brief overview:
-docker-compose.yml: sets up the multi-service enviroment (the four containers) and connects each container with a bridge network
-Dockerfile: creates a docker image for our flask application (app.py)
-requirements.txt: contains the libraries and versions required for the app
-app.py : flask app that interacts with mongoDB , redis , kafka , handles movie recommendations and ratings
-redis_caching.py: handles the redis logic for checking cache and generating recommendations if empty
-recommendation_engine: spark ml model trained and generates (by default 5) movie recommendations based on ratings and info
-index.html: displays the movie information , ratings (pop up for succesful submission) and on call recommendations
-login.html: basic login page via user_id

Steps in terminal:
- Docker-compose up --build
- venv\Scripts\activate
- flask run
- webbrowser: http://127.0.0.1:5000/login
