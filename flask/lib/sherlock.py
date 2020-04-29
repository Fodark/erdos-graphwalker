from neo4j import GraphDatabase
from aragog import search

#connect to neo4j
to_db = GraphDatabase.driver('bolt://localhost:7687/',auth=('neo4j','test'))

def exists_author(tx, name):
    profiles = tx.run("MATCH (a:Person{name:$name})return a.name as name", name=name)
    
    profiles = [p['name']for p in profiles] 

    if len(profiles)>1:
        #pensareeeeee
        pass 
    elif len(profiles)==0: 
        search(name) #return an array of tuples with coauthors 

    else:
        return profiles[0]




def search_author(name):
#query 
    with to_db.session() as session:
        person_name = session.read_transaction(exists_author, name)
    
    return [person_name]




