import streamlit as st

# --- Configuración de Página ---
st.set_page_config(page_title="NEXUS – Hamiltonian Builder", layout="wide")

# --- CSS Profesional NEXUS: Contenedores Unificados ---
st.markdown("""
<style>
    /* Ocultar elementos nativos */
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .block-container { padding-top: 0rem !important; padding-bottom: 2rem !important; }
    
    /* Fondo e Identidad */
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; }
    
    /* Header con Stepper */
    .nexus-header {
        background: linear-gradient(90deg, #001f3f 0%, #003366 100%);
        color: white;
        padding: 15px 30px;
        border-bottom: 4px solid #00d4ff;
        margin-bottom: 20px;
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
    
    /* Estilo de los Paneles Blancos (Todo el contenido vivirá aquí) */
    .nexus-card {
        background-color: white;
        border-radius: 4px;
        padding: 25px;
        border-top: 4px solid #0056b3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .card-title {
        color: #001f3f;
        font-size: 14px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Caja Gris para la Ecuación */
    .equation-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    
    .equation-label {
        font-size: 9px;
        font-weight: 800;
        color: #adb5bd;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        display: block;
        text-align: left;
    }

    /* Botón RUN SIMULATION: Pequeño y elegante */
    .stButton>button {
        background-color: #0056b3 !important;
        color: white !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 8px 25px !important;
        border-radius: 2px !important;
        border: none !important;
        display: block !important;
        margin: 0 auto !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00d4ff !important;
        color: #001f3f !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. HEADER Y STEPPER ---
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

# --- 2. ÁREA DE TRABAJO ---
col_main, col_side = st.columns([0.73, 0.27])

# --- COLUMNA IZQUIERDA: BUILD HAMILTONIAN ---
with col_main:
    st.markdown("<div class='nexus-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'> Build Hamiltonian</div>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 10px; font-weight: 800; color: #6c757d; text-transform: uppercase; margin-bottom: 15px;'>Model Configuration Matrix</p>", unsafe_allow_html=True)
    
    # Controles dentro del recuadro
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f;'>Dimensionality</p>", unsafe_allow_html=True)
        dim_opt = st.radio("Dim", ["1D (Quantum Ring)", "2D (Bulk Plane)"], label_visibility="collapsed")
        
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-top: 15px;'>Boundary Conditions</p>", unsafe_allow_html=True)
        bc_opt = st.selectbox("BC", ["Periodic (Ring Topology)", "Open (Wire)"], label_visibility="collapsed")

    with c2:
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f;'>Spin-Orbit Coupling</p>", unsafe_allow_html=True)
        rashba = st.checkbox("Rashba Interaction", value=True)
        dresselhaus = st.checkbox("Dresselhaus Interaction", value=False)

    with c3:
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f;'>External Fields</p>", unsafe_allow_html=True)
        zeeman = st.checkbox("Magnetic Field / Zeeman", value=False)

    # Lógica de la Ecuación Dinámica
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

    # Caja Gris de la Ecuación (DENTRO del recuadro blanco)
    st.markdown("<div class='equation-box'><span class='equation-label'>Explicit Hamiltonian (Real-time rendering)</span>", unsafe_allow_html=True)
    st.latex(eq)
    st.markdown("</div>", unsafe_allow_html=True)

    # Botón RUN (DENTRO del recuadro blanco)
    st.button("Run Simulation")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- COLUMNA DERECHA: PHYSICS INSIGHTS ---
with col_side:
    st.markdown("<div class='nexus-card' style='border-top-color: #00d4ff;'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'> Physics Insights</div>", unsafe_allow_html=True)
    
    # Insight 1: Sistema
    st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-bottom: 4px;'>System Representation</p>", unsafe_allow_html=True)
    if "1D" in dim_opt:
        st.markdown("<p style='font-size: 11px; color: #555;'>Modeling a <b>Quantum Ring</b>. Curvature induces a geometric phase and restricts momentum to angular components.</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size: 11px; color: #555;'>Modeling a <b>2D Bulk System</b>. Translation symmetry allows continuous momentum $\mathbf{k}$ in the plane.</p>", unsafe_allow_html=True)
    
    # Insight 2: Física Activa
    st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-top: 15px; margin-bottom: 4px;'>Active Physics</p>", unsafe_allow_html=True)
    if not rashba and not dresselhaus:
        st.markdown("<p style='font-size: 11px; color: #555;'>Spin degeneracy is preserved. No spin-orbit splitting active.</p>", unsafe_allow_html=True)
    else:
        txt = "<ul style='font-size: 11px; color: #555; padding-left: 15px;'>"
        if rashba: txt += "<li><b>Rashba:</b> Spin-locking due to structural asymmetry (electric gates).</li>"
        if dresselhaus: txt += "<li><b>Dresselhaus:</b> Induced by crystal inversion asymmetry.</li>"
        txt += "</ul>"
        st.markdown(txt, unsafe_allow_html=True)

    # Insight 3: Campos
    if zeeman:
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #001f3f; margin-top: 15px; margin-bottom: 4px;'>Magnetic Regime</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 11px; color: #555;'><b>Zeeman splitting</b> active. Time-reversal symmetry is broken, lifting Kramers degeneracy.</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)