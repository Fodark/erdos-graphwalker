from neo4j import GraphDatabase
from .aragog import search
import redis
import logging

# connect to neo4j
to_db = GraphDatabase.driver('bolt://localhost:7687/', auth=('neo4j', 'test'))
r = redis.Redis(host='172.18.0.2', port=6379, db=0)


def calculate_coauthor_graph(id_):
    query_string = """MATCH (a:Person {google_id: $google_id}) 
                    WITH a 
                    MATCH path=(a)-[:COAUTHOR*1..5]-(b:Person) 
                    WITH b, path 
                    ORDER BY LENGTH(path) ASC 
                    RETURN b, HEAD(COLLECT(path)) AS path, LENGTH(path) AS distance  
                    ORDER BY distance ASC"""
    with to_db.session() as session:
        results = session.run(query_string, google_id=id_)
        graph = []
        for record in results:
            end_node = record["path"].end_node["name"]
            distance = record["distance"]
            path = [x["name"] for x in record["path"].nodes]
            graph.append((end_node, path, distance))
        logging.debug("SHERLOCK: saving graph on redis")
        r.set("{}.graph".format(id_), graph)
        r.expire("{}.graph".format(id_), 1209600)
        return graph


def exists_author(tx, name):
    profiles = tx.run(
        "MATCH (a:Person{name:$name}) return a.name as name, a.google_id as google_id, a.affiliation as affiliation", name=name)

    profiles = [(p['name'], p['google_id'], p['affiliation'])
                for p in profiles]

    logging.debug("SHERLOCK: number of profiles in DB: {}".format(len(profiles)))

    if len(profiles) > 1:
        return profiles
    elif len(profiles) == 0:
        return search(name)  # return an array of tuples with coauthors
    else:
        coauthor_graph = r.get("{}.graph".format(profiles[0][1]))
        #logging.debug("SHERLOCK: author in db, redis available? {}".format(coauthor_graph != None))
        if coauthor_graph == None:
            logging.debug("SHERLOCK: calculating graph")
            return calculate_coauthor_graph(profiles[0][1])
        else:
            logging.debug("SHERLOCK: graph found on redis")
            return coauthor_graph


def search_author(name):
    # query
    with to_db.session() as session:
        person_name = session.read_transaction(exists_author, name)

    return [person_name]
