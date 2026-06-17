import streamlit as st

# --- Configuración de Página ---
st.set_page_config(page_title="NEXUS – Hamiltonian Builder", layout="wide")

# --- CSS DEFINITIVO: Un solo fondo para el contenedor con borde ---
st.markdown("""
<style>
    /* Ocultar elementos nativos de Streamlit */
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .block-container { padding-top: 0rem !important; padding-bottom: 2rem !important; }
    
    /* Fondo e Identidad General */
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; }
    
    /* Header Principal */
    .nexus-header {
        background: linear-gradient(90deg, #001f3f 0%, #003366 100%);
        color: white;
        padding: 15px 30px;
        border-bottom: 4px solid #00d4ff;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stepper-container { display: flex; gap: 8px; }
    .step-tab {
        background-color: rgba(255, 255, 255, 0.1);
        color: #b0c4de;
        font-size: 10px;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 2px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .step-tab.active {
        background-color: #0056b3;
        color: white;
        border: 1px solid #00d4ff;
    }
    
    /* FORZAR CONTENEDORES NATIVOS A SER BLANCOS Y LIMPIOS (SIN REPETICIONES) */
    [data-testid="stContainer"] {
        background-color: white !important;
        border: 1px solid #e6e9ef !important;
        border-radius: 6px !important;
        padding: 24px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }
    
    /* Títulos de sección elegantes */
    .card-title-inline {
        color: #001f3f;
        font-size: 14px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid #f0f2f6;
        padding-bottom: 10px;
        margin-bottom: 20px;
        margin-top: 0px;
    }

    /* Recuadro Gris de la Ecuación */
    .equation-grey-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 12px 15px;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .equation-label {
        font-size: 9px;
        font-weight: 800;
        color: #868e96;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Botón RUN SIMULATION Compacto */
    .stButton>button {
        background-color: #0056b3 !important;
        color: white !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 8px 30px !important;
        border-radius: 3px !important;
        border: none !important;
        display: block !important;
        margin: 25px auto 0 auto !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    .stButton>button:hover {
        background-color: #001f3f !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. NAVBAR SUPERIOR ---
st.markdown("""
<div class='nexus-header'>
    <div>
        <h1 style='color: white !important; margin: 0; font-size: 22px; font-weight: 900;'>NEXUS</h1>
        <p style='margin: 0; font-size: 11px; color: #00d4ff;'>Advanced Quantum Simulation Environment</p>
    </div>
    <div class='stepper-container'>
        <div class='step-tab active'>1. Hamiltonian</div>
        <div class='step-tab'>2. Eigenenergies</div>
        <div class='step-tab'>3. Eigenstates</div>
        <div class='step-tab'>4. States</div>
        <div class='step-tab'>5. Conductance</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2. GRID PRINCIPAL (73% vs 27%) ---
col_main, col_side = st.columns([0.73, 0.27])

# ==========================================
# 3. COLUMNA IZQUIERDA: BUILD HAMILTONIAN
# ==========================================
with col_main:
    # Usamos el contenedor nativo con borde, el CSS se encargará de ponerlo blanco completo sin sub-cuadros
    with st.container(border=True):
        st.markdown("<div class='card-title-inline'>⚙️ Build Hamiltonian</div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 10px; font-weight: 800; color: #6c757d; text-transform: uppercase; margin-top: -10px; margin-bottom: 25px;'>Model Configuration Matrix</p>", unsafe_allow_html=True)
        
        # Columnas para los parámetros
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-bottom: 8px;'>Dimensionality</p>", unsafe_allow_html=True)
            dim_opt = st.radio("Dim", ["1D (Quantum Ring)", "2D (Bulk Plane)"], label_visibility="collapsed")
            
            st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-top: 18px; margin-bottom: 8px;'>Boundary Conditions</p>", unsafe_allow_html=True)
            bc_opt = st.selectbox("BC", ["Periodic (Ring Topology)", "Open (Wire)"], label_visibility="collapsed")

        with c2:
            st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-bottom: 8px;'>Spin-Orbit Coupling</p>", unsafe_allow_html=True)
            rashba = st.checkbox("Rashba Interaction", value=True)
            dresselhaus = st.checkbox("Dresselhaus Interaction", value=False)

        with c3:
            st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-bottom: 8px;'>External Fields</p>", unsafe_allow_html=True)
            zeeman = st.checkbox("Magnetic Field / Zeeman", value=False)

        # Lógica matemática dinámica
        eq = r"\hat{H} = "
        if "1D" in dim_opt:
            eq += r"\frac{\hbar^2 p_\phi^2}{2m^*R^2}"
            if rashba: eq += r" + \frac{\alpha_R}{\hbar}(\sigma_x \sin\phi - \sigma_y \cos\phi)p_\phi"
            if dresselhaus: eq += r" + \frac{\beta_D}{\hbar}(\sigma_x \cos\phi - \sigma_y \sin\phi)p_\phi"
        else:
            eq += r"\frac{\hbar^2 \mathbf{k}^2}{2m^*}"
            if rashba: eq += r" + \alpha_R(\sigma_x k_y - \sigma_y k_x)"
            if dresselhaus: eq += r" + \beta_D(\sigma_x k_x - \sigma_y k_y)"
        if zeeman: eq += r" + \frac{1}{2}g\mu_B B_z \sigma_z"

        # Caja Gris del Hamiltoniano de Renderizado
        st.markdown("<div class='equation-grey-box'><span class='equation-label'>Explicit Hamiltonian (Real-time rendering)</span></div>", unsafe_allow_html=True)
        st.latex(eq)

        # Botón ejecutor
        st.button("Run Simulation")

# ==========================================
# 4. COLUMNA DERECHA: PHYSICS INSIGHTS
# ==========================================
with col_side:
    with st.container(border=True):
        st.markdown("<div class='card-title-inline'>💡 Physics Insights</div>", unsafe_allow_html=True)
        
        # Sistema
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-bottom: 4px;'>System Representation</p>", unsafe_allow_html=True)
        if "1D" in dim_opt:
            st.markdown("<p style='font-size: 11px; color: #495057; line-height: 1.4; margin-bottom: 18px;'>Modeling a <b>Quantum Ring</b>. Curvature induces a geometric phase and restricts momentum to spatial angular components $p_\phi$.</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 11px; color: #495057; line-height: 1.4; margin-bottom: 18px;'>Modeling a <b>2D Bulk System</b>. Translation symmetry allows continuous momentum components $\mathbf{k}$ in the interface plane.</p>", unsafe_allow_html=True)
        
        # Física Activa
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-bottom: 4px;'>Active Physics</p>", unsafe_allow_html=True)
        if not rashba and not dresselhaus:
            st.markdown("<p style='font-size: 11px; color: #495057; line-height: 1.4; margin-bottom: 18px;'>Spin degeneracy is fully preserved. No spin-orbit splitting active in the band structure.</p>", unsafe_allow_html=True)
        else:
            txt = "<ul style='font-size: 11px; color: #495057; padding-left: 15px; margin-bottom: 18px; line-height: 1.4;'>"
            if rashba: txt += "<li style='margin-bottom: 4px;'><b>Rashba:</b> Momentum-dependent spin splitting caused by structural inversion asymmetry.</li>"
            if dresselhaus: txt += "<li><b>Dresselhaus:</b> Spin splitting related to bulk inversion asymmetry.</li>"
            txt += "</ul>"
            st.markdown(txt, unsafe_allow_html=True)

        # Campo Magnético
        if zeeman:
            st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-bottom: 4px;'>Magnetic Regime</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 11px; color: #495057; line-height: 1.4; margin-bottom: 0;'><b>Zeeman splitting active</b>. Time-reversal symmetry is broken, lifting Kramers degeneracy.</p>", unsafe_allow_html=True)