# Imports
# Standard Library Imports
from __future__ import annotations
import json

# External Imports
import ibis
import streamlit as st

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
def get_tf_list():
    with open("./data/tf_list.json") as f:
        tf_list = json.load(f)
    return tf_list


TF_LIST = get_tf_list()

tfoe_table = md_con.table("tfoe")

st.title("Transcription Factor Overexpression")
st.markdown("""
    Welcome to the Transcription Factor (TF) Overexpression viewer! This tool uses data from Rustad et al., 2014 to
    explore the impact that TF overexpression has on gene expression in *Mycobacterium tuberculosis*. 
    
    The first section allows for visualizing differential gene expression caused by TF overexpression as a volcano 
    plot, where the fold-change (log2) of gene expression is plotted along the x-axis, and the significance is plotted
    along the y-axis (in the form of -log10(p-value), so higher is more significant). The visualization includes 
    tooltips if you hover over the points including the Rv number, fold change, and p-value. A region can be selected by 
    clicking and draggin on the plot, and the table to the right will update to show 30 of the genes in that region 
    (not sorted). 
    
    In the second section, you can filter the differential gene expression data by significance (p-value), 
    and fold-change (log2), and a table will be displayed showing information about the gene expression changes
    meeting your criteria. Multiple TFs can be selected simultaneously, and will all be included in the table. 
    The table can be downloaded as a csv by clicking the download button near the top right of the table 
    (which shows up when you mouse is hovering over the table). 
""")

st.header("Volcano Plot")

tf_selected = st.selectbox(
    "Select which TF you want to view the changes in gene expression for:",
    options=TF_LIST,
    index=None
)


# submit button
def volcano_submit_button_clicked():
    st.session_state.form_submitted = True


st.button("Submit", on_click=volcano_submit_button_clicked)


def display_volcano_chart(container):
    if not tf_selected:
        return None
    filtered_table = tfoe_table.filter(
        tfoe_table["TF"] == tf_selected
    )
    container.altair_chart(
        mkview.tf_volcano_plot(
            data_table=filtered_table,
            foldchange_col="fold_change",
            pval_col="p_value",
            gene_col="Gene",
            volcano_width=600,
            volcano_height=600,
        ),
        use_container_width=False
    )
    st.session_state.volcano_submit_button_clicked = False


c = st.empty()

if st.session_state.form_submitted:
    display_volcano_chart(c)

# Data Table Section
st.header("Differential Gene Expression Table")

# second submit button
if "table_submitted" not in st.session_state:
    st.session_state.table_submitted = False

tf_table_select = st.multiselect(
    "Select TFs to display data for:", TF_LIST, default=None
)

pval_cutoff = st.number_input("Choose a p-value cutoff", value=0.005, format="%f")

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


#  Submit button
def table_submit_clicked():
    st.session_state.table_submitted = True


st.button("Submit", on_click=table_submit_clicked, key="table_submit")


def display_tf_table(container):
    if not tf_table_select:
        return None
    filtered_table = (tfoe_table
    .filter(tfoe_table["TF"].isin(tf_table_select))
    .filter(tfoe_table["p_value"] <= pval_cutoff)
    .filter(
        (tfoe_table["fold_change"] <= neg_bound) | (tfoe_table["fold_change"] >= pos_bound)
    ))
    container.dataframe(filtered_table.to_pandas())
    st.session_state.table_submitted = False


table_container = st.empty()

if st.session_state.table_submitted:
    display_tf_table(table_container)

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
