# BDT Project

### Structure

- `client` contains the frontend in React
- `flask` contains the API written in Python with Flask
- `neo4j` contains Neo4j data


### How to start

#### Neo4j
- `docker-compose build neo` created Neo4j docker image, run **only the first time**
- `docker-compose run neo` starts Neo4j container, and makes DB accessible

#### Flask
- `cd flask`
- `pip install requirements.txt` installs Python packages
- `python flask/app.py` starts Python API

#### React
- `cd client`
- `npm install` installs required packages
- `npm start` starts the application
