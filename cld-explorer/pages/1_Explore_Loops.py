import base64

import pandas as pd
import streamlit as st
from db_config import get_connection
from loops_generator import generate_graphs

st.set_page_config(layout="wide", page_title="CLD-Explorer")

# controllo se la chiave 'graph_logs' esiste nello stato della sessione. Se non esiste, la chiave viene creata e associata a un dizionario vuoto.
if "graph_logs" not in st.session_state:
    st.session_state["graph_logs"] = {}


def log_activity(activity_description):

    # ottengo il grafo selezionato dall'utente, oppure si imposta su 'Unknown' se non è stato selezionato ancora nulla.
    loop_grafo_scelto = st.session_state.get("loop_grafo_scelto", "Unknown")

    # se non esiste un log per il grafo corrente, lo creo
    if loop_grafo_scelto not in st.session_state["graph_logs"]:
        st.session_state["graph_logs"][loop_grafo_scelto] = []

    # logga l'attività solo se non si tratta della selezione del grafo
    # aggiunge un nuovo log all'interno della lista di log di quel grafo. Ogni log contiene un timestamp e una descrizione dell'attività,passata come parametro alla funzione
    st.session_state["graph_logs"][loop_grafo_scelto].append(
        {"timestamp": pd.Timestamp.now(), "activity": activity_description}
    )


# esegue la query e ottieni i risultati
def run_query(query):
    conn = get_connection()
    if conn is not None:
        try:
            df = pd.read_sql(
                query, conn
            )  # esegue la query  e restituisce i risultati come dataFrame di Pandas.
            if df.empty:
                st.warning(
                    "There are no results that meet your request. Please try with other filters"
                )  # se il df è vuoto, avvisa l'utente che non ci sono risultati per la query.
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
        finally:
            conn.close()
    else:
        return pd.DataFrame()  # restituisce un data frame vuoto in caso di errore


# funzione per caricare file SVG
# @st.cache_data  # per memorizzare il risultato della funzione in cache, se viene chiamata più volte con lo stesso image_path
def load_svg(image_path):
    try:
        with open(image_path, "r", encoding="utf-8") as file:
            return file.read()  # lo restituisce come stringa
    except FileNotFoundError:
        st.error(f"File not found: {image_path}")
        return None


# aggiorna il grafo selezionato, quando si cambia grafo
def update_graph_selection():

    st.session_state["loop_grafo_scelto"] = st.session_state["radio_selection"]
    if "grafo_scelto" in st.session_state:
        st.session_state["grafo_scelto"] = st.session_state["loop_grafo_scelto"]

    # salvo il image path del grafo
    if st.session_state["loop_grafo_scelto"].lower() == "covid":
        st.session_state["graph_image_path"] = "./assets/graph_covid.svg"
    elif st.session_state["loop_grafo_scelto"].lower() == "fashion":
        st.session_state["graph_image_path"] = "./assets/graph_fashion.svg"
    elif st.session_state["loop_grafo_scelto"].lower() == "australian hotel":
        st.session_state["graph_image_path"] = "./assets/graph_hotel.svg"
    elif st.session_state["loop_grafo_scelto"].lower() == "custom":
        st.session_state["graph_image_path"] = "./output/custom_diagram.svg"


# funzione per visualizzare l'immagine SVG con zoom
def display_svg_with_zoom_pan(image_path, width="100%"):
    svg_content = load_svg(image_path)
    if svg_content:
        svg_encoded = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"  # codifica il contenuto SVG in base64 per renderlo compatibile con HTML.
        st.markdown(
            f"""
            <style>
            .zoom-container {{
                width: {width}; /* Imposta una larghezza fissa solo se necessario */
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
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Unable to load the SVG content.")


# la stessa come sopara ma usata per i loop perchè devono essere più piccole le foto e centrate
def display_loop_svg(image_path, width="500px"):
    svg_content = load_svg(image_path)
    if svg_content:
        svg_encoded = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
        st.markdown(
            f"""
            <style>
            .loop-container {{
                display: flex;
                justify-content: center; /* Centra l'immagine orizzontalmente */
                align-items: center;
                width: 100%; /* Larghezza massima del contenitore */
                height: auto;
                overflow: hidden;
                position: relative;
                border: 1px solid black;
                cursor: grab;
                margin-bottom: 20px;
            }}
            .loop-container img {{
                width: {width}; /* Imposta una larghezza ridotta per le immagini dei loop */
                height: auto;
                transition: transform 0.2s ease-in-out;
                transform-origin: center center;
            }}
            .loop-container:active {{
                cursor: grabbing;
            }}
            </style>
            <div class="loop-container">
                <img src="{svg_encoded}" class="loop-content">
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Unable to load the SVG content.")


# primo carosello di immagini
def show_main_carousel(
    side_by_side=False,
):  # side_by_side è settato a falso perchè non deve essere visualizzato affiancato inizialmente
    if "loop_generated_files" in st.session_state:
        images = st.session_state[
            "loop_generated_files"
        ]  # questa chiave dovrebbe contenere i file delle immagini generate per il carosello.
        # print(f"Immagini nel primo carosello: {images}")

        if len(images) == 0:  # verifica se la lista è vuota
            st.warning(
                "There are no results that meet your request. Please try with other filters"
            )
            return

        # se l'indice corrente dell'immagine non è ancora stato inizializzato nella sessione, viene impostato a 0
        if "loop_main_image_index" not in st.session_state:
            st.session_state["loop_main_image_index"] = 0

        # contiene l'indice della foto corrente del carosello
        current_index = st.session_state["loop_main_image_index"]

        col1, col2, col3 = st.columns([1, 6, 1])

        # usa chiavi diverse se stiamo visualizzando i caroselli affiancati
        prev_key = "main_prev_button_side" if side_by_side else "main_prev_button"
        next_key = "main_next_button_side" if side_by_side else "main_next_button"
        save_key = (
            f"save_main_image_{current_index}_side"
            if side_by_side
            else f"save_main_image_{current_index}"
        )

        with col1:
            if st.button("⬅️", key=prev_key):
                st.session_state["loop_main_image_index"] = (current_index - 1) % len(
                    images
                )
                current_index = st.session_state["loop_main_image_index"]

        with col3:
            if st.button("➡️", key=next_key):
                st.session_state["loop_main_image_index"] = (current_index + 1) % len(
                    images
                )
                current_index = st.session_state["loop_main_image_index"]

        display_loop_svg(images[current_index], width="500px")

        # per la visualizazzione dell'indice dell'immagine nel carosello
        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 10px;'>
                Image {st.session_state['loop_main_image_index'] + 1} of {len(images)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # pulsante per salvare l'immagine corrente
        if st.button("Save this image", key=save_key):

            # controlla se la lista 'loop_saved_images' esiste in st.session_state. Se non esiste, la crea come una lista vuota.
            if "loop_saved_images" not in st.session_state:
                st.session_state["loop_saved_images"] = []

            current_image_path = images[current_index]  # percorso immagine corrente

            # verifica se l'immagine corrente è già nella lista delle immagini salvate
            already_saved = any(
                saved_image["loop_image_path"] == current_image_path
                for saved_image in st.session_state["loop_saved_images"]
            )

            if already_saved:
                st.warning("You already saved this image!")
            else:
                saved_image_data = {
                    "timestamp": pd.Timestamp.now(),
                    "loop_image_path": current_image_path,
                    "carosello": "first",
                    "loop_grafo_scelto": st.session_state["loop_grafo_scelto"],
                }
                st.session_state["loop_saved_images"].append(saved_image_data)

                image_position = f"{current_index + 1}/{len(images)}"
                # st.write(st.session_state['loop_saved_images'])
                st.success("Image saved successfully!")

                log_activity(
                    f"You saved the image {image_position} from the first carousel generated above."
                )
                st.session_state["graph_logs"][st.session_state["loop_grafo_scelto"]][
                    -1
                ]["loop_image_path"] = saved_image_data["loop_image_path"]


# funzione per il reset della pagina
def reset_query_state():
    keys_to_reset = [
        "loop_generated_files",
        "current_loop_image_index",
        "loop_type",
        "loop_length",
        "loop_node_name",
        "compare_loop_generated_files",
        "compare_loop_image_index",
        "loop_show_compare_form",
        "loop_show_side_by_side",
        "loop_previous_carousel_filters",
    ]

    # reset forzato dei dati in sessione
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    # reset esplicito dei filtri selezionati nel form
    st.session_state["loop_type"] = "No Filter"
    st.session_state["loop_length"] = "No Filter"
    st.session_state["loop_node_name"] = "No Filter"


def reset_form_state():
    # reset esplicito dei filtri selezionati nel form perchè Gesù cristo prima non andava, non so perchè
    st.session_state["loop_type"] = "No Filter"
    st.session_state["loop_length"] = "No Filter"
    st.session_state["loop_node_name"] = "No Filter"


# funzione del secondo carosello, come quello sopra, ma cambiano le chiavi dei bottoni obv;)
def show_compare_carousel(side_by_side=False):
    if "compare_loop_generated_files" in st.session_state:
        images = st.session_state["compare_loop_generated_files"]
        print(f"Immagini nel secondo carosello: {images}")

        if len(images) == 0:
            st.warning(
                "There are no reuslts that meet your request Please try with other filters"
            )
            return

        if "compare_loop_image_index" not in st.session_state:
            st.session_state["compare_loop_image_index"] = 0

        current_index = st.session_state["compare_loop_image_index"]

        col1, col2, col3 = st.columns([1, 6, 1])

        # Usa chiavi diverse se stiamo visualizzando i caroselli affiancati
        prev_key = "compare_prev_button_side" if side_by_side else "compare_prev_button"
        next_key = "compare_next_button_side" if side_by_side else "compare_next_button"
        save_key = (
            f"save_compare_image_{current_index}_side"
            if side_by_side
            else f"save_compare_image_{current_index}"
        )

        with col1:
            if st.button("⬅️", key=prev_key):
                st.session_state["compare_loop_image_index"] = (
                    current_index - 1
                ) % len(images)
                current_index = st.session_state["compare_loop_image_index"]

        with col3:
            if st.button("➡️", key=next_key):
                st.session_state["compare_loop_image_index"] = (
                    current_index + 1
                ) % len(images)
                current_index = st.session_state["compare_loop_image_index"]

        display_loop_svg(images[current_index], width="500px")

        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 10px;'>
                Image {st.session_state['compare_loop_image_index'] + 1} of {len(images)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Save this image", key=save_key):
            # controlla se l'immagine è già stata salvata
            if "loop_saved_images" not in st.session_state:
                st.session_state["loop_saved_images"] = []

            current_image_path = images[current_index]

            # verifica se l'immagine corrente è già nella lista delle immagini salvate
            already_saved = any(
                saved_image["loop_image_path"] == current_image_path
                for saved_image in st.session_state["loop_saved_images"]
            )

            if already_saved:
                st.warning("You already saved this image!")
            else:
                saved_image_data = {
                    "timestamp": pd.Timestamp.now(),
                    "loop_image_path": current_image_path,
                    "carosello": "second",
                    "loop_grafo_scelto": st.session_state["loop_grafo_scelto"],
                }
                st.session_state["loop_saved_images"].append(saved_image_data)

                image_position = f"{current_index + 1}/{len(images)}"
                # st.write(st.session_state['loop_saved_images'])
                st.success("Image saved successfully!")

                log_activity(
                    f"You saved the image {image_position} from the second carousel generated above."
                )
                st.session_state["graph_logs"][st.session_state["loop_grafo_scelto"]][
                    -1
                ]["loop_image_path"] = saved_image_data["loop_image_path"]


# funzione per affiancare i due caroselli
def show_side_by_side_carousels():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### First Carousel")
        show_main_carousel(
            side_by_side=True
        )  # Aggiungiamo un prefisso per evitare conflitti

    with col2:
        st.markdown("### Second Carousel")
        show_compare_carousel(side_by_side=True)


# funzione principale per la pagina Loop
def loop_page():

    st.markdown(
        """
    <style>
    /* Cambia il colore del bottone con il testo "Submit" */
    div.stButton > button:has(span:contains("Submit")) {
        background-color: white;
        color: black;
    }

    /* Cambia il colore del bottone con il testo "Compare with other loops" */
    div.stButton > button:has(span:contains("Compare with other loops")) {
        background-color: white;
        color: black;
    }

    /* Cambia il colore del bottone con il testo "Compare selected Loops" */
    div.stButton > button:has(span:contains("Compare selected Loops")) {
        background-color: white;
        color: black;
    }
    </style>
""",
        unsafe_allow_html=True,
    )

    st.title("Explore Loops")

    st.subheader("What can you do in this page?")

    st.markdown(
        """
    -  Select the CLD from the options.
    -  Review the CLD and its statistics displayed below. You can see the **total number of loops**, **the number of balancing loops**, **the number of reinforcing loops**,**the number of loops by length range** and **how many distinct loops each variable takes part to.**
    -  Use the form to select the loop type, the length, and a specific variable and generate the loops with those filters.
    -  You can next compare 2 different sets of loops by generating a second carousel and using the comparison button.
    -  Save any images you want to keep for your analysis in the report.
    -  Use the reset button to clear your filters and start a new analysis with the same or with a  different CLD.
    """
    )

    # imposta il valore di default del grafo se non è stato selezionato nulla(quello covid)
    if "loop_grafo_scelto" not in st.session_state:
        st.session_state["loop_grafo_scelto"] = "Covid"

    if "graph_image_path" not in st.session_state:
        st.session_state["graph_image_path"] = "./assets/graph_covid.svg"

    # # grafo di default registrato
    # if "radio_selection" not in st.session_state:
    #     if "loop_grafo_scelto" in st.session_state:
    #         st.session_state["radio_selection"] = st.session_state["loop_grafo_scelto"]
    #     else:
    #         st.session_state["radio_selection"] = "Covid"

    # radio button per cambiare grafo
    # st.write(st.session_state["loop_grafo_scelto"])
    # st.write(st.session_state["radio_selection"])
    st.radio(
        "Select the CLD ",
        ("Covid", "Fashion", "Australian Hotel", "Custom"),
        index=("Covid", "Fashion", "Australian Hotel", "Custom").index(
            " ".join(
                (x.capitalize() for x in st.session_state["loop_grafo_scelto"].split())
            )
        ),
        # index=0,
        key="radio_selection",
        on_change=update_graph_selection,
    )

    # determina il grafo scelto e la tabella associata
    if st.session_state["loop_grafo_scelto"].lower() == "covid":
        table_name = "loops_covid"
        grafo = "relationships_covid"
        image_path = "./assets/graph_covid.svg"
        file_name = "graph_from_files1.svg"
        nodes = [
            "economic_growth",
            "unemployment",
            "business_restrictions",
            "interventions",
            "social_restrictions",
            "government_stimulus_package",
            "speed_of_government_action",
            "ICU_admission",
            "confirmed_cases",
            "mental_wellbeing",
            "one_health",
            "health_worker_load",
            "health_service_capacity",
            "access_to_health_service",
            "prevention_practices_for_many_pathologies",
            "travel_restrictions",
            "social_interactions",
            "new_dangerous_variant",
        ]
    elif st.session_state["loop_grafo_scelto"].lower() == "fashion":
        table_name = "loops_fashion"
        grafo = "relationships_fashion"
        image_path = "./assets/graph_fashion.svg"
        file_name = "graph_from_files2.svg"
        nodes = [
            "consumer_income_spending_power",
            "investments_in_marketing",
            "consumers_desire_to_buy",
            "purchases_of_new_clothes",
            "availability_of_second_hand_clothes",
            "owned_clothes",
            "market_competitiveness",
            "fashion_industry_profit",
            "production_costs",
            "production_intensity",
            "global_economic_trends",
            "government_policies",
            "enviroinmental_regulations",
            "clothing_production",
            "clothes_quality",
            "clothes_thrown_away",
            "clothing_lifespan",
            "clothes_washes",
            "consumers_awareness",
            "incentives_for_sustainability",
            "work_exploitation",
            "landfills_exploitation",
            "natural_resources_exploitation",
            "chemical_pollution",
            "greenhouse_gases_emission",
            "energy consumption",
            "textile_waste",
            "fashion_industry_footprint",
            "innovations_for_transition",
            "industry_investments_in_sustainability",
            "fashion_industry_sustainability",
        ]
    elif st.session_state["loop_grafo_scelto"].lower() == "australian hotel":
        table_name = "loops_australian_hotel"
        grafo = "relationships_australian_hotel"
        image_path = "./assets/graph_hotel.svg"
        file_name = "graph_from_files3.svg"
        nodes = [
            "number_of_hotels_adopting_RET",
            "demand_for_small_medium_scale_RET",
            "distribution_network_usage",
            "gross_electricity_retail_profit_margin",
            "lobby_government_to_remove_RET_incentive",
            "incentive_policy",
            "owner_manager_perception_of_RET_financial_benefits",
            "hotel_sets_aside_money_for_RET_investment",
            "efficiency_of_engineers_at_hotel",
            "electricity_retailer_perception_of_RET_financial_benefits",
            "large_scale_RET_investment",
            "australias_emissions_amount",
            "gap_between_target_and_actual_emission",
            "owner_manager_awareness_of_energy_conservation_method_financial_benefits",
            "hotels_adoption_of_other_energy_conservation_methods",
            "hotels_energy_demand_profile",
            "value_of_hotels_electricity_bill",
            "hotels_profit",
            "amount_of_energy_charged_by_electricity_retailer",
            "domestic_and_other_industries_electricity_bills",
            "innovation_investment",
            "RET_technology_maturity_and_storage",
            "reliability_of_electricity_produced_by_RET",
            "RET_benefits",
            "price_of_RET",
            "tourists_willingness_to_stay_in_RET_hotel",
            "hotel_owner_manager_perception_of_RET_as_competitive_advantage",
            "gap_between_cost_of_electricity from grid and from RET",
            "gap_between_RET_investment_and_purchasing_electricity_with greenPower",
            "hotel_purchase_electricity_with greenPower",
            "tourist_awareness_and_attitude_about environment",
            "green_tourists_environmentally_friendly_behaviour",
            "tourists_electricity_consumption in room",
            "extreme_weather",
            "hotels_in_the_same_brand_bargain_together",
            "hotel_rating",
            "hotel_participant_of_brand_affiliation",
            "proximity_of_hotel_location_to_urban_area",
            "hotel_availability_of_space",
            "electricity_retailer options",
            "tourist_perceived_levels_of_comfort_and_value_of price",
            "cost_of_non_renewable supply",
        ]
    elif st.session_state["loop_grafo_scelto"].lower() == "custom":
        table_name = "loops_custom"
        grafo = "relationships_custom"
        image_path = "./output/custom_diagram.svg"
        file_name = "graph_from_files1.svg"
        nodes = run_query(f"SELECT node_name FROM nodes_custom")["node_name"].tolist()
        print("Nodes from the custom graph:" + str(nodes))

    # visualizzazione del grafo selezionato
    st.markdown(f"### CLD: {st.session_state['loop_grafo_scelto'].capitalize()}")
    display_svg_with_zoom_pan(image_path)

    # Da qua visualizzazione del preview

    # numero totale di loop
    query_total_loops = f"SELECT count(*) FROM {table_name};"
    total_loops = run_query(query_total_loops)["count(*)"][0]

    # nmero di loop balancing e reinforcing
    query_balancing_loops = (
        f"SELECT count(*) FROM {table_name} WHERE state='balancing';"
    )
    balancing_loops = run_query(query_balancing_loops)["count(*)"][0]

    query_reinforcing_loops = (
        f"SELECT count(*) FROM {table_name} WHERE state='reinforcing';"
    )
    reinforcing_loops = run_query(query_reinforcing_loops)["count(*)"][0]

    # numero di loop per range di lunghezza
    query_loop_length = f"""
    SELECT 
        CASE 
            WHEN l.loop_length <= 5 THEN 'length<=5'
            WHEN l.loop_length BETWEEN 6 AND 10 THEN '5<length<=10'
            WHEN l.loop_length BETWEEN 11 AND 15 THEN '10<length<=15'
            WHEN l.loop_length BETWEEN 16 AND 20 THEN '15<length<=20'
            WHEN l.loop_length BETWEEN 21 AND 25 THEN '20<length<=25'
            ELSE 'k>25'
        END AS length_range,
        COUNT(*) AS number_of_loops
    FROM {table_name} AS l
    GROUP BY length_range;
    """
    loop_length_df = run_query(query_loop_length)

    # abella con nodi e numero di loop in cui sono coinvolti
    query_node_loops = f"""
    WITH NodeCounts AS (
        SELECT node_name, COUNT(*) AS count
        FROM bridge_nodes_{table_name}
        GROUP BY node_name
    )
    SELECT node_name AS variable_name, count AS number_of_loops
    FROM NodeCounts
    ORDER BY node_name ASC;
    """
    node_loop_df = run_query(query_node_loops)

    # layout delle metriche
    st.markdown(f"## Loops Overview")

    # visualizzazione della display del numero totale di loop
    st.metric(label="Total Loops", value=total_loops)

    # visualizzazione della display dei loop balancing e reinforcing
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Balancing Loops", value=balancing_loops)
    with col2:
        st.metric(label="Reinforcing Loops", value=reinforcing_loops)

    # visualizzazione della tabella numero di loop per range di lunghezza
    st.markdown("### Number of loops by length range")
    st.table(loop_length_df)

    # visualizzazione della ttabella odi e numero di loop in cui sono coinvolti
    st.markdown("### Variables and the number of distinct loops they are involved in")
    st.table(node_loop_df)

    # form dei filtri
    st.markdown("## Find Loops")
    with st.form(key="loop_filter_form"):
        # selezione de tipo
        loop_type = st.selectbox(
            "Select the loop type",
            ["No Filter", "Balancing", "Reinforcing"],
            key="loop_type",
        )

        # selezione lunghezza
        loop_length = st.selectbox(
            "Select the loop length",
            ["No Filter"] + list(range(2, 26)),
            key="loop_length",
        )

        # selezione del nodo
        # Usa solo le variabili che partecipano ai loop
        variables_in_loops = ["No Filter"] + node_loop_df["variable_name"].tolist()
        selected_node = st.selectbox(
            "Select a variable", variables_in_loops, key="loop_node_name"
        )

        submit = st.form_submit_button("Submit")

    if submit:
        # logga la selezione del grafo solo al primo submit
        if (
            st.session_state["loop_grafo_scelto"] not in st.session_state["graph_logs"]
            or not st.session_state["graph_logs"][st.session_state["loop_grafo_scelto"]]
        ):
            st.session_state["graph_logs"][st.session_state["loop_grafo_scelto"]] = []
            st.session_state["graph_logs"][
                st.session_state["loop_grafo_scelto"]
            ].append(
                {
                    "timestamp": pd.Timestamp.now(),
                    "image_path": st.session_state["graph_image_path"],
                }
            )

        if "loop_previous_carousel_filters" not in st.session_state:
            st.session_state["loop_previous_carousel_filters"] = {}

        current_filters = {
            "loop_type": loop_type,
            "loop_length": loop_length,
            "loop_node_name": selected_node,
        }

        # generazione dei caroslli
        if st.session_state["loop_previous_carousel_filters"] != current_filters:
            # print(f"Generazione primo carosello: Loop Type={loop_type}, Loop Length={loop_length}, Node Name={selected_node}")
            loop_generated_files = generate_graphs(
                table_name,
                grafo,
                loop_type=loop_type,
                loop_length=loop_length,
                node_name=selected_node,
                carousel_type="main",
            )
            # print(f"File generati per il primo carosello: {loop_generated_files}")
            st.session_state["loop_generated_files"] = loop_generated_files
            st.session_state["current_loop_image_index"] = (
                0  # reset dell'indice quando vengono generate nuove immagini
            )

            # aggiorna i filtri precedenti con quelli attuali
            st.session_state["loop_previous_carousel_filters"] = current_filters

            if not loop_generated_files:
                # st.warning("There are no results that meet your request.")
                log_activity(
                    f"You have generated the first carousel with the following filter: loop type={loop_type}, loop length={loop_length}, variable={selected_node} but no results were found"
                )
            else:

                # log di generazione effettiva del primo carosello
                if (
                    loop_type == "No Filter"
                    and loop_length == "No Filter"
                    and selected_node == "No Filter"
                ):
                    log_activity(
                        "You have generated the first carousel without any filter"
                    )
                else:
                    log_activity(
                        f"You have generated the first carousel with the following filter: loop rype={loop_type}, loop length={loop_length}, variable={selected_node}"
                    )

    # mostra il carosello di immagini
    if "loop_generated_files" in st.session_state and not st.session_state.get(
        "loop_show_side_by_side", False
    ):
        show_main_carousel()

        if "loop_show_compare_form" not in st.session_state:
            st.session_state["loop_show_compare_form"] = False

        # bottone per generare il secondo carosello
        if st.button("Compare with other loops"):
            st.session_state["loop_show_compare_form"] = True

        # mostra il secondo form solo dopo che il bottone Compare è stato premuto
        if st.session_state["loop_show_compare_form"]:
            st.markdown("## Find Loops for the second carousel")
            with st.form(key="compare_loop_filter_form"):
                compare_loop_type = st.selectbox(
                    "Select the loop type",
                    ["No Filter", "Balancing", "Reinforcing"],
                    key="compare_loop_type",
                )
                compare_loop_length = st.selectbox(
                    "Select the loop length",
                    ["No Filter"] + list(range(2, 26)),
                    key="compare_loop_length",
                )
                compare_selected_node = st.selectbox(
                    "Select a variable",
                    ["No Filter"] + nodes,
                    key="compare_selected_node",
                )
                compare_submit = st.form_submit_button("Submit")

            if compare_submit:
                # richiama la funzione per generare i grafici per il secondo carosello
                # print(f"Generazione secondo carosello: Loop Type={compare_loop_type}, Loop Length={compare_loop_length}, Node Name={compare_selected_node}")
                compare_loop_generated_files = generate_graphs(
                    table_name,
                    grafo,
                    loop_type=compare_loop_type,
                    loop_length=compare_loop_length,
                    node_name=compare_selected_node,
                    carousel_type="compare",
                )
                # print(f"File generati per il secondo carosello: {compare_loop_generated_files}")
                st.session_state["compare_loop_generated_files"] = (
                    compare_loop_generated_files
                )
                st.session_state["compare_loop_image_index"] = 0
                if not compare_loop_generated_files:
                    # Loggare che non ci sono risultati per il secondo carosello
                    log_activity(
                        f"You have generated the second carousel with the following filters: loop type={compare_loop_type}, loop length={compare_loop_length}, variable={compare_selected_node}, but no results were found"
                    )
                else:
                    # log dell'attività di generazione del secondo carosello
                    if (
                        compare_loop_type == "No Filter"
                        and compare_loop_length == "No Filter"
                        and compare_selected_node == "No Filter"
                    ):
                        log_activity(
                            "You have generated the second carousel without any filter"
                        )
                    else:
                        # log_activity(f"You have generated the first carousel with the following filter: Loop Type={loop_type}, Loop Length={loop_length}, Varible Name={selected_node}")
                        log_activity(
                            f"You have generated the second carousel with the following filters: loop type={compare_loop_type}, loop length={compare_loop_length}, variable={compare_selected_node}"
                        )

            # mostra il secondo carosello
            if "compare_loop_generated_files" in st.session_state:
                show_compare_carousel()

                # pulsante per affiancare i caroselli solo dopo aver generato il secondo carosello
                if st.button("Compare selected Loops"):
                    st.session_state["loop_show_side_by_side"] = True

    # mostra i caroselli affiancati
    if st.session_state.get("loop_show_side_by_side", False):
        show_side_by_side_carousels()

    # pulsnte reset
    if st.session_state.get("loop_generated_files") or st.session_state.get(
        "compare_loop_generated_files"
    ):
        if st.button("Reset All"):
            reset_query_state()
            reset_form_state()
            # log_activity("Hai resettato la pagina.")
            st.rerun()


if __name__ == "__main__":
    loop_page()
