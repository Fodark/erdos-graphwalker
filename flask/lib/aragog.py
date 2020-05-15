import requests
from bs4 import BeautifulSoup
from urllib.parse import quote 
import redis
from neo4j import GraphDatabase
import logging

driver = GraphDatabase.driver('bolt://localhost:7687/', auth=('neo4j', 'test'))
r = redis.Redis(host="172.18.0.2", port=6379, db=0)

BASE_URL = "https://scholar.google.com"
SEARCH_AUTHOR_URL = BASE_URL + "/scholar?hl=it&as_sdt=0%2C5&q={}&btnG="
COATHOURS_URL = BASE_URL + "/citations?view_op=list_colleagues&hl=it&json=&user={}#t=gsc_cod_lc"

def add_node(tx, id_, name, affiliation):
    query_string = """MERGE (a:Person {google_id: $google_id, name: $name, affiliation: $affiliation})"""
    tx.run(query_string, google_id=id_, name=name, affiliation=affiliation)

def search(q):
    # convert spaces to %20
    q = quote(q)
    page = requests.get(SEARCH_AUTHOR_URL.format(q))
    soup = BeautifulSoup(page.content, 'html.parser')
    profili_utente_per = soup.find_all('h3', class_="gs_rt")
    # extract profiles page matching the given query
    page_elenco_profili = requests.get(BASE_URL + profili_utente_per[0].a['href'])
    soup_elenco_profili = BeautifulSoup(page_elenco_profili.content, 'html.parser')
    # extract the profiles in the page
    soup_profili = soup_elenco_profili.find_all('h3', class_="gs_ai_name")

    logging.debug("ARAGOG: profiles found: {}".format(len(soup_profili)))

    if len(soup_profili) == 1:
        quasi_id = soup_profili[0].a['href']
        id_ = quasi_id.split('user=')[1]
        name = soup_profili[0].a.text
        affiliation = soup_profili[0].findNext('div').string
        r.zadd('queue', {id_: 5})
        logging.debug("ARAGOG: enqueuing: {} {}".format(id_, name))

        with driver.session() as session:
            session.write_transaction(add_node, id_, name, affiliation)
            
        return {"status_code": 202} # da definire
    elif len(soup_profili) == 0:
        return {"status_code": 404}
    else:
        logging.debug("ARAGOG: multiple users found")
        return {"status_code": 200, "data": [(pr.a['href'].split('user=')[1], pr.a.text, pr.findNext('div').string) for pr in soup_profili]}
