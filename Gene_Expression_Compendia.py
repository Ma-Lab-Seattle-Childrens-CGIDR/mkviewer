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


selected_genes = st.multiselect("Select genes of interest:", GENE_LIST, default=None)

pos_bound = st.number_input(
    "Choose a positive bound (selecting conditions of interest with log2(fold-change) above this bound)",
    value=1.0,
)

neg_bound = st.number_input(
    "Choose a negative bound (selecting conditions of interest with log2(fold-change) below this bound)",
    value=-1.0,
)


# Submit button
def submit_button_clicked():
    st.session_state.form_submitted = True


st.button("Submit", on_click=submit_button_clicked)


def display_table(container):
    if selected_genes is None:
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
        filtered_table.select(
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
            "LibraryLayout",
            "Platform",
            "Model",
            "BioSample",
            "Submission",
            "SRA ID",
            "GEO Series",
            "GEO Sample",
            "PMID",
            "Biological Replicates",
            "full_name",
            "Feature",
            "Start",
            "Stop",
            "Frame",
            "Function",
            "Product",
            "Comments",
            "UniProt_AC",
            "Functional_Category",
            "Protein Data Bank",
            "PFAM",
            "UniProt",
            "Gene Ontology",
            "Enzyme Classification",
            "Drug Resistance Mutations",
            "InterPro",
            "SWISS-MODEL",
        )
        .to_pandas()
        .to_csv(),
        mime="text/csv",
        file_name="filtered_gene_info.csv"
    )
    st.session_state.form_submitted = False


c = st.empty()

if st.session_state.form_submitted:
    display_table(c)
