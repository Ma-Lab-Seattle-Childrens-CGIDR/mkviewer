# Imports
# Standard Library Imports
from __future__ import annotations
import json

# External Imports
import ibis
import streamlit as st

# Local imports

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


# Get database connection
md_con = get_database_connection()

mycobrowser_table = md_con.table("mycobrowser")
possible_columns = mycobrowser_table.columns

# Get list of possible species
with open("./data/mycobrowser_species_list.json", "r") as f:
    possible_species_list = json.load(f)

# Start of page
st.title("Mycobrowser")

st.markdown(
    """ 
    Welcome to the Mycobrowser Data Viewer! This tool allows the exploration of information about the genomes of several mycobacteria complex 
    bacteria, including *Mycobacterium tuberculosis*, *Mycobacterium smegmatis*, and *Mycobacterium marinum*.  

    Start by choosing a search term (such as a gene name or function, the search term can also be a regular expression), as well 
    as which columns you want to display in the resulting table (select as many as you want, leave blank to include all possible columns). 
    Each of the columns you choose which contain text data 
    (gene name, locus, comments, function etc.) will be searched for matches to your search term. You can further filter you search by species, 
    if you want to include all species in the search, simply leave this field blank.   
      
    A table will be displayed of all you selected columns, with all the genes which include data matching your search term. This table can be downloaded as 
    a csv by clicking the download as csv button (which is displayed at the top right of the table when you mouse is hovering over the table). 
    """
)

search_str = st.text_input(
    "Search term",
    value="",
    help="Will search for a match in the columns selected below, case insensitive",
)

case_insensitive = st.checkbox("Case Insensitive Search", value=True)

columns_selected = st.multiselect(
    "Select columns of interest (leave blank to include all)",
    possible_columns,
    default=None,
)

species_selected = st.multiselect(
    "Select species of interest (leave blank to include all)",
    possible_species_list,
    default=None,
)

# Submit button
def submit_button_clicked():
    st.session_state.form_submitted = True


st.button("Submit", on_click=submit_button_clicked)


def display_mycobrowser_table(container, search_str, species_selected, columns_selected):
    if search_str == "":
        return None
    if not species_selected:
        species_selected = possible_species_list
    if not columns_selected:
        columns_selected = possible_columns
    if case_insensitive:
        search_str = "(?i)"+search_str
    # Create a list of searchable columns (those that contain strings)
    search_columns = [
        col
        for col in columns_selected
        if isinstance(mycobrowser_table.schema()[col], ibis.expr.datatypes.core.String)
    ]
    filtered_table = mycobrowser_table.filter(
        mycobrowser_table["species"].isin(species_selected)
    )
    search_filter = filtered_table[search_columns.pop()].re_search(search_str)
    for col in search_columns:
        search_filter |= filtered_table[col].re_search(search_str)
    filtered_table = filtered_table.filter(search_filter)

    # Display dataframe
    st.dataframe(
        filtered_table.select(columns_selected).to_pandas(),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download Full csv",
        filtered_table.to_pandas().to_csv(),
        mime="text/csv",
        file_name="filtered_mycobrowser.csv",
    )
    st.session_state.form_submitted = False


c = st.empty()

if st.session_state.form_submitted:
    display_mycobrowser_table(
        c, search_str=search_str, species_selected=species_selected, columns_selected=columns_selected
    )

st.markdown(
    """
    ## Sources:
    -  [Kapopoulou A, Lew JM, Cole ST. The MycoBrowser portal: a comprehensive and manually annotated 
    resource for mycobacterial genomes. Tuberculosis (Edinb). 2011 Jan;91(1):8-13. doi: 10.1016/j.tube.2010.09.006. 
    Epub 2010 Oct 25. PMID: 20980200.](https://www.sciencedirect.com/science/article/abs/pii/S1472979210001095?via%3Dihub)
    """
)
