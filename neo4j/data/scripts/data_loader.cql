WITH "https://raw.githubusercontent.com/neo4j-graph-analytics/book/master/data/transport-nodes.csv" AS uri
LOAD CSV WITH HEADERS FROM uri AS row
MERGE (place:Place {id:row.id})
SET place.latitude = toFloat(row.latitude),
	place.longitude = toFloat(row.longitude),
	place.population = toInteger(row.population);
