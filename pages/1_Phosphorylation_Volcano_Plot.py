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
st.title("STPK Differential Phosphorylation Volcano Plot")

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
        mkview.volcano_plot(
            data_table=filtered_table, 
            foldchange_col="Fold-change (log2)",
            pval_col="p-value", 
            locus_col="Rv Number", 
            genename_col="Gene Name",
            volcano_width=600,
            volcano_height=600
        ),
        use_container_width=True,
    )
    st.session_state.form_submitted=False

c=st.empty()

if st.session_state.form_submitted:
    display_volcano_chart(c)