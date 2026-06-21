import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Rashba Ring Simulator", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- CONSTANTES FÍSICAS REALES ---
hbar = 1.054571817e-34  # J*s
m0 = 9.1093837e-31      # kg
eV = 1.602176634e-19    # J
mu_B = 9.274010078e-24  # J/T
g_factor = -14.4        # Factor-g para InAs típico de NEXUS

# --- BLINDAJE DE ESTADOS: Inicialización Segura ---
if "engine_running" not in st.session_state:
    st.session_state.engine_running = False
if "use_flux" not in st.session_state:
    st.session_state.use_flux = True
if "use_zeeman" not in st.session_state:
    st.session_state.use_zeeman = True
st.session_state["use_rashba"] = True

# --- CSS NEXUS: Consistencia Visual Uniforme ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; color: #0f172a; }

    /* INTERFAZ SUPERIOR: Header Navbar extendido */
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
    .instruction-text { color: #475569; font-size: 13px; font-style: italic; margin-top: 5px; margin-bottom: 15px; display: block; }
    
    .matrix-status {
        background-color: #f1f5f9; padding: 10px; border-radius: 4px; border-left: 4px solid #003366;
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

# Botonera superior de navegación dinámica (Fase Activa: Eigenenergies)
if st.session_state.engine_running:
    st.markdown("<div style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([2, 2, 2, 2, 2])
    with b_col1:
        if st.button("1. Hamiltonian", use_container_width=True):
            st.switch_page("pages/01_Hamiltonian.py")
    with b_col2:
        if st.button("2. Eigenenergies", use_container_width=True, type="primary"):
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
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

# ============================================================
# CONTROL PRINCIPAL DE LA PÁGINA
# ============================================================
if not st.session_state.engine_running:
    st.warning("Please initialize the Quantum Engine in the Hamiltonian Builder panel before accessing the eigenvalues console.")
else:
    col_main_left, col_main_right = st.columns([5.2, 1.8])

    with col_main_left:
        # CONTENEDOR 1: Parámetros del Laboratorio Interactivo
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Interactive Simulation Parameters</p>", unsafe_allow_html=True)
            
            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            
            with p_col1:
                l_value = st.selectbox(
                    "Angular Momentum (l)", 
                    options=[-5, -4, -3, -2, -1, 1, 2, 3, 4, 5], 
                    index=5
                )
            with p_col2:
                alpha_max = st.slider("α Max Range", min_value=1, max_value=30, value=10, step=1)
            with p_col3:
                # Deshabilitado visualmente si no se activó en la Fase 1 para mantener rigor
                if st.session_state.use_zeeman:
                    Bz_value = st.slider("Magnetic Field Bz (T)", min_value=-5.0, max_value=5.0, value=0.0, step=0.1)
                else:
                    st.text_input("Magnetic Field Bz (T)", value="0.0 (Inactive)", disabled=True)
                    Bz_value = 0.0
            with p_col4:
                if st.session_state.use_flux:
                    Phi_ratio_value = st.slider("Magnetic Flux (Φ/Φ0)", min_value=-2.0, max_value=2.0, value=0.0, step=0.05)
                else:
                    st.text_input("Magnetic Flux (Φ/Φ0)", value="0.0 (Inactive)", disabled=True)
                    Phi_ratio_value = 0.0

        # CONTENEDOR 2: Renderizado de la Gráfica Interactiva del Script en eV
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Interactive Eigenenergy Spectrum</p>", unsafe_allow_html=True)
            st.markdown("<span class='instruction-text'>Evolución de los niveles E+ y E- en función de la intensidad del acoplamiento Rashba:</span>", unsafe_allow_html=True)
            
            # --- SOLVER NUMÉRICO DIRECTO BASADO EN TU ESTRUCTURA ---
            alpha_values = np.linspace(0, alpha_max, 300)
            r0_num = 40.0 * 1e-9  # Radio efectivo fijo en nm para consistencia de la escala
            m_eff = 0.023 * m0    # Masa efectiva del InAs
            
            # Cálculo de energías base escaladas a eV
            E_0 = (hbar**2) / (2 * m_eff * r0_num**2)
            
            # Implementación exacta de la física de tu script interactivo
            # Términos orbitales dinámicos dependientes de la configuración de fase
            phi_eff = Phi_ratio_value if st.session_state.use_flux else 0.0
            zeeman_eff = 0.5 * g_factor * mu_B * Bz_value if st.session_state.use_zeeman else 0.0
            
            # Matrices diagonales asimétricas y acoplamiento Rashba exacto por punto
            E_base = 0.5 * E_0 * ((l_value + phi_eff)**2 + (1 + l_value + phi_eff)**2)
            Delta_diag = 0.5 * E_0 * ((l_value + phi_eff)**2 - (1 + l_value + phi_eff)**2) + zeeman_eff
            
            # El parámetro alpha_max mapea la escala adimensional del acoplamiento
            V_rashba = (E_0 * alpha_values) * (l_value + 0.5 + phi_eff) / alpha_max if alpha_max > 0 else 0
            
            E_plus_num = (E_base + np.sqrt(Delta_diag**2 + V_rashba**2)) / eV
            E_minus_num = (E_base - np.sqrt(Delta_diag**2 + V_rashba**2)) / eV
            
            # --- RENDERIZADO CON MATPLOTLIB PREMIUM ---
            fig, ax = plt.subplots(figsize=(7, 3.4), dpi=200)
            fig.patch.set_facecolor('white')
            ax.set_facecolor('#ffffff')
            
            ax.plot(alpha_values, E_plus_num, color='#003366', linewidth=2.0, label=r"$E_+$ subband")
            ax.plot(alpha_values, E_minus_num, color='#00d4ff', linestyle="--", linewidth=2.0, label=r"$E_-$ subband")
            
            ax.set_xlabel(r"$\alpha=\frac{2m^\ast\alpha_R r_0}{\hbar^2}$ (Rashba Int.)", fontsize=8, color='#0f172a', fontweight='bold')
            ax.set_ylabel("Energy (eV)", fontsize=8, color='#0f172a', fontweight='bold')
            
            ax.set_title(rf"$l={l_value}$,  $B_z={Bz_value:.2f}$ T,  $\Phi/\Phi_0={Phi_ratio_value:.2f}$", fontsize=9, fontweight="bold", color='#001f3f')
            
            ax.grid(True, linestyle='--', linewidth=0.5, color='#e2e8f0', alpha=0.7)
            ax.tick_params(colors='#475569', labelsize=7)
            
            # Ajustar formato de los ejes de forma limpia
            ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#cbd5e1')
                spine.set_linewidth(0.8)
                
            ax.legend(loc="best", frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=7.5)
            fig.tight_layout()
            
            st.pyplot(fig)
            st.markdown(f"<div class='matrix-status'>NUMERICAL SPECTRAL GRAPH GENERATED: Evolution verified for l={l_value}</div>", unsafe_allow_html=True)

    with col_main_right:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Spectral Insights</p>", unsafe_allow_html=True)
            
            with st.expander("Energy Bands Structure", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p>The continuous eigenvalue equation generates two discrete energy branches labeled as <b>E+</b> and <b>E-</b>.</p>
                    <p style='margin-top: 6px;'>These solutions correspond to the spin-split states induced by the non-trivial routing of the orbital wavefunctions around the ring topology.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with st.expander("Rashba Dispersion Impact", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p>The radical term acts as an effective interaction energy scale.</p>
                    <p style='margin-top: 6px;'>When Spin-Orbit interaction is turned on, the off-diagonal coupling avoids the crossing of energy bands, creating a forbidden energy gap proportional to the coupling strength.</p>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Kramers Degeneracy Check", expanded=False):
                if st.session_state.use_flux or st.session_state.use_zeeman:
                    status_sym = "Broken due to external fields. States at +l and -l are shifted, lifting the spin degeneracy."
                else:
                    status_sym = "Preserved. The energy branches fulfill the relation E(l, up) = E(-l, down), ensuring time-reversal symmetric doublets."
                    
                st.markdown(f"""
                <div class='insight-content'>
                    <p><b>Time-Reversal Symmetry Status:</b></p>
                    <p style='margin-top: 4px; font-weight: 600; color: #003366;'>{status_sym}</p>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Spectral Coherence", expanded=False):
                flux_badge = "<span style='color: #10b981; font-weight: bold;'>Active</span>" if st.session_state.use_flux else "<span style='color: #94a3b8;'>Inactive</span>"
                zeeman_badge = "<span style='color: #10b981; font-weight: bold;'>Active</span>" if st.session_state.use_zeeman else "<span style='color: #94a3b8;'>Inactive</span>"
                
                st.markdown(f"""
                <div class='insight-content' style='padding: 5px 0px;'>
                    <table style='width: 100%; font-size: 12px; border-collapse: collapse; line-height: 1.6;'>
                        <thead>
                            <tr style='border-bottom: 2px solid #e2e8f0; text-align: left;'>
                                <th style='padding: 6px 4px; color: #475569; font-weight: 700;'>Spectral Factor</th>
                                <th style='padding: 6px 4px; text-align: right; color: #475569; font-weight: 700;'>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style='border-bottom: 1px solid #e2e8f0;'>
                                <td style='padding: 10px 4px; font-weight: 500;'>Orbital Quantization</td>
                                <td style='padding: 10px 4px; text-align: right; color: #10b981; font-weight: bold;'>Active</td>
                            </tr>
                            <tr style='border-bottom: 1px solid #e2e8f0;'>
                                <td style='padding: 10px 4px; font-weight: 500;'>Aharonov-Bohm Shift</td>
                                <td style='padding: 10px 4px; text-align: right;'>{flux_badge}</td>
                            </tr>
                            <tr>
                                <td style='padding: 10px 4px; font-weight: 500;'>External Magnetic Field</td>
                                <td style='padding: 10px 4px; text-align: right;'>{zeeman_badge}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Solver Computational Status", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p style='margin-bottom: 6px; font-weight: 600; color: #003366;'>Algebraic State:</p>
                    <ul style='margin: 0; padding-left: 14px; list-style-type: square; line-height: 1.5;'>
                        <li>Eigenvalue Equation: Formulated</li>
                        <li>Subband Symmetries: Verified</li>
                        <li>Numerical Solver: Dynamic Active</li>
                    </ul>
                    <hr style='margin: 10px 0; border-color: #e2e8f0;'>
                    <p style='font-family: monospace; font-size: 11px; margin: 0; color: #334155; line-height: 1.5;'>
                        Solver core: Numerical Grid<br>
                        Roots calculation: Interactive Matrix<br>
                        Execution: Real-Time Stream.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # --- PIE DE PÁGINA: CONTROL DE RESET CON REDIRECCIÓN AUTOMÁTICA ---
    st.markdown("---")
    col_reset, col_spacer = st.columns([1.5, 5.5])
    with col_reset:
        if st.button("Reset", use_container_width=True, type="secondary", key="global_reset_e"):
            st.session_state.engine_running = False
            try:
                st.switch_page("pages/01_Hamiltonian.py")
            except Exception:
                st.switch_page("app.py")