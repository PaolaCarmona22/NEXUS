import streamlit as st

# --- Configuración de Página ---
st.set_page_config(page_title="NEXUS – Quantum Spintronics Platform", layout="wide")

# --- CSS Profesional y Ocultar Sidebar ---
st.markdown("""
<style>
    /* Ocultar la barra lateral por completo */
    [data-testid="stSidebar"] { display: none; }
    
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; }
    
    .nexus-header {
        background: linear-gradient(90deg, #001f3f 0%, #003366 100%);
        color: white;
        padding: 30px;
        border-bottom: 4px solid #00d4ff;
    }
    
    .module-card {
        background: white;
        padding: 15px 20px;
        border-radius: 4px;
        border-left: 4px solid #0056b3;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .btn-status {
        background-color: #f8f9fa;
        color: #495057;
        border: 1px solid #ced4da;
        font-size: 11px;
        font-weight: 600;
        padding: 5px 10px;
        text-transform: uppercase;
        border-radius: 2px;
        pointer-events: none; /* Desactivar interacción */
    }
    
    .btn-launch {
        background-color: #0056b3 !important;
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class='nexus-header'>
    <h1 style='color: white !important;'>NEXUS</h1>
    <p>Quantum Spintronics Platform | Advanced Simulation Environment</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: #001f3f; margin-top: 20px;'>Model Builder Index</h2>", unsafe_allow_html=True)
st.write("Select a physics module from the index below to initialize the simulation environment.")

# --- Función Auxiliar para Cards ---
def render_module(name, status):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"<div class='module-card'><span>{name}</span></div>", unsafe_allow_html=True)
    with col2:
        if status == "Available":
            if st.button("Launch Module", key=name, help="Launch"):
                st.switch_page("pages/01_Hamiltonian.py")
        else:
            st.markdown(f"<button class='btn-status'>{status}</button>", unsafe_allow_html=True)

# --- Módulos (Corregidos con expanded=False) ---
with st.expander("Spin-Orbit Physics", expanded=False):
    render_module("Rashba Semiconductor Ring", "Available")
    render_module("Rashba Interaction", "Research Roadmap")
    render_module("Dresselhaus Interaction", "Research Roadmap")
    render_module("Zeeman Splitting", "Research Roadmap")
    render_module("Aharonov-Bohm Effects", "Research Roadmap")

with st.expander("Spin Transport", expanded=False):
    render_module("Spin Polarization", "Research Roadmap")
    render_module("Spin Currents", "Research Roadmap")
    render_module("Spin Filtering", "Research Roadmap")
    render_module("Spin Injection", "Research Roadmap")

with st.expander("Topological Systems", expanded=False):
    render_module("Topological Insulators", "Future Development")
    render_module("Edge-state Transport", "Future Development")
    render_module("Quantum Spin Hall Systems", "Future Development")
    render_module("Topological Superconductors", "Future Development")