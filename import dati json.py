import json
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"  
user = "neo4j"  
password = "3utoeZVN!"  
driver = GraphDatabase.driver(uri, auth=(user, password))

#funzione per creare nodi in Neo4j con il comando
def create_node(tx, label, numeric_id, id_custom, group, x, y):
    query = (
        f"CREATE ({id_custom}:{label}{{numeric_id:{numeric_id}, id_custom:'{id_custom}', group:'{group}', x:{x}, y:{y}}})"
    )
    tx.run(query)

#funzione per creare relazioni in Neo4j 
def create_relationship(tx, from_node, to_node, relation_type, numeric_id, delay):
    query = (
        f"MATCH (a {{id_custom:'{from_node}'}}), (b {{id_custom:'{to_node}'}}) "
        f"CREATE (a)-[:{relation_type}{{numeric_id:{numeric_id}, delay:'{delay}'}}]->(b)"
    )
    tx.run(query)

#path json file
json_file_path = r"C:\Users\danyl\Downloads\kumu-lauradanielamaftei-cld-fashion (1).json"

#carica il file json
with open(json_file_path) as f:
    data = json.load(f)

#inizializzazione  ID incrementali per nodi e relazioni
node_id_counter = 1
relationship_id_counter = 0

#estrazione elementi e rel dal file JSON
elements = data['elements']
maps = data['maps'][0]['elements']  #coordinate dei nodi
connections = data['connections']

#gruppo perché per ora neo4j ha bisogno per ora di una label per ogni cld
group = input("Inserire il gruppo del CLD: ")

#dizionario per tenere traccia degli id dei nodi creati
node_dict = {}

with driver.session() as session:
    #creazione dei nodi con coordinate
    for element in elements:
        elem_id = element['_id']
        label = element['attributes']['label']
        id_custom = label.lower().replace(" ", "_")
        
        #trova le coordinate dal JSON maps
        for map_elem in maps:
            if map_elem['element'] == elem_id:
                x = map_elem['position']['x']
                y = map_elem['position']['y']
                break
        
        #esegue il comando per creare il nodo in Neo4j
        session.write_transaction(create_node, id_custom.upper(), node_id_counter, id_custom, group, x, y)
        
        #salva il nodo creato nel dizionario
        node_dict[elem_id] = id_custom
        node_id_counter += 1

    #creazione delle relazioni
    for connection in connections:
        from_elem = connection['from']
        to_elem = connection['to']
        
        #verifica se la chiave 'connection type' esiste
        connection_type = connection['attributes'].get('connection type')
        
        if connection_type:
            #determina il tipo di relazione
            relation_type = "CONG_CHANGE" if connection_type == "+" else "DISC_CHANGE"
            
            #recupera gli id custom dei nodi dai dati
            from_node = node_dict[from_elem]
            to_node = node_dict[to_elem]
            
            #imposta il valore del delay su 'yes' se 'delayed' è true, altrimenti 'no'
            delay = 'yes' if connection.get('delayed') else 'no'
            
            #esegue il comando per creare la relazione in Neo4j
            session.write_transaction(create_relationship, from_node, to_node, relation_type, relationship_id_counter, delay)
            relationship_id_counter += 1

driver.close()
