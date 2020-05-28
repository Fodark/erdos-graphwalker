import redis
from neo4j import GraphDatabase
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logging.basicConfig(level=logging.INFO)

neo_driver = GraphDatabase.driver('bolt://neo:7687/', auth=('neo4j', 'test'))
r = redis.Redis(host="redis", port=6379, db=0)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--start-maximized")


def add_author_node(tx, name, affiliation, google_id):
  query = """MERGE(a:Person {name: $name, affiliation: $affiliation, google_id: $google_id})"""
  tx.run(query, name=name, affiliation=affiliation, google_id=google_id)


def add_authorship_relation(tx, google_id, name, paper_name):
  if google_id:
    query = """MERGE(p:Paper {title: $title}) WITH p MATCH(a:Person {google_id: $google_id}) MERGE(a)-[:AUTHOR]->(p)"""
    tx.run(query, title=paper_name, google_id=google_id)
  else:
    query = """MERGE(p:Paper {title: $title}) WITH p MERGE(a:Person {name: $name}) MERGE(a)-[:AUTHOR]->(p)"""
    tx.run(query, title=paper_name, name=name)


def analyze(author, paper):
  d = DesiredCapabilities.CHROME
  d['loggingPrefs'] = { 'performance':'ALL' }
  found = False
  driver = webdriver.Chrome(options=chrome_options)
  driver.set_window_size(960, 1080)
  driver.implicitly_wait(4)
  driver.get("https://scholar.google.com/")
  logging.info("LTC: loaded Gscholar")
  sleep(1)
  elem = driver.find_element_by_name("q")
  elem.clear()
  elem.send_keys(author)
  elem.send_keys(Keys.RETURN)
  logging.info("LTC: query sent")
  try:
    elem = driver.find_element_by_partial_link_text(author)
  except:
    logging.info("LTC: No gscholar with this name and paper")
    with neo_driver.session() as session:
      session.write_transaction(add_authorship_relation, None, author, paper)
    return
  elem.click()
  logging.info("LTC: entering profile page")
  sleep(1)
  profs = driver.find_elements_by_xpath("/html/body/div/div[8]/div[2]/div/div/div/div/h3/a")
  n_profs = len(profs)
  logging.info(f"LTC: profs found: {n_profs}")
  for i in range(n_profs):
    driver.delete_all_cookies()
    em = profs[i]
    em.click()
    sleep(.5)
    logging.info(driver.current_url)
    google_id = driver.current_url.split('&user=')[1]
    name = driver.find_element_by_id('gsc_prf_in').text
    affiliation = driver.find_element_by_class_name('gsc_prf_il').text
    bb = driver.find_element_by_id("gsc_bpf_more")
    while not bb.get_attribute('disabled'):
      bb.click()
      bb = driver.find_element_by_id("gsc_bpf_more")
    sleep(1)
    publications = driver.find_elements_by_xpath("//*[@id=\"gsc_a_b\"]/tr/td[1]/a")
    publications_titles = [e.text for e in publications]
    
    if r.get('{}.papers.analyzed'.format(google_id)):
      logging.info("LTC: author already analyzed {} {}".format(google_id, name))
      if paper in publications_titles:
        found = True
        break
      else:
        continue

    if not paper in publications_titles:
      logging.info("This author hasn't the publication {}".format(google_id))
      continue
    else:
      found = True
      n_pubs = len(publications_titles)
      logging.info("LTC: adding author node {}: {}".format(google_id, name))
      with neo_driver.session() as session:
        session.write_transaction(add_author_node, name, affiliation, google_id)
        for idx, emm in enumerate(publications):
          sleep(.5)
          driver.execute_script("arguments[0].click();", emm)
          title_div = driver.find_element_by_id('gsc_vcd_title')
          title = title_div.text
          author_div = driver.find_element_by_class_name('gsc_vcd_value')
          authors = author_div.text.split(', ')
          logging.info(f"{idx + 1}/{n_pubs} {title}\n\t{authors}")
          session.write_transaction(add_authorship_relation, google_id, name, title)
          for au in authors:
            if au != author:
              logging.info("\t\tLTC: adding author to analyze {} {}".format(au, title))
              r.rpush('lts', au, title)
          sleep(1)
          close_button = driver.find_element_by_id('gs_md_cita-d-x')
          close_button.click()
            # driver.back() 
      
      r.set('{}.papers.analyzed'.format(google_id), 1)
      break
    sleep(2)
    driver.back()
    profs = driver.find_elements_by_xpath("/html/body/div/div[8]/div[2]/div/div/div/div/h3/a")

  if not found:
    logging.info("LTC: No gscholar with this name and paper")
    with neo_driver.session() as session:
      session.write_transaction(add_authorship_relation, None, author, paper)

  driver.close()


while True:
  try:
    [author, paper] = r.lrange("lts", 0, 1)
    r.ltrim('lts', 2, -1)
    author = author.decode('UTF-8') if not isinstance(author, str) else author
    paper = paper.decode('UTF-8') if not isinstance(paper, str) else paper
    logging.info("LTC: analyzing {} {}".format(author, paper))
    analyze(author, paper)
    # logging.info('Taking a break, otherwise google gets mad')
    #sleep(180)
  except Exception as e:
    logging.info(e)
    sleep(3)