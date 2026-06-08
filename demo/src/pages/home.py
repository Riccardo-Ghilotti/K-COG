import streamlit as st
from streamlit_theme import st_theme

st.markdown("## K-COG - Knowledge COverage Graph")
st.markdown("""
    A tool for comparing knowledge graphs against text corpora, highlighting which parts 
    of a candidate ontology are covered, missing, or exclusive to the source text.
    
    Applied here to European city ontologies derived from Wikidata and Wikivoyage.
""")

st.divider()

with st.container():
    st.header("Goal of the project")
    st.markdown("""
        We focused on creating a pipeline that allows Knowledge Graph and text corpus comparison.
        
        Given a corpus and a knowledge graph, highlights which part of the knowledge graph is not covered by the corpus.
        
        To achieve that, we extract the concepts of a text corpus and then we compare those to the ones we extract from the candidate ontology.
        
        In this website, it is possible to explore the results achieved in our domain case.
        
        However, the whole pipeline is consultable and downloadable in the following repository.
    """)
    
    st.link_button(label="GitHub Repository", url="https://github.com/Riccardo-Ghilotti/K-COG", type="primary", icon=":material/commit:", icon_position="left")

st.divider()



st.markdown("#### In this domain we have worked with")
c1, c2, c3 = st.columns(3)
c1.metric("European cities", 133, border=True)
c2.metric("POI types", 23,  border=True)
c3.metric("BERT models", 2, border=True)

st.divider()

# Pipeline
st.markdown("#### Project pipeline")

theme = st_theme()
is_dark = False
if theme and theme["base"] == "dark":
    path_pipeline = "./images/pipeline_scurapng.png"
else:
    path_pipeline = "./images/pipeline_chiarapng.png"

_, col_img, _ = st.columns([1, 5, 1])
with col_img:
    st.image(path_pipeline,)
