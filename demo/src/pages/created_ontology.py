import streamlit as st
import pandas as pd
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge, EdgeStyle, Layout, NodeStyle, DashStyle, NodeShape
import json
import re
import random

# ----------------- UTILITIES
types = {"tourist_attraction", "archaeological_site", "monument", "museum",
    "palace", "monastery", "cathedral", "square", "castle",
    "tower", "park", "lake", "theatre", "stadium", "gallery", 
    "river", "beach", "waterfall", "mountain", "market", "church",
    "synagogue", "mosque"} # types


def extract_cities_and_types(ontology, max_nodes):
    new_ontology = {
        "nodes": random.sample(ontology["nodes"], max_nodes),
        "edges": ontology["edges"]
    } # select random MAX_NODES nodes
    cities = {e["to"] for e in new_ontology["edges"] if e["relation"]=="located_in"}
    new_ontology["nodes"].extend(cities)
    new_ontology["nodes"].extend(types)

    return new_ontology, cities

def extract_cities_and_types_json(ontology, max_nodes, allowed_statuses):
    global types
    all_nodes = ontology["nodes"]

    nodes_by_name = {node["name"]: node for node in all_nodes}
    # fast lookup set

    # filter nodes by selected statuses
    eligible_nodes = [
        node
        for node in ontology["nodes"]
        if node["status"] in allowed_statuses
    ]

    new_ontology = {
        "nodes": random.sample(eligible_nodes, max_nodes),
        "edges": ontology["edges"]
    } # select random MAX_NODES nodes

    cities = {e["to"] for e in new_ontology["edges"] if e["relation"]=="located_in"} # select all cities

    missing = []
    existing_names = {node["name"] for node in new_ontology["nodes"]}

    types = {_type.replace("_", " ") for _type in types}

    for name in cities | types:
        if name in existing_names: 
            continue
        node = nodes_by_name.get(name)
        if node:
            new_ontology["nodes"].append(node)
        else:
            missing.append(name)

    for name in missing:
        print(f"Node not found: {name}")

    return new_ontology, cities


def remove_edges_and_nodes_not_connected(ontology, cities):
    valid_nodes = set(ontology["nodes"]) # remove edges that don't come from and go to selected nodes
    valid_edges = [e for e in ontology["edges"] if e["from"] in valid_nodes and e["to"] in valid_nodes] 

    valid_nodes = set() # remove isolated nodes(adding node types includes some isolated nodes) and remove duplicates
    for edge in valid_edges:
        if (
            edge["from"] not in types 
            and edge["from"] not in cities 
            and edge["from"] != edge["to"]
        ):
            valid_nodes.add(edge["from"])
            valid_nodes.add(edge["to"])
    ontology["nodes"] = list(valid_nodes)

    return ontology, valid_edges


def remove_edges_and_nodes_not_connected_json(ontology, cities):

    valid_node_names = {n["name"] for n in ontology["nodes"]}
    
    valid_edges = []

    connected_names = set()
    for edge in ontology["edges"]:
        if (
            edge["from"] in valid_node_names
            and edge["to"] in valid_node_names
            and edge["from"] != edge["to"]
            and edge["from"] not in types
            and edge["from"] not in cities
        ):
            valid_edges.append(edge)
            connected_names.add(edge["from"])
            connected_names.add(edge["to"])

    ontology["nodes"] = [
        n for n in ontology["nodes"]
        if n["name"] in connected_names
    ]

    

    return ontology, valid_edges


# ----------------- STARTING TEXT

st.title("European Points of Interst Ontologies")

st.markdown("""
This demo explores the construction and comparison of knowledge graphs
describing European cities and points of interest.

The page will show the following:

1. Ontology extracted from Wikivoyage text corpus using LangExtract.
2. Ontology extracted from Wikidata.
3. Graph matching and fusion between the two sources.
""")


# ----------------- ONTOLOGY EXTRACTED FROM LangExtract

st.header("1. Ontology Extracted from Text")

st.markdown("""
This graph represents entities extracted from a textual corpus using
LangExtract. Nodes correspond to cities, landmarks, monuments, museums,
and other cultural heritage entities, while edges represent the semantic
relationships that the LLM had to extract.
""")

MAX_NODES = st.slider("Select the number of nodes", 0, 1000, 100)

ontology = ""
with open("./demo/resources/ontology_extracted.json", encoding='utf-8') as ontology_file:
    ontology = json.load(ontology_file)

ontology, cities = extract_cities_and_types(ontology, MAX_NODES)

ontology, valid_edges = remove_edges_and_nodes_not_connected(ontology, cities)

node_index = {node: i for i, node in enumerate(ontology["nodes"])}


# create the graph
nodes = []
for node in ontology["nodes"]:
    nodes.append(Node(id = node_index[node], properties = {"label": node}))

seen_edges = set() # remove multiple edges
edges = []
for edge in valid_edges:
    if (edge["from"], edge["to"], edge["relation"]) not in seen_edges: # remove multiple edges
        if (edge["from"] == edge["to"]) or edge["from"] in types or edge["from"] in cities:
            seen_edges.add((edge["from"], edge["to"], edge["relation"]))
            continue
        edges.append(Edge(start=node_index[edge["from"]], end=node_index[edge["to"]], properties={"label":edge["relation"]}))
        seen_edges.add((edge["from"], edge["to"], edge["relation"])) # remove multiple edges

StreamlitGraphWidget(nodes=nodes,
                    edges=edges, 
                    edge_styles_mapping = lambda edge: EdgeStyle(
                    color = "red" if edge["properties"]["label"] == "located_in" else "#999"
                    )).show(graph_layout=Layout.HIERARCHIC)

# ----------------- ONTOLOGY CREATED FROM WIKIDATA VISUALIZATION MAP

st.header("2. Reference Ontology from Wikidata")
st.markdown("""
The reference graph is generated using the data extracted from Wikidata and contains structured
information about cities and their associated points of interest.

Nodes are positioned according to their geographic coordinates,
allowing the graph to be visualized directly on a map layout.
""")

MAX_PLACES_PER_CITY = st.slider("Select the number of interest points per city", 0, 40, 10)

# const to extract floating numbers from string
NUMERIC_CONST_PATTERN = r"""
    [-+]?
    (?:
        (?: \d* \. \d+ )
        |
        (?: \d+ \.? )
    )
    (?: [Ee] [+-]? \d+ ) ?
    """
rx = re.compile(NUMERIC_CONST_PATTERN, re.VERBOSE)

ontology = ""
with open("./demo/resources/europe_ontology.json", encoding='utf-8') as ontology_file:
    ontology = json.load(ontology_file)


cities = ontology.keys()

graph = {
    "nodes":[],
    "edges":[]
}
i = 0
for city in cities:
    coord_list = rx.findall(ontology[city]["coord"])
    coord_list = [float(coord_list[1]), float(coord_list[0])]
    properties = {
        "label": city,
        "QID": ontology[city]["QID"],
        "country": ontology[city]["country"],
        "population": ontology[city]["population"],
        "coord": coord_list,
        "size": (30, 30)
    }
    graph["nodes"].append(Node(id = i, properties=properties))
    j = 1
    for place in ontology[city]["places"][:MAX_PLACES_PER_CITY]:
        if place["coord"] == None:
            continue
        coord_list = rx.findall(place["coord"])
        coord_list = [float(coord_list[1]), float(coord_list[0])]
        properties = {
            "label": place["label"],
            "type": place["type"],
            "coord": coord_list,
            "inception": place["inception"],
            "size": (20, 20)
        }
        graph["nodes"].append(Node(id = i+j, properties=properties))
        graph["edges"].append(Edge(start=i, end=i+j, properties={"label":"located_in"}))
        j += 1
    i = i+j

StreamlitGraphWidget(nodes=graph["nodes"],
                    edges=graph["edges"], 
                    node_styles_mapping = lambda _: NodeStyle(shape=NodeShape.TRIANGLE),
                    # adjust edge visualization
                    edge_styles_mapping = lambda _: EdgeStyle(
                        dash_style = DashStyle.DASH,
                        color = "black"
                    ),
                    node_coordinate_mapping = "coord",
                    node_size_mapping="size").show(graph_layout=Layout.MAP)

# ----------------- FUSION OF OBTAINED ONTOLOGIES
st.header("3. Sub-Ontology from Extracted and Reference Data")

st.markdown("""
The final graph combines the ontology extracted from text with the
reference ontology obtained from Wikidata.

Entities and relationships are classified according to their matching status:

- **SHARED**: present in both sources.
- **CORPUS_ONLY**: found only in the ontology extracted from the corpus.
- **REFERENCE_ONLY**: found only in the ontology extracted from Wikidata.

This visualization highlights agreements and discrepancies between
the two knowledge sources.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("SHARED")

with col2:
    st.error("CORPUS_ONLY")

with col3:
    st.info("REFERENCE_ONLY")

MAX_NODES = st.slider("Select the number of nodes", 0, 500, 100)

selected_status = st.multiselect(
    "Status da includere",
    ["SHARED", "CORPUS_ONLY", "REFERENCE_ONLY"],
    default=["SHARED"]
)

if selected_status == []:
    selected_status = ["SHARED"]

ontology = ""
with open("./demo/resources/final_graph_matching.json", encoding='utf-8') as ontology_file:
    ontology = json.load(ontology_file)

ontology, cities = extract_cities_and_types_json(ontology, MAX_NODES, selected_status)

ontology, valid_edges = remove_edges_and_nodes_not_connected_json(ontology, cities)

node_index = {
    node["name"]: i
    for i, node in enumerate(ontology["nodes"])
}

# create the graph
nodes = []
for node in ontology["nodes"]:
    nodes.append(Node(id = node_index[node["name"]], properties = {"label": node["name"], "status": node["status"]}))

edges = []
for edge in valid_edges:
    edges.append(Edge(start=node_index[edge["from"]], end=node_index[edge["to"]], properties={"label":edge["relation"], "status": edge["status"]}))


StreamlitGraphWidget(nodes=nodes,
                    edges=edges,
                    node_styles_mapping= lambda node: NodeStyle(
                        color = "red" if node["properties"]["status"] == "CORPUS_ONLY" else "blue" if node["properties"]["status"] == "REFERENCE_ONLY" else "green" 
                    ),
                    edge_styles_mapping = lambda edge: EdgeStyle(
                    color = "red" if edge["properties"]["status"] == "CORPUS_ONLY" else "blue" if edge["properties"]["status"] == "REFERENCE_ONLY" else "green" 
                    )).show(graph_layout=Layout.HIERARCHIC)
