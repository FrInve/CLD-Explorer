import pandas as pd
import mysql.connector

#lettura file csv input
csv_path = r"C:\Users\danyl\OneDrive\Desktop\fashionNodesNeo4j.csv"
df = pd.read_csv(csv_path)
#rimozione tutte virgolette inutili
df = df.replace('"', '', regex=True)

# aggiunge colonna cldID, ogni cld ha un id numerico diverso
df['cldID'] = 2
#ordina colonne del df cosi da avere cdlID come prima
df = df[['cldID'] + [col for col in df.columns if col != 'cldID']]

#csv output per verficare
output_path = r"C:\Users\danyl\OneDrive\Desktop\outputNodes.csv"
df.to_csv(output_path, index=False)


#connessione to mysql
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='3utoeZVN!',
    database='cld'
)

cursor = conn.cursor()

#creazione tabella tabella nodes_table( bisogna mettere covid, fashion o australian_hotel al posto di table)
create_table_query = """
CREATE TABLE IF NOT EXISTS nodes_fashion (
    cldID INT,
    nodeID INT,
    label VARCHAR(244),
    description TEXT
);
"""
cursor.execute(create_table_query)

#query per inserire i dati dal df nella tabella
for _, row in df.iterrows():
    insert_query = """
    INSERT INTO nodes_table (cldID, nodeID, label, description)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(insert_query, tuple(row))

conn.commit()
cursor.close()
conn.close()


