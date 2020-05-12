import redis
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687/', auth=('neo4j', 'test'))

BASE_URL = "https://scholar.google.com"
COATHOURS_URL = BASE_URL + "/citations?view_op=list_colleagues&hl=it&json=&user={}#t=gsc_cod_lc"

r = redis.Redis(host="localhost", port=6379, db=0)

def add_coauthorship(tx, id_1, id_2, name, affiliation):
    query_string = """MERGE(a:Person {google_id: $id_1})-[:COAUTHOR]->(b:Person {google_id: $id_2, name: $name, affiliation: $affiliation})"""
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
            list_name_id.append((name,id_coauthors))
            
            session.write_transaction(add_coauthorship, id_, id_coauthors, name, affiliation)

            if not r.get(id_):
                r.zadd('queue', {id_coauthors: max(1, value - 1)})

    r.set(id_, True)
    r.expire(id_, 2592000)


while True:
  id_, value = r.bzpopmax('queue', 5) # Blocking Extraction of Max Value from queue (program blocks for 5 seconds if the queue is empty)
  if not r.get(id_):
    extract_coauthors(id_, value)