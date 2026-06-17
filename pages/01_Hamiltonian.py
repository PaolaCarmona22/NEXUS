import streamlit as st

# --- Configuración de página ---
st.set_page_config(page_title="NEXUS – Hamiltonian", layout="wide")

# --- CSS para limpiar interfaz ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #001f3f; font-weight: 700; }
    .card-build { 
        background: white; padding: 30px; border-radius: 8px; 
        border: 1px solid #dee2e6; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- Navegación Superior ---
tabs = st.tabs(["Hamiltonian", "Eigenenergies", "Eigenstates", "States", "Conductance"])

with tabs[0]: # Pestaña del Hamiltoniano
    
    # Layout de 3 columnas
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    
    with col_left:
        st.subheader("System Parameters")
        st.write("Configuración de variables del sistema.")
        # Aquí irán tus sliders
        
    with col_mid:
        st.markdown("<h1 class='main-title'>Hamiltonian Formulation</h1>", unsafe_allow_html=True)
        
        # --- Fase: Build Hamiltonian ---
        if 'system_initialized' not in st.session_state:
            with st.container():
                st.markdown("<div class='card-build'>", unsafe_allow_html=True)
                st.subheader("🛠 Build Hamiltonian")
                st.write("Configure the physical components of your model:")
                
                # Checkboxes para "construir" la física
                r_soc = st.checkbox("Rashba Spin-Orbit Coupling", True)
                z_split = st.checkbox("Zeeman Splitting")
                mag_flux = st.checkbox("External Magnetic Flux")
                
                # Ejemplo de cómo se vería la ecuación dinámica
                equation = r"H = H_{kin}"
                if r_soc: equation += r" + H_{Rashba}"
                if z_split: equation += r" + H_{Zeeman}"
                
                st.latex(equation)
                
                if st.button("Initialize System & Compute Matrix"):
                    st.session_state['system_initialized'] = True
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        
        # --- Fase: Resultados (Se activará tras el botón) ---
        else:
            st.write("### Numerical Representation")
            st.info("Matriz construida y lista para análisis.")
            if st.button("Reset Hamiltonian Builder"):
                del st.session_state['system_initialized']
                st.rerun()

    with col_right:
        st.subheader("Physical Insight")
        st.write("El análisis físico aparecerá aquí una vez que el Hamiltoniano esté construido.")