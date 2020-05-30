import requests
from bs4 import BeautifulSoup
from urllib.parse import quote 
import redis
from neo4j import GraphDatabase
import logging

driver = GraphDatabase.driver('bolt://neo:7687/', auth=('neo4j', 'test'))
r = redis.Redis(host="redis", port=6379, db=0)

BASE_URL = "https://scholar.google.com"
SEARCH_AUTHOR_URL = BASE_URL + "/scholar?hl=it&as_sdt=0%2C5&q={}&btnG="
AUTHORS_PAGE_URL = BASE_URL + "/citations?view_op=search_authors&mauthors={}&hl=it&oi=ao"
COATHOURS_URL = BASE_URL + "/citations?view_op=list_colleagues&hl=it&json=&user={}#t=gsc_cod_lc"

def add_node(tx, id_, name, affiliation):
    query_string = """MERGE (a:Person {google_id: $google_id, name: $name, affiliation: $affiliation})"""
    tx.run(query_string, google_id=id_, name=name, affiliation=affiliation)

def get_nodes_by_name(tx, name):
    query_string = """MATCH(p:Person {name: $name}) where not exists (p.google_id) return ID(p), p"""
    return tx.run(query_string, name=name)

def search(q):
    # convert spaces to %20
    quoted_query = quote(q)
    page_elenco_profili = requests.get(AUTHORS_PAGE_URL.format(quoted_query))
    soup_elenco_profili = BeautifulSoup(page_elenco_profili.content, 'html.parser')
    # extract the profiles in the page
    soup_profili = soup_elenco_profili.find_all('h3', class_="gs_ai_name")

    logging.info("ARAGOG: profiles found on GScholar: {}".format(len(soup_profili)))

    # check if there are any person matching the name but without google ID
    neo_data = []
    with driver.session() as session:
        db_results = session.read_transaction(get_nodes_by_name, q)
        for node in db_results:
            user = {"node_id": node["p"].id, "name": node["p"]["name"]}
            neo_data.append(user)

    # no data neither on GScholar and the DB, return 404
    if len(soup_profili) == 0 and len(neo_data) == 0:
        return {"status_code": 404, "data": [], "neo_data": []}
    else:
        logging.info("ARAGOG: users found")
        data = []
        with driver.session() as session:
            for pr in soup_profili:
                google_id = pr.a['href'].split('user=')[1]
                name = pr.a.text
                affiliation = pr.findNext('div').string
                if affiliation == None:
                    affiliation = "No affiliation"
                user = {"google_id": google_id, "name": name, "affiliation": affiliation}
                data.append(user)
                session.write_transaction(add_node, google_id, name, affiliation)
        # return differentiated data for GScholar and DB users
        return {"status_code": 200, "data": data, "neo_data": neo_data}
