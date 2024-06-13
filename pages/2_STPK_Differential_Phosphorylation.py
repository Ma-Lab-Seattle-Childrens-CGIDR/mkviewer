# Imports
# Standard Library Imports
from __future__ import annotations

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
phospho_table = md_con.table("all_phosphosites")

STPK_LIST = [
    "PknB",
    "PknD",
    "PknE",
    "PknF",
    "PknG",
    "PknH",
    "PknI",
    "PknJ",
    "PknK",
    "PknL",
]

# Start of page
st.title("Serine Threonine Protein Kinase Differential Phosphorylation")

st.markdown(
    """ 
    Welcome to the STPK Differential Phosphorylation Viewer! This tool uses data from Frando et al., 2023 to explore 
    the impact that perturbing the Serine Threonine Protein Kinases (STPKs) has on the phosphoproteome of 
    *Myobacterium tuberulosis*. 

    The first section allows for visualizing differential phosphoryaltion as a volcano plot, where the fold-change 
    (log2) of 
    phosphorylation level is plotted along the x-axis, and the significance is plotted along the y-axis (in the form of 
    -log10(p-value), so higher is more significant). The visualization includes tooltips if you hover over the points 
    including information on the gene, the
    p-value, and the fold change. A region can be selected by clicking and dragging on the plot, and the table to the 
    right
    will update to show 30 of the genes in that region (not sorted).   

    In the second section, you can filter the differential phosphorylation data by significance (p-value), 
    and fold-change (log2), and a table will be displayed showing information about the phsohorylations meeting
    your criteria. Multiple STPKs can be selcted simultaneously, and will all be included in the table. The 
    table can be downloaded as a csv by clicking the download button near the top right of the table (which shows up
    when your mouse is hovering over the table). 
    """
)

st.header("Volcano Plot")

# Select kinase, and which type of mutant is desired
stpk_selected = st.selectbox(
    "Select which STPK you want to view differential phosphorylation for:",
    options=STPK_LIST,
    index=None,
)

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


# Submit button
def submit_button_clicked():
    st.session_state.form_submitted = True


st.button("Submit", on_click=submit_button_clicked)


def display_volcano_chart(container):
    if stpk_selected is None:
        return None
    filtered_table = phospho_table.filter(
        (phospho_table["STPK"] == stpk_selected)
        & (phospho_table["Mutant"].isin(mutant_selected_list))
    )
    container.altair_chart(
        mkview.kinase_volcano_plot(
            data_table=filtered_table,
            foldchange_col="Fold-change (log2)",
            pval_col="p-value",
            locus_col="Rv Number",
            genename_col="Gene Name",
            volcano_width=600,
            volcano_height=600,
        ),
        use_container_width=True,
    )
    st.session_state.form_submitted = False


c = st.empty()

if st.session_state.form_submitted:
    display_volcano_chart(c)

# Data table section
st.header("Differential Phosphorylation Table")

# Second submit button
if "table_submitted" not in st.session_state:
    st.session_state.table_submitted = False

stpk_table_select = st.multiselect(
    "Choose STPKs to display data for:", STPK_LIST, default=None
)

# Select Mutant
mutant_table_selected = st.radio(
    "Select which mutant of the STPK you want to view differential phosphorylation for:",
    ["OE", "LOF", "Both"],
    key="mutant_table_selector",
)

mutant_table_selected_list = []
if mutant_table_selected == "OE":
    mutant_table_selected_list += ["OE"]
elif mutant_table_selected == "LOF":
    mutant_table_selected_list += ["LOF"]
elif mutant_table_selected == "Both":
    mutant_table_selected_list += ["OE", "LOF"]
else:
    raise ValueError("Invalid Mutant Value Selected")

pval_cutoff = st.number_input("Choose a p-value cutoff", value=0.005, format="%f")

pos_fold_change_bound = st.number_input(
    "Choose a positive bound (selecting proteins with differential phosphorylation (log2(fold-change) above this bound))",
    value=1.0,
    format="%f",
)

neg_fold_change_bound = st.number_input(
    "Choose a negative bound (selecting proteins with differential phosphorylation (log2(fold-change) below this bound))",
    value=-1.0,
    format="%f",
)


# Submit button
def table_submit_clicked():
    st.session_state.table_submitted = True


st.button("Submit", on_click=table_submit_clicked, key="table_submit")


def display_phos_table(container):
    if not stpk_table_select:
        return None
    filtered_table = (
        phospho_table.filter(phospho_table["STPK"].isin(stpk_table_select))
        .filter(phospho_table["p-value"] <= pval_cutoff)
        .filter(
            (phospho_table["Fold-change (log2)"] <= neg_fold_change_bound)
            | (phospho_table["Fold-change (log2)"] >= pos_fold_change_bound)
        )
        .filter(phospho_table["Mutant"].isin(mutant_table_selected_list))
    )
    st.dataframe(filtered_table.to_pandas())
    st.session_state.table_submitted = False


table_container = st.empty()

if st.session_state.table_submitted:
    display_phos_table(table_container)

st.markdown(
    """
    ## Sources:
    -  [Frando A, Boradia V, Gritsenko M, Beltejar C, Day L, Sherman DR, Ma S, Jacobs JM, Grundner C. The Mycobacterium   
    tuberculosis protein O-phosphorylation landscape. Nat Microbiol. 2023 Mar;8(3):548-561. doi: 10.1038/s41564-022-01313-7.   
    Epub 2023 Jan 23. PMID: 36690861.](https://doi.org/10.1038/s41564-022-01313-7)
    """
)

st.link_button(
    label="Github Repository",
    url="https://github.com/Ma-Lab-Seattle-Childrens-CGIDR/mkviewer_st",
)
