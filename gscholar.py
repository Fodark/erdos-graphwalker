import requests
from bs4 import BeautifulSoup

page = requests.get("https://scholar.google.com/scholar?hl=it&as_sdt=0%2C5&q=ivano+bison&btnG=")

soup = BeautifulSoup(page.content, 'html.parser')

profili_utente_per = soup.find_all('h3', class_="gs_rt")


page_elenco_profili = requests.get('https://scholar.google.com'+profili_utente_per[0].a['href'])

soup_elenco_profili = BeautifulSoup(page_elenco_profili.content, 'html.parser')

soup_profili = soup_elenco_profili.find_all('h3', class_="gs_ai_name")

quasi_id = soup_profili[0].a['href']
id_ = quasi_id.split('user=')[1]


page_coauthors = requests.get("https://scholar.google.com/citations?view_op=list_colleagues&hl=it&json=&user={}#t=gsc_cod_lc".format(id_))

soup_elenco_coauthors = BeautifulSoup(page_coauthors.content, 'html.parser')

soup_profili_coauthors = soup_elenco_coauthors.find_all('h3', class_="gs_ai_name")



list_name_id = []

for el in soup_profili_coauthors:
    id_coauthors = el.a['href'].split('user=')[1]
    name = el.a.string
    list_name_id.append((name,id_coauthors))
    print("id: ",id_coauthors,"name: ",name)
    
list_name_id


