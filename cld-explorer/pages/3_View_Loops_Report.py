import streamlit as st
from fpdf import FPDF
import os
import tempfile
import cairosvg
import base64
import pandas as pd

st.set_page_config(layout="wide", page_title="CLD-Explorer")

def convert_svg_to_png(svg_path):
    try:
        with open(svg_path, "rb") as svg_file:
            svg_content = svg_file.read()

        temp_png = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        cairosvg.svg2png(bytestring=svg_content, write_to=temp_png.name)

        if os.path.exists(temp_png.name):
            return temp_png.name
        else:
            raise FileNotFoundError(f"PNG file not created from {svg_path}")
    except Exception as e:
        st.error(f"Error converting SVG to PNG: {str(e)}")
        return None

# carica immagine SVG dal percorso fornito e restituisce il contenuto come stringa.
@st.cache_data
def load_svg(image_path):
    try:
        with open(image_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {image_path}")
        return None

# funzione per visualizzare immagini SVG nel report HTML
def display_graph_image(image_path):
    svg_content = load_svg(image_path)
    if svg_content:
        svg_encoded = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{svg_encoded}" alt="Grafo selezionato" style="width:100%; max-width:600px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("Unable to load the graph image.")

# funzione per generare il report in PDF
def generate_pdf_report(graph_logs):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # titolo del report
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Loop Activity Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)  # torna alla dimensione normale del font
    pdf.ln(10)

    # aggiunge attività nel pdf con funzione cell()
    for graph, activities in graph_logs.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=f"Selected Graph: {graph}", ln=True, align="L")  # nome grafo

        first_session = activities[0]
        pdf.set_font("Arial", size=12)
        formatted_timestamp = first_session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        pdf.cell(200, 10, txt=f"On {formatted_timestamp}, you performed the following activities:", ln=True)
  # linea che dice quando ha fatto le attività
        pdf.ln(5)

        # aggiunge l'immagine del grafo principale
        if 'image_path' in first_session:
            image_path = first_session['image_path']
            png_image_path = convert_svg_to_png(image_path)

            if png_image_path and os.path.exists(png_image_path):
                pdf.ln(5)
                pdf.cell(200, 10, txt="Graph Image:", ln=True)
                pdf.image(png_image_path, x=(210 - 190) // 2, w=190)  # immagine larga e centrata del grafo
                pdf.ln(10)
            else:
                pdf.cell(200, 10, txt="Unable to load the graph image.", ln=True)

        # altre attività + immagini dei loop
        for session in activities:
            if 'activity' in session and "Hai selezionato il grafo" not in session['activity']:
                activity_text = session['activity']
                pdf.multi_cell(0, 10, txt=f"- {activity_text}", align="L")

                # se questa attività è un salvataggio di un'immagine, aggiunge l'immagine sotto l'attività
                if "You saved the image" in activity_text:
                    loop_image_path = session.get('loop_image_path')
                    if loop_image_path:
                        loop_png_image_path = convert_svg_to_png(loop_image_path)
                        if loop_png_image_path and os.path.exists(loop_png_image_path):
                            pdf.ln(5)
                            pdf.image(loop_png_image_path, x=(210 - 120) // 2, w=120)  # i loop vengono centrati nella pagina del pdf
                        else:
                            pdf.cell(200, 10, txt=f"Unable to load saved loop image: {loop_image_path}", ln=True)

        # separatore per ogni sezione
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # linea separatrice
        pdf.ln(5)

    # creazione e salvataggio per successivo download del pdf
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(pdf_file)

    st.session_state['loop_pdf_report'] = pdf_file
    return pdf_file

# funzione per mostrare il report in streamlit
def show_report():
    if 'graph_logs' not in st.session_state or not st.session_state['graph_logs']:
        st.error("No activities logged yet.")
        st.info("Once you select the CLD and submit the form, you will be able to see here the chosen CLD, the information about the filters and the saved images. Everytime you will change the CLD, a new section will be created.")
        return

    st.title("Report Loop Page")

    for grafo, activities in st.session_state['graph_logs'].items():
        st.markdown(f"### Selected Causal Loop Diagram: {grafo}")

        graph_image_path = None
        graph_timestamp = None
        for activity in activities:
            if 'image_path' in activity:
                graph_image_path = activity['image_path']
                graph_timestamp = activity['timestamp']
                break

        if graph_image_path:
            display_graph_image(graph_image_path)
        else:
            st.error(f"Graph image for {grafo} not found in session state!")

        formatted_timestamp = graph_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        st.markdown(f"**On {formatted_timestamp} you performed the following activities:**")


        # mostra le attività
        st.markdown("### Activities:")
        for log in activities:
            if 'activity' in log and "Hai selezionato il grafo" not in log['activity']:
                st.markdown(f"* {log['activity']}")
            if 'loop_image_path' in log:
                if os.path.exists(log['loop_image_path']):
                    display_graph_image(log['loop_image_path'])
                else:
                    st.error(f"Image not found: {log['loop_image_path']}")
        st.markdown("---")

    # Verifica se ci sono nuove attività rispetto all'ultimo PDF generato
    if 'last_activity_timestamp' not in st.session_state or \
            st.session_state['last_activity_timestamp'] < max([activity['timestamp'] for activities in st.session_state['graph_logs'].values() for activity in activities]):
        st.session_state['last_activity_timestamp'] = pd.Timestamp.now()

        # Genera il PDF ogni volta che si visita la pagina report o ci sono nuove attività
        with st.spinner('Generating PDF report...'):
            pdf_file = generate_pdf_report(st.session_state['graph_logs'])

    if 'loop_pdf_report' in st.session_state:
        with open(st.session_state['loop_pdf_report'], "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="loop_activity_report.pdf",
                mime="application/pdf"
            )

# Esegui il report
show_report()
