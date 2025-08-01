from uuid import uuid4

import pandas as pd
from neo4j import GraphDatabase
from sqlalchemy import create_engine, text


class AnalyzeCLDGraph:
    def __init__(self, uuid: uuid4 = None):
        self.uuid = str(uuid)
        pass

    def set_database_conf(self, url: str, user: str, password: str):
        self.url = url
        self.user = user
        self.password = password

        with GraphDatabase.driver(self.url, auth=(self.user, self.password)) as driver:
            try:
                self.session = driver.verify_connectivity()
            except Exception as e:
                raise ValueError(f"Could not connect to database: {e}")

    def extract_loops(self):
        query = """
MATCH p = (n{uuid:$uuid})-[*2..20]->(n)
WHERE NOT apoc.coll.containsDuplicates(tail(nodes(p))) 
AND n.external_id = apoc.coll.min([node IN nodes(p) | node.external_id])

WITH nodes(p) AS nodePath, relationships(p) AS rels

RETURN
     [i IN range(0, size(nodePath)-1 + size(rels) - 1) | 
        CASE 
          WHEN i % 2 = 0 THEN nodePath[i / 2].label
          ELSE toString(id(rels[(i - 1) / 2]))
        END
     ] AS loop_path,
       CASE 
           WHEN size([rel IN rels WHERE type(rel) = 'DISC_CHANGE']) % 2 = 0 
           THEN 'reinforcing' 
           ELSE 'balancing' 
       END AS state,
       size(rels) AS loop_length;
                """
        return self._run_query(query)

    def extract_routes(self):
        query = """
MATCH (startNode{uuid:$uuid}), (endNode{uuid:$uuid})
WHERE startNode.external_id <> endNode.external_id
CALL apoc.algo.allSimplePaths(startNode, endNode, '>', 20) YIELD path
WITH startNode,endNode,path,relationships(path) AS rels,nodes(path) as nodePath
WITH 
    [x IN range(0, size(nodePath) + size(rels) - 1) |
        CASE 
            WHEN x % 2 = 0 THEN nodePath[x / 2].label // Indice per i nodi
            ELSE toString(id(rels[(x - 1) / 2]))      // Indice per le relazioni
        END
    ] AS path_sequence,rels,
    path,startNode,endNode
WITH rels,path_sequence,startNode,endNode,
path,size(rels) as pathlength,
size([rel in rels WHERE type(rel) = 'CONC_CHANGE']) AS hopsCon,
size([rel in rels WHERE type(rel) = 'DISC_CHANGE']) AS hopsDisc,
       CASE
           WHEN size([rel in rels WHERE type(rel) = 'DISC_CHANGE']) % 2 = 0 
           THEN 'increasing'
           ELSE 'decreasing'
       END AS pathState
RETURN  startNode.label AS start_node,endNode.label AS end_node, path_sequence AS route, pathlength AS route_length,pathState AS state
"""
        return self._run_query(query)

    def extract_nodes(self):
        query = """
    MATCH ( n { uuid: $uuid } )
    RETURN n.label as node_name, n . x as pos_x , n . y as pos_y
            """
        return self._run_query(query)

    def extract_edges(self):
        query = """
MATCH ( a { uuid: $uuid}) -[ r ] - >( b { uuid: $uuid})
 RETURN id(r)  as relationshipID , type ( r ) as type
 """
        return self._run_query(query)

    def _run_query(self, query: str) -> pd.DataFrame:
        def _tx_run_query(tx):
            result = tx.run(query, uuid=self.uuid)
            return result.to_df()

        with GraphDatabase.driver(self.url, auth=(self.user, self.password)) as driver:
            with driver.session(database="neo4j") as session:
                data = session.execute_read(_tx_run_query)
                return data


class LoadAnalyses:
    def __init__(self, uuid: uuid4 = None):
        self.uuid = str(uuid)
        pass

    def set_database_conf(self, url: str, user: str, password: str):
        self.conn_string = f"mysql+mysqlconnector://{user}:{password}@{url}/cld"

    def _clear_table(self, table_name: str):
        engine = create_engine(self.conn_string)
        with engine.connect() as connection:
            connection.execute(text(f"DELETE FROM {table_name};"))
            connection.commit()

    def load_nodes(self, df: pd.DataFrame):
        df["cldID"] = 99
        self._clear_table("nodes_custom")
        df.to_sql("nodes_custom", self.conn_string, if_exists="append", index=False)

    def load_relationships(self, df: pd.DataFrame):
        df["cldID"] = 99
        # TODO: Add delay and type
        df["delay"] = "no"
        df["type"] = "CONC_CHANGE"
        self._clear_table("relationships_custom")
        df.to_sql(
            "relationships_custom", self.conn_string, if_exists="append", index=False
        )

    def load_loops(self, df: pd.DataFrame):
        df["cldID"] = 99
        self._clear_table("loops_custom")
        df["loopID"] = range(1, len(df) + 1)
        df["loop_path"] = (
            df["loop_path"]
            .apply(lambda x: str(x))
            .replace(r"[\[\]]", "", regex=True)
            .replace("'", "", regex=True)
        )
        df.to_sql("loops_custom", self.conn_string, if_exists="append", index=False)

    def load_nodes_loops(self, df_loops: pd.DataFrame):
        df_loops["node_name"] = df_loops.loop_path.apply(lambda x: x[::2])
        # print(type(df_loops.loop_path.iloc[0]))
        # print(df_loops.head())
        df_loops["loopID"] = range(1, len(df_loops) + 1)
        df_nodes_loops = df_loops.explode("node_name")
        df_nodes_loops["cldID"] = 99
        self._clear_table("bridge_nodes_loops_custom")
        df_nodes_loops = df_nodes_loops[["node_name", "loopID", "cldID"]]
        df_nodes_loops.drop_duplicates(inplace=True)
        df_nodes_loops.to_sql(
            "bridge_nodes_loops_custom",
            self.conn_string,
            if_exists="append",
            index=False,
        )

    def load_routes(self, df: pd.DataFrame):
        df["cldID"] = 99
        self._clear_table("routes_custom")
        df["routeID"] = range(1, len(df) + 1)
        df.route = (
            df.route.apply(lambda x: str(x))
            .replace(r"[\[\]]", "", regex=True)
            .replace("'", "", regex=True)
        )
        df.to_sql("routes_custom", self.conn_string, if_exists="append", index=False)
