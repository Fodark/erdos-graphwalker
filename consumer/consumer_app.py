import redis
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from neo4j import GraphDatabase
import time
import logging

logging.basicConfig(level=logging.DEBUG)

driver = GraphDatabase.driver('bolt://localhost:7687/', auth=('neo4j', 'test'))

BASE_URL = "https://scholar.google.com"
COATHOURS_URL = BASE_URL + "/citations?view_op=list_colleagues&hl=it&json=&user={}#t=gsc_cod_lc"

r = redis.Redis(host="172.18.0.3", port=6379, db=0)

def add_coauthorship(tx, id_1, id_2, name, affiliation):
    query_string = """MATCH(a:Person {google_id: $id_1}) MERGE(b:Person {google_id: $id_2, name: $name, affiliation: $affiliation}) MERGE(a)-[:COAUTHOR]->(b)"""
    logging.info("CONSUMER: adding relation between {} and {}".format(id_1, id_2))
    tx.run(query_string, id_1=id_1, id_2=id_2, name=name, affiliation=affiliation)

def extract_coauthors(id_, value):
    # download the coauthors page
    page_coauthors = requests.get(COATHOURS_URL.format(id_))
    soup_elenco_coauthors = BeautifulSoup(page_coauthors.content, 'html.parser')
    soup_profili_coauthors = soup_elenco_coauthors.find_all('h3', class_="gs_ai_name")

    list_name_id = []

    # extract id and name for every coauthor
    with driver.session() as session:
        for el in soup_profili_coauthors:
            id_coauthors = el.a['href'].split('user=')[1]
            name = el.a.string
            affiliation = el.findNext('div').string
            if affiliation == None:
                affiliation = "No affiliation"
            list_name_id.append((name,id_coauthors))
            
            session.write_transaction(add_coauthorship, id_, id_coauthors, name, affiliation)

            if not r.get(id_coauthors):
                logging.info("CONSUMER: enqueuing {}".format(id_coauthors))
                r.zadd('queue', {id_coauthors: max(1, value - 1)})

    r.set(id_, 1)
    r.expire(id_, 2592000)


while True:
    _, id_, value = r.bzpopmax('queue', 5) # Blocking Extraction of Max Value from queue (program blocks for 5 seconds if the queue is empty)
    # underscore significa che ignoriamo il primo valore restituito da redis (nome della coda)
    id_ = id_.decode('UTF-8') # passiamo da lista di bytes a stringa
    logging.info("CONSUMER: analyzing {} w/ priority {}".format(id_, value))
    if not r.get(id_):
      time.sleep(.5)
      extract_coauthors(id_, value)