from neo4j import GraphDatabase
from .aragog import search
import redis
import logging
import json

# connect to neo4j
to_db = GraphDatabase.driver('bolt://neo:7687/', auth=('neo4j', 'test'))
r = redis.Redis(host='redis', port=6379, db=0)


def calculate_coauthor_graph(id_, is_google_id):
    logging.info(f"SHERLOCK: ID: {id_}")
    logging.info(f"SHERLOCK: ID: {type(id_)}")
    # the query differs if it is a person with google ID or only with node ID
    if is_google_id:
        logging.info("GID")
        query_string = """MATCH (a:Person {google_id: $id}) 
                    WITH a 
                    MATCH path=(a)-[:COAUTHOR*0..5]-(b:Person) 
                    WITH b, path 
                    ORDER BY LENGTH(path) ASC 
                    RETURN b, HEAD(COLLECT(path)) AS path, LENGTH(path) AS distance  
                    ORDER BY distance ASC"""
        query_string_papers = """MATCH (a:Person {google_id: $id}) 
                    WITH a 
                    MATCH path=(a)-[:AUTHOR*0..10]-(b:Person) 
                    WITH b, path 
                    ORDER BY LENGTH(path) ASC 
                    RETURN b, HEAD(COLLECT(path)) AS path, LENGTH(path) AS distance  
                    ORDER BY distance ASC"""
    else:
        id_ = int(id_)
        logging.info("NOT GID")
        query_string = """MATCH (a:Person) WHERE ID(a)=$id 
                    WITH a 
                    MATCH path=(a)-[:COAUTHOR*0..5]-(b:Person) 
                    WITH b, path 
                    ORDER BY LENGTH(path) ASC 
                    RETURN b, HEAD(COLLECT(path)) AS path, LENGTH(path) AS distance  
                    ORDER BY distance ASC"""
        query_string_papers = """MATCH (a:Person) WHERE ID(a)=$id 
                    WITH a 
                    MATCH path=(a)-[:AUTHOR*0..10]-(b:Person) 
                    WITH b, path 
                    ORDER BY LENGTH(path) ASC 
                    RETURN b, HEAD(COLLECT(path)) AS path, LENGTH(path) AS distance  
                    ORDER BY distance ASC"""

    with to_db.session() as session:
        results = session.run(query_string, id=id_)
        results_paper = session.run(query_string_papers, id=id_)
        
        # extract relevant information from direct coauthorship relations
        end_nodes = []
        end_nodes_ids = []
        for record in results:
            end_node_id = record["path"].end_node.id
            if not end_node_id in end_nodes_ids:
                end_nodes_ids.append(end_node_id)
                end_node_name = record["path"].end_node["name"]
                affiliation = record["path"].end_node["affiliation"]
                distance = record["distance"]
                path = [x.id for x in record["path"].nodes]
                end_nodes.append((end_node_id, end_node_name, distance, path, affiliation))

        # extract relevant information from relations derived from papers
        end_nodes_publications = []
        end_nodes_publications_ids = []
        for record in results_paper:
            end_node_id = record["path"].end_node.id
            if not end_node_id in end_nodes_publications_ids:
                end_nodes_publications_ids.append(end_node_id)
                end_node_name = record["path"].end_node["name"]
                distance = record["distance"]/2
                affiliation = record["path"].end_node["affiliation"]
                path = [x.id for x in record["path"].nodes]
                path = path[::2]
                end_nodes_publications.append((end_node_id, end_node_name, distance, path, affiliation))
        
        # merge the two lists
        end_nodes.extend(end_nodes_publications)

        # sort by distance
        end_nodes.sort(key=lambda x: x[2])
        graph = []
        already_seen_nodes = []
        for node in end_nodes:
            if not node[0] in already_seen_nodes:
                tmp = {
                    "end_node_id": node[0],
                    "end_node_name": node[1],
                    "distance": node[2],
                    "path": node[3],
                    "affiliation": node[4]
                }
                graph.append(tmp)
                already_seen_nodes.append(node[0])
        logging.info("SHERLOCK: saving graph on redis")
        r.set("{}.graph".format(id_), json.dumps(graph))
        r.expire("{}.graph".format(id_), 1209600)
        return graph


def exists_author(tx, google_id, node_id, name):
    # google id and node id behaves differently
    # for g_id, it is needed to check its existence
    if google_id is not None:
        exists = r.exists(google_id)
        logging.info("SHERLOCK: number of profiles in DB: {}".format(exists))

        # we have not short-term analyzed the person, enqueue with max priority
        if not exists:
            logging.info(f"SHERLOCK: enqueuing {google_id} for stc")
            logging.info(f"SHERLOCK: enqueuing {name} for ltc")
            r.zadd('queue', {google_id: 5})
            key = json.dumps([name, "no_paper"])
            r.zadd('ltc', {key: 5})
            return {"status_code": 202, "data": []}
        else:
            # check if we have a cached version of the graph
            coauthor_graph = r.get("{}.graph".format(google_id))
            if coauthor_graph == None:
                logging.info("SHERLOCK: calculating graph")
                return {"status_code": 200, "data": calculate_coauthor_graph(google_id, True)}
            else:
                logging.info("SHERLOCK: graph found on redis")
                return {"status_code": 200, "data": json.loads(coauthor_graph)}
    else:
        coauthor_graph = r.get("{}.graph".format(node_id))
        if coauthor_graph == None:
            print("SHERLOCK: calculating graph")
            logging.info("SHERLOCK: calculating graph")
            return {"status_code": 200, "data": calculate_coauthor_graph(node_id, False)}
        else:
            logging.info("SHERLOCK: graph found on redis")
            return {"status_code": 200, "data": json.loads(coauthor_graph)}


def search_author(name):
    return search(name)

def search_author_by_id(author_id, node_id, name):
    logging.info(author_id)
    logging.info(node_id)
    with to_db.session() as session:
        # check the existance of the author
        result = session.read_transaction(exists_author, author_id, node_id, name)
        return result
