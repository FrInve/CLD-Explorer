import pandas as pd
import mysql.connector

#lettura csv
csv_path = r"C:\Users\danyl\OneDrive\Desktop\fashionRoutesNeo4j.csv"
df = pd.read_csv(csv_path)

#modifica nomi header
df.rename(columns={
    'startNode.id_custom': 'start_node',
    'endNode.id_custom': 'end_node',
    'path_sequence': 'route',
    'pathlength': 'route_length',
    'pathState': 'state'
}, inplace=True)

#rimuovere le virgolette ovunque
df = df.replace('"', '', regex=True)
df['route'] = df['route'].replace(r'[\[\]]', '', regex=True)

#aggiungere la colonna cldID con un valore costante
df['cldID'] = 2

#aggiungere una colonna routeID con valori incrementali
df['routeID'] = range(1, len(df) + 1)

#riordina colonne
df = df[['cldID', 'routeID'] + [col for col in df.columns if col not in ['cldID', 'routeID']]]

#solo per controllare
output_path = r"C:\Users\danyl\OneDrive\Desktop\fashionRoutesNeo4j.csv"
df.to_csv(output_path, index=False)

print("CSV delle routes modificato e salvato con successo!")

#connessione al db. 
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password= '3utoeZVN!',
    database='cld'  
)

cursor = conn.cursor()

#tab mysql per routes:bisogna mettere covid, fashion o australian_hotel al posto di table
create_table_query = """
CREATE TABLE IF NOT EXISTS routes_fashion(
    cldID INT,
    routeID INT,
    start_node text,
    end_node text,
    route text,
    route_length int,
    state text
);
"""
cursor.execute(create_table_query)

#data frame
for _, row in df.iterrows():
    insert_query = """
    INSERT INTO routes_table (cldID, routeID, start_node, end_node, route,route_length, state)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, tuple(row))

conn.commit()
cursor.close()
conn.close()

