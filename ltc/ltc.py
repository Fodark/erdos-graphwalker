import redis
from neo4j import GraphDatabase
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json

logging.basicConfig(level=logging.INFO)

neo_driver = GraphDatabase.driver('bolt://neo:7687/', auth=('neo4j', 'test'))
r = redis.Redis(host="redis", port=6379, db=0)

BASE_URL = "https://scholar.google.com"
AUTHORS_PAGE_URL = BASE_URL + "/citations?view_op=search_authors&mauthors={}&hl=it&oi=ao"

# initialize selenium options to run chrome in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


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


def analyze(author, paper, value):
  # open a new chrome instance
  driver = webdriver.Chrome(options=chrome_options)
  driver.set_window_size(960, 1080)
  driver.implicitly_wait(4)
  # connect to gscholar
  #driver.get("https://scholar.google.com/")
  #sleep(1)
  # find the text field in the page
  #elem = driver.find_element_by_name("q")
  #elem.clear()
  # send the author name
  #elem.send_keys(author)
  #elem.send_keys(Keys.RETURN)
  #logging.info("LTC: query sent")
  # try to find the "profiles for" link in the page, if none it means no author with that name exist on gscholar
  #try:
  #  element_present = EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, author))
  #  WebDriverWait(driver, 5).until(element_present)
  #  elem = driver.find_element_by_partial_link_text(author)
  #except Exception as e:
  #  logging.info(e)
  #  logging.info("LTC: No gscholars")
  #  with neo_driver.session() as session:
  #    session.write_transaction(add_authorship_relation, None, author, paper)
  #  return
  
  #elem.click()
  logging.info("LTC: entering profile page")
  #sleep(1)
  driver.get(AUTHORS_PAGE_URL.format(author))
  # extract the profiles links
  profiles = driver.find_elements_by_xpath("/html/body/div/div[8]/div[2]/div/div/div/div/h3/a")
  n_profiles = len(profiles)
  logging.info(f"LTC: profiles found: {n_profiles}")

  # iterate over every profile
  found = False
  for i in range(n_profiles):
    driver.delete_all_cookies()
    em = profiles[i]
    # enter the profile page
    em.click()
    sleep(1)
    # extract the information needed, id, name, affiliation
    google_id = driver.current_url.split('&user=')[1]
    name = driver.find_element_by_id('gsc_prf_in').text
    affiliation = driver.find_element_by_class_name('gsc_prf_il').text
    # click the "show more" button until it is possibile
    more_papers_button = driver.find_element_by_id("gsc_bpf_more")
    while not more_papers_button.get_attribute('disabled'):
      more_papers_button.click()
      more_papers_button = driver.find_element_by_id("gsc_bpf_more")
      sleep(.5)
    sleep(1)
    # extract the publications links and titles
    publications = driver.find_elements_by_xpath("//*[@id=\"gsc_a_b\"]/tr/td[1]/a")
    publications_titles = [e.text for e in publications]

    # check if the author has the required publication
    # if not, skip him/her
    if paper != "no_paper" and not paper in publications_titles:
      logging.info("{} does not have the publication".format(google_id))
      driver.back()
      profiles = driver.find_elements_by_xpath("/html/body/div/div[8]/div[2]/div/div/div/div/h3/a")
      continue
    
    # the author has that publication, did we already anlyze him/her?
    found = True
    if r.get('{}.papers.analyzed'.format(google_id)):
      logging.info("LTC: author already analyzed {} {}".format(google_id, name))
      break
    
    # not previously analyzed
    n_pubs = len(publications_titles)
    logging.info("LTC: adding author node {}: {}".format(google_id, name))
    with neo_driver.session() as session:
      session.write_transaction(add_author_node, name, affiliation, google_id)
      # iterate over every publication
      for idx, emm in enumerate(publications):
        sleep(.5)
        # click the pub link
        driver.execute_script("arguments[0].click();", emm)
        # extract title and authors
        title_div = driver.find_element_by_id('gsc_vcd_title')
        title = title_div.text
        author_div = driver.find_element_by_class_name('gsc_vcd_value')
        authors = author_div.text.split(', ')
        logging.info(f"{idx + 1}/{n_pubs} {title}\n\t{authors}")
        # add the paper and connect it to the person
        session.write_transaction(add_authorship_relation, google_id, name, title)
        # enqueue every author except for the current one
        for au in authors:
          if au != author:
            logging.info("\t\tLTC: adding author to analyze {} {}".format(au, title))
            key = json.dumps([au, title])
            r.zadd('ltc', {key: max(1, value - 1)})
        sleep(1)
        # close the publication and go to the next one
        close_button = driver.find_element_by_id('gs_md_cita-d-x')
        close_button.click()
    
    r.set('{}.papers.analyzed'.format(google_id), 1)
    break

  # the cycle ended, was it because it was found or not?
  if not found:
    logging.info("LTC: No gscholar with this name and paper")
    with neo_driver.session() as session:
      session.write_transaction(add_authorship_relation, None, author, paper)

  # close chrome
  driver.close()


while True:
  try:
    # extract from the queue the pair (author, paper name)
    _, key, value = r.bzpopmax('ltc', 5)
    [author, paper] = json.loads(key)
    # redis stores bytes, convert them to string
    author = author.decode('UTF-8') if not isinstance(author, str) else author
    paper = paper.decode('UTF-8') if not isinstance(paper, str) else paper
    logging.info("LTC: analyzing {} {}".format(author, paper))
    # start analysis
    analyze(author, paper, value)
  except Exception as e:
    logging.info(e)
    # the queue was empty, wait and repeat
    sleep(3)