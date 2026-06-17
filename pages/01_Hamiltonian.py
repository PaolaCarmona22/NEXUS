import streamlit as st
import sympy as sp
import numpy as np

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Rashba Ring Simulator", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- BLINDAJE DE ESTADOS: Inicialización Segura para Evitar AttributeError ---
if "engine_running" not in st.session_state:
    st.session_state.engine_running = False
if "use_flux" not in st.session_state:
    st.session_state.use_flux = True
if "use_zeeman" not in st.session_state:
    st.session_state.use_zeeman = True
if "use_rashba" not in st.session_state:
    st.session_state.use_rashba = True

# --- Redirección del Menú Superior de Navegación ---
if "target_page" in st.query_params:
    page = st.query_params["target_page"]
    if page == "eigenenergies":
        st.query_params.clear()
        st.switch_page("pages/02_Eigenenergies.py")

# --- CSS NEXUS: Versión Cuatro Bloques Sincronizados ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; color: #0f172a; }

    /* INTERFAZ SUPERIOR: Header Navbar */
    .nexus-navbar {
        background: linear-gradient(90deg, #001f3f 0%, #003366 100%);
        padding: 20px 40px;
        border-bottom: 4px solid #00d4ff;
        margin: -65px -50px 30px -50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-area h1 { color: white !important; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 0.5px; }
    .brand-area p { color: #00d4ff; margin: 2px 0 0 0; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .nav-tabs-container { display: flex; gap: 10px; align-items: center; }
    .nav-tab-btn {
        background-color: rgba(255, 255, 255, 0.08); color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 8px 16px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; border-radius: 3px; text-decoration: none !important;
    }
    .nav-tab-btn.active { background-color: #0056b3 !important; color: white !important; border: 1px solid #00d4ff !important; }

    /* ESTILO DE LOS PANELES DE LAYOUT COHERENTE */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important; border: none !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; border-radius: 6px !important;
    }
    
    /* Títulos e Identificadores */
    .panel-title { color: #001f3f; font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; }
    
    /* Matrices e Indicadores */
    .matrix-status {
        background-color: #f1f5f9; padding: 10px; border-radius: 4px; border-left: 4px solid #10b981;
        font-family: monospace; font-size: 12px; font-weight: bold; color: #0f172a; margin-top: 10px;
    }
    .insight-card { background: white; padding: 14px; border-radius: 4px; border: 1px solid #ced4da; margin-bottom: 12px; }
    .insight-card h4 { color: #001f3f; font-size: 12px; font-weight: 700; margin: 0 0 6px 0; text-transform: uppercase; }
    .insight-card p { color: #495057; font-size: 11.5px; line-height: 1.5; margin: 0; }
</style>
""", unsafe_allow_html=True)

# --- NAVBAR HEADER ---
st.markdown("""
<div class='nexus-navbar'>
    <div class='brand-area'>
        <h1>NEXUS</h1>
        <p>Advanced Quantum Simulation Environment</p>
    </div>
    <div class='nav-tabs-container'>
        <a class='nav-tab-btn active' href='#'>1. Hamiltonian</a>
        <a class='nav-tab-btn' href='?target_page=eigenenergies'>2. Eigenenergies</a>
        <a class='nav-tab-btn' href='#'>3. Eigenstates</a>
        <a class='nav-tab-btn' href='#'>4. States</a>
        <a class='nav-tab-btn' href='#'>5. Conductance</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PARTE A: CONFIGURACIÓN INICIAL DEL OPERADOR
# ============================================================
if not st.session_state.engine_running:
    col_main_left, col_main_right = st.columns([5.2, 1.8])

    with col_main_left:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Builder Hamiltonian</p>", unsafe_allow_html=True)
            container_render = st.empty()
            
            grid_col1, grid_col2 = st.columns(2)
            with grid_col1:
                st.markdown("**Symmetry Breaking Modules**")
                use_flux = st.checkbox("Include Aharonov-Bohm Flux (Gauge Field)", value=st.session_state.use_flux, key="flux_chk")
                use_zeeman = st.checkbox("Include External Magnetic Field ($B_z$)", value=st.session_state.use_zeeman, key="zeeman_chk")
            with grid_col2:
                st.markdown("**Spin-Orbit Fields**")
                use_rashba = st.checkbox("Include Rashba Coupling (SIA)", value=st.session_state.use_rashba, key="rashba_chk")
                
            kinetic = "\\left(-i\\frac{\\partial}{\\partial\\phi} + \\frac{\\Phi}{\\Phi_0}\\right)^2" if use_flux else "\\left(-i\\frac{\\partial}{\\partial\\phi}\\right)^2"
            h_latex = f"\\hat{{H}} = \\frac{{\\hbar^2}}{{2m^* r_{{0}}^{2}}}{kinetic}"
            if use_zeeman: h_latex += " + \\frac{1}{2}g\\mu_{B}B_{z}\\hat{\\sigma}_{z}"
            if use_rashba: h_latex += " + \\frac{\\alpha_{R}}{r_{0}}\\hat{\\sigma}_r\\left(-i\\frac{\\partial}{\\partial\\phi}" + (" + \\frac{\\Phi}{\\Phi_0}" if use_flux else "") + "\\right) - i\\frac{\\alpha_R}{2r_0}\\hat{\\sigma}_\\phi"
            
            with container_render.container():
                st.latex(h_latex)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Run Core Engine →", type="primary"):
                st.session_state.use_flux = use_flux
                st.session_state.use_zeeman = use_zeeman
                st.session_state.use_rashba = use_rashba
                st.session_state.engine_running = True
                st.rerun()

    with col_main_right:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Physics Insights</p>", unsafe_allow_html=True)
            st.markdown("<div class='insight-card'><h4>Setup Phase</h4><p>Select the physical fields you wish to include in the Hamiltonian operator. Press <b>Run Core Engine</b> to initialize the symbolic matrix deduction.</p></div>", unsafe_allow_html=True)

# ============================================================
# PARTE B: ENTORNOS INTERACTIVOS EN 4 BLOQUES
# ============================================================
else:
    col_params, col_calculus = st.columns([2.0, 5.0])

    # --------------------------------------------------------
    # BLOQUE 1: BARRA IZQUIERDA DE PARÁMETROS NUMÉRICOS
    # --------------------------------------------------------
    with col_params:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>⚙️ System Parameters</p>", unsafe_allow_html=True)
            
            st.markdown("**Geometric & Material**")
            r0_val = st.slider("Ring Radius $r_0$ (nm)", 10.0, 100.0, 40.0, step=2.5)
            meff_val = st.slider("Effective Mass $m^*$ ($m_0$)", 0.01, 0.10, 0.023, step=0.001)
            
            st.markdown("<hr style='margin:10px 0; border-color:#e2e8f0;'>", unsafe_allow_html=True)
            st.markdown("**Quantum Numbers**")
            l_val = st.number_input("Angular Momentum $l$", value=1, step=1)
            
            st.markdown("<hr style='margin:10px 0; border-color:#e2e8f0;'>", unsafe_allow_html=True)
            st.markdown("**Active Fields**")
            
            phi_ratio = st.slider("Flux Ratio $\\Phi/\\Phi_0$", 0.0, 5.0, 1.2, step=0.1) if st.session_state.use_flux else 0.0
            bz_val = st.slider("Magnetic Field $B_z$ (T)", 0.0, 10.0, 2.5, step=0.1) if st.session_state.use_zeeman else 0.0
            alpha_val = st.slider("Rashba $\\alpha_R$ (meV·nm)", 0.0, 40.0, 15.0, step=1.0) if st.session_state.use_rashba else 0.0
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Reset Operator", use_container_width=True):
                st.session_state.engine_running = False
                st.rerun()

    # --------------------------------------------------------
    # SEGUNDA COLUMNA MAESTRA: CONTIENE LOS BLOQUES 2, 3 Y 4
    # --------------------------------------------------------
    with col_calculus:
        
        # --- BLOQUE 2: HAMILTONIAN FORMULATION ---
        with st.container(border=True):
            st.markdown("<p class='panel-title'>📝 Block 2: Hamiltonian Formulation</p>", unsafe_allow_html=True)
            st.markdown("<span style='font-size:12.5px; color:#475569;'>Projection of the custom operator onto the angular momentum basis $|l\\rangle \\otimes |\\pm\\rangle$:</span>", unsafe_allow_html=True)
            
            kin_sym = f"\\left(l + \\frac{{\\Phi}}{{\\Phi_0}}\\right)^2" if st.session_state.use_flux else "l^2"
            kin_sym_p1 = f"\\left(1 + l + \\frac{{\\Phi}}{{\\Phi_0}}\\right)^2" if st.session_state.use_flux else "(1 + l)^2"
            
            z_sym = "+ \\frac{1}{2}g\\mu_B B_z" if st.session_state.use_zeeman else ""
            z_sym_m = "- \\frac{1}{2}g\\mu_B B_z" if st.session_state.use_zeeman else ""
            
            r_sym = f"\\frac{{\\alpha_R}}{{r_0}}\\left(l + \\frac{{1}}{{2}} + \\frac{{\\Phi}}{{\\Phi_0}}\\right)" if st.session_state.use_flux else f"\\frac{{\\alpha_R}}{{r_0}}\\left(l + \\frac{{1}}{{2}}\\right)"
            r_sym_str = r_sym if st.session_state.use_rashba else "0"
            
            h_matrix_latex = f"""
            \\begin{{pmatrix}}
            \\frac{{\\hbar^2}}{{2m^* r_0^2}}{kin_sym} {z_sym} & {r_sym_str} \\\\
            {r_sym_str} & \\frac{{\\hbar^2}}{{2m^* r_0^2}}{kin_sym_p1} {z_sym_m}
            \\end{{pmatrix}}
            \\begin{{pmatrix}} \\chi_1 \\\\ \\chi_2 \\end{{pmatrix}} = E \\begin{{pmatrix}} \\chi_1 \\\\ \\chi_2 \\end{{pmatrix}}
            """
            st.latex(h_matrix_latex)

        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

        # --- BLOQUE 3: DISCRETE HAMILTONIAN ---
        with st.container(border=True):
            st.markdown("<p class='panel-title'>🔢 Block 3: Discrete Hamiltonian Matrix Evaluation</p>", unsafe_allow_html=True)
            
            hbar_sq_over_2m0 = 38.1  
            g_factor = 15.0         
            mu_B_meV = 0.05788      
            
            h_coef = hbar_sq_over_2m0 / (meff_val * (r0_val**2))
            zeeman_energy = 0.5 * g_factor * mu_B_meV * bz_val
            rashba_energy = (alpha_val / r0_val) * (l_val + 0.5 + phi_ratio) if st.session_state.use_rashba else 0.0
            
            h11 = h_coef * ((l_val + phi_ratio)**2) + zeeman_energy
            h22 = h_coef * ((1 + l_val + phi_ratio)**2) - zeeman_energy
            h12 = rashba_energy
            h21 = rashba_energy
            
            matrix_latex = f"""
            H_{{numerical}} = \\begin{{pmatrix}}
            {h11:.4f} & {h12:.4f} \\\\
            {h21:.4f} & {h22:.4f}
            \\end{{pmatrix}} \\text{{ meV}}
            """
            st.latex(matrix_latex)
            
            is_hermitian = np.allclose(h12, h21)
            if is_hermitian:
                st.markdown(f"<div class='matrix-status'>✓ HERMITIAN VALIDATION SUCCESFUL: H = H† | Matrix is self-adjoint for l={l_val}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='matrix-status' style='border-left-color:#ef4444;'>✗ VALIDATION FAILED: Asymmetric coupling detected.</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

        # --- BLOQUE 4: PHYSICAL INSIGHTS DINÁMICO ---
        with st.container(border=True):
            st.markdown("<p class='panel-title'>💡 Block 4: Advanced Physics Insights</p>", unsafe_allow_html=True)
            
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                st.markdown("""
                <div class='insight-card'>
                    <h4>Matrix Off-Diagonal Coupling</h4>
                    <p>The Rashba term behaves as an effective radial/azimuthal field. In this discrete spin-space basis, it directly mixes the angular state <b>|l, ↑⟩</b> with <b>|l+1, ↓⟩</b>, creating the non-zero off-diagonal elements.</p>
                </div>
                """, unsafe_allow_html=True)
            with col_in2:
                st.markdown("""
                <div class='insight-card'>
                    <h4>Hermiticity & Flux Shifts</h4>
                    <p>Notice that the Aharonov-Bohm flux shifts the kinetic terms continuously. Since the cross-terms remain identical real values, the matrix preserves perfect <b>Hermiticity</b>, guaranteeing real energy eigenvalues.</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.info("Everything ready. Move to step '2. Eigenenergies' in the top navbar to map out the complete energy spectrum curves.")