import streamlit as st

# Page configuration
st.set_page_config(page_title="About CLD Explorer", page_icon="ℹ️", layout="wide")

# Main title
st.title("About CLD Explorer")

# About section
st.header("About")

st.markdown(
    """
The **CLD Explorer** application was designed and developed by **Francesco Invernici**, **Prof. Anna Bernasconi**, and **Prof. Stefano Ceri**.

**Department of Electronics, Information, and Bioengineering (DEIB)**  
Politecnico di Milano  
Via Ponzio 34/5 Milano  
20133 Milano  
Italy

The authors would like to acknowledge with thanks **Luca Minotti** for implementing the front-end of the GRAPH-SEARCH web application.
"""
)

# Citation section
st.header("Citation")

st.markdown(
    """
Our paper is in preparation. In the meanwhile, if you use **GRAPH-SEARCH**, please cite it as follows:

Francesco Invernici, Anna Bernasconi, and Stefano Ceri. 2023.  
"GRAPH-SEARCH: Searching COVID-19 clinical research using graph queries".  
http://gmql.eu/graph-search
"""
)

# Additional styling with custom CSS
st.markdown(
    """
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMarkdown {
        text-align: justify;
    }
    
    h1 {
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
    
    h2 {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2rem;'>
        CLD Explorer - Causal Loop Diagram Explorer
    </div>
    """,
    unsafe_allow_html=True,
)
