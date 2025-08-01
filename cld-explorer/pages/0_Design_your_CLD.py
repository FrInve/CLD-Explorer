from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components
from db_config import db_config
from models.causal_loop_diagram import AnalyzeCLDGraph, LoadAnalyses
from models.loopy import Loopy, LoopyNeo4jLoader

st.set_page_config(layout="wide")
st.title("Design your Causal Loop Diagram")

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid4()

components.iframe(
    # "https://ncase.me/loopy/v1.1/?data=[[],[],[],2%5D", height=768, width=1280
    "https://geco.deib.polimi.it/loopy/?data=[[],[],[],2%5D",
    height=768,
    width=1280,
)

with st.form("loopy_form"):
    loopy_import_string = st.text_input(
        "Paste the link from LOOPY here",
        # value="https://ncase.me/loopy/v1.1/?data=[[[3,245,183,1,%22hello%22,4]],[],[],3%5D",
    )
    # st.write(
    #     "Instructions: draw your CLD in LOOPY, copy the link from 'save as link' and paste it in the field above."
    # )
    submitted = st.form_submit_button("Load")

if submitted and loopy_import_string:
    l = Loopy(loopy_import_string)
    l.load()
    lnl = LoopyNeo4jLoader(st.session_state.session_id)
    lnl.set_database_conf("bolt://neo4j:7687", "neo4j", "password")
    lnl.load(l)

    analyzer = AnalyzeCLDGraph(st.session_state.session_id)
    analyzer.set_database_conf("bolt://neo4j:7687", "neo4j", "password")

    loader = LoadAnalyses(st.session_state.session_id)
    loader.set_database_conf(
        db_config["host"] + ":" + db_config["port"],
        db_config["user"],
        db_config["password"],
    )
    loader.load_nodes(analyzer.extract_nodes())
    loader.load_relationships(analyzer.extract_edges())
    loops = analyzer.extract_loops()
    nodes_loops = loops.copy(deep=True)
    loader.load_loops(loops)
    loader.load_nodes_loops(nodes_loops)
    loader.load_routes(analyzer.extract_routes())

    # Display success message
    st.success("Diagram loaded successfully!")

    # Show SVG representation of the imported diagram
    st.subheader("Imported Diagram Visualization")
    svg_content = l.to_svg(width=600, height=400)
    st.markdown(
        f'<div style="text-align: center;">{svg_content}</div>', unsafe_allow_html=True
    )

    # Save svg to file "output/custom_diagram.svg"
    output_path = "output/custom_diagram.svg"
    with open(output_path, "w") as f:
        f.write(svg_content)

    with st.expander("Show debug info"):
        st.write("Structures from LOOPY")
        st.write(l.nodes)
        st.write(l.edges)

        st.write("Structures from Neo4j")
        st.write(analyzer.extract_loops())

        st.write(analyzer.extract_routes())

        st.write(analyzer.extract_nodes())

        st.write(analyzer.extract_edges())

    st.session_state.grafo_scelto = "Custom"
    st.session_state.loop_grafo_scelto = "Custom"
    st.session_state.graph_image_path = output_path
