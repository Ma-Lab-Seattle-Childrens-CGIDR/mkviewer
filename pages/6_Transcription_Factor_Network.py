# Imports
# Standard Library Imports
from __future__ import annotations
import json

# External Imports
import ibis
import streamlit as st
import streamlit.components.v1 as components

# Local imports
import mkview

# Setup/Data Reading
# Streamlit setup
st.set_page_config(layout="wide")

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False


# Connect to database
@st.cache_resource
def get_database_connection():
    md_token = st.secrets["MD_TOKEN"]
    return ibis.duckdb.connect(f"md:mkviewer?motherduck_token={md_token}")


md_con = get_database_connection()


@st.cache_data
def get_gene_list():
    with open("./data/tf_gene_list.json") as f:
        gene_list = json.load(f)
    return gene_list

GENE_LIST = get_gene_list()

# Start of Page
st.title("Transcription Factor Network Viewer")

st.markdown(
    """
    Welcome to the Kinase Network Viewer! This tool allows the visualization of the transcription factor network in 
    *Mycobacterium tuberculosis*. First select a list of genes of interest, 
    as well as your desired p-value cutoff. Then choose which cutoffs you want to use for the fold-change in gene 
    expression caused by the transcription factor overexpression (in log2). For example, if you want to 
    view all genes in your gene list which have their expression double when the transcription factors are 
    overexpressed, used a positive bound of 1.  The remaining options customize the appearance of the network, 
    and whether to include physics in the graph (which will generate a force directed layout for the network). 
    """
)

# Select genes of interest
selected_genes = st.multiselect("Select genes of interest:", GENE_LIST, default=None)

# Select p-value cutoff
pval_cutoff = st.number_input(
    "Choose an upper p-value for significance", value=0.005, format="%f"
)

pos_bound = st.number_input(
    "Choose a positive bound (including TF-gene interactions where the TF overexpression induces a (log2) fold change"
    "above this level)",
    value=1.0,
    format="%f",
)

neg_bound = st.number_input(
    "Choose a negative bound (including TF-gene interactions where the TF overexpression induces a (log2) fold change"
    "below this level)",
    value=-1.0,
    format="%f",
)

# Add physics?
physics = st.checkbox("Add physics to graph?")

# TF size
tf_size = st.number_input("Choose size for TF nodes", value=20)

# Gene Size
gene_size = st.number_input("Choose size for gene nodes", value=10)

# TF Color
tf_color = st.text_input(
    "Choose Color for TF nodes",
    value="red",
    help="You can select colors by name (or any html color identifier)",
)

# Gene Color
gene_color = st.text_input(
    "Choose Color for gene nodes",
    value="blue",
    help="You can select colors by name (or any html color identifier)",
)

# Submit button
def submit_button_clicked():
    st.session_state.form_submitted = True


st.button("Submit", on_click=submit_button_clicked)

def display_network(container):
    if selected_genes is None:
        return None
    tf_network = mkview.create_tf_network(
        gene_list=selected_genes,
        tf_target_table=md_con.table("tfoe"),
        tf_size=tf_size,
        gene_size=gene_size,
        tf_color=tf_color,
        gene_color=gene_color,
        pval_cutoff=pval_cutoff,
        neg_bound = neg_bound,
        pos_bound=pos_bound,
        gene_col="Gene",
        pval_col="p_value",
    )
    tf_network.toggle_physics(physics)
    with container:
        components.html(tf_network.generate_html(), height=800, width=800)

    # Reset form submitted button
    st.session_state.form_submitted = False


c = st.empty()

if st.session_state.form_submitted:
    display_network(c)

st.markdown(
    """
    ## Sources:
    - [Rustad TR, Minch KJ, Ma S, Winkler JK, Hobbs S, Hickey M, Brabant W, Turkarslan S, Price ND, Baliga NS, 
    Sherman DR. Mapping and manipulating the Mycobacterium tuberculosis transcriptome using a transcription factor 
    overexpression-derived regulatory network. Genome Biol. 2014;15(11):502. doi: 10.1186/PREACCEPT-1701638048134699. 
    PMID: 25380655; PMCID: PMC4249609.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4249609/)
    """
)

st.link_button(
    label="Github Repository",
    url="https://github.com/Ma-Lab-Seattle-Childrens-CGIDR/mkviewer_st",
)
