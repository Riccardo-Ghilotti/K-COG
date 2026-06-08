# K-COG — Knowledge COverage Graph

A pipeline for comparing **knowledge graphs against text corpora**, highlighting which parts of a candidate ontology are covered, partially covered, or missing from the source text and vice versa.

Applied here to European city ontologies derived from **Wikidata** and **Wikivoyage**.

---

## Overview

Knowledge graphs and text corpora are two complementary ways of representing domain knowledge, but they are rarely evaluated against each other systematically. K-COG addresses this gap.

Given a **candidate ontology** and a **text corpus**, K-COG:

- Extracts concepts from the corpus using [LangExtract](https://github.com/google/langextract) 
- Compares those concepts against the ontology's nodes and relations
- Quantifies how much of the ontology is "covered" by the corpus, and how much of the corpus is outside the ontology's scope

In this repository, the pipeline is applied to a domain of **133 European cities**, **23 point-of-interest types**, and text sourced from **Wikivoyage** city pages.

---

## Pipeline

```
Wikidata SPARQL  -->  Ontology Extraction  -->  europe_ontology.json
                                                        │
Wikivoyage pages -->  Corpus Extraction    -->  Concept Extraction
                                                        │
                                              BERT Fine-tuning (KCOG-BERT)
                                                        │
                                              Graph Matching & Metrics
```

The full pipeline is implemented as a series of Jupyter notebooks in the `notebooks/` directory:

| Notebook | Description |
|----------|-------------|
| `wikidata-ontology-extraction.ipynb` | SPARQL queries to Wikidata to build the candidate ontology of European cities and their points of interest |
| `extract-corpus.ipynb` | Collects Wikivoyage pages for each city as the text corpus |
| `LangExtract-corpus.ipynb` | Extracts domain concepts from the corpus text |
| `LangExtract-output-merger.ipynb` | Merges and deduplicates concept extraction outputs |
| `extract-graphs.ipynb` | Constructs knowledge graphs from extracted data |
| `BERT-pre-training-dataset-preparation.ipynb` | Prepares the pre-training dataset for domain-adapted BERT |
| `BERT-pre-training-training.ipynb` | Continues the pre-train of BERT on the domain corpus (KCOG-BERT) |
| `ontology-evaluation.ipynb` | Computes coverage metrics between the ontology and the corpus concepts |

---

## Demo

An interactive Streamlit app is available in `demo/` with the following pages:

- **Home**: project overview
- **Queries**: the SPARQL queries used to extract cities and POIs from Wikidata
- **Wikivoyage Corpus Map**: interactive map of the 133 European cities; click any city to visit its Wikivoyage source page
- **Ontology**: interactive graph visualization of the extracted ontologies
- **Metrics**: dashboard with computed coverage metrics and charts
- **BERT Comparison**: 3D embedding explorer comparing vanilla BERT vs KCOG-BERT (PCA and t-SNE projections)

### Running the demo

Download the KCOG-BERT model from the [Kaggle dataset](https://www.kaggle.com/datasets/mattiaingrassia/bert-trained-on-wikivoyage/data) and place it in a newly created `models/` directory at the repository root.

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run demo/src/main.py
```

---

## Repository Structure

```
K-COG/
├── demo/
│   ├── resources/              # Pre-computed JSON data files
│   │   ├── europe_ontology.json
│   │   ├── final_graph_matching.json
│   │   ├── metrics.json
│   │   ├── ontology_extracted.json
│   │   └── wikivoyage_cities.json
│   └── src/
│       ├── main.py             # Streamlit entry point
│       └── pages/
│           ├── home.py
│           ├── queries.py
│           ├── wikivoyage_resources.py
│           ├── created_ontology.py
│           ├── metrics.py
│           ├── bert_comparison.py
│           └── cache.py
├── images/                     # Pipeline diagrams and screenshots
├── notebooks/                  # Full pipeline as Jupyter notebooks
├── requirements.txt
└── README.md
```

---

## Domain at a Glance

| Statistic | Value |
|-----------|-------|
| European cities | 133 |
| Point-of-interest types | 23 |
| BERT models compared | 2 (vanilla + KCOG-BERT) |

POI types include: tourist attraction, archaeological site, monument, museum, palace, monastery, cathedral, square, castle, tower, park, lake, theatre, stadium, gallery, river, beach, waterfall, mountain, market, church, synagogue, mosque.
