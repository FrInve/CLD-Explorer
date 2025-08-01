import os
from db_config import get_connection
from graphviz import Digraph
from datetime import datetime

#funzione con le query per ottenere i risultati delle route
def generate_graphs(table_name, grafo, loop_type="No Filter", loop_length="No Filter", node_name="No Filter", carousel_type="main"):

    try:
        conn = get_connection()  # Usa la funzione centralizzata per ottenere la connessione
        cursor = conn.cursor()

        #query di base
        query_routes = f"SELECT l.loop_path, l.state FROM {table_name} as l WHERE 1=1"

        #applica il filtro del type
        if loop_type != "No Filter":
            query_routes += f" AND l.state = '{loop_type}'"

        #applica il filtro della lunghezza
        if loop_length != "No Filter":
            query_routes += f" AND l.loop_length = {loop_length}"

        #applica il filtro del nodo, che è l'unico che richiede il JOIN con la tabella bridge
        if node_name != "No Filter":
            query_routes += f"""
            AND l.loopID IN (
                SELECT loopID 
                FROM bridge_nodes_{table_name} 
                WHERE node_name = '{node_name}'
            )
            """

        #execute della query
        cursor.execute(query_routes)
        results_routes = cursor.fetchall()

        #prende la posizione dei nodi
        query_positions = f"SELECT node_name, pos_x, pos_y FROM nodes_{table_name.split('_', 1)[1]}"
        cursor.execute(query_positions)
        node_positions = {name: (pos_x, pos_y) for name, pos_x, pos_y in cursor.fetchall()}

        #prendi i tipi di relazione
        query_relations = f"SELECT relationshipID, type, delay FROM {grafo}"
        cursor.execute(query_relations)
        relation_types = {rid: (rtype, delay) for rid, rtype, delay in cursor.fetchall()}

    finally:
        cursor.close()
        conn.close()

    print(f"Generating graphs for {carousel_type} carousel")

    #creazione di una cartella specifica per le foto del carosello
    output_dir = os.path.join('output', carousel_type)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #genera i grafici dai risultati della query
    generated_files = generate_graphs_from_results(results_routes, node_positions, relation_types, carousel_type=carousel_type)
    return generated_files


def generate_graphs_from_results(results_routes, node_positions, relation_types, highlight_node=None, carousel_type="main"):
    
    output_dir = os.path.join('output', carousel_type)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generated_files = [] #inizializza una lista vuota per memorizzare i nomi dei file SVG generati.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  #aggiungo un timestamp per differenziare i file

    for idx, (route, state) in enumerate(results_routes, start=1): #ciclo for sugli elementi di results_routes, elenco di tuple. Ogni tupla contiene una route e un state.
        #estrazione dei nodi e degli archi
        nodes_and_edges = route.split(', ')
        nodes = [item for item in nodes_and_edges if not item.isdigit()]
        edges_ids = [int(item) for item in nodes_and_edges if item.isdigit()]
        
        #creazione delle relazioni tra i nodi, associando ogni nodo a quello successivo
        edges = [(nodes[i], nodes[i + 1], edges_ids[i]) for i in range(len(nodes) - 1)]
        edges.append((nodes[-1], nodes[0], edges_ids[-1]))  #aggiunge l'ultimo edge per chiudere il loop

      
        dot = Digraph(comment=f'Routes Graph {idx}')
        
        #dimensione fissa dell'immagine bianca e proporzioni.
        #imposta le dimensioni dell'immagine generata la parte bianca, riempie lo spazio disponibile con il grafo, e aggiunge margini.

        dot.attr(size="7,7!", ratio="fill", margin="0.2", pad="1")

        #aggiunge lo stat come etichetta del grafico in basso e centrato
        dot.attr(label=f'State: {state}', fontsize='20', labelloc='b', labeljust='c', splines='true', overlap='false')

        #definisce l'aspetto dei nodi con una dimensione del carattere), dimensioni variabili per i nodi (fixedsize='false').
        dot.attr('node', fontsize='12', width='0.5', height='0.5', fixedsize='false', shape='oval')  
        for node in nodes:
            if node in node_positions:
                pos_x, pos_y = node_positions[node]
                if node == highlight_node:
                    dot.node(node, pos=f"{pos_x},{pos_y}!", style='filled', color='black', fillcolor='lightblue')
                else:
                    dot.node(node, pos=f"{pos_x},{pos_y}!")

        #aggiunge gli archi  con i relativi tipi di relazioni
        dot.attr('edge', fontsize='10')  #dimensione fissa per il testo degli archi
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

        #nome file che include il tipo di carosello e un timestamp
        file_name = f'{output_dir}/loop_graph_{idx}_{state}_{len(nodes)}nodes_{timestamp}'
        dot.save(f'{file_name}.dot')
        dot.render(file_name, format='svg')
        generated_files.append(f'{file_name}.svg')

    return generated_files
