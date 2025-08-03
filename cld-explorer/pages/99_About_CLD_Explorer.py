import streamlit as st

# Page configuration
st.set_page_config(page_title="About CLD Explorer", page_icon="ℹ️", layout="wide")

# Main title
st.title("About CLD Explorer")

# About section
st.header("About")

col1, col2 = st.columns([0.3, 0.7])

with col1:
    st.image("./assets/deib_logo.png", use_column_width=True)

with col2:
    st.markdown(
        """
    The **CLD Explorer** application was designed and developed by **Anna Bernasconi**, **Stefano Ceri**, **Francesco Invernici**, **Chiara Leonardi**, and **Laura Daniela Maftei**.

    **Department of Electronics, Information, and Bioengineering (DEIB)**  
    Politecnico di Milano  
    Via Ponzio 34/5 Milano  
    20133 Milano  
    Italy

    """
    )

# Citation section
st.header("Citation")

st.markdown(
    """
Our paper is in preparation. In the meanwhile, if you use **CLD Explorer**, please cite it as follows:

Anna Bernasconi, Stefano Ceri, Francesco Invernici, Chiara Leonardi, and Laura Daniela Maftei. 2025.  
"CLD-Explorer: toward a tool for Causal Loop Diagrams analytics".  
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
    
    /* Style for the image container */
    div[data-testid="column"]:first-child img {
        background-color: #f8f9fa !important;
        padding: 20px !important;
        border-radius: 10px !important;
        width: 100% !important;
        box-sizing: border-box !important;
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
