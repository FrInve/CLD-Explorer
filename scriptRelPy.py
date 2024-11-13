import pandas as pd
import mysql.connector

#lettura file csv input
csv_path = r"C:\Users\danyl\OneDrive\Desktop\fashionRelNeo4j.csv"
df = pd.read_csv(csv_path)

#rimuovere le virgolette da ovunque
df = df.replace('"', '', regex=True)

#agiunge la colonna 'cldID' con un valore costante
df['cldID'] = 1  # Sostituisci 1 per covid,2 fashion, 3 hotel

#rinominare le colonne (Scelte random, senza una motivazione precisa)
df.rename(columns={'relationship_type': 'type', 'ID': 'relationshipID'}, inplace=True)

#per controllare che vada tutto bene prima di caricare sul db
output_path = r"C:\Users\danyl\OneDrive\Desktop\outputRel.csv"
df.to_csv(output_path, index=False)

#connessione al database 
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='3utoeZVN!', 
    database='cld'  
)

cursor = conn.cursor()

#creare la tabella in MySQL (bisogna mettere covid, fashion o australian_hotel al posto di table)
create_table_query = """
CREATE TABLE IF NOT EXISTS relationships_fashion (
    cldID INT,
    relationshipID INT,
    type TEXT,
    delay TEXT  
);
"""
#ho messo TEXT nel tipo ma forse meglio mettere VARCHAR(244)
cursor.execute(create_table_query)

#inserire i dati del dataframe della tabella 
for _, row in df.iterrows():
    insert_query = """
    INSERT INTO relationships_table (cldID, relationshipID, type, delay)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(insert_query, tuple(row))

conn.commit()
cursor.close()
conn.close()
