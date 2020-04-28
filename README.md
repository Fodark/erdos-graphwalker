# BDT Project

### Structure

- `client` contains the frontend in React
- `flask` contains the API written in Python with Flask
  - `app.py` contains the entrypoint of the Flask application
  - `aragog.py` contains the Google Scholar crawler
- `neo4j` contains Neo4j data


### How to start

#### Neo4j
- `docker-compose up neo` creates and runs neo4j container

#### Flask
- `cd flask`
- `pip install requirements.txt` installs Python packages
- `python app.py` starts Python API

#### React
- `cd client`
- `pnpm install` installs required packages
- `pnpm start` starts the application
