import pandas as pd
import mysql.connector

#lettura csv
csv_path = r"C:\Users\danyl\OneDrive\Desktop\fashionLoopsNeo4j.csv"
df = pd.read_csv(csv_path)

#elimina la colonna 'hopsDisc' perchè non serve. 
if 'hopsDisc' in df.columns:
    df.drop(columns=['hopsDisc'], inplace=True)

#rimozione virgolette
df = df.replace('"', '', regex=True)
df['loop_path'] = df['loop_path'].replace(r'[\[\]]', '', regex=True)

#rinomina cdi alcuni headers
df.rename(columns={'pathState': 'state', 'path_sequence': 'loop_path'}, inplace=True)


df['cldID'] = 1  

#aggiunge colonna loopID con valori icnrementali
df['loopID'] = range(1, len(df) + 1)

#riordinare le colonne
df = df[['cldID', 'loopID'] + [col for col in df.columns if col not in ['cldID', 'loopID']]]


output_path = r"C:\Users\danyl\OneDrive\Desktop\fashionLoopsNeo4j.csv"
df.to_csv(output_path, index=False)

#connessione my sql
conn = mysql.connector.connect(
    host='localhost', 
    user='root',       
    password='3utoeZVN!',  
    database='cld'     
)

cursor = conn.cursor()

# tabella mysql-> bisogna mettere covid, fashion o australian_hotel al posto di table
create_table_query = """
CREATE TABLE IF NOT EXISTS loops_fashion (
    cldID INT,
    loopID INT,
    loop_path TEXT,
    state TEXT,
    loop_length INT
);
"""
cursor.execute(create_table_query)

#data frame
for _, row in df.iterrows():
    insert_query = """
    INSERT INTO loops_table (cldID, loopID, loop_path, state, loop_length)
    VALUES (%s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, tuple(row))


conn.commit()
cursor.close()
conn.close()

