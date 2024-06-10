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
    with open("./data/gene_list.json") as f:
        gene_list = json.load(f)
    return gene_list


GENE_LIST = get_gene_list()

# Start of Page
st.title("Kinase Network Viewer")

st.markdown(
    """
    Welcome to the Kinase Network Viewer! This tool allows the visualization of the kinase phosphoryaltion or 
    gene expression change network in *Mycobacterium tuberculosis*. First select a list of genes of interest, 
    as well as whether you want the network to be from the OE (overexpression) mutant, the LOF (loss of function)
    mutant, or both. Then choose whether you want to visualize the phosphorylation, or differential gene expression (DEG
    network, and what level of significance you want to filter for. The remaining options customize the appearence of the network, 
    and whether to include physics in the graph (which will generate a force directed layout for the network). 
    """
)

# Select genes of interest
selected_genes = st.multiselect("Select genes of interest:", GENE_LIST, default=None)

# Select Mutant
mutant_selected = st.radio(
    "Select which mutant of the STPK you want to view differential phosphorylation for:",
    ["OE", "LOF", "Both"],
)

mutant_selected_list = []
if mutant_selected == "OE":
    mutant_selected_list += ["OE"]
elif mutant_selected == "LOF":
    mutant_selected_list += ["LOF"]
elif mutant_selected == "Both":
    mutant_selected_list += ["OE", "LOF"]
else:
    raise ValueError("Invalid Mutant Value Selected")

# Select target type
target_type_selected = st.radio(
    "Select which type of target you want to visualize:",
    ["Differential Gene Expression", "Differential Phosphorylation"],
)


# Select p-value cutoff
pval_cutoff = st.number_input("Choose an upper p-value for significance", value=0.005, format="%f")

# Add physics?
physics = st.checkbox("Add physics to graph?")

# Kinase size
kinase_size = st.number_input("Choose size for kinase nodes", value=20)

# Gene Size
gene_size = st.number_input("Choose size for kinase nodes", value=10)

# Kinase Color
kinase_color = st.text_input(
    "Choose Color for kinase nodes",
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
    if target_type_selected == "Differential Gene Expression":
        kinase_target_table = md_con.table("all_kinase_diff_genes")
        gene_col = "DEG"
    elif target_type_selected == "Differential Phosphorylation":
        kinase_target_table = md_con.table("all_phosphosites")
        gene_col = "Rv Number"
    else:
        ValueError("Invalid selection for target type")
    kinase_network = mkview.create_kinase_network(
        gene_list=selected_genes,
        kinase_target_table=kinase_target_table,
        kinase_size=kinase_size,
        gene_size=gene_size,
        kinase_color=kinase_color,
        gene_color=gene_color,
        mutant_type=mutant_selected_list,
        pval_cutoff=pval_cutoff,
        gene_col=gene_col,
        pval_col="p-value",
    )
    kinase_network.toggle_physics(physics)
    # There has to be a way to do this directly, TODO: Fix this!
    with container:
        components.html(kinase_network.generate_html(), height=800, width=800)

    # Reset form submitted button
    st.session_state.form_submitted = False


c = st.empty()

if st.session_state.form_submitted:
    display_network(c)

st.markdown(
    """
    ## Sources:
    -  [Frando A, Boradia V, Gritsenko M, Beltejar C, Day L, Sherman DR, Ma S, Jacobs JM, Grundner C. The Mycobacterium   
    tuberculosis protein O-phosphorylation landscape. Nat Microbiol. 2023 Mar;8(3):548-561. doi: 10.1038/s41564-022-01313-7.   
    Epub 2023 Jan 23. PMID: 36690861.](https://doi.org/10.1038/s41564-022-01313-7)
    """
)
