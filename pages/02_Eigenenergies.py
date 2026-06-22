import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Eigenenergies Simulator", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- STATE PROTECTION & LINKING WITH BUILDER ---
if "engine_running" not in st.session_state:
    st.session_state.engine_running = False
if "use_flux" not in st.session_state:
    st.session_state.use_flux = True
if "use_zeeman" not in st.session_state:
    st.session_state.use_zeeman = True
st.session_state["use_rashba"] = True

# Fallback session settings matching the Hamiltonian builder exactly
if "r0_val" not in st.session_state: st.session_state["r0_val"] = 40.0
if "meff_val" not in st.session_state: st.session_state["meff_val"] = 0.023
if "l_val" not in st.session_state: st.session_state["l_val"] = 1
if "phi_ratio" not in st.session_state: st.session_state["phi_ratio"] = 1.2
if "bz_val" not in st.session_state: st.session_state["bz_val"] = 2.5
if "alpha_val" not in st.session_state: st.session_state["alpha_val"] = 15.0

# --- NEXUS CSS: Unified Premium Visual Theme ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; color: #0f172a; }

    /* UPPER INTERFACE: Extended Header Navbar */
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

    /* PANEL LAYOUT STYLE */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important; border: none !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; border-radius: 6px !important;
    }
    
    .panel-title { color: #001f3f; font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; }
    .latex-title { font-size: 11px; font-weight: 700; color: #003366; text-transform: uppercase; letter-spacing: 1px; display: block; margin-top: 15px; margin-bottom: 5px; }
    
    .matrix-status {
        background-color: #f1f5f9; padding: 10px; border-radius: 4px; border-left: 4px solid #003366;
        font-family: monospace; font-size: 12px; font-weight: bold; color: #0f172a; margin-top: 10px;
    }

    /* EXPANDER CAMOUFLAGE */
    .stDetails {
        background: white !important; border: 1px solid #ced4da !important; border-radius: 4px !important; margin-bottom: 12px !important;
    }
    .stDetails summary p {
        color: #001f3f !important; font-size: 12px !important; font-weight: 700 !important; text-transform: uppercase !important; margin: 0 !important;
    }
    .insight-content { color: #495057; font-size: 11.5px; line-height: 1.5; padding: 0px 14px 14px 14px; }
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

# Dynamic Top Navigation Panel
if st.session_state.engine_running:
    st.markdown("<div style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        if st.button("1. Hamiltonian", use_container_width=True): st.switch_page("pages/01_Hamiltonian.py")
    with b_col2:
        if st.button("2. Eigenenergies", use_container_width=True, type="primary"): st.switch_page("pages/02_Eigenenergies.py")
    with b_col3:
        if st.button("3. Eigenstates", use_container_width=True): st.switch_page("pages/03_Eigenstates.py")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: -5px 0 25px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)
else:
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

if not st.session_state.engine_running:
    st.warning("Please initialize the Quantum Engine in the Hamiltonian Builder panel before accessing the eigenvalues console.")
else:
    has_flux = st.session_state.use_flux and st.session_state.phi_ratio != 0.0
    has_zeeman = st.session_state.use_zeeman and st.session_state.bz_val != 0.0
    is_general_case = has_flux or has_zeeman
    case_title = "General Regime (Rashba + Flux + Zeeman)" if is_general_case else "Base Regime (Rashba Only - Recovered)"

    # --- MAIN ASYMMETRIC GRID WORKSPACE ---
    col_main_left, col_main_right = st.columns([5.2, 1.8])

    with col_main_left:
        # PANEL 1: Interactive System Controls
        with st.container(border=True):
            st.markdown(f"<p class='panel-title'>Interactive Spectrum Laboratory — {case_title}</p>", unsafe_allow_html=True)
            
            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            with p_col1:
                alpha_max_slider = st.slider("α Max Range", min_value=1.0, max_value=30.0, value=10.0, step=1.0)
            with p_col2:
                l_options = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
                try: default_index = l_options.index(st.session_state.l_val)
                except ValueError: default_index = 6
                l_selected = st.selectbox("Quantum Number (l)", options=l_options, index=default_index)
                st.session_state.l_val = l_selected
            with p_col3:
                if st.session_state.use_zeeman:
                    bz_live = st.slider("Zeeman Field (B_z)", min_value=0.0, max_value=5.0, value=float(st.session_state.bz_val), step=0.1)
                    st.session_state.bz_val = bz_live
                else:
                    st.text_input("Zeeman Field (B_z)", value="0.0 (Inactive)", disabled=True)
            with p_col4:
                if st.session_state.use_flux:
                    phi_live = st.slider("Magnetic Flux (Φ/Φ0)", min_value=-2.0, max_value=2.0, value=float(st.session_state.phi_ratio), step=0.1)
                    st.session_state.phi_ratio = phi_live
                else:
                    st.text_input("Magnetic Flux (Φ/Φ0)", value="0.0 (Inactive)", disabled=True)

        # PANEL 2: Symbolic Equations & Dynamic Graphs Grid
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Secular Equation & Multi-Subband Dispersion Vectors</p>", unsafe_allow_html=True)
            
            st.markdown("<span class='latex-title'>Characteristic Analytical Solution from Literature:</span>", unsafe_allow_html=True)
            if is_general_case:
                E_final_latex = (
                    r"E_{\pm} = \frac{\hbar^{2}}{2m^*r_{0}^{2}} \left[ \left(l+\frac{\Phi}{\Phi_{0}}+\frac{1}{2}\right)^{2} + \frac{1}{4} \right] "
                    r"\pm \sqrt{ \left[ \frac{1}{2}g\mu_BB_z - \frac{\hbar^2}{2m^*r_0^2}\left(l+\frac{\Phi}{\Phi_{0}}+\frac{1}{2}\right) \right]^{2} "
                    r"+ \left[ \frac{\alpha_R}{r_{0}}\left(l+\frac{\Phi}{\Phi_{0}}+\frac{1}{2}\right) \right]^{2} }"
                )
            else:
                E_final_latex = (
                    r"E_\pm = \frac{\hbar^2}{2m^*r_0^2} \begin{Bmatrix} \begin{bmatrix} \left(l+\frac{1}{2}\right)^2 "
                    r"+ \frac{1}{4} \end{bmatrix} \pm \sqrt{\left(l+\frac{1}{2}\right)^2 \begin{bmatrix} 1 "
                    r"+ \left(\frac{2m^\ast \alpha_R r_0}{\hbar^2}\right)^2 \end{bmatrix}} \end{Bmatrix}"
                )
            st.latex(E_final_latex)

            # Mathematical Physical Solvers
            hbar_num = 1.05457e-34
            m_e = 9.10938e-31
            m_eff = st.session_state.meff_val * m_e
            r0_num = st.session_state.r0_val * 1e-9 
            eV = 1.6022e-19
            p_factor = (hbar_num**2) / (2 * m_eff * r0_num**2) / eV

            mu_B_num = 9.27401e-24
            g_num = 2.0
            Z_factor = 0.5 * g_num * mu_B_num * (st.session_state.bz_val if st.session_state.use_zeeman else 0.0) / eV

            def scientific_formatter(y, pos):
                if y == 0: return "0"
                exponent = int(np.floor(np.log10(abs(y))))
                coeff = y / 10**exponent
                coeff = round(coeff, 2)
                if float(coeff).is_integer(): coeff = int(coeff)
                superscript_map = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
                return f"{coeff}×10{str(exponent).translate(superscript_map)}"

            formatter = FuncFormatter(scientific_formatter)

            alpha_space = np.linspace(0.0, alpha_max_slider, 300)
            l_actual = st.session_state.l_val

            fig, ax = plt.subplots(figsize=(11, 4.5), dpi=200)
            fig.patch.set_facecolor('white')
            ax.set_facecolor('#ffffff')
            
            def compute_bands(l_val):
                f_ratio = st.session_state.phi_ratio if st.session_state.use_flux else 0.0
                q_eff = l_val + f_ratio + 0.5
                t1 = q_eff**2 + 0.25
                alpha_energy = alpha_space * p_factor
                t2 = np.sqrt((Z_factor - p_factor * q_eff)**2 + (alpha_energy * q_eff)**2)
                return p_factor * t1 + t2, p_factor * t1 - t2

            E_plus_num, E_minus_num = compute_bands(l_actual)
            
            ax.plot(alpha_space, E_plus_num, label=r"$E_+$ Subband", color='#e11d48', linewidth=2.5)
            ax.plot(alpha_space, E_minus_num, label=r"$E_-$ Subband", color='#003366', linestyle='--', linewidth=2.5)
            
            mid_idx = len(alpha_space) // 2
            gap_x = alpha_space[mid_idx]
            gap_y_minus = E_minus_num[mid_idx]
            gap_y_plus = E_plus_num[mid_idx]
            gap_val_actual = gap_y_plus - gap_y_minus
            
            ax.axvline(x=gap_x, color='#475569', linestyle=':', alpha=0.5, linewidth=1)
            ax.annotate('', xy=(gap_x, gap_y_plus), xytext=(gap_x, gap_y_minus),
                        arrowprops=dict(arrowstyle="<->", color='#e11d48', lw=1.5))
            ax.text(gap_x + (alpha_max_slider * 0.02), (gap_y_plus + gap_y_minus) / 2, 
                    f"Current Gap\n{gap_val_actual:.2e} eV", color='#e11d48', fontsize=8, weight='bold', va='center')

            ax.set_title(rf"Dispersion Curves for Selected Quantum State: $l = {l_actual}$", fontsize=12, fontweight='bold', color='#001f3f')
            ax.set_xlabel(r"Rashba Spin-Orbit Interaction Parameter ($\alpha$)", fontsize=9, color='#0f172a')
            ax.set_ylabel("Energy Spectrum (eV)", fontsize=9, color='#0f172a')
            ax.yaxis.set_major_formatter(formatter)
            ax.grid(True, linestyle='--', linewidth=0.5, color='#e2e8f0', alpha=0.7)
            ax.tick_params(colors='#475569', labelsize=8)
            ax.legend(loc="best", frameon=True, fontsize=8)
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#cbd5e1')
                spine.set_linewidth(0.8)

            plt.tight_layout()
            st.pyplot(fig)
            
            status_msg = f"LIVE MATRIX SOLVER RUNNING | r0={st.session_state.r0_val}nm | m*={st.session_state.meff_val}m0"
            st.markdown(f"<div class='matrix-status'>FORTRAN ENGINE COHERENCE STATUS: {status_msg}</div>", unsafe_allow_html=True)

    with col_main_right:
        # PANEL 3: System Physical Insights & Diagnostics
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Physical Insights</p>", unsafe_allow_html=True)
            
            # CORREGIDO: Ahora 'Determinant Analysis' espera el click del usuario al entrar cerrado (expanded=False)
            with st.expander("Determinant Analysis", expanded=False):
                if is_general_case:
                    det_text = "The secular matrix determinant reveals an asymmetric coupling. The square root term contains the gauge field parameter B_z directly competing against the effective angular momentum."
                else:
                    det_text = "In the base configuration, the secular equation reduces to a symmetric product displaying a clean, linear scaling relative to the Rashba interaction intensity."
                st.markdown(f"<div class='insight-content'><p>{det_text}</p></div>", unsafe_allow_html=True)

            with st.expander("Subband Curve Evolution", expanded=False):
                st.markdown("""
                <div class='insight-content'>
                    <p>As the spin-orbit coupling parameter α increases, a progressive hyperbolic separation occurs between the branches.</p>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Quantum Symmetry Structure", expanded=False):
                if is_general_case:
                    sym_status = "<b>Broken Time-Reversal Symmetry:</b> Concurrent magnetic flux and Zeeman splitting eliminate the standard Kramers degeneracy."
                else:
                    sym_status = "<b>Preserved Spatial Parity Symmetry:</b> Without gauge fields breaking phase coherence, eigenstates preserve tight chiral symmetries."
                st.markdown(f"<div class='insight-content'><p>{sym_status}</p></div>", unsafe_allow_html=True)

# --- GLOBAL INTERACTIVE BOTTOM FOOTER ---
st.markdown("---")
col_btn_reset, col_btn_spacer = st.columns([1.5, 8.5])
with col_btn_reset:
    if st.button("Reset", use_container_width=True, type="secondary", key="nexus_global_reset"):
        st.session_state.engine_running = False
        try: st.switch_page("pages/01_Hamiltonian.py")
        except Exception: st.rerun()