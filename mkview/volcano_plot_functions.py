"""
Module for creating Volcano Plots with altair
"""

# Imports
# Standard Library
from __future__ import annotations

# External Imports
import altair as alt
import ibis
import vegafusion as vf

# Local Imports

# Setup vegafusion
alt.data_transformers.enable("vegafusion")


# Main Function
def kinase_volcano_plot(
    data_table: ibis.Table,
    pval_col:str,
    foldchange_col:str,
    locus_col:str,
    genename_col:str,
    volcano_width:int=600,
    volcano_height:int=600,
    font_size:int=20,
)->alt.Chart:
    # Create columns for transformed pvalue, and fold change color
    plot_data = data_table.mutate(
        neg_log10_pval = data_table[pval_col].log10().negate(),
        pos_fold = (data_table[foldchange_col]>0.)
    )

    # Create brush for selection
    brush = alt.selection_interval()

    # Create Scatter Plot
    scatter = alt.Chart(plot_data).mark_circle().encode(
        alt.X(foldchange_col, title="Fold-change (log2)"),
        alt.Y("neg_log10_pval", title="Significance (-log10(p-value))"),
        alt.Color("pos_fold", legend=None),
        tooltip = [alt.Tooltip(locus_col),
            alt.Tooltip(genename_col),
            alt.Tooltip(foldchange_col, format=".2f"),
            alt.Tooltip(pval_col, format=".2e")],
        opacity = alt.condition(brush, alt.value(0.8), alt.value(0.1))
    ).add_params(brush).properties(
        width=volcano_width, 
        height=volcano_height
    )

    # Create base for table columns
    ranked_text = alt.Chart(plot_data).mark_text(align='right', fontSize=font_size).encode(
        y=alt.Y("row_number:O", axis=None)
    ).transform_filter(
        brush
    ).transform_window(
        row_number='row_number()'
    ).transform_filter(
        'datum.row_number < 30'
    ).properties(
        height=volcano_height,
    )

    # Create the columns
    # Locus tag
    locus = ranked_text.encode(
        alt.Text(locus_col, type='nominal')
    ).properties(title=alt.TitleParams(
        text="Rv Number", align='center', fontSize=30
    ))
    # Name
    name = ranked_text.encode(
        alt.Text(genename_col, type='nominal')
    ).properties(title=alt.TitleParams(
        text="Gene Name", align='center', fontSize=30
    ))
    # Fold Change
    fold_change = ranked_text.encode(
        alt.Text(foldchange_col, type='nominal', format=".2f")
    ).properties(title=alt.TitleParams(
        text="Fold-change (log2)", align='center', fontSize=30
    ))
    # P value
    pval = ranked_text.encode(
        alt.Text(pval_col, type='nominal', format=".2e")
    ).properties(title=alt.TitleParams(
        text="P-value", align='center', fontSize=30
    ))

    # Combine text into table
    text = alt.hconcat(locus, name, pval, fold_change)

    # Build final chart
    volcano_chart = alt.hconcat(scatter, text).resolve_legend(color="independent"
    ).configure_view(strokeWidth=0)

    return volcano_chart


def tf_volcano_plot(
        data_table:ibis.Table,
        pval_col:str,
        foldchange_col:str,
        gene_col:str,
        volcano_width:int=600,
        volcano_height:int = 600,
        font_size:int=20,
)->alt.Chart:
    # Create columns for transformed pvalue, and fold change color
    plot_data = data_table.mutate(
        neg_log10_pval=data_table[pval_col].log10().negate(),
        pos_fold=(data_table[foldchange_col] > 0.)
    )

    # Create brush for selection
    brush = alt.selection_interval()

    # Create Scatter Plot
    scatter = alt.Chart(plot_data).mark_circle().encode(
        alt.X(foldchange_col, title="Fold-change (log2)"),
        alt.Y("neg_log10_pval", title="Significance (-log10(p-value))"),
        alt.Color("pos_fold", legend=None),
        tooltip=[alt.Tooltip(gene_col),
                 alt.Tooltip(foldchange_col, format=".2f"),
                 alt.Tooltip(pval_col, format=".2e")],
        opacity=alt.condition(brush, alt.value(0.8), alt.value(0.1))
    ).add_params(brush).properties(
        width=volcano_width,
        height=volcano_height
    )

    # Create base for table columns
    ranked_text = alt.Chart(plot_data).mark_text(align='right', fontSize=font_size).encode(
        y=alt.Y("row_number:O", axis=None)
    ).transform_filter(
        brush
    ).transform_window(
        row_number='row_number()'
    ).transform_filter(
        'datum.row_number < 30'
    ).properties(
        height=volcano_height,
    )

    # Create the columns
    # Locus tag
    gene = ranked_text.encode(
        alt.Text(gene_col, type='nominal')
    ).properties(title=alt.TitleParams(
        text="Rv Number", align='center', fontSize=30
    ))
    # Fold Change
    fold_change = ranked_text.encode(
        alt.Text(foldchange_col, type='nominal', format=".2f")
    ).properties(title=alt.TitleParams(
        text="Fold-change (log2)", align='center', fontSize=30
    ))
    # P value
    pval = ranked_text.encode(
        alt.Text(pval_col, type='nominal', format=".2e")
    ).properties(title=alt.TitleParams(
        text="P-value", align='center', fontSize=30
    ))

    # Combine text into table
    text = alt.hconcat(gene, pval, fold_change)

    # Build final chart
    volcano_chart = alt.hconcat(scatter, text).resolve_legend(color="independent"
                                                              ).configure_view(strokeWidth=0)

    return volcano_chart





# Helper Functions
