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

        # Controlla se il file PNG è stato creato correttamente
        if os.path.exists(temp_png.name):
            return temp_png.name
        else:
            raise FileNotFoundError(f"PNG file not created from {svg_path}")
    except Exception as e:
        st.error(f"Error converting SVG to PNG: {str(e)}")
        return None
    
@st.cache_data
def load_svg(image_path):
    try:
        with open(image_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {image_path}")
        return None
    
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


def generate_pdf_report(route_graph_logs):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Route Activity Report", ln=True, align="C")

    pdf.set_font("Arial", size=12)  # Torna alla dimensione normale del font
    pdf.ln(10) 

    for graph, activities in route_graph_logs.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=f"Selected Graph: {graph}", ln=True, align="L")
        first_session = activities[0]
        pdf.set_font("Arial", size=12)
        formatted_timestamp = first_session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        pdf.cell(200, 10, txt=f"On {formatted_timestamp}, you performed the following activities:", ln=True)

        pdf.ln(5)

        # Aggiungi l'immagine del grafo se presente
        if 'image_path' in first_session:
            image_path = first_session['image_path']

            # Converti SVG in PNG e verifica se esiste
            png_image_path = convert_svg_to_png(image_path)

            if png_image_path and os.path.exists(png_image_path):
                pdf.ln(5)
                pdf.cell(200, 10, txt="Graph Image:", ln=True)
                pdf.image(png_image_path, x=(210 - 190) // 2, w=190)  # Mantieni l'immagine larga e centrata
                pdf.ln(10)
            else:
                pdf.cell(200, 10, txt="Unable to load the graph image.", ln=True)

        # Aggiungi tutte le attività, escludendo quelle relative alla selezione del grafo
        for session in activities:
            if 'activity' in session and "Hai selezionato il grafo" not in session['activity']:
                activity_text = session['activity']
                pdf.multi_cell(0, 10, txt=f"- {activity_text}", align="L")

                # Se questa attività corrisponde a un salvataggio di un'immagine, aggiungi l'immagine sotto l'attività
                if "You saved the image" in activity_text:
                    route_image_path = session.get('route_image_path')
                    if route_image_path:
                        route_png_image_path = convert_svg_to_png(route_image_path)
                        if route_png_image_path and os.path.exists(route_png_image_path):
                            pdf.ln(5)
                            pdf.image(route_png_image_path, x=(210 - 120) // 2, w=120)  # Centra l'immagine e riduci la dimensione delle immagini dei loop
                        else:
                            pdf.cell(200, 10, txt=f"Unable to load saved route image: {route_image_path}", ln=True)

        # Aggiungi un separatore per ogni sezione
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)  # Imposta il colore per il separatore (grigio chiaro)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Aggiunge una linea separatrice
        pdf.ln(5)

    # Crea e salva il file PDF
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(pdf_file)

    # Salva il percorso del report PDF nello stato della sessione
    st.session_state['route_pdf_report'] = pdf_file
    return pdf_file

def show_report():
    if 'route_graph_logs' not in st.session_state or not st.session_state['route_graph_logs']:
        st.error("No activities logged yet.")
        st.info("Once you select the CLD and submit the form, you will be able to see here the chosen CLD, the information about the filters and the saved images. Everytime you will change the CLD, a new section will be created.")
        return

    st.title("Report Route Page")

    # Itera su ciascun grafo e mostra le attività registrate
    for grafo, activities in st.session_state['route_graph_logs'].items():
        st.markdown(f"### Selected Causal Loop Diagram: {grafo}")

        # Cerca l'immagine del grafo nel log
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

        # Mostra il testo "On [timestamp] you performed the following activities:" sopra la sezione Activities
        formatted_timestamp = graph_timestamp.strftime('%Y-%m-%d %H:%M:%S')
      
        st.markdown(f"**On {formatted_timestamp} you performed the following activities:**")

        # Mostra le attività (senza la selezione del grafo)
        st.markdown("### Activities:")
        for log in activities:
            if 'activity' in log and "Hai selezionato il grafo" not in log['activity']:
                st.markdown(f"* {log['activity']}")

            if 'route_image_path' in log:
              
              if os.path.exists(log['route_image_path']):
                display_graph_image(log['route_image_path'])
              else:
                st.error(f"Image not found: {log['route_image_path']}")

    # Verifica se ci sono nuove attività rispetto all'ultimo PDF generato
    if 'last_activity_timestamp' not in st.session_state or \
            st.session_state['last_activity_timestamp'] < max([activity['timestamp'] for activities in st.session_state['route_graph_logs'].values() for activity in activities]):
        st.session_state['last_activity_timestamp'] = pd.Timestamp.now()

        # Genera il PDF ogni volta che si visita la pagina report o ci sono nuove attività
        with st.spinner('Generating PDF report...'):
            pdf_file = generate_pdf_report(st.session_state['route_graph_logs'])

    if 'route_pdf_report' in st.session_state:
        with open(st.session_state['route_pdf_report'], "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="route_activity_report.pdf",
                mime="application/pdf"
            )

# Esegui il report
show_report()
