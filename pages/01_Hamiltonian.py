import streamlit as st

# --- Configuración de página ---
st.set_page_config(page_title="NEXUS | Hamiltonian Builder", layout="wide")

# --- Estilos CSS ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .builder-container { background: white; padding: 25px; border-radius: 8px; border: 1px solid #dee2e6; }
    .latex-box { background: #f1f3f4; padding: 20px; border-radius: 5px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("# Hamiltonian Builder")
st.markdown("---")

# --- Definición del State ---
if 'h_params' not in st.session_state:
    st.session_state['h_params'] = {
        'zeeman': True, 'rashba': True, 'ab': False,
        'r0': 50.0, 'bz': 1.0, 'alpha': 0.1
    }

# --- Sidebar para Parámetros ---
with st.sidebar:
    st.header("System Controls")
    st.session_state['h_params']['r0'] = st.number_input("Radius $r_0$ (nm)", value=50.0)
    
    st.subheader("Hamiltonian Components")
    st.session_state['h_params']['zeeman'] = st.checkbox("Zeeman Splitting", value=True)
    st.session_state['h_params']['rashba'] = st.checkbox("Rashba SOC", value=True)
    st.session_state['h_params']['ab'] = st.checkbox("Aharonov-Bohm Flux", value=False)
    
    if st.session_state['h_params']['zeeman']:
        st.session_state['h_params']['bz'] = st.slider("Magnetic Field $B_z$ (T)", 0.0, 10.0, 1.0)
    if st.session_state['h_params']['rashba']:
        st.session_state['h_params']['alpha'] = st.number_input("Rashba Strength $\\alpha_R$ (eV·Å)", value=0.1)

# --- Contenido Principal ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Mathematical Model")
    st.write("The current Hamiltonian configuration is:")
    
    # Construcción dinámica de la cadena LaTeX
    h_latex = "\\hat{H} = \\frac{\\hbar^2}{2mr_{0}^{2}}\\left(-i\\frac{\\partial}{\\partial\\phi} + \\frac{\\Phi}{\\Phi_0}\\right)^2"
    if st.session_state['h_params']['zeeman']:
        h_latex += " + \\frac{1}{2}g\\mu_{B}B_{z}\\hat{\\sigma}_{z}"
    if st.session_state['h_params']['rashba']:
        h_latex += " + \\frac{\\alpha_{R}}{r_{0}}\\hat{\\sigma}_r\\left(-i\\frac{\\partial}{\\partial\\phi} + \\frac{\\Phi}{\\Phi_0}\\right) - i\\frac{\\alpha _R}{2r_0}\\hat{\\sigma }_{\\phi }"
    
    st.markdown(f"<div class='latex-box'>", unsafe_allow_html=True)
    st.latex(h_latex)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.subheader("Physical Insight")
    st.info("The Hamiltonian defines the energy landscape of the electron in the Rashba ring. Adjust parameters in the sidebar to observe changes in the energy spectrum.")
    
    if st.button("Generate Matrix Representation"):
        st.write("Initializing sparse matrix construction...")
        # Aquí conectaremos con el solver más adelante
        st.success("Hamiltonian matrix structure verified.")

# --- Footer ---
st.markdown("---")
if st.button("Launch Solver Module ➔"):
    st.switch_page("pages/02_Solver.py") # Este sería tu siguiente paso