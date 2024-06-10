# Imports
# Standard Library Imports
from __future__ import annotations

# External Imports
import streamlit as st

# Local imports

# Setup/Data Reading
# Streamlit setup
# st.set_page_config(layout="wide")

st.title("Home")

st.markdown(
    """
    Welcome to MKViewer! This website is designed to help explore data associated with *Mycobacterium tuberculosis*, and other *Mycobacteria*.  
    It includes data and visualizations about changes in gene expression, phsohprylation by the Serine threonine protein kinases, and   
    information about genes in various *Mycobacteria* species.  
"""
)
st.page_link(
    "pages/1_Gene_Expression_Compendia.py", label="Gene Expression Compendia Viewer"
)
st.page_link(
    "pages/2_STPK_Differential_Phsohporylation.py",
    label="STPK Differential Phosphorylation Viewer",
)
st.page_link(
    "pages/2_STPK_Differential_Phsohporylation.py",
    label="STPK Differential Gene Expression Viewer",
)
st.page_link("pages/4_Kinase_Network.py", label="Kinase Network Viewer")
st.page_link("pages/5_Mycobrowser.py", label="Mycobrowser Data Viewer")

st.markdown(
    """
    ##  Gene Expression Compendia

    Explore under which conditions different genes change their expression. Uses data from Yoo et al., 2022  
    which can be filtered by gene, and level of change in expression to show conditions associated with large  
    fold changes in expression of genes of interest.   
    """
)

st.markdown(
    """
    ## STPK Differential Phosphorylation

    Investigate the changes in phosphorylation caused by perturbations in the Serine Threonine Protein Kinases (STPKs).   
    Uses data from Frando et al., 2023 to visualize changes in phosphorylation caused by gain- and loss- of function     
    STPK mutants. Also includes table showing the differential phosphorylations which can be filtered by mutant   
    (either gain of function(GOF), or loss of function (LOF)), significance of differential phosphorylation,   
    and fold-change (log2). 
    """
)
st.markdown(
    """
    ## STPK Differential Gene Expression

    Investigate the changes in gene expression caused by perturbations in the STPKs. Using the data from      
    Frando et al., 2023, allows visualization of changes in gene expression caused by gain- and loss- of function     
    STPK mutants. Also includes table showing the differential gene expression which can be filtered by mutant   
    (either gain of function(GOF), or loss of function (LOF)), significance of differential gene expression,   
    and fold-change (log2). 
    """
)

st.markdown(
    """
    ## STPK Kinase Network

    Investigate which genes are targeted by the STPKs. Using data from Frando et al., 2023, visualizes the   
    network of genes which are phosphorylated by different kinases, or have their gene expression significantly   
    altered by STPK perturbations.  
    """
)

st.markdown(
    """
    ## Mycobrowser Data Viewer
     
    Explore data and annotations about the genomes of *Mycobacterium tuberculosis*, *Mycobacterium leprae*,  
    *Mycobacterium marinum*, *Mycobacterium smegmatis*, *Mycobacterium bovis*, *Mycobacterium lepromatosis*,   
    *Mycobacterium abscessus*, *Mycobacterium haemophilum*, and *Mycobacterium orygis*. Uses data from   
    the last release of [Mycobrowser](https://mycobrowser.epfl.ch/), so the annotations are falling behind the latest  
    publications and other resources, but hopefully this can still be a helpful resource.  
    """
)

st.markdown(
    """
    ## Sources:
    -  [Frando A, Boradia V, Gritsenko M, Beltejar C, Day L, Sherman DR, Ma S, Jacobs JM, Grundner C. The Mycobacterium   
    tuberculosis protein O-phosphorylation landscape. Nat Microbiol. 2023 Mar;8(3):548-561. doi: 10.1038/s41564-022-01313-7.   
    Epub 2023 Jan 23. PMID: 36690861.](https://doi.org/10.1038/s41564-022-01313-7)
    -  [Kapopoulou A, Lew JM, Cole ST. The MycoBrowser portal: a comprehensive and manually annotated 
    resource for mycobacterial genomes. Tuberculosis (Edinb). 2011 Jan;91(1):8-13. doi: 10.1016/j.tube.2010.09.006. 
    Epub 2010 Oct 25. PMID: 20980200.](https://www.sciencedirect.com/science/article/abs/pii/S1472979210001095?via%3Dihub)
     - [Yoo R, Rychel K, Poudel S, Al-Bulushi T, Yuan Y, Chauhan S, Lamoureux C, Palsson BO, Sastry A. Machine Learning of   
    All Mycobacterium tuberculosis H37Rv RNA-seq Data Reveals a Structured Interplay between Metabolism, Stress Response,   
    and Infection. mSphere. 2022 Apr 27;7(2)\:e0003322. doi: 10.1128/msphere.00033-22. Epub 2022 Mar 21. PMID: 35306876;   
    PMCID: PMC9044949.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9044949/)
    """
)

st.link_button(
    label="Github Repository",
    url="https://github.com/Ma-Lab-Seattle-Childrens-CGIDR/mkviewer_st",
)
