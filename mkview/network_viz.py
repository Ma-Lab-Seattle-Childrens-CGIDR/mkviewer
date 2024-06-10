""" 
Module for visualizing gene and kinase networks
"""

# Imports
# Standard Library Imports
from __future__ import annotations

# External Imports
import numpy as np
import pyvis

# Local Imports


def create_kinase_network(
    gene_list: list,
    kinase_target_table: ibis.Table,
    kinase_size:int,
    gene_size:int,
    kinase_color:str,
    gene_color:str,
    mutant_type:list,
    pval_cutoff: float,
    gene_col: str,
    pval_col:str,
) -> pyvis.network.Network:
    # Filter down the kinase table 
    # Only include only the edges which are below the 
    # Cutoff
    edge_df = kinase_target_table.filter(
        kinase_target_table[pval_col]<pval_cutoff
    ).filter(
        kinase_target_table["Mutant"].isin(mutant_type)
    ).filter(
        kinase_target_table[gene_col].isin(gene_list)
    ).select("STPK", gene_col).to_pandas()
    # Rename the edges
    edge_df = edge_df.rename({gene_col:"gene"},axis=1)
    # Get a list of the kinases of interest
    kinase_list = np.unique(edge_df["STPK"])
    gene_list = np.unique(edge_df["gene"])
    # Create network
    kinase_network = pyvis.network.Network()
    # Add kinase nodes
    kinase_network.add_nodes(
        kinase_list,
        size=[kinase_size]*len(kinase_list),
        color=[kinase_color]*len(kinase_list),
        title=kinase_list
    )
    # Add gene nodes
    kinase_network.add_nodes(
        gene_list, 
        size=[gene_size]*len(gene_list),
        color=[gene_color]*len(gene_list),
        title=gene_list
    )
    # Add edges
    kinase_network.add_edges(
        [
            (row["STPK"], row["gene"]) for _, row in edge_df.iterrows()
        ]
    )
    return kinase_network
