import requests
from bs4 import BeautifulSoup
from urllib.parse import quote 


BASE_URL = "https://scholar.google.com"
SEARCH_AUTHOR_URL = BASE_URL + "/scholar?hl=it&as_sdt=0%2C5&q={}&btnG="
COATHOURS_URL = BASE_URL + "/citations?view_op=list_colleagues&hl=it&json=&user={}#t=gsc_cod_lc"


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

    if len(soup_profili) == 1:
        quasi_id = soup_profili[0].a['href']
        id_ = quasi_id.split('user=')[1]
        return extract_coauthors(id_)
    elif len(soup_profili) == 0:
        pass # no profiles with that name
    else:
        pass # many results, should ask the user
