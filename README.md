# Mycoviewer

This is the repository for the [mycoviewer.streamlit.app](mycoviewer.streamlit.app) website, which includes various tools for exploring
data and visualizations related to *Mycobacterium tuberculosis* and other mycobacterial species. 

## Tools
The website was created with [Streamlit](https://streamlit.io/), and is hosted on streamlit community cloud. [Motherduck](https://motherduck.com/) is used 
to host the DuckDB database with all associated data.   
- [Ibis](https://ibis-project.org/) is used to interact with the DuckDB database
- [Pandas](https://pandas.pydata.org/) is used to translate between the Ibis and Streamlit
- [Pyvis](https://pyvis.readthedocs.io/en/latest/) is used for creating the interactive network visualizations
- [Vega-Altair](https://altair-viz.github.io/) is used for visualizing the volcano plots
- [Vega-Fusion](https://vegafusion.io/) is used to improve the performance of the vega-altair plotting

## Structure 
- Home.py: Main landing page for the website
- pages: Directory containing all the pages for the different tools on the website
- mkview: Python helper scripts for the Streamlit pages
- data: Directory containing json data about the Genes and Species in the database