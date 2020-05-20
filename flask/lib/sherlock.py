from neo4j import GraphDatabase
from .aragog import search
import redis
import logging
import json

# connect to neo4j
to_db = GraphDatabase.driver('bolt://neo:7687/', auth=('neo4j', 'test'))
r = redis.Redis(host='redis', port=6379, db=0)


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
        logging.info("SHERLOCK: saving graph on redis")
        r.set("{}.graph".format(id_), json.dumps(graph))
        r.expire("{}.graph".format(id_), 1209600)
        return graph


def exists_author(tx, id_):
    #profiles = tx.run(
    #    "MATCH (a:Person{google_id:$google_id}) return a.name as name, a.google_id as google_id, a.affiliation as affiliation", google_id=id_)

    #profiles = [(p['name'], p['google_id'], p['affiliation'])
    #            for p in profiles]
    exists = r.exists(id_)
    logging.info("SHERLOCK: number of profiles in DB: {}".format(exists))

    if exists == None:
        r.zadd('queue', {id_: 5})
        return {"status_code": 202}
    else:
        coauthor_graph = r.get("{}.graph".format(id_))
        #logging.info("SHERLOCK: author in db, redis available? {}".format(coauthor_graph != None))
        if coauthor_graph == None:
            logging.info("SHERLOCK: calculating graph")
            return {"status_code": 200, "data": calculate_coauthor_graph(id_)}
        else:
            logging.info("SHERLOCK: graph found on redis")
            return {"status_code": 200, "data": json.loads(coauthor_graph)}


def search_author(name):
    # query
    return search(name)
    #with to_db.session() as session:
    #    person_name = session.read_transaction(exists_author, name)
#
    #return [person_name]

def search_author_by_id(author_id):
    with to_db.session() as session:
        result = session.read_transaction(exists_author, author_id)
        return result
