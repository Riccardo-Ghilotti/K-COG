import streamlit as st
import pandas as pd

from pages.cache import load_metrics



# =========================
# CONFIG / TITLE
# =========================
st.set_page_config(page_title="Metrics Dashboard", layout="wide")

# darken graph notation
st.markdown("""
<style>
[data-testid="stVegaLiteChart"] text {
    fill: #333333 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Metrics Dashboard")


col1, col2, col3 = st.columns([8, 1, 8])
with col1:
    st.header("Basic Concepts")
    st.markdown(r"""
    Let $O$ be the number of concepts in the candidate ontology.  

    Let $D$ be the number of domain concepts extracted from the domain corpus after pruning.  

    Let $S$ be the number of shared concepts between the candidate ontology and the domain concepts extracted from the corpus.  

    Let $H$ be the number of concepts in the subset of the candidate ontology constructed by taking the shared concepts and expanding them using the ontology’s hierarchical relations.
    """)

    st.header("Basic Metrics")
    st.markdown("To determine the completeness of the candidate ontology, we compute three metrics: Ontology Relevance, Sub-Ontology Relevance, and Domain Coverage based upon three quantifcations of the concept overlap between the candidate ontology and the concept set extracted from the text corpus, representing the domain")

    st.latex(r'\text{Domain Coverage} = \frac{S}{D}')
    st.latex(r'\text{Ontology Relevance} = \frac{S}{O}')
    st.latex(r'\text{Sub-Ontology Relevance} = \frac{S}{H}')

    st.header("Advanced Concepts")

    st.markdown("""
    Let C be a set of concepts, R a set of relations, and A a set of associations such that:
    """)

    st.latex(r'A \subseteq \{\, r(x,y) \mid \forall r \in R,\ \forall x \in C,\ \forall y \in C \,\}')

    st.markdown("""
    An ontology O is defined as a triple:
    """)

    st.latex(r'O = \langle C, R, A \rangle')

    

# st.divider()

with col3:
    
    st.markdown(r"""
    Let $O = \langle C, R, A \rangle$ be an ontology and $r_{\text{IS-A}} \in R$.

    A Concept Family (CF) is defined as follows:
    """)

    st.latex(r'CF = \langle C_p, C_s \rangle')

    st.latex(r'C_p \in C,\quad C_s \subseteq C,\quad \forall c \in C_s \Rightarrow r_{\text{IS-A}}(c, C_p)')
    
    # st.divider()
    st.header("Advanced Metrics")
    st.markdown("""
        ### Child Similarity Score (CSS)

        Child Similarity Score (CSS) is the mean cosine similarity between every pair of siblings in a Concept Family (CF). We define this function where M is the number of CF child concepts.
    """)
    st.latex(r'CSS(CF) = \frac{2}{M(M-1)} \sum_{i=1}^{M-1}\sum_{j=i+1}^{M} similarity(C_i, C_j)')

    st.markdown("""
        

        ### Parent Similarity Score (PSS)

        Parent Similarity Score (PSS) is the mean cosine similarity between the parent and each of its direct child concepts.

        Where P is the parent concept and M is the number of child concepts.
    """)
    st.latex(r'PSS(CF) = \frac{1}{M} \sum_{i=1}^{M} similarity(C_i, C_p)')

    st.markdown("""
        

        ### Parent Difference Agreement (PDA)

        Parent Difference Agreement (PDA) makes use of the standard deviation of the similarity between the parent concept and its direct children. It can be interpreted as the amount of agreement between the siblings towards the parent with respect to similarity.
        """)

    st.latex(r'''PDA(CF) = 1 - \sqrt{\frac{1}{M-1} \sum_{i=1}^{M} (similarity(C_i, C_p) - PSS(CF))^2}''')
            
# =========================
# LOAD DATA
# =========================
data = load_metrics()

# =========================
# BERT SECTION
# =========================
with st.expander("BERT Metrics"):
# st.header("BERT Metrics")

    df_bert = pd.DataFrame(data["BERT"])
    df_bert = df_bert.drop(["mean_CSS", "mean_PSS", "mean_PDA"], axis=1)


    st.header("Metric values per configuration")
    st.table(df_bert)

    st.header("Metric trends across configurations")
    st.subheader("CSS")
    st.bar_chart(df_bert.iloc[0], stack=False, color="#e05653")
    st.subheader("PSS")
    st.bar_chart(df_bert.iloc[1], stack=False, color="#c4ab64")
    st.subheader("PDA")
    st.bar_chart(df_bert.iloc[2], stack=False, color="#46a67d")

# =========================
# KCOG-BERT SECTION
# =========================
with st.expander("KCOG-BERT Metrics"):

    df_kcog = pd.DataFrame(data["KCOG-BERT"])
    df_kcog = df_kcog.drop(["mean_CSS", "mean_PSS", "mean_PDA"], axis=1)

    st.header("Metric values per configuration")
    st.table(df_kcog)

    st.header("Metric trends across configurations")
    st.subheader("CSS")
    st.bar_chart(df_kcog.iloc[0], stack=False, color="#e05653")
    st.subheader("PSS")
    st.bar_chart(df_kcog.iloc[1], stack=False, color="#c4ab64")
    st.subheader("PDA")
    st.bar_chart(df_kcog.iloc[2], stack=False, color="#46a67d")

with st.expander("Metrics Summary"):
    # =========================
    # SUMMARY TABLE
    # =========================
    table_data = {
        "Domain Coverage": data["Domain Coverage"],
        "Ontology Relevance": data["Ontology Relevance"],
        "Sub-Ontology Relevance": data["Sub-Ontology Relevance"],
        "mean CSS (BERT)": data["BERT"]["mean_CSS"],
        "mean PSS (BERT)": data["BERT"]["mean_PSS"],
        "mean PDA (BERT)": data["BERT"]["mean_PDA"],
        "mean CSS (KCOG-BERT)": data["KCOG-BERT"]["mean_CSS"],
        "mean PSS (KCOG-BERT)": data["KCOG-BERT"]["mean_PSS"],
        "mean PDA (KCOG-BERT)": data["KCOG-BERT"]["mean_PDA"]
    }

    df_summary = pd.DataFrame(list(table_data.items()), columns=["Metric", "Value"])

    st.table(df_summary)
    

    plot_df = pd.DataFrame({
        "Domain Coverage": [data["Domain Coverage"]],
        "Ontology Relevance": [data["Ontology Relevance"]],
        "Sub-Ontology Relevance": [data["Sub-Ontology Relevance"]]
    })

    # fondamentale: le etichette diventano l'asse X
    plot_df.index = ["Metrics"]

    st.header("Domain Metrics")

    st.bar_chart(
        plot_df,
        use_container_width=True,
        stack=False,
        color = ["#e05653","#c4ab64","#46a67d"]
    )

    metrics_df = pd.DataFrame({
        "Metric": ["CSS", "PSS", "PDA"],
        "BERT": [
            data["BERT"]["mean_CSS"],
            data["BERT"]["mean_PSS"],
            data["BERT"]["mean_PDA"]
        ],
        "KCOG-BERT": [
            data["KCOG-BERT"]["mean_CSS"],
            data["KCOG-BERT"]["mean_PSS"],
            data["KCOG-BERT"]["mean_PDA"]
        ]
    })

    st.header("Intrinsic Metrics Comparison (BERT vs KCOG-BERT)")

    colors = ["#698996","#407076"]
    st.bar_chart(metrics_df.set_index("Metric"), use_container_width=True, stack=False, color = colors)