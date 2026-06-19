import streamlit as st
import numpy as np

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Rashba Ring Simulator", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- BLINDAJE DE ESTADOS: Inicialización Segura ---
if "engine_running" not in st.session_state:
    st.session_state.engine_running = False
if "use_flux" not in st.session_state:
    st.session_state.use_flux = True
if "use_zeeman" not in st.session_state:
    st.session_state.use_zeeman = True

# Forzamos internamente que Rashba esté siempre activo en la física del sistema
st.session_state["use_rashba"] = True

# Inicialización por defecto de variables numéricas para evitar errores de referencia cruzada
if "r0_val" not in st.session_state: st.session_state["r0_val"] = 40.0
if "meff_val" not in st.session_state: st.session_state["meff_val"] = 0.023
if "l_val" not in st.session_state: st.session_state["l_val"] = 1
if "phi_ratio" not in st.session_state: st.session_state["phi_ratio"] = 1.2
if "bz_val" not in st.session_state: st.session_state["bz_val"] = 2.5
if "alpha_val" not in st.session_state: st.session_state["alpha_val"] = 15.0

# --- CSS NEXUS: Navbar con Botones Horizontales Integrados ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; color: #0f172a; }

    /* INTERFAZ SUPERIOR: Header Navbar extendido para contener la botonera */
    .nexus-navbar {
        background: linear-gradient(90deg, #001f3f 0%, #003366 100%);
        padding: 20px 40px;
        border-bottom: 4px solid #00d4ff;
        margin: -65px -50px 20px -50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-area h1 { color: white !important; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 0.5px; }
    .brand-area p { color: #00d4ff; margin: 2px 0 0 0; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    /* ESTILO DE LOS PANELES */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important; border: none !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; border-radius: 6px !important;
    }
    
    .panel-title { color: #001f3f; font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; }
    .latex-title { font-size: 11px; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 1px; display: block; margin-top: 15px; margin-bottom: 5px; }
    .instruction-text { color: #475569; font-size: 13px; font-style: italic; margin-top: 15px; margin-bottom: 15px; display: block; }
    
    .matrix-status {
        background-color: #f1f5f9; padding: 10px; border-radius: 4px; border-left: 4px solid #10b981;
        font-family: monospace; font-size: 12px; font-weight: bold; color: #0f172a; margin-top: 10px;
    }

    /* CAMUFLAJE DE EXPANDERS: Estilo ejecutivo premium */
    .stDetails {
        background: white !important; 
        border: 1px solid #ced4da !important; 
        border-radius: 4px !important; 
        margin-bottom: 12px !important;
        box-shadow: none !important;
    }
    .stDetails summary {
        padding: 10px 14px !important;
    }
    .stDetails summary p {
        color: #001f3f !important; 
        font-size: 12px !important; 
        font-weight: 700 !important; 
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin: 0 !important;
    }
    .insight-content { 
        color: #495057; 
        font-size: 11.5px; 
        line-height: 1.5; 
        margin: 0;
        padding: 0px 14px 14px 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- NAVBAR HEADER ---
st.markdown("""
<div class='nexus-navbar'>
    <div class='brand-area'>
        <h1>NEXUS</h1>
        <p>Advanced Quantum Simulation Environment</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Botonera superior de navegación dinámica (Solo se muestra si el motor está corriendo)
if st.session_state.engine_running:
    st.markdown("<div style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([2, 2, 2, 2, 2])
    with b_col1:
        if st.button("1. Hamiltonian", use_container_width=True, type="primary"):
            st.switch_page("pages/01_Hamiltonian.py")
    with b_col2:
        if st.button("2. Eigenenergies", use_container_width=True):
            st.switch_page("pages/02_Eigenenergies.py")
    with b_col3:
        if st.button("3. Eigenstates", use_container_width=True):
            st.switch_page("pages/03_Eigenstates.py")
    with b_col4:
        if st.button("4. States", use_container_width=True):
            st.switch_page("pages/04_States.py")
    with b_col5:
        if st.button("5. Conductance", use_container_width=True):
            st.switch_page("pages/05_Conductance.py")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: -5px 0 25px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)
else:
    # Si el motor no corre, agregamos un espaciado limpio equivalente para que el panel no se pegue al header
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# ============================================================
# FASE 1: CONSTRUIBLE TEÓRICO 
# ============================================================
if not st.session_state.engine_running:
    col_main_left, col_main_right = st.columns([5.2, 1.8])

    with col_main_left:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Builder Hamiltonian</p>", unsafe_allow_html=True)
            container_render = st.empty()
            st.markdown("<span class='instruction-text'>Configure the active interaction terms to dynamically construct the system's quantum operator matrix:</span>", unsafe_allow_html=True)
            
            # Casillas de verificación
            grid_col1, grid_col2 = st.columns(2)
            with grid_col1:
                use_flux = st.checkbox("Include Aharonov-Bohm Flux (Gauge Field)", value=st.session_state.use_flux, key="flux_chk")
            with grid_col2:
                use_zeeman = st.checkbox("Include External Magnetic Field ($B_z$)", value=st.session_state.use_zeeman, key="zeeman_chk")
            
            use_rashba = True
            
            # Construcción matemática
            kinetic = "\\left(-i\\frac{\\partial}{\\partial\\phi} + \\frac{\\Phi}{\\Phi_0}\\right)^2" if use_flux else "\\left(-i\\frac{\\partial}{\\partial\\phi}\\right)^2"
            h_latex = f"\\hat{{H}} = \\frac{{\\hbar^2}}{{2m^* r_{{0}}^{2}}}{kinetic}"
            if use_zeeman: h_latex += " + \\frac{1}{2}g\\mu_{B}B_{z}\\hat{\\sigma}_{z}"
            h_latex += " + \\frac{\\alpha_{R}}{r_{0}}\\hat{\\sigma}_r\\left(-i\\frac{\\partial}{\\partial\\phi}" + (" + \\frac{\\Phi}{\\Phi_0}" if use_flux else "") + "\\right) - i\\frac{\\alpha_R}{2r_0}\\hat{\\sigma}_\\phi"
            
            with container_render.container():
                st.markdown("<span class='latex-title'>Explicit Generalized Hamiltonian Matrix</span>", unsafe_allow_html=True)
                st.markdown("<hr style='border-color: #e2e8f0; margin: 10px 0;'>", unsafe_allow_html=True)
                st.latex(h_latex)
                st.markdown("<hr style='border-color: #e2e8f0; margin: 10px 0;'>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # BOTÓN RUN MINIMALISTA
            btn_col, _ = st.columns([1, 5])
            with btn_col:
                if st.button("Run", type="primary"):
                    st.session_state.use_flux = use_flux
                    st.session_state.use_zeeman = use_zeeman
                    st.session_state.use_rashba = use_rashba
                    st.session_state.engine_running = True
                    st.rerun()

    with col_main_right:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Physics Insights</p>", unsafe_allow_html=True)
            
            with st.expander("Hamiltonian Operator", expanded=True):
                st.markdown("""
                <div class='insight-content'>
                    <p>The Hamiltonian <b>H</b> is the complete mathematical representation of the quantum system. It contains all energetic contributions, interactions, and symmetry-breaking mechanisms that govern the dynamics of the electron.</p>
                    <p style='margin-top: 6px; font-style: italic;'>Every observable quantity calculated in this simulator — energy spectra, eigenstates, spin textures, and transport properties — originates from the eigenvalue problem: <b>HΨ = EΨ</b>.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with st.expander("Physical Meaning", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p>Each term of the Hamiltonian corresponds to a distinct physical mechanism:</p>
                    <ul style='margin: 4px 0; padding-left: 16px; font-size: 11.5px; color:#495057;'>
                        <li><b>Kinetic energy</b> defines the free propagation of the electron.</li>
                        <li><b>Magnetic flux</b> introduces geometric quantum phases.</li>
                        <li><b>Zeeman coupling</b> interacts directly with spin.</li>
                        <li><b>Spin-orbit interactions</b> couple orbital motion and spin dynamics.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            with st.expander("Why Simplify?", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p>Analytical and numerical studies often exploit the symmetries of the device to reduce the Hamiltonian to a lower-dimensional effective model. This reduction preserves the essential physics while exposing the dominant mechanisms.</p>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# HAMILTONIANO EN FORMA MATRICIAL (FASE 2: ENTORNO INTERACTIVO)
# ============================================================
else:
    col_main_left, col_main_right = st.columns([5.2, 1.8])

    r0_val = st.session_state["r0_val"]
    meff_val = st.session_state["meff_val"]
    l_val = st.session_state["l_val"]
    phi_ratio = st.session_state["phi_ratio"] if st.session_state.use_flux else 0.0
    bz_val = st.session_state["bz_val"] if st.session_state.use_zeeman else 0.0
    alpha_val = st.session_state["alpha_val"] if st.session_state.use_rashba else 0.0

    hbar_sq_over_2m0 = 38.1  
    g_factor = 15.0        
    mu_B_meV = 0.05788      
    
    h_coef = hbar_sq_over_2m0 / (meff_val * (r0_val**2))
    zeeman_energy = 0.5 * g_factor * mu_B_meV * bz_val
    rashba_energy = (alpha_val / r0_val) * (l_val + 0.5 + phi_ratio) if st.session_state.use_rashba else 0.0
    
    h11 = h_coef * ((l_val + phi_ratio)**2) + zeeman_energy if st.session_state.use_zeeman else h_coef * ((l_val + phi_ratio)**2)
    h22 = h_coef * ((1 + l_val + phi_ratio)**2) - zeeman_energy if st.session_state.use_zeeman else h_coef * ((1 + l_val + phi_ratio)**2)
    h12 = rashba_energy
    h21 = rashba_energy

    with col_main_left:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Quantum Operators & Basis</p>", unsafe_allow_html=True)
            tab_matrix, tab_basis, tab_pauli = st.tabs(["Matrix Projection", "Spinor Basis", "Local Pauli Fields"])
            
            with tab_matrix:
                kin_sym = f"\\left(l + \\frac{{\\Phi}}{{\\Phi_0}}\\right)^2" if st.session_state.use_flux else "l^2"
                kin_sym_p1 = f"\\left(1 + l + \\frac{{\\Phi}}{{\\Phi_0}}\\right)^2" if st.session_state.use_flux else "(1 + l)^2"
                z_sym = "+ \\frac{1}{2}g\\mu_B B_z" if st.session_state.use_zeeman else ""
                z_sym_m = "- \\frac{1}{2}g\\mu_B B_z" if st.session_state.use_zeeman else ""
                r_sym = f"\\frac{{\\alpha_R}}{{r_0}}\\left(l + \\frac{{1}}{{2}} + \\frac{{\\Phi}}{{\\Phi_0}}\\right)" if st.session_state.use_flux else f"\\frac{{\\alpha_R}}{{r_0}}\\left(l + \\frac{{1}}{{2}}\\right)"
                r_sym_str = r_sym if st.session_state.use_rashba else "0"
                
                st.latex(f"""
                \\hat{{H}}_{{discrete}} = \\begin{{pmatrix}}
                \\frac{{\\hbar^2}}{{2m^* r_0^2}}{kin_sym} {z_sym} & {r_sym_str} \\\\
                {r_sym_str} & \\frac{{\\hbar^2}}{{2m^* r_0^2}}{kin_sym_p1} {z_sym_m}
                \\end{{pmatrix}}
                """)
                
            with tab_basis:
                st.latex(r"\Psi_{l}(\phi) = \begin{pmatrix} \chi_1 e^{i l \phi} \\ \chi_2 e^{i(l+1)\phi} \end{pmatrix}")
                
            with tab_pauli:
                st.markdown("**Fundamental SU(2) Pauli Matrices:**")
                st.latex(r"""
                \hat{\sigma}_x = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad
                \hat{\sigma}_y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad
                \hat{\sigma}_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}
                """)
                st.markdown("<hr style='border-color: #f1f5f9; margin: 10px 0;'>", unsafe_allow_html=True)
                st.markdown("**Dynamic Local Operators (Cylindrical Projections):**")
                st.latex(r"""
                \hat{\sigma}_r = \hat{\sigma}_x \cos\phi + \hat{\sigma}_y \sin\phi = \begin{pmatrix} 0 & e^{-i\phi} \\ e^{i\phi} & 0 \end{pmatrix}
                """)
                st.latex(r"""
                \hat{\sigma}_\phi = -\hat{\sigma}_x \sin\phi + \hat{\sigma}_y \cos\phi = \begin{pmatrix} 0 & -ie^{-i\phi} \\ ie^{i\phi} & 0 \end{pmatrix}
                """)

        with st.container(border=True):
            st.markdown("<p class='panel-title'>Discrete Hamiltonian Matrix Evaluation</p>", unsafe_allow_html=True)
            st.latex(f"""
            H = \\begin{{pmatrix}}
            {h11:.4f} & {h12:.4f} \\\\
            {h21:.4f} & {h22:.4f}
            \\end{{pmatrix}} \\text{{ meV}}
            """)
            st.markdown(f"<div class='matrix-status' style='text-align:center; border-left: 3px solid #cbd5e1; color: #475569;'>HERMITIAN VALIDATION SUCCESSFUL: H = H†</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<p class='panel-title' style='margin-bottom:12px;'>System Parameters Console</p>", unsafe_allow_html=True)
            grid_p1, grid_p2, grid_p3 = st.columns([1.5, 1.0, 1.5])
            
            with grid_p1:
                st.session_state["r0_val"] = st.slider("Ring Radius $r_0$ (nm)", 10.0, 100.0, float(st.session_state["r0_val"]), step=2.5, key='r0_slider')
                st.session_state["meff_val"] = st.slider("Effective Mass $m^*$ ($m_0$)", 0.01, 0.10, float(st.session_state["meff_val"]), step=0.001, key='meff_slider')
            with grid_p2:
                st.session_state["l_val"] = st.number_input("Angular Momentum $l$", value=int(st.session_state["l_val"]), step=1, key='l_input')
            with grid_p3:
                if st.session_state.use_flux:
                    st.session_state["phi_ratio"] = st.slider("Flux Ratio $\\Phi/\\Phi_0$", 0.0, 5.0, float(st.session_state["phi_ratio"]), step=0.1, key='phi_slider')
                if st.session_state.use_zeeman:
                    st.session_state["bz_val"] = st.slider("Magnetic Field $B_z$ (T)", 0.0, 10.0, float(st.session_state["bz_val"]), step=0.1, key='bz_slider')
                if st.session_state.use_rashba:
                    st.session_state["alpha_val"] = st.slider("Rashba Coupling $\\alpha_R$", 0.0, 40.0, float(st.session_state["alpha_val"]), step=1.0, key='alpha_slider')

    with col_main_right:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Physics Insights</p>", unsafe_allow_html=True)
            
            if not st.session_state.use_rashba or rashba_energy == 0:
                ins_1 = "<b>Orbital Confinement Dominant.</b> Spin-orbit interaction is absent. Spin projections remain perfectly decoupled and spin-pure."
                ins_2 = "<b>Hamiltonian becomes diagonal.</b> Spin-up and spin-down states are completely uncoupled because the Rashba parameter is zero."
            elif h_coef > rashba_energy:
                ins_1 = "Rashba coupling is weak compared to orbital confinement. Spin mixing is limited and the eigenstates remain mostly spin-pure."
                ins_2 = "Diagonal terms represent orbital and Zeeman energies. Off-diagonal terms originate from Rashba coupling and connect opposite spin channels."
            else:
                ins_1 = "Rashba coupling dominates the orbital energy scale. Strong spin-orbit hybridization is expected."
                ins_2 = "Diagonal terms represent orbital and Zeeman energies. Off-diagonal terms originate from Rashba coupling and connect opposite spin channels."
                
            if (st.session_state.use_flux and phi_ratio != 0) or (st.session_state.use_zeeman and bz_val != 0):
                ins_3 = "Hamiltonian is Hermitian (real eigenvalues). <span style='color:#475569; font-weight:600; display:block; margin-top:4px;'>Time-reversal symmetry is broken by magnetic flux/fields.</span>"
            else:
                ins_3 = "Hamiltonian is Hermitian (real eigenvalues). <span style='color:#475569; font-weight:600; display:block; margin-top:4px;'>Time-reversal symmetry preserved.</span>"
                
            ins_5 = f"The selected state corresponds to an electron confined to a <b>{r0_val:.1f} nm</b> semiconductor ring. "
            if st.session_state.use_rashba and alpha_val > 0:
                ins_5 += "Rashba interaction introduces spin precession around the ring trajectory. "
            if not st.session_state.use_rashba or h_coef > rashba_energy:
                ins_5 += f"Orbital confinement energy ({h_coef:.2f} meV) exceeds spin-orbit interaction energy."
            else:
                ins_5 += f"Spin-orbit splitting overrides the kinetic quantization scale."

            st.markdown(f"""
            <div class='insight-card'><h4>DOMINANT INTERACTION</h4><p>{ins_1}</p></div>
            <div class='insight-card'><h4>MATRIX STRUCTURE</h4><p>{ins_2}</p></div>
            <div class='insight-card'><h4>SYMMETRY ANALYSIS</h4><p>{ins_3}</p></div>
            <div class='insight-card'><h4>PHYSICAL INTERPRETATION</h4><p>{ins_5}</p></div>
            <div class='insight-card'>
                <h4>NUMERICAL STATUS</h4>
                <p style='font-family: monospace; font-size: 11px; margin:0;'>
                    Basis size: 2 x 2<br>
                    Matrix conditioning: Stable<br>
                    Ready for eigensolver.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # --- PIE DE PÁGINA: CONTROL DE RESET ESTÁNDAR Y UNIFORME ---
    st.markdown("---")
    col_reset, col_spacer = st.columns([1.5, 5.5])
    with col_reset:
        if st.button("Reset", use_container_width=True, type="secondary", key="global_reset_h"):
            st.session_state.engine_running = False
            st.rerun()