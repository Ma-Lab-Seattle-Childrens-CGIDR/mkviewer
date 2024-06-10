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


md_con = get_database_connection()


@st.cache_data
def get_gene_list():
    with open("./data/gene_list.json") as f:
        gene_list = json.load(f)
    return gene_list


GENE_LIST = get_gene_list()

expression_table = md_con.table("gene_expression_compendia_unpivoted")
meta_table = md_con.table("gene_expression_metadata")
gene_info_table = md_con.table("gene_info")

# Start of Page
st.title("Gene Expression Compendia Viewer")
st.markdown(
    """
    Welcome to the Gene Expression Compendia Viewer! This tool uses data from Yoo et al., 2022
    to explore how different conditions impact gene expression. You can select a list of genes of interest, 
    as well as cutoffs for the fold change to be considered large, and then a table will be displayed 
    showing all of the conditions where a gene from your list has an log2(fold-change) in expression
    level above your positive bound, or below your negative bound, compared to the reference
    condition in a given study.   

    For example, if you select Rv0023, and a positive bound of 1, and a negative bound of -1, then
    the table will include entries for all the conditions where Rv0023 had an expression 
    greater than double that of the reference condition, or less than half that of the 
    reference condition (bounds of -2, and 2 will be those conditions with more than 4 times 
    that of the reference condition, or less than one quarter of the reference condition).  

    The table will include links to the studies associated with each of the conditions, and the table can
    be downloaded by clicking the download as csv button that shows up near the top right of the table when 
    your mouse is hovering over the table, or the full data set (including much more information about
    the conditions and the genes) can be downloaded by clicking the download full csv button below the 
    table. 
    """
)


selected_genes = st.multiselect("Select genes of interest:", GENE_LIST, default=None)

pos_bound = st.number_input(
    "Choose a positive bound (selecting conditions of interest with log2(fold-change) above this bound)",
    value=1.0, format="%f"
)

neg_bound = st.number_input(
    "Choose a negative bound (selecting conditions of interest with log2(fold-change) below this bound)",
    value=-1.0,
    format="%f",
)


# Submit button
def submit_button_clicked():
    st.session_state.form_submitted = True


st.button("Submit", on_click=submit_button_clicked)


def display_table(container):
    if not selected_genes:
        return None
    filtered_table = (
        expression_table.filter(expression_table["Gene"].isin(selected_genes))
        .filter(
            (expression_table["fold_change_log2_tpm"] >= pos_bound)
            | (expression_table["fold_change_log2_tpm"] <= neg_bound)
        )
        .left_join(meta_table, meta_table["sample_id"] == expression_table["sample"])
        .left_join(gene_info_table, expression_table["Gene"] == gene_info_table["gene"])
    )
    display_table = filtered_table.select(
        "Gene",
        "sample",
        "condition",
        "fold_change_log2_tpm",
        "project",
        "ReleaseDate",
        "reference_condition",
        "SRAStudy",
        "DOI",
        "pubmed_link",
    )

    st.dataframe(
        display_table.to_pandas(),
        use_container_width=True,
        hide_index=True,
        column_config={
            "pubmed_link": st.column_config.LinkColumn(
                "Pubmed",
                help="Link to associated paper on pubmed",
                validate=r"^https://pubmed.ncbi.nlm.nih.gov/\d+/",
                max_chars=100,
                display_text=r"^https://pubmed.ncbi.nlm.nih.gov/(\d+)/",
            ),
            "DOI": st.column_config.LinkColumn(
                "DOI",
                help="DOI link to associated paper",
                validate=r"^https://dx.doi.org/.+",
                width="medium",
            ),
            "fold_change_log2_tpm": "Fold Change (log2(tpm))",
        },
    )
    st.download_button(
        "Download full csv",
        filtered_table.to_pandas().to_csv(),
        mime="text/csv",
        file_name="filtered_gene_info.csv",
    )
    st.session_state.form_submitted = False


c = st.empty()

if st.session_state.form_submitted:
    display_table(c)

st.markdown(
    """
    ## Sources:
     - [Yoo R, Rychel K, Poudel S, Al-Bulushi T, Yuan Y, Chauhan S, Lamoureux C, Palsson BO, Sastry A. Machine Learning of   
    All Mycobacterium tuberculosis H37Rv RNA-seq Data Reveals a Structured Interplay between Metabolism, Stress Response,   
    and Infection. mSphere. 2022 Apr 27;7(2)\:e0003322. doi: 10.1128/msphere.00033-22. Epub 2022 Mar 21. PMID: 35306876;   
    PMCID: PMC9044949.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9044949/)
    """
)
