import streamlit as st

if __name__ == "__main__":

    st.set_page_config(
        page_title="Esame IA 2025-2026",
        page_icon="🥇",
        layout="wide",
    )   
    
    pages = {
    "": [
        st.Page("./pages/home.py", title="Home", icon=":material/home:"),
        st.Page("./pages/queries.py", title="Queries"),
        st.Page("./pages/wikivoyage_resources.py", title="Wikivoyage Corpus Map"),
        st.Page("./pages/created_ontology.py", title="Ontology"),
        st.Page("./pages/metrics.py", title="Metrics"),
        st.Page("./pages/bert_comparison.py", title="Bert comparison"),
        ],
    }

    pg = st.navigation(pages, position="top")
    pg.run()
    