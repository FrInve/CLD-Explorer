import json
from urllib.parse import parse_qs, unquote, urlparse
from uuid import uuid4

from graphviz import Digraph
from neo4j import GraphDatabase


class Loopy:
    def __init__(self, data: str):
        self.data = data

    def load(self):
        parsed_url = urlparse(self.data)
        try:
            self.query_list_graph = parse_qs(parsed_url.query)["data"][0]
            self.query_list_graph = json.loads(self.query_list_graph)
            # 0 are nodes
            # 1 are edges
            # 2 are labels - only text objects
            # 3 are uid - only numbers

            # Counter for anonymous nodes
            anonymous_node_counter = 1

            # Process nodes and handle anonymous ones
            self.nodes = []
            for x in self.query_list_graph[0]:
                label = x[4]  # The label is at index 4

                # Handle double URL encoding - decode the label if it contains URL encoded characters
                try:
                    # Apply additional URL decoding to handle double-encoded strings
                    decoded_label = unquote(label)
                    # If the decoded version is different, use it
                    if decoded_label != label:
                        label = decoded_label
                except Exception:
                    # If decoding fails, keep the original label
                    pass

                # If label is empty string, assign anonymous name
                if label == "" or label == "?":
                    label = f"_{anonymous_node_counter}"
                    anonymous_node_counter += 1

                # If label consists only of digits, append underscore
                if label.isdigit():
                    label = label + "_"

                node = LoopyNode(x[0], x[1], x[2], x[3], label, x[5])
                self.nodes.append(node)

            self.edges = [
                LoopyEdge(x[0], x[1], x[2], x[3], x[4])
                for x in self.query_list_graph[1]
            ]

        except KeyError:
            raise ValueError("Invalid LOOPY URL")

    def to_svg(self, width=600, height=400, output_path=None):
        """
        Generate an SVG representation of the Loopy diagram using Graphviz.

        Args:
            width (int): Width of the output SVG
            height (int): Height of the output SVG
            output_path (str): Optional path to save the SVG file. If None, returns SVG string.

        Returns:
            str: SVG content as string if output_path is None, otherwise file path
        """
        dot = Digraph(comment="Loopy Causal Loop Diagram", engine="neato")

        # Set overall graph attributes - neato engine is needed for absolute positioning
        dot.attr(size=f"{width/72},{height/72}!", ratio="fill", margin="0.2", pad="1")

        # Set node and edge attributes
        dot.attr(
            "node",
            fontsize="24",
            width="1.5",
            height="1.5",
            fixedsize="false",
            shape="oval",
        )
        dot.attr("edge", fontsize="18")
        dot.attr(splines="true", overlap="false")

        # Add nodes with their positions
        for node in self.nodes:
            # Loopy coordinates range from 0-200 or similar, need to convert to graphviz coordinates
            # First, normalize coordinates to 0-1 range, then scale to desired size in inches
            # Assuming Loopy coords are roughly in 0-200 range
            max_coord = 200
            pos_x = (node.x / max_coord) * (width / 72)  # Convert to inches
            pos_y = ((max_coord - node.y) / max_coord) * (
                height / 72
            )  # Flip Y and convert to inches

            # Use hue to determine node color (convert from HSV hue to a color)
            # hue_normalized = (node.hue % 360) / 360  # Normalize to 0-1 range
            # hue_color = (
            #     f"{hue_normalized:.3f} 0.7 0.9"  # HSV format: hue saturation value
            # )

            dot.node(
                str(node.id),
                label=node.label,
                pos=f"{pos_x},{pos_y}!",
                style="filled",
                fillcolor="white",
                color="black",
            )

        # Add edges based on their strength (positive = CONC_CHANGE, negative = DISC_CHANGE)
        for edge in self.edges:
            source_id = str(edge.source)
            target_id = str(edge.target)

            # Determine edge style based on strength (similar to routes_generator logic)
            if edge.strength > 0:
                # Positive feedback (reinforcing) - solid line
                edge_style = "solid"
                edge_color = "black"
            else:
                # Negative feedback (balancing) - dashed line
                edge_style = "dashed"
                edge_color = "black"

            # Add strength as edge label
            # edge_label = f"{abs(edge.strength)}"

            dot.edge(
                source_id,
                target_id,
                style=edge_style,
                color=edge_color,
                # label=edge_label,
                fontcolor=edge_color,
            )

        if output_path:
            # Save to file
            dot.render(output_path, format="svg", cleanup=True)
            return f"{output_path}.svg"
        else:
            # Return SVG string
            return dot.pipe(format="svg", encoding="utf-8")


class LoopyNode:
    def __init__(
        self, id: int, x: float, y: float, init_value: float, label: str, hue: int
    ):
        self.id = id
        self.x = x
        self.y = y
        self.init_value = init_value
        self.label = str(label)
        self.hue = hue

    def __repr__(self):
        return f"Node {self.id}: {self.label}"


class LoopyEdge:
    def __init__(
        self, source: int, target: int, arc: float, strength: int, rotation: float
    ):
        self.source = source
        self.target = target
        self.arc = arc
        self.strength = strength
        self.rotation = rotation

    def __repr__(self):
        return f"Edge from {self.source} to {self.target}"


class LoopyNeo4jLoader:
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

    def load(self, loopy: Loopy):
        self.clear()
        for node in loopy.nodes:
            self.load_node(node)

        for edge in loopy.edges:
            self.load_edge(edge)

    def load_node(self, node: LoopyNode):
        def _tx_merge_node(tx, node):
            tx.run(
                "MERGE (n:Node {external_id: $id, x: $x, y: $y, init_value: $init_value, label: $label, hue: $hue, uuid: $uuid})",
                id=node.id,
                x=node.x,
                y=node.y,
                init_value=node.init_value,
                label=node.label,
                hue=node.hue,
                uuid=self.uuid,
            )

        with GraphDatabase.driver(self.url, auth=(self.user, self.password)) as driver:
            with driver.session(database="neo4j") as session:
                session.execute_write(_tx_merge_node, node)

    def load_edge(self, edge: LoopyEdge):
        """
        CONG_CHANGE for positive feedback
        DISC_CHANGE for negative feedback
        """
        edge_label = "CONG_CHANGE" if edge.strength > 0 else "DISC_CHANGE"

        def _tx_merge_edge(tx, edge):
            tx.run(
                f"MATCH (source:Node {{external_id: $source, uuid: $uuid}}), (target:Node {{external_id: $target, uuid: $uuid}}) MERGE (source)-[:{edge_label} {{arc: $arc, strength: $strength, rotation: $rotation, uuid: $uuid}}]->(target)",
                source=edge.source,
                target=edge.target,
                arc=edge.arc,
                strength=edge.strength,
                rotation=edge.rotation,
                uuid=self.uuid,
            )

        with GraphDatabase.driver(self.url, auth=(self.user, self.password)) as driver:
            with driver.session(database="neo4j") as session:
                session.execute_write(_tx_merge_edge, edge)

    def clear(self):
        with GraphDatabase.driver(self.url, auth=(self.user, self.password)) as driver:
            with driver.session(database="neo4j") as session:
                session.run("MATCH (n {uuid: $uuid}) DETACH DELETE n", uuid=self.uuid)
                session.run("MATCH (n {uuid: $uuid}) DETACH DELETE n", uuid=self.uuid)
