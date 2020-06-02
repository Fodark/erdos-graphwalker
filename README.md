# Erdos Graphwalker - BDT Project
 
The project provides a set of API to retrieve the coauthorship graph of a given author and builds the equivalent of the Erdos distance for the person requested.
The system, from the first requests, keeps collecting every coauthor in a recursive manner in two parallel ways, through the direct coauthors defined by the person itself on GScholar and from analyzing the publications and extracting every coauthor.

A live version can be found at: http://104.155.115.87/, precomputed graphs can be found for:
- Daniele Miorandi
- Ivano Bison
- Alberto Montresor

### Structure
 
The project is organized in 6 dockerized microservices in the following folders (Redis is not listed as it does not need any particular configuration), every folder contains at least one Dockerfile.
 
- `client` contains the frontend in React, composed by three pages
 - `homepage (SearchPage)` which allows to enter the desired author
 - `search (ListResults)` which displays the found authors, both on Google Scholar and on our database
 - `author (DisplayResults)`, which displays the graph and lists the coauthors and their distances
- `flask` contains the API written in Python with Flask
 - `app.py` contains the entrypoint of the Flask application and the endpoints of the application
   - `/search?name=name` allows to search for a person, the system will check against Google Scholar and Neo4j
   - `/author?id=id&node_id=node_id` allows to retrieve the graph, `id` refers to the Google ID of the person while `node_id` refers to the node ID on Neo4j, the first one overrides the second.
 - `aragog.py` contains the Google Scholar crawler, it gets the list of matching authors, it uses `Requests` and `BeautifulSoup` to scrape the search page on Google Scholar
 - `sherlock` contains the logic for neo4j, calculating the graph and determining the response.
 If the author is not present in the system, it is enqueued to be analyzed on Redis with the maximum priority, so the two consumers will analyze him/her as soon as possible. The graph calculation merges information coming both from direct coauthorship and publications coauthorship, obviously taking the shortest one in case of multiple paths.
- `stc` (Short-Term Consumer) analyzes only the publicly available coauthor list, to provide a fast answer to the user. By knowing the Google ID of a person, the coauthors page can be accessed directly and data can be scraped with `BeautifulSoup`. Priority of the analysis is determined on queues on Redis, and every coauthor of the person in enqueued again with less priority, so to foster new requests incoming.
- `ltc` (Long-Term Consumer), based on Selenium, scrapes paper by paper and extract every coauthor of a person. As `stc` it uses Redis priority queues to extract the most relevant person to analyze, and enqueues back with lower priority every coauthor. It simulates the human activity of clicking in order to avoid automated blocking by Google.
- `neo4j` contains Neo4j data and configuration, at the moment it is configured for a GCP instance with 64GB of RAM, for local execution `conf/neo4j.conf` should be updated accordingly to your machine.
 
### CI
 
Alongside the code there is `.gitlab-ci.yml`, which setups a Continous Integration environment on GitLab that builds the images of the services and pushes them onto the GitLab Container Registry
 
### How to start
 
It can be started service by service or, alternatively, there are two docker-compose files that help doing that.
 
`docker-compose-build.yml` builds the images locally with the source contained in the repo.
 
`docker-compose.yml` pulls the images from Gitlab Container Registry, so it is updated to the latest commit that triggered the build.
 
The second one is the easier way and can be achieved with
`docker-compose up`
 
### FAQs
 
#### Won’t Google ban me?
We accurately designed the system to elude Google, `stc` requests are delayed over time so to not bomb Google Scholar, while `ltc`, using Selenium, seems like a human to Google. We have run it for several hours on our machines and on the deployed version but we were not blocked.
 
#### Why there is the need for a first request?
Because we could not bulk download Google Scholar archive, so we need a starting point from which to start our analysis, from this the system will crawl endlessly.
 
#### How well does it perform?
If the number of vertices is below around 10000 the coauthorship graph can be built in a few seconds, higher number of nodes leads to higher computational time. From our tests, with > 30000 nodes calculating the coauthorship with distance at maximum 5 will take several minutes, since 5 hops can take to almost every other author, especially if publications were analyzed