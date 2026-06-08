import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from streamlit_theme import st_theme

from pages.cache import load_custom_bert, load_vanilla_bert

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Embedding Explorer",
    layout="wide"
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Embedding Explorer")
st.subheader("3D Visualization - BERT vs KCOG-BERT")

theme = st_theme()
is_dark = False
if theme:
    is_dark = theme["base"] == "dark"

# ── Theme detection ───────────────────────────────────────────────────────────
def get_theme_colors():
    return {
        "paper_bg":      "#13131f" if is_dark else "#ffffff",
        "scene_bg":      "#1a1a2e" if is_dark else "#f8f8f8",
        "grid_color":    "#3a3a5c" if is_dark else "#dddddd",
        "tick_color":    "#8888aa" if is_dark else "#888888",
        "text_color":    "#e0e0ff" if is_dark else "#222222",
        "title_color":   "#ffffff" if is_dark else "#000000",
        "marker_default": "#6666aa" if is_dark else "#aaaacc",
    }

# ── Dimensionality reduction ──────────────────────────────────────────────────
def reduce_to_3d(embeddings: np.ndarray, method: str) -> np.ndarray:
    """
    embeddings: shape (N, 768) - N must be > 1 for meaningful reduction.
    Returns: shape (N, 3)
    """
    if method == "PCA":
        reducer = PCA(n_components=3, random_state=42)
        return reducer.fit_transform(embeddings)
    else:  # t-SNE
        perplexity = min(5, max(1, len(embeddings) - 1))
        reducer = TSNE(n_components=3, random_state=42, perplexity=perplexity)
        return reducer.fit_transform(embeddings)

# ── 3D Plot builder ───────────────────────────────────────────────────────────
def build_3d_scatter(coords: np.ndarray, labels: list[str],
                     highlight_idx: int, color_accent: str,
                     title: str) -> go.Figure:
    theme = get_theme_colors()
    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
    colors = [color_accent if i == highlight_idx else "#334" for i in range(len(labels))]
    sizes  = [14 if i == highlight_idx else 8 for i in range(len(labels))]

    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers+text",
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.92,
            line=dict(color="#000", width=0.5),
        ),
        text=labels,
        textposition="top center",
        textfont=dict(family="JetBrains Mono", size=11, color=theme["text_color"]),
        hovertemplate="<b>%{text}</b><br>x: %{x:.3f}<br>y: %{y:.3f}<br>z: %{z:.3f}<extra></extra>",
        showlegend=False,
    ),
    go.Scatter3d(                          # ← origin trace
            x=[0], y=[0], z=[0],
            mode="markers+text",
            marker=dict(
                size=3,
                color="#ff4444",
                opacity=1.0,
                line=dict(color="#000", width=1),
            ),
            text=["origin"],
            textposition="top center",
            textfont=dict(family="JetBrains Mono", size=10, color=theme["text_color"]),
            hovertemplate="<b>Origin</b><br>x: 0<br>y: 0<br>z: 0<extra></extra>",
            showlegend=False,
    )])

    fig.update_layout(
        title=dict(text=title, font=dict(family="Syne", size=14, color=theme["title_color"]), x=0.5),
        paper_bgcolor=theme["paper_bg"],
        scene=dict(
            bgcolor=theme["scene_bg"],
            xaxis=dict(showgrid=True, gridcolor=theme["grid_color"], zeroline=False,
                       tickfont=dict(color=theme["tick_color"], size=9), title=""),
            yaxis=dict(showgrid=True, gridcolor=theme["grid_color"], zeroline=False,
                       tickfont=dict(color=theme["tick_color"], size=9), title=""),
            zaxis=dict(showgrid=True, gridcolor=theme["grid_color"], zeroline=False,
                       tickfont=dict(color=theme["tick_color"], size=9), title=""),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=480,
    )
    return fig

# ── Controls ──────────────────────────────────────────────────────────────────
ctrl_col1, ctrl_col2 = st.columns([1, 1])
with ctrl_col1:
    with st.form("embedding_form", border = False):
        sentence_input = st.text_input(
            "Insert a sentence",
            placeholder="e.g. house, school, computer...",
        )
        calc_btn = st.form_submit_button("Compute Embedding")

with ctrl_col2:
    reduction_method = st.radio(
                "Reduction Method",
                ["PCA", "t-SNE"],
                horizontal=True
            )

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Session state: store past embeddings for context ─────────────────────────
if "history_sentences" not in st.session_state:
    st.session_state.history_sentences = []
if "history_vanilla" not in st.session_state:
    st.session_state.history_vanilla = []
if "history_custom" not in st.session_state:
    st.session_state.history_custom = []

# ── Compute on button click ───────────────────────────────────────────────────
if calc_btn and sentence_input.strip():
    sentence = sentence_input.strip()
    with st.spinner("Computing embeddings..."):
        vanilla_bert = load_vanilla_bert()
        custom_bert = load_custom_bert()

        emb_v = vanilla_bert.get_sentence_embedding(sentence)
        emb_c = custom_bert.get_sentence_embedding(sentence)

    # Add to history (keep last 20)
    if sentence not in st.session_state.history_sentences:
        st.session_state.history_sentences.append(sentence)
        st.session_state.history_vanilla.append(emb_v)
        st.session_state.history_custom.append(emb_c)

    st.success(f"Embedding computed for **{sentence}** - {len(st.session_state.history_sentences)} sentences in memory")
    
# ── Render plots ──────────────────────────────────────────────────────────────
if len(st.session_state.history_sentences) >= 3:
    sentences = st.session_state.history_sentences
    all_vanilla = np.array(st.session_state.history_vanilla)  # (N, 768)
    all_custom  = np.array(st.session_state.history_custom)   # (N, 768)
    highlight   = len(sentences) - 1  # last sentence = highlighted

    # Need at least 3 points for reduction; 
    coords_v = reduce_to_3d(all_vanilla, reduction_method)
    coords_c = reduce_to_3d(all_custom,  reduction_method)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_v = build_3d_scatter(coords_v, sentences, highlight,
                                "#7b61ff", f"{reduction_method} - BERT")
        st.plotly_chart(fig_v, use_container_width=True)

    with col_right:
        fig_c = build_3d_scatter(coords_c, sentences, highlight,
                                "#ff6bce", f"{reduction_method} - KCOG-BERT")
        st.plotly_chart(fig_c, use_container_width=True)
else:
    # Empty state
    st.write("Insert at least 3 sentences")