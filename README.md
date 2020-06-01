# BDT Project

### Structure

- `client` contains the frontend in React, there are three pages
  - `homepage` which allows to enter the desired author
  - `search` which displays the found authors, both on Google Scholar and on our database
  - `author`, which displays the graph and lists the coauthors and their distances
- `flask` contains the API written in Python with Flask
  - `app.py` contains the entrypoint of the Flask application
  - `aragog.py` contains the Google Scholar crawler, it gets the list of matching authors
  - `sherlock` contains the logic for neo4j, calculating the graph and determining the response
- `stc` (Short-Term Consumer) analyzes only the publicly available coauthor list, to provide a fast answer to the user
- `ltc` (Long-Term Consumer), based on Selenium, scrapes paper by paper and extract every coauthor of aperson
- `neo4j` contains Neo4j data


### How to start

It can be started service by service or, alternatively, there are two docker-compose files that help doing that

`docker-compose.yml` builds the images locally with the source of the repo

`docker-compose-production.yml` pulls the images from Gitlab Container Registry, so it is updated to the latest commit that triggered the build

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
