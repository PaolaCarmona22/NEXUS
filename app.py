import streamlit as st

# Clean, professional page configuration
st.set_page_config(page_title="NEXUS Simulator", layout="wide")

st.title("NEXUS: Quantum Spintronics Platform")
st.subheader("Modular Simulation Environment for Semiconductor Rings")

# Sidebar for global physical parameters
st.sidebar.header("System Parameters")
R = st.sidebar.slider("Ring Radius (nm)", 10.0, 100.0, 25.0)
m_star = st.sidebar.number_input("Effective Mass (m/m0)", 0.01, 1.0, 0.067)
alpha_R = st.sidebar.slider("Rashba Parameter (alpha)", 0.0, 50.0, 10.0)

st.markdown("""
Welcome to **NEXUS**. This computational environment allows for the exploration of quantum behavior and spin-orbit coupling in spintronic systems.
Select an analysis module below to begin:
""")

# Navigation layout mapped directly to your 5 core files
col1, col2 = st.columns(2)

with col1:
    if st.button("Hamiltonian Formulation"):
        st.switch_page("pages/01_Hamiltonian.py")
    if st.button("Energy Spectrum Analysis"):
        st.switch_page("pages/02_Eigenenergies.py")
    if st.button("Eigenstates Visualization"):
        st.switch_page("pages/03_Eigenstates.py")

with col2:
    if st.button("Quantum States & Orthogonality"):
        st.switch_page("pages/04_States.py")
    if st.button("Conductance Computation"):
        st.switch_page("pages/05_Conductance.py")