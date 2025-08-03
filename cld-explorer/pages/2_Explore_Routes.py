import base64

import pandas as pd
import streamlit as st
from db_config import get_connection
from routes_generator import generate_route_graphs

st.set_page_config(layout="wide", page_title="CLD-Explorer")

# controllo se la chiave 'graph_logs' esiste nello stato della sessione. Se non esiste, la chiave viene creata e associata a un dizionario vuoto.
if "route_graph_logs" not in st.session_state:
    st.session_state["route_graph_logs"] = {}


def log_activity_route(activity_description):

    # ottengo il grafo selezionato dall'utente, oppure si imposta su 'Unknown' se non è stato selezionato ancora nulla.
    grafo_scelto = st.session_state.get("grafo_scelto", "Unknown")

    # if 'route_graph_logs' not in st.session_state:
    #   st.session_state['route_graph_logs'] = {}

    # se non esiste un log per il grafo corrente, lo creo
    if grafo_scelto not in st.session_state["route_graph_logs"]:
        st.session_state["route_graph_logs"][grafo_scelto] = []

    # logga l'attività solo se non si tratta della selezione del grafo
    # aggiunge un nuovo log all'interno della lista di log di quel grafo. Ogni log contiene un timestamp e una descrizione dell'attività,passata come parametro alla funzione
    st.session_state["route_graph_logs"][grafo_scelto].append(
        {"timestamp": pd.Timestamp.now(), "activity": activity_description}
    )


# funzione per eseguire query
def run_query(query):
    conn = get_connection()
    if conn is not None:
        try:
            df = pd.read_sql(
                query, conn
            )  # esegue la query  e restituisce i risultati come dataFrame di Pandas.
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
        finally:
            conn.close()
    else:
        return pd.DataFrame()  # restituisce un data frame vuoto in caso di errore


# @st.cache_data
def load_svg(image_path):
    try:
        with open(image_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {image_path}")
        return None


# funzione per resettare lo stato della sessione
def reset_query_state():

    # chiavi da resettare
    keys_to_reset = [
        "route_generated_files",
        "current_route_image_index",
        "route_type",
        "route_length",
        "compare_route_generated_files",
        "compare_route_image_index",
        "route_show_compare_form",
        "route_show_side_by_side",
        "route_previous_carousel_filters",
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state["route_type"] = "No Filter"
    st.session_state["route_length"] = "No Filter"


def reset_form_state():

    st.session_state["route_type"] = "No Filter"
    st.session_state["route_length"] = "No Filter"


# funzione per aggiornare la selezione del grafo
def update_graph_selection():
    # aggiorna il grafo selezionato
    st.session_state["grafo_scelto"] = st.session_state["radio_selection"]
    st.session_state["loop_grafo_scelto"] = st.session_state["radio_selection"]

    if st.session_state["grafo_scelto"].lower() == "covid":
        st.session_state["graph_image_path"] = "./assets/graph_covid.svg"
    elif st.session_state["grafo_scelto"].lower() == "fashion":
        st.session_state["graph_image_path"] = "./assets/graph_fashion.svg"
    elif st.session_state["grafo_scelto"].lower() == "australian hotel":
        st.session_state["graph_image_path"] = "./assets/graph_hotel.svg"
    elif st.session_state["grafo_scelto"].lower() == "custom":
        st.session_state["graph_image_path"] = "./assets/graph_covid.svg"


# funzione per visualizzare l'immagine SVG con zoom
def display_svg_with_zoom_pan(image_path, width="100%"):
    svg_content = load_svg(image_path)
    if svg_content:
        svg_encoded = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"  # codifica il contenuto SVG in base64 per renderlo compatibile con HTML.
        st.markdown(
            f"""
            <style>
            .zoom-container {{
                width: {width};
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
def display_route_svg(image_path, width="500px"):
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


# primo carosello di immagini come quella dei loop
def show_main_carousel(side_by_side=False):

    if (
        "route_generated_files" in st.session_state
    ):  # questa chiave dovrebbe contenere i file delle immagini generate per il carosello.
        images = st.session_state["route_generated_files"]
        print(f"Immagini nel primo carosello: {images}")

        if len(images) == 0:
            st.warning(
                "There are no results that meet your request. Please try again with other filters"
            )
            return

        if "current_route_image_index" not in st.session_state:
            st.session_state["current_route_image_index"] = 0

        current_index = st.session_state["current_route_image_index"]

        col1, col2, col3 = st.columns([1, 6, 1])

        # Usa chiavi diverse se stiamo visualizzando i caroselli affiancati
        prev_key = "main_prev_button_side" if side_by_side else "main_prev_button"
        next_key = "main_next_button_side" if side_by_side else "main_next_button"
        save_key = (
            f"save_main_image_{current_index}_side"
            if side_by_side
            else f"save_main_image_{current_index}"
        )

        with col1:
            if st.button("⬅️", key=prev_key):
                st.session_state["current_route_image_index"] = (
                    current_index - 1
                ) % len(images)
                current_index = st.session_state["current_route_image_index"]

        with col3:
            if st.button("➡️", key=next_key):
                st.session_state["current_route_image_index"] = (
                    current_index + 1
                ) % len(images)
                current_index = st.session_state["current_route_image_index"]

        display_route_svg(images[current_index], width="500px")

        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 10px;'>
                Image {st.session_state['current_route_image_index'] + 1} of {len(images)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # pulsante salva immagine corrente
        if st.button("Save this Route into report", key=save_key):
            # controlla se l'immagine è già stata salvata
            if "saved_route_images" not in st.session_state:
                st.session_state["saved_route_images"] = []

            current_image_path = images[
                current_index
            ]  # percorso dell'immagine corrente

            # verifica se l'immagine corrente è già nella lista delle immagini salvate
            already_saved = any(
                saved_image["route_image_path"] == current_image_path
                for saved_image in st.session_state["saved_route_images"]
            )

            if already_saved:
                st.warning("You already saved this image!")
            else:
                saved_image_data = {
                    "timestamp": pd.Timestamp.now(),
                    "route_image_path": current_image_path,
                    "carosello": "first",
                    "grafo_scelto": st.session_state[
                        "grafo_scelto"
                    ],  # aggiunge il grafo selezionato
                }
                st.session_state["saved_route_images"].append(saved_image_data)

                image_position = f"{current_index + 1}/{len(images)}"
                st.success("Image saved successfully!")
                log_activity_route(
                    f"You saved the image {image_position} from the first carousel generated above."
                )
                st.session_state["route_graph_logs"][st.session_state["grafo_scelto"]][
                    -1
                ]["route_image_path"] = saved_image_data["route_image_path"]


def show_compare_carousel(side_by_side=False):
    if "compare_route_generated_files" in st.session_state:
        images = st.session_state["compare_route_generated_files"]
        print(f"Immagini nel secondo carosello: {images}")

        if len(images) == 0:
            st.warning(
                "There are no reuslts that meet your request. Please try again with other filters."
            )
            return

        if "compare_route_image_index" not in st.session_state:
            st.session_state["compare_route_image_index"] = 0

        current_index = st.session_state["compare_route_image_index"]

        col1, col2, col3 = st.columns([1, 6, 1])

        prev_key = "compare_prev_button_side" if side_by_side else "compare_prev_button"
        next_key = "compare_next_button_side" if side_by_side else "compare_next_button"
        save_key = (
            f"save_compare_image_{current_index}_side"
            if side_by_side
            else f"save_compare_image_{current_index}"
        )

        with col1:
            if st.button("⬅️", key=prev_key):
                st.session_state["compare_route_image_index"] = (
                    current_index - 1
                ) % len(images)
                current_index = st.session_state["compare_route_image_index"]

        with col3:
            if st.button("➡️", key=next_key):
                st.session_state["compare_route_image_index"] = (
                    current_index + 1
                ) % len(images)
                current_index = st.session_state["compare_route_image_index"]

        display_route_svg(images[current_index], width="500px")

        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 10px;'>
                Image {st.session_state['compare_route_image_index'] + 1} of {len(images)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Save this image", key=save_key):

            if "saved_route_images" not in st.session_state:
                st.session_state["saved_route_images"] = []

            current_image_path = images[current_index]

            already_saved = any(
                saved_image["route_image_path"] == current_image_path
                for saved_image in st.session_state["saved_route_images"]
            )

            if already_saved:
                st.warning("You already saved this image!")
            else:
                saved_image_data = {
                    "timestamp": pd.Timestamp.now(),
                    "route_image_path": current_image_path,
                    "carosello": "second",
                    "grafo_scelto": st.session_state["grafo_scelto"],
                }
                st.session_state["saved_route_images"].append(saved_image_data)
                image_position = f"{current_index + 1}/{len(images)}"
                # st.write(st.session_state['loop_saved_images'])
                st.success("Image saved successfully!")

                log_activity_route(
                    f"You saved the image {image_position} from the second carousel generated above."
                )
                st.session_state["route_graph_logs"][st.session_state["grafo_scelto"]][
                    -1
                ]["route_image_path"] = saved_image_data["route_image_path"]


def show_side_by_side_carousels():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### First cart")
        show_main_carousel(side_by_side=True)

    with col2:
        st.markdown("### Second cart")
        show_compare_carousel(side_by_side=True)


# fnzione per il count delle route
def get_route_count(table_name, start_node):
    query = f"""
        SELECT COUNT(*) AS route_count
        FROM {table_name}
        WHERE start_node = '{start_node}';
    """
    result = run_query(query)
    if not result.empty:
        return result.iloc[0]["route_count"]
    return 0


# funzioen per ottenere gli end node e il numero di increasing e decreasing route
def get_route_details(
    table_name, start_node, route_length="No Filter", route_type="No Filter"
):
    query = f"""
        SELECT 
            end_node AS end_variable,
            SUM(CASE WHEN state = 'increasing' THEN 1 ELSE 0 END) AS number_of_increasing_routes,
            SUM(CASE WHEN state = 'decreasing' THEN 1 ELSE 0 END) AS number_of_decreasing_routes
        FROM {table_name}
        WHERE start_node = '{start_node}'
    """

    # filtro per la lunghezza della route
    if route_length != "No Filter":
        query += f" AND route_length = {route_length}"

    # filtro per il tipo di route (increasing, decreasing)
    if route_type != "No Filter":
        query += f" AND state = '{route_type}'"

    query += " GROUP BY end_node"

    query += " ORDER BY number_of_increasing_routes DESC;"
    # Questo ti permetterà di vedere l'output della query
    df = run_query(query)

    # converte i valori di increasing_count e decreasing_count in numeri interi
    df["number_of_increasing_routes"] = df["number_of_increasing_routes"].astype(int)
    df["number_of_decreasing_routes"] = df["number_of_decreasing_routes"].astype(int)

    return df


# funzione pagina route
def route_page():
    # st.set_page_config(layout="wide", page_title="Route Analysis")

    st.title("Explore Routes")

    # mini introduzione con sottotitolo
    st.subheader("What can you do in this page?")

    st.markdown(
        """
    -  Select the CLD from the options.
    -  Select a start variable for the routes and analyze the information displayed below. You can see the **total number of routes starting from the chosen variable**, which are the possible end variable and how many routes there are beetwen the chosen start variable and each end variable.           
    -  Select an end variable
    -  Use the filter form to select the route type and the length.
    -  Next you can compare 2 different sets of routes by generating a second set of filtered routes and using the comparison button.
    -  Save any images you want to keep for your analysis in the report.
    -  Use the reset button to clear your filters and start a new analysis with the same or with a different CLD.
    """
    )

    # imposta il valore di default del grafo se non è stato selezionato nulla
    if "grafo_scelto" not in st.session_state:
        if "loop_grafo_scelto" in st.session_state:
            st.session_state["grafo_scelto"] = st.session_state["loop_grafo_scelto"]
        else:
            st.session_state["grafo_scelto"] = "Covid"
            st.session_state["graph_image_path"] = "./assets/graph_covid.svg"

    # if "radio_selection" not in st.session_state:
    #     # if "radio_selection" in st.session_state:
    #     #     st.session_state["radio_selection_2"] = st.session_state["radio_selection"]
    #     # else:
    #     #     st.session_state["radio_selection_2"] = "Covid"
    #     st.session_state["radio_selection"] = "Covid"

    st.radio(
        "Select the CLD:",
        ("Covid", "Fashion", "Australian Hotel", "Custom"),
        index=("Covid", "Fashion", "Australian Hotel", "Custom").index(
            # st.session_state["radio_selection"]
            " ".join((x.capitalize() for x in st.session_state["grafo_scelto"].split()))
        ),
        key="radio_selection",
        on_change=update_graph_selection,
    )

    if st.session_state["grafo_scelto"].lower() == "covid":
        table_name = "routes_covid"
        grafo = "relationships_covid"
        image_path = "./assets/graph_covid.svg"
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
    elif st.session_state["grafo_scelto"].lower() == "fashion":
        table_name = "routes_fashion"
        grafo = "relationships_fashion"
        image_path = "./assets/graph_fashion.svg"
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
    elif st.session_state["grafo_scelto"].lower() == "australian hotel":
        table_name = "routes_australian_hotel"
        grafo = "relationships_australian_hotel"
        image_path = "./assets/graph_hotel.svg"
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
    elif st.session_state["grafo_scelto"].lower() == "custom":
        table_name = "routes_custom"
        grafo = "relationships_custom"
        image_path = "./output/custom_diagram.svg"
        nodes = run_query(f"SELECT node_name FROM nodes_custom")["node_name"].tolist()

    # visualizzazione del grafo selezionato
    st.markdown(f"### CLD: {st.session_state['grafo_scelto'].capitalize()}")
    display_svg_with_zoom_pan(image_path)

    # selezione del nodo di partenza
    st.markdown(f"### Routes preview")
    # Ordina la lista dei nodi in modo insensibile al caso
    nodes = sorted(nodes, key=lambda x: x.lower())

    # Seleziona il nodo di partenza
    selected_node = st.selectbox("Select the start variable ", nodes, key="node_name")

    # da qua visualizzazione del preview
    if selected_node:
        # st.markdown(f"### Routes preview for start variable: {selected_node}")
        route_count = get_route_count(table_name, selected_node)
        st.metric(
            label=f"Number of routes starting from {selected_node}:", value=route_count
        )

        # Ordina la tabella in base alla colonna 'end_variable'
        route_details = get_route_details(table_name, selected_node)
        # route_details = route_details.sort_values(by='end_variable',key=lambda col: col.str.lower())

        st.markdown("### Possible end variables")
        st.table(route_details)

        if not route_details.empty:
            end_nodes = sorted(
                route_details["end_variable"].tolist(), key=lambda x: x.lower()
            )
            selected_end_node = st.selectbox(
                "Choose the end variable:", end_nodes, key="end_variable"
            )
            # st.write(f"End node selected: {selected_end_node}")

        if route_details.empty:
            st.warning(
                "There are no routes starting from the selected variable. Please try with another variable."
            )
            return

        # form per selezionare filtri
        st.markdown("## Find Routes")
        with st.form(key="route_filter_form"):
            route_type = st.selectbox(
                "Select route type:",
                ["No Filter", "increasing", "decreasing"],
                key="route_type",
                index=["No Filter", "increasing", "decreasing"].index(
                    st.session_state.get("route_type", "No Filter")
                ),
            )
            route_length = st.selectbox(
                "Select route length:",
                ["No Filter"] + list(range(1, 31)),
                key="route_length",
                index=(["No Filter"] + list(range(1, 31))).index(
                    st.session_state.get("route_length", "No Filter")
                ),
            )

            submit_filter = st.form_submit_button("Submit")

        if submit_filter:
            # verifica se esistono log del grafo
            if (
                st.session_state["grafo_scelto"]
                not in st.session_state["route_graph_logs"]
            ):
                st.session_state["route_graph_logs"][
                    st.session_state["grafo_scelto"]
                ] = []

            # gnera il carosello solo se i filtri sono cambiati
            if "route_previous_carousel_filters" not in st.session_state:
                st.session_state["route_previous_carousel_filters"] = {}

            current_filters = {"route_type": route_type, "route_length": route_length}

            if st.session_state["route_previous_carousel_filters"] != current_filters:
                route_generated_files = generate_route_graphs(
                    table_name,
                    grafo,
                    route_length,
                    route_type,
                    selected_node,
                    selected_end_node,
                )
                if not route_generated_files:
                    st.warning(
                        "There are no results that meet your request.  Please try again with other filters"
                    )

                    # Aggiungi il log per il report
                    log_activity_route(
                        f"You have generated the first carousel with the following filters: start variable= {selected_node}, end variable= {selected_end_node}, route type= {route_type}, route length= {route_length} but no results were found"
                    )
                else:
                    st.session_state["route_generated_files"] = route_generated_files
                    st.session_state["current_route_image_index"] = 0

                    # aggiorna i filtri precedenti con quelli attuali
                    st.session_state["route_previous_carousel_filters"] = (
                        current_filters
                    )

                    # log dell'attività di generazione del primo carosello
                    if route_type == "No Filter" and route_length == "No Filter":
                        log_activity_route(
                            f"You have generated the first carousel with start variable={selected_node} and end variable={selected_end_node}, but without any filter"
                        )
                    else:
                        log_activity_route(
                            f"You have generated the first carousel with the following filters: start variable= {selected_node}, end variable= {selected_end_node}, route type={route_type}, route length={route_length}"
                        )
            if (
                "image_path"
                not in st.session_state["route_graph_logs"][
                    st.session_state["grafo_scelto"]
                ][-1]
            ):
                st.session_state["route_graph_logs"][st.session_state["grafo_scelto"]][
                    -1
                ]["image_path"] = st.session_state["graph_image_path"]
            # log dell'immagine del grafo solo ora, dopo l'attività
            if not any(
                "image_path" in log
                for log in st.session_state["route_graph_logs"][
                    st.session_state["grafo_scelto"]
                ]
            ):
                st.session_state["route_graph_logs"][
                    st.session_state["grafo_scelto"]
                ].append(
                    {
                        "timestamp": pd.Timestamp.now(),
                        "image_path": st.session_state["graph_image_path"],
                    }
                )

    # mostra il carosello principale
    if "route_generated_files" in st.session_state and not st.session_state.get(
        "route_show_side_by_side", False
    ):
        show_main_carousel()

        # bottone per generare il secondo carosello
        if "route_show_compare_form" not in st.session_state:
            st.session_state["route_show_compare_form"] = False

        if st.button("Compare with other Routes"):
            st.session_state["route_show_compare_form"] = True

        if st.session_state["route_show_compare_form"]:
            st.markdown("## Filter Routes (Comparison)")
            with st.form(key="compare_route_filter_form"):
                compare_route_type = st.selectbox(
                    "Select route type:",
                    ["No Filter", "increasing", "decreasing"],
                    key="compare_route_type",
                )
                compare_route_length = st.selectbox(
                    "Select route length:",
                    ["No Filter"] + list(range(1, 31)),
                    key="compare_route_length",
                )
                compare_submit = st.form_submit_button("Submit")

            if compare_submit:
                compare_route_generated_files = generate_route_graphs(
                    table_name,
                    grafo,
                    route_length=compare_route_length,
                    route_type=compare_route_type,
                    start_node=selected_node,
                    end_node=selected_end_node,
                )

                # verifica se ci sonorisultati
                if not compare_route_generated_files:
                    st.warning(
                        "There are no results that meet your request. Please try again with other filters"
                    )
                    log_activity_route(
                        f"You have generated the second carousel with the following filters: route type= {route_type}, route length= {route_length} but no results were found"
                    )
                else:
                    st.session_state["compare_route_generated_files"] = (
                        compare_route_generated_files
                    )
                    st.session_state["compare_route_image_index"] = 0

                    # log dell'attività di generazione del secondo carosello
                    if (
                        compare_route_type == "No Filter"
                        and compare_route_length == "No Filter"
                    ):
                        log_activity_route(
                            "You have generated the second carousel without any filter"
                        )
                    else:
                        log_activity_route(
                            f"You generate dthe second carousel with the followinf filters: route type={compare_route_type}, route length={compare_route_length}"
                        )

        # mostra il secondo carosello
        if "compare_route_generated_files" in st.session_state:
            show_compare_carousel()

            if st.button("Compare selected Routes"):
                st.session_state["route_show_side_by_side"] = True

        # mostra i due caroselli affiancati
    if st.session_state.get("route_show_side_by_side", False):
        show_side_by_side_carousels()

    # pulsante di reset
    if st.session_state.get("route_generated_files") or st.session_state.get(
        "compare_route_generated_files"
    ):
        if st.button("Reset All"):
            reset_query_state()
            reset_form_state()
            st.rerun()


if __name__ == "__main__":
    route_page()
