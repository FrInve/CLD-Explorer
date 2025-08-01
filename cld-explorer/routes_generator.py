import os
import mysql.connector
from graphviz import Digraph
from datetime import datetime
from db_config import db_config

#funzione per generare i grafici delle route in base ai filtri
def generate_route_graphs(table_name, grafo, route_length="No Filter", route_type="No Filter", start_node=None, end_node=None, carousel_type="main"):
#     db_config = {
#         'host': 'mysql',
#         'user': 'app',
#         'password': '3utoeZVN!',
#         'database': 'cld'
#     }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        #query di base
        query_routes = f"SELECT r.route, r.state FROM {table_name} as r WHERE r.start_node = '{start_node}' AND r.end_node = '{end_node}'"

        #aggiunge un filtro per la lunghezza della route
        if route_length != "No Filter":
            query_routes += f" AND r.route_length = {route_length}"

        #aggiunge un filtro per la lunghezza della route
        if route_type != "No Filter":
            query_routes += f" AND r.state = '{route_type}'"

        #execute query
        cursor.execute(query_routes)
        results_routes = cursor.fetchall()
        
        #prende la posizione dei nodi
        query_positions = f"SELECT node_name, pos_x, pos_y FROM nodes_{table_name.split('_', 1)[1]}"
        cursor.execute(query_positions)
        node_positions = {name: (pos_x, pos_y) for name, pos_x, pos_y in cursor.fetchall()}

        #prendi i tipi di relazion
        query_relations = f"SELECT relationshipID, type, delay FROM {grafo}"
        cursor.execute(query_relations)
        relation_types = {rid: (rtype, delay) for rid, rtype, delay in cursor.fetchall()}

    finally:
        cursor.close()
        conn.close()
        #pass

    print(f"Generating graphs for {carousel_type} carousel")

    #creazione di una directory specifica per le foto del carosello
    output_dir = os.path.join('output', carousel_type)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #genera i grafici dai risultati della query
    generated_files = generate_graphs_from_results(results_routes, node_positions, relation_types, carousel_type=carousel_type)
    return generated_files


#funzione per generare i grafici dai risultati e dalle posizioni dei nodi
def generate_graphs_from_results(results_routes, node_positions, relation_types, highlight_node=None, carousel_type="main"):
    output_dir = os.path.join('output', carousel_type)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generated_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for idx, (route, state) in enumerate(results_routes, start=1):
        nodes_and_edges = route.split(', ')
        nodes = [item for item in nodes_and_edges if not item.isdigit()]
        edges_ids = [int(item) for item in nodes_and_edges if item.isdigit()]

        #crea le relazioni solo tra i nodi consecutivi, senza collegare l'ultimo al primo
        edges = [(nodes[i], nodes[i + 1], edges_ids[i]) for i in range(len(nodes) - 1)]

        dot = Digraph(comment=f'Routes Graph {idx}')
        
        #dimensione complessiva dell'immagine bianca
        dot.attr(size="14,14!", ratio="fill", margin="0.2", pad="1")  

        #dimensioni dei nodi e del testo
        dot.attr('node', fontsize='24', width='1.5', height='1.5', fixedsize='false', shape='oval')  
        dot.attr('edge', fontsize='18')  #testo sugli archi 

        #stato della route in basso e centrato
        dot.attr(label=f'State: {state}', fontsize='30', labelloc='b', labeljust='c', splines='true', overlap='false')

        for node in nodes:
            if node in node_positions:
                pos_x, pos_y = node_positions[node]
                if node == highlight_node:
                    dot.node(node, pos=f"{pos_x},{pos_y}!", style='filled', color='black', fillcolor='lightblue')
                else:
                    dot.node(node, pos=f"{pos_x},{pos_y}!")

        for start_node, end_node, relation_id in edges:
            relation_type, delay = relation_types.get(relation_id, ('CONC_CHANGE', 'no'))
            edge_color = 'black'
            edge_label = ''
            if delay == 'yes':
                edge_color = 'red'
                edge_label = 'Delay'

            if relation_type == 'CONC_CHANGE':
                dot.edge(start_node, end_node, style='solid', color=edge_color, label=edge_label)
            elif relation_type == 'DISC_CHANGE':
                dot.edge(start_node, end_node, style='dashed', color=edge_color, label=edge_label)

        file_name = f'{output_dir}/route_graph_{idx}_{state}_{len(nodes)}nodes_{timestamp}'
        dot.save(f'{file_name}.dot')
        dot.render(file_name, format='svg')
        generated_files.append(f'{file_name}.svg')

    return generated_files

