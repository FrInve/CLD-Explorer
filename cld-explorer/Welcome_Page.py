import debugpy

debugpy.listen(("0.0.0.0", 5678))  # Open debug port
print("✅ Debugger is listening on port 5678")
# debugpy.wait_for_client()  # Optional: wait for VSCode debugger to attach

import base64
import os
import shutil

import cairosvg
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="CLD-Explorer", layout="wide")

import os


def clear_images_in_folders(folder_name):
    # percorso della cartella principale output
    output_dir = os.path.abspath(folder_name)

    # sottocartelle 'main' e 'compare'
    subfolders = ["main", "compare"]

    # per ogni sottocartella, cancella i file
    for subfolder in subfolders:
        subfolder_path = os.path.join(output_dir, subfolder)

        # se la sottocartella esiste, rimuovi i file al suo interno
        if os.path.exists(subfolder_path):
            for file_name in os.listdir(subfolder_path):
                file_path = os.path.join(subfolder_path, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)  # elimina il file
                        print(f"File eliminato: {file_name}")
                except Exception as e:
                    print(f"Errore durante l'eliminazione di {file_name}: {e}")
        else:
            # crea la sottocartella se non esiste
            os.makedirs(subfolder_path)
            print(f"Cartella creata: {subfolder_path}")


output_folder = "output"
clear_images_in_folders(output_folder)


def convert_svg_to_png(svg_content):
    png_data = cairosvg.svg2png(bytestring=svg_content.encode("utf-8"))
    return png_data


def img_to_base64(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


st.title("Causal Loop Diagrams Explorer")
st.header("Introduction to the Platform")
st.write(
    """
This platform is designed to help you extract information from Causal Loop Diagrams (CLDs) quickly and efficiently. Given a CLD, the platform can automatically extract and present all the data you need, including the variables involved, the feedback loops, and the causal routes. By making these key data readily accessible, it simplifies the analysis of complex systems, allowing you to better understand the system’s overall behavior."""
)

# descrizione di cosa è un Causal Loop Diagram
st.header("What is a Causal Loop Diagram?")
st.write(
    """
Causal Loop Diagrams (CLDs) are a visual tool used to document and analyze the dynamics of complex systems. They represent the relevant factors, known as variables, and the causal relationships between them, helping to illustrate how these elements influence one another through feedback loops and causal routes. CLDs are essential for understanding how changes in one part of a system can influence other areas.
"""
)


# colonne per centrare l'immaginel del mini grafo
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("./assets/image_cld.png", use_column_width=True)


# tabella per i loop
st.markdown(
    """
    <style>
    .legend-table {
        width: 100%;
        border-collapse: collapse;
        color: white; 
    }
    .legend-table td {
        padding: 8px;
        text-align: left;
        vertical-align: middle;
        border: 1px solid #555; /*bordo chiaro per le celle*/
    }
    .legend-symbol {
        font-size: 28px;
        color: white; /*simboli in bianco */
        padding-right: 15px;
    }
    .delay-symbol {
        font-size: 28px;
        color: white; /
        padding-right: 5px;
    }
    .red-arrow {
        font-size: 28px;
        color: red; /*solo la freccia del delay è rossa */
        padding-left: 5px;
    }
    .legend-description {
        font-size: 16px;
        color: white; /* descrizioni in bianco */
    }
    </style>
""",
    unsafe_allow_html=True,
)


st.header("Essentials to know")
st.write("Below there are the key elements involved in a Causal Loop Diagram:")

st.markdown(
    """
<table class="legend-table">
    <tr>
        <td><span class="legend-symbol">⇢</span></td>
        <td class="legend-description">The dashed arrow shows causality, where a variable at the tail causes a change in the variable at the head. The variables change in opposite directions: if the tail increases, the head decreases; if the tail decreases, the head increases.</td>
    </tr>
    <tr>
        <td><span class="legend-symbol">⟶</span></td>
        <td class="legend-description">The solid arrow shows causality, where a variable at the tail causes a change in the variable at the head. The variables change in the same direction: if the tail increases, the head increases; if the tail decreases, the head decreases.</td>
    </tr>
    <tr>
        <td><span class="delay-symbol">delay</span><span class="red-arrow">⟶</span></td>
        <td class="legend-description">The red arrow with the label "delay" indicates that the effect of the first variable on the second is delayed, meaning it occurs after a certain period of time rather than immediately.</td>
    </tr>
</table>
""",
    unsafe_allow_html=True,
)


balancing_loop_image = img_to_base64("./assets/balancing_loop.png")
reinforcing_loop_image = img_to_base64("./assets/reinforcing_loop.png")
agreeing_loop_image = img_to_base64("./assets/agreeing_loops.png")
disagreeing_loop_image = img_to_base64("./assets/disagreeing_loop.png")


st.markdown(
    """
    <style>
    .loop-table {
        width: 100%;
        border-collapse: collapse;
        color: white; 
    }
    .loop-table td {
        padding: 10px;
        text-align: left;
        vertical-align: middle; /*allinea verticalmente tutto */
        border: 1px solid #555; 
    }
    .loop-title {
        font-size: 20px;
        font-weight: bold;
        color: white;
        text-align: center;
        width: 20%; /*larghezza della prima colonna */
    }
    .loop-description {
        font-size: 16px;
        color: white;
        padding-right: 10px;
        width: 30%; /*larghezza ridotta per la seconda colonna */
    }
    .loop-image {
        width: 50%; /*larghezza aumentata per la terza colonna (immagini) */
        height: auto;
        text-align: center;
    }
    .image {
        width: 300px; /*dimensione delle immagini aumentata */
        height: auto;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# sezione per descrivere i "Causal Loops"
st.markdown(
    '<h3 class="section-title">Causal Loops Types:</h3>', unsafe_allow_html=True
)
st.write(
    """
Cyclic paths that loop from one variable back to the same variable.
"""
)


st.markdown(
    f"""
<table class="loop-table">
    <tr>
        <td class="loop-title">Balancing Loop</td>
        <td class="loop-description">A balancing loop contains an odd number of dashed arrows. The effects along the arrows combine in such a way that any increase(or decrease) in the target variable is countered by a decrease(or increase) elsewhere in the loop, ultimately bringing the variable back toward equilibrium. In other words, increases will cancel out with decreases, and decreases will cancel out with increases.</td>
        <td><img src="data:image/png;base64,{balancing_loop_image}" class="image" alt="Balancing Loop"></td>
    </tr>
    <tr>
        <td class="loop-title">Reinforcing Loop</td>
        <td class="loop-description">A reinforcing loop contains an even number of dashed arrows. An increase along the outgoing arrow will eventually lead to an increase in the target variable along the incoming arrow, creating positive reinforcement throughout the loop: the same applies for negative reinforcement.</td>
        <td><img src="data:image/png;base64,{reinforcing_loop_image}" class="image" alt="Reinforcing Loop"></td>
    </tr>
    <tr>
        <td class="loop-title">Agreeing Loops</td>
        <td class="loop-description">Two (or more) loops are agreeing when they share a certain variable and are all of the same type.</td>
        <td><img src="data:image/png;base64,{agreeing_loop_image}" class="image" alt="Agreeing Loop"></td>
    </tr>
    <tr>
        <td class="loop-title">Disagreeing Loops</td>
        <td class="loop-description">Two (or more) loops are disagreeing when they share a certain variable and there is at least one balancing loop and one reinforcing loop.</td>
        <td><img src="data:image/png;base64,{disagreeing_loop_image}" class="image" alt="Disagreeing Loop"></td>
    </tr>
</table>
""",
    unsafe_allow_html=True,
)


increasing_route_image = img_to_base64("./assets/increasing_route.png")
decreasing_route_image = img_to_base64("./assets/decreasing_route.png")
agreeing_route_image = img_to_base64("./assets/agreeing_routes.png")
disagreeing_route_image = img_to_base64("./assets/disagreeing_route.png")


st.markdown(
    """
    <style>
    .loop-table {
        width: 100%;
        border-collapse: collapse;
        color: white;
    }
    .loop-table td {
        padding: 10px;
        text-align: left;
        vertical-align: middle; 
        border: 1px solid #555; 
    }
    .loop-title {
        font-size: 20px;
        font-weight: bold;
        color: white;
        text-align: center;
        width: 20%;
    }
    .loop-description {
        font-size: 16px;
        color: white;
        padding-right: 10px;
        width: 30%; 
    }
    .loop-image {
        width: 50%;
        height: auto;
        text-align: center;
    }
    .image {
        width: 300px; 
        height: auto;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# sezione per descrivere i causal routes
st.markdown(
    '<h3 class="section-title">Causal Routes Types:</h3>', unsafe_allow_html=True
)
st.write(
    """
Sequence of connections between given source and destination variables.
"""
)


st.markdown(
    f"""
<table class="loop-table">
    <tr>
        <td class="loop-title">Increasing Route</td>
        <td class="loop-description">An increasing route contains an even number of dashed arrows.</td>
        <td><img src="data:image/png;base64,{increasing_route_image}" class="image" alt="Balancing Loop"></td>
    </tr>
    <tr>
        <td class="loop-title">Decreasing Route</td>
        <td class="loop-description">A decreasing route contains an odd number of dashed arrows.</td>
        <td><img src="data:image/png;base64,{decreasing_route_image}" class="image" alt="Reinforcing Loop"></td>
    </tr>
    <tr>
        <td class="loop-title">Agreeing Routes</td>
        <td class="loop-description">Two(or more) routes are agreeing when they share a certain variable and are all of the same type.</td>
        <td><img src="data:image/png;base64,{agreeing_route_image}" class="image" alt="Agreeing Loop"></td>
    </tr>
    <tr>
        <td class="loop-title">Disagreeing Routes</td>
        <td class="loop-description">Two (or more) routes are disagreeing when they share a certain variable and there is at least one increasing route and one decreasing route.</td>
        <td><img src="data:image/png;base64,{disagreeing_route_image}" class="image" alt="Disagreeing Loop"></td>
    </tr>
</table>
""",
    unsafe_allow_html=True,
)


st.header("Causal Loop Diagrams to Explore")
st.write("Below there are the CLDs that you can analyze:")


# Funzione per visualizzare SVG con zoom e pan
def display_svg_with_zoom_pan(svg_content):
    svg_encoded = (
        f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
    )
    st.markdown(
        f"""
        <style>
        .zoom-container {{
            width: 100%;
            height: auto;
            overflow: hidden;
            position: relative;
            border: 1px solid black;
            cursor: grab;
            margin-bottom: 20px;
        }}
        .zoom-container img {{
            width: 100%;
            height: auto;
            transition: transform 0.2s ease-in-out;
            transform-origin: center center;
        }}
        .zoom-container:active {{
            cursor: grabbing;
        }}
        </style>
        <div class="zoom-container">
            <img src="{svg_encoded}" class="zoom-content">
        </div>

        <script>
            const container = document.querySelector('.zoom-container');
            const content = container.querySelector('img');
            let scale = 1;
            let panX = 0;
            let panY = 0;

            function updateTransform() {{
                content.style.transform = "translate(" + panX + "px, " + panY + "px) scale(" + scale + ")";
            }}

            container.onwheel = (e) => {{
                e.preventDefault();
                const zoom = e.deltaY < 0 ? 1.1 : 0.9;
                const rect = content.getBoundingClientRect();
                const offsetX = e.clientX - rect.left;
                const offsetY = e.clientY - rect.top;

                const newScale = scale * zoom;
                panX = offsetX - newScale / scale * (offsetX - panX);
                panY = offsetY - newScale / scale * (offsetY - panY);
                scale = newScale;

                updateTransform();
            }};

            let isDragging = false;
            let startX, startY;

            container.onmousedown = (e) => {{
                isDragging = true;
                startX = e.clientX - panX;
                startY = e.clientY - panY;
            }};

            container.onmousemove = (e) => {{
                if (isDragging) {{
                    panX = e.clientX - startX;
                    panY = e.clientY - startY;
                    updateTransform();
                }}
            }};

            container.onmouseup = () => {{
                isDragging = false;
            }};

            container.onmouseleave = () => {{
                isDragging = false;
            }};
        </script>
        """,
        unsafe_allow_html=True,
    )


# inserimento di immagini SVG
svg_file_1 = open("./assets/graph_covid.svg", "r").read()
svg_file_2 = open("./assets/graph_fashion.svg", "r").read()
svg_file_3 = open("./assets/graph_hotel.svg", "r").read()

st.markdown("<h4>Covid-19</h4>", unsafe_allow_html=True)
display_svg_with_zoom_pan(svg_file_1)
png_file_1 = convert_svg_to_png(svg_file_1)
st.write(
    "The Covid_19 CLD illustrates the various feedback loops involved in the spread of COVID-19 and its impact on societal and economic factors. It shows how variables like government interventions, healthcare capacity, and economic growth are connected, and how they influence the progression of the pandemic, including delays in response times and their effects on outcomes."
)

st.download_button(
    label="Download image",
    data=png_file_1,
    file_name="graph_covid.png",
    mime="image/png",
)

st.markdown(
    "<h4>Fashion Industry Footprint and Sustainability</h4>", unsafe_allow_html=True
)
display_svg_with_zoom_pan(svg_file_2)
png_file_2 = convert_svg_to_png(svg_file_2)
st.write(
    "This CLD visualizes the relationships between economic trends and sustainability practices in the fashion industry. It emphasizes how consumer behavior, production cycles, and environmental impacts are interlinked, providing insights into potential areas for sustainable intervention."
)

st.download_button(
    label="Download image",
    data=png_file_2,
    file_name="graph_fashion.png",
    mime="image/png",
)

st.markdown("<h4>Australian Hotel RET</h4>", unsafe_allow_html=True)
display_svg_with_zoom_pan(svg_file_3)
png_file_3 = convert_svg_to_png(svg_file_3)
st.write(
    "The Australian Hotel CLD focuses on the adoption of Renewable Energy Technologies (RET) in Queensland’s(Australia) hotel industry, aiming to reduce greenhouse gas emissions. Hotels, being large energy consumers, face increasing energy demands due to rising tourism, and RET adoption can significantly lower their environmental impact and operational costs."
)
with st.expander("References"):
    st.markdown(
        """
    **Australian Hotel RET CLD** is based on:

    A multi-methodology approach to creating a causal loop diagram.
    by Dhirasasna,N., et al. Systems 7(3), 2009.
    """
    )


st.download_button(
    label="Download image",
    data=png_file_3,
    file_name="graph_hotel.png",
    mime="image/png",
)
