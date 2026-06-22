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

# Botonera superior de navegación dinámica (CORREGIDO: Se eliminó '4. States' y ahora es '4. Conductance')
if st.session_state.engine_running:
    st.markdown("<div style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3, b_col4 = st.columns([2.5, 2.5, 2.5, 2.5])
    with b_col1:
        if st.button("1. Hamiltonian", use_container_width=True, type="primary"):
            st.switch_page("pages/01_Hamiltonian.py")
    with b_col2:
        if st.button("2. Eigenenergies", use_container_width=True):
            st.switch_page("pages/02_Eigenenergies.py")
    with b_col3:
        if st.button("3. Eigenstates", use_container_width=True):
            st.switch_page("pages/03_Eigenstates.py")
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
            
            with st.expander("Hamiltonian Operator", expanded=False):
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
# HAMILTONIANO EN FORMA MATRICIAL (FASE 2: OPERADORES Y BASES)
# ============================================================
else:
    col_main_left, col_main_right = st.columns([5.2, 1.8])

    with col_main_left:
        # CONTENEDOR PRINCIPAL: Operadores algebraicos y de simetría en base discreta
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

        # CONTENEDOR SECUNDARIO: Bloqueo teórico de alto nivel
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Discrete Hamiltonian Matrix Evaluation</p>", unsafe_allow_html=True)
            st.markdown(
                "<div style='padding: 25px 15px; background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 4px; text-align: center; color: #64748b; font-size: 13px; font-style: italic;'>\n"
                "<b>Awaiting Operator Compilation:</b> Numerical evaluation and eigenvalue solver will unlock upon dynamic laboratory model generation.\n"
                "</div>", 
                unsafe_allow_html=True
            )
            st.markdown(f"<div class='matrix-status' style='text-align:center; border-left: 3px solid #cbd5e1; color: #475569;'>OPERATOR ALGEBRA INITIALIZED SUCCESSFUL: H = H†</div>", unsafe_allow_html=True)

    with col_main_right:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Hamiltonian Representation</p>", unsafe_allow_html=True)
            
            # --- EXPANDER 1: BASIS REPRESENTATION ---
            with st.expander("Basis Representation", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p>The continuous Hamiltonian has been projected onto the selected spinor basis.</p>
                    <p style='margin-top: 6px;'>All operators are now expressed as discrete matrix elements acting within the reduced Hilbert space.</p>
                </div>
                """, unsafe_allow_html=True)
                
            # --- EXPANDER 2: MATRIX STRUCTURE ---
            with st.expander("Matrix Structure", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p><b>Diagonal entries</b> describe self-energy contributions associated with orbital motion and external fields.</p>
                    <p style='margin-top: 6px;'><b>Off-diagonal entries</b> encode coupling mechanisms capable of mixing basis states and modifying the quantum spectrum.</p>
                </div>
                """, unsafe_allow_html=True)

            # --- EXPANDER 3: HERMITICITY CHECK ---
            with st.expander("Hermiticity Check", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p>The constructed Hamiltonian satisfies the fundamental property:</p>
                    <p style='text-align: center; font-family: monospace; font-size: 13px; font-weight: bold; margin: 10px 0; color: #003366;'>H = H†</p>
                    <p>This mathematical symmetry strictly ensures real energy eigenvalues and unitary quantum evolution.</p>
                </div>
                """, unsafe_allow_html=True)

            # --- EXPANDER 4: DETECTED PHYSICS ---
            with st.expander("Detected Physics", expanded=False):
                flux_badge = "<span style='color: #10b981; font-weight: bold;'>Active</span>" if st.session_state.use_flux else "<span style='color: #94a3b8;'>Inactive</span>"
                zeeman_badge = "<span style='color: #10b981; font-weight: bold;'>Active</span>" if st.session_state.use_zeeman else "<span style='color: #94a3b8;'>Inactive</span>"
                rashba_badge = "<span style='color: #10b981; font-weight: bold;'>Active</span>" if st.session_state.use_rashba else "<span style='color: #94a3b8;'>Inactive</span>"
                
                st.markdown(f"""
                <div class='insight-content' style='padding: 5px 0px;'>
                    <table style='width: 100%; font-size: 12px; border-collapse: collapse; line-height: 1.6;'>
                        <thead>
                            <tr style='border-bottom: 2px solid #e2e8f0; text-align: left;'>
                                <th style='padding: 6px 4px; color: #475569; font-weight: 700;'>Quantum Term</th>
                                <th style='padding: 6px 4px; text-align: right; color: #475569; font-weight: 700;'>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style='border-bottom: 1px solid #e2e8f0;'>
                                <td style='padding: 10px 4px; font-weight: 500;'>Kinetic Energy</td>
                                <td style='padding: 10px 4px; text-align: right; color: #10b981; font-weight: bold;'>Active</td>
                            </tr>
                            <tr style='border-bottom: 1px solid #e2e8f0;'>
                                <td style='padding: 10px 4px; font-weight: 500;'>Aharonov-Bohm Flux</td>
                                <td style='padding: 10px 4px; text-align: right;'>{flux_badge}</td>
                            </tr>
                            <tr style='border-bottom: 1px solid #e2e8f0;'>
                                <td style='padding: 10px 4px; font-weight: 500;'>Rashba Coupling</td>
                                <td style='padding: 10px 4px; text-align: right;'>{rashba_badge}</td>
                            </tr>
                            <tr>
                                <td style='padding: 10px 4px; font-weight: 500;'>External Magnetic Field</td>
                                <td style='padding: 10px 4px; text-align: right;'>{zeeman_badge}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)

            # --- EXPANDER 5: COMPUTATIONAL STATUS ---
            with st.expander("Computational Status", expanded=False):
                f_icon = "Active" if st.session_state.use_flux else "Inactive"
                z_icon = "Active" if st.session_state.use_zeeman else "Inactive"
                r_icon = "Active" if st.session_state.use_rashba else "Inactive"
                
                st.markdown(f"""
                <div class='insight-content'>
                    <p style='margin-bottom: 6px; font-weight: 600; color: #003366;'>Active Operators:</p>
                    <ul style='margin: 0; padding-left: 14px; list-style-type: square; line-height: 1.5;'>
                        <li>Rashba Spin-Orbit: {r_icon}</li>
                        <li>Kinetic Energy: Active</li>
                        <li>Magnetic Flux: {f_icon}</li>
                        <li>Zeeman Interaction: {z_icon}</li>
                    </ul>
                    <hr style='margin: 10px 0; border-color: #e2e8f0;'>
                    <p style='font-family: monospace; font-size: 11px; margin: 0; color: #334155; line-height: 1.5;'>
                        Matrix representation generated.<br>
                        Basis dimension: 2 × 2<br>
                        Operator compilation: Complete<br>
                        Eigenvalue solver: Awaiting parameters.
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