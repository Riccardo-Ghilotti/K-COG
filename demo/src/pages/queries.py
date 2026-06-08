import streamlit as st


with st.container():
    # Move queries bit into another page
    st.subheader("Queries")

    st.markdown("""
                Two queries to wikidata were used to get the information we needed to construct the ontology.
                The first one recovers the most populated cities in Europe:
                """)

    st.code("""
            SELECT ?city ?cityLabel ?countryLabel (SAMPLE(?population) AS ?population) (SAMPLE(?coord) AS ?coord) 
            WHERE { 
                ?city wdt:P31/wdt:P279* wd:Q515 ; 
                      wdt:P17 ?country ; 
                      wdt:P1082 ?population . 
                ?country wdt:P30 wd:Q46 . 
                FILTER(?population >= 500000 || EXISTS { ?country wdt:P36 ?city }) 
                MINUS { ?city wdt:P31 wd:Q3024240 } 
                MINUS { ?city wdt:P17 / wdt:P31 wd:Q3024240 }
                OPTIONAL { ?city wdt:P625 ?coord } 
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en, [AUTO_LANGUAGE], mul" } 
            } 
            GROUP BY ?city ?cityLabel ?countryLabel 
            ORDER BY DESC(?population)
        """, language="sparql")
    
    st.markdown("""
            Then, for every city extracted by the first query, the second query extracts all the point of interests that belong in that city:
            """)
        
    st.code("""
            SELECT DISTINCT ?place ?placeLabel ?typeLabel ?coord ?inception
            WHERE {
                ?place wdt:P131* wd:{city_qid} .
                ?place wdt:P31/wdt:P279* ?type .
                VALUES ?type {
                    wd:Q570116 wd:Q839954 wd:Q4989906 wd:Q33506
                    wd:Q16560  wd:Q44613  wd:Q2977    wd:Q23413
                    wd:Q12518  wd:Q174782 wd:Q24354   wd:Q22698
                    wd:Q23397  wd:Q4022   wd:Q483110  wd:Q118554787
                    wd:Q40080  wd:Q34038  wd:Q8502    wd:Q132510
                    wd:Q16970  wd:Q34627  wd:Q32815
                }
                OPTIONAL { ?place wdt:P625 ?coord }
                OPTIONAL { ?place wdt:P571 ?inception }
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en,[AUTO_LANGUAGE], mul" }
            }
        """, language="sparql")
           
           
    POI_TYPES = {
        "Heritage & history": [
            ("Tourist attraction", "Q570116"),
            ("Archaeological site", "Q839954"),
            ("Monument", "Q4989906"),
            ("Castle", "Q23413"),
            ("Palace", "Q16560"),
        ],
        "Religious buildings": [
            ("Cathedral", "Q2977"),
            ("Church building", "Q16970"),
            ("Monastery", "Q44613"),
            ("Synagogue", "Q34627"),
            ("Mosque", "Q32815"),
        ],
        "Culture & arts": [
            ("Museum", "Q33506"),
            ("Gallery", "Q118554787"),
            ("Theatre building", "Q24354"),
            ("Market", "Q132510"),
            ("Stadium", "Q483110"),
        ],
        "Urban spaces": [
            ("Square", "Q174782"),
            ("Park", "Q22698"),
            ("Tower", "Q12518"),
        ],
        "Nature": [
            ("Lake", "Q23397"),
            ("River", "Q4022"),
            ("Beach", "Q40080"),
            ("Waterfall", "Q34038"),
            ("Mountain", "Q8502"),
        ],
    }

    WIKIDATA_BASE = "https://www.wikidata.org/wiki/"

    for category, items in POI_TYPES.items():
        st.markdown(f"#### **{category}**")
        # 3 columns per row
        cols = st.columns(3)
        for i, (label, qid) in enumerate(items):
            with cols[i % 3]:
                st.markdown(f"[{label} `{qid}`]({WIKIDATA_BASE}{qid})")
        st.markdown("")  # spacing between groups
           
           
           #TODO cancellare
        # st.markdown("""
        #     In the second query, every point of interest has been chosen looking at wikidata's types for buildings.
        #     The chosen types of buildings extracted are:
        #     - Tourist attraction (Q570116)
        #     - Archaeological site (Q839954)
        #     - Monument (Q4989906)
        #     - Museum (Q33506)
        #     - Palace (Q16560)
        #     - Monastery (Q44613)
        #     - Cathedral (Q44613)
        #     - Castle (Q23413)
        #     - Tower (Q12518)
        #     - Square (Q174782)
        #     - Theatre building (Q24354)
        #     - Park (Q22698)
        #     - Lake (Q23397)
        #     - River (Q4022)
        #     - Stadium (Q483110)
        #     - Art gallery (Q1007870) --> mo gallery Q118554787
        #     - Beach (Q40080)
        #     - Waterfall (Q34038)
        #     - Mountain (Q8502)
        #     - Market (Q132510)
        #     - Church building (Q16970)
        #     - Synagogue (Q34627)
        #     - Mosque (Q32815)
        # """)
        
    st.image("./images/Milan_points_of_interest.png", caption="Points of interest of Milan")