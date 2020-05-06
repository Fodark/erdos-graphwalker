import redis
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote 

BASE_URL = "https://scholar.google.com"
COATHOURS_URL = BASE_URL + "/citations?view_op=list_colleagues&hl=it&json=&user={}#t=gsc_cod_lc"

r = redis.Redis(host="localhost", port=6379, db=0)

def extract_coauthors(id_):
    # download the coauthors page
    page_coauthors = requests.get(COATHOURS_URL.format(id_))
    soup_elenco_coauthors = BeautifulSoup(page_coauthors.content, 'html.parser')
    soup_profili_coauthors = soup_elenco_coauthors.find_all('h3', class_="gs_ai_name")

    list_name_id = []

    # extract id and name for every coauthor
    for el in soup_profili_coauthors:
        id_coauthors = el.a['href'].split('user=')[1]
        name = el.a.string
        list_name_id.append((name,id_coauthors))
        # print("id: ",id_coauthors,"name: ",name)

    return list_name_id

while True:
  id_ = r.bzpopmax('queue')