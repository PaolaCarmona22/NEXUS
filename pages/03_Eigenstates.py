import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Eigenstates", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- BLINDAJE DE SEGURIDAD: CONTROL DE FLUJO ---
if "engine_running" not in st.session_state or not st.session_state.engine_running:
    st.warning("⚠️ No active Hamiltonian configuration detected. Please initialize the Core Engine in step 1 first.")
    if st.button("Go to 1. Hamiltonian"):
        st.switch_page("pages/01_Hamiltonian.py")
    st.stop()

# --- SINCRO ESTRICTA: Heredamos la estructura activa de la Pág 1 ---
use_flux = st.session_state.get("use_flux", True)
use_zeeman = st.session_state.get("use_zeeman", True)
use_rashba = st.session_state.get("use_rashba", True)

# --- CSS NEXUS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; color: #0f172a; }
    .nexus-header {
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
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important; border: none !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; border-radius: 6px !important;
    }
    .panel-title { color: #001f3f; font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; }
    .insight-card { background: white; padding: 14px; border-radius: 4px; border: 1px solid #ced4da; margin-bottom: 12px; }
    .insight-card h4 { color: #001f3f; font-size: 12px; font-weight: 700; margin: 0 0 6px 0; text-transform: uppercase; }
    .insight-card p { color: #495057; font-size: 11.5px; line-height: 1.5; margin: 0; }
    
    /* Custom layout formatting for the four analytical state columns */
    .state-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 6px; text-align: center; }
    .state-card h6 { margin: 0 0 8px 0; color: #003366; font-size: 13px; font-weight: 700; }
    .state-numeric-box { font-family: monospace; font-size: 11px; color: #334155; margin-top: 8px; background: #ffffff; padding: 4px 6px; border-radius: 4px; border: 1px solid #cbd5e1;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='nexus-header'><div class='brand-area'><h1>NEXUS</h1><p>Advanced Quantum Simulation Environment</p></div></div>", unsafe_allow_html=True)

# --- NAVEGACIÓN DE PÁGINAS ESTÁNDAR NEXUS (5 ETAPAS) ---
nav_cols = st.columns([2, 5])
with nav_cols[0]:
    menu_options = [
        "3. Eigenstates", 
        "1. Hamiltonian", 
        "2. Eigenenergies", 
        "4. Matrix Elements", 
        "5. Optical Absorption"
    ]
    selected_page = st.selectbox("ENVIRONMENT NAVIGATION", menu_options, index=0, key="nav_eigenstates_v5")
    
    if "1. Hamiltonian" in selected_page:
        st.switch_page("pages/01_Hamiltonian.py")
    elif "2. Eigenenergies" in selected_page:
        st.switch_page("pages/02_Eigenenergies.py")
    elif "4. Matrix Elements" in selected_page:
        st.switch_page("pages/04_MatrixElements.py")
    elif "5. Optical Absorption" in selected_page:
        st.switch_page("pages/05_OpticalAbsorption.py")

# --- RECUPERACIÓN DE PARÁMETROS DEL SISTEMA ---
r0_val = st.session_state.get('r0_val', 40.0)
meff_val = st.session_state.get('meff_val', 0.023)
l_val = st.session_state.get('l_val', 1)
phi_ratio = st.session_state.get('phi_ratio', 1.2) if use_flux else 0.0
bz_val = st.session_state.get('bz_val', 2.5) if use_zeeman else 0.0
alpha_val = st.session_state.get('alpha_val', 15.0) if use_rashba else 0.0

# --- EXPLICIT LATEX STRINGS CONSTRUCTOR ---
hbar_factor_sym = r"\frac{\hbar^2}{2m^* r_0^2}"
zeeman_factor_sym = r"\frac{B_z \mu_B g}{2}"

if use_flux:
    a_kin = f"{hbar_factor_sym}\\left(\\frac{{\\Phi}}{{\\Phi_0}} + l\\right)^2"
    orb_h22 = r"\left(\frac{\Phi}{\Phi_0} + l + 1\right)^2"
    b_rashba = r"\frac{\alpha_R \left(\frac{\Phi}{\Phi_0} + l + \frac{1}{2}\right)}{r_0}"
else:
    a_kin = f"{hbar_factor_sym}l^2"
    orb_h22 = r"(l+1)^2"
    b_rashba = r"\frac{\alpha_R \left(l + \frac{1}{2}\right)}{r_0}"

h11_str = f"{zeeman_factor_sym} + {a_kin}" if use_zeeman else a_kin
h22_str = f"-{zeeman_factor_sym} + {hbar_factor_sym}{orb_h22}" if use_zeeman else f"{hbar_factor_sym}{orb_h22}"
h12_str = b_rashba if use_rashba else "0"

# --- REAL-TIME NUMERICAL COUPLING ENGINE ---
hbar_sq_over_2m0 = 38.1  
g_factor = 15.0         
mu_B_meV = 0.05788      

h_coef = hbar_sq_over_2m0 / (meff_val * (r0_val**2))
zeeman = 0.5 * g_factor * mu_B_meV * bz_val
rashba = (alpha_val / r0_val) * (l_val + 0.5 + phi_ratio) if use_rashba else 0.0

h11 = h_coef * ((l_val + phi_ratio)**2) + zeeman if use_zeeman else h_coef * ((l_val + phi_ratio)**2)
h22 = h_coef * ((1 + l_val + phi_ratio)**2) - zeeman if use_zeeman else h_coef * ((1 + l_val + phi_ratio)**2)

trace_half = (h11 + h22) / 2.0
diff_half_sq = ((h11 - h22) / 2.0) ** 2
root = np.sqrt(diff_half_sq + rashba**2)

e_plus = trace_half + root
e_minus = trace_half - root

# Normalized Eigensystem probabilities
if use_rashba and rashba != 0:
    gamma_plus = (e_plus - h11) / rashba
    gamma_minus = (e_minus - h11) / rashba
    prob_up_plus = 1.0 / (1.0 + gamma_plus**2)
    prob_down_plus = gamma_plus**2 / (1.0 + gamma_plus**2)
else:
    prob_up_plus = 1.0
    prob_down_plus = 0.0
    gamma_plus = 0.0

# --- COMPUTACIÓN REGLAMENTARIA DE QR Y LA VARIABLE DE CONTROL ξ ---
if use_rashba:
    numerator_QR = (alpha_val / r0_val) * (l_val + phi_ratio + 0.5)
    denominator_QR = (h_coef * (l_val + phi_ratio + 0.5)) - zeeman
    QR_val = numerator_QR / denominator_QR if abs(denominator_QR) > 1e-12 else (np.inf if numerator_QR >= 0 else -np.inf)
    xi_rad = np.arctan(QR_val)
    xi_deg = np.degrees(xi_rad)
else:
    QR_val = 0.0
    xi_rad = 0.0
    xi_deg = 0.0

# ==============================================================================
# STEP 1: DYNAMIC DERIVATION OF AMBIGUOUS TRIGONOMETRIC COEFFICIENTS
# ==============================================================================
s_coef = np.sin(xi_rad / 2.0)
c_coef = np.cos(xi_rad / 2.0)

# Exposing variables natively to safety/future-hook scopes
st.session_state['current_xi_rad'] = xi_rad
st.session_state['current_QR'] = QR_val
st.session_state['current_s_coef'] = s_coef
st.session_state['current_c_coef'] = c_coef

# --- TWO-COLUMN MAIN NEXUS LAYOUT ---
col_left, col_right = st.columns([5.2, 1.8])

with col_left:
    # --- MÓDULO 1: TRAZA ANALÍTICA DE LOS AUTOCONJUNTOS ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Analytical Eigensystem Trace</p>", unsafe_allow_html=True)
        st.markdown("We begin with the matrix eigenvalue equation derived from the core Hamiltonian configuration:")

        st.latex(f"""
        \\begin{{pmatrix}} {h11_str} & {h12_str} \\\\ {h12_str} & {h22_str} \\end{{pmatrix}} 
        \\begin{{pmatrix}} c_1 \\\\ c_2 \\end{{pmatrix}} = E 
        \\begin{{pmatrix}} c_1 \\\\ c_2 \\end{{pmatrix}}
        """)
        
        st.markdown("The normalized eigensystem states can be expressed in their general parametric form:")
        if use_rashba:
            st.latex(r"\chi_\pm = \frac{1}{\sqrt{1+\Gamma_\pm^2}} \begin{pmatrix} 1 \\ \Gamma_\pm \end{pmatrix}")
            a_display = f"\\frac{{B_z \\mu_B g}}{{2}} + {a_kin}" if use_zeeman else a_kin
            st.latex(f"\Gamma_\\pm = \\frac{{ E_\\pm - \\left( {a_display} \\right) }}{{ {b_rashba} }}")
        else:
            st.markdown("Since the **Rashba coupling is disabled**, the Hamiltonian matrix remains strictly diagonal ($H_{12} = 0$).")
            st.latex(r"\chi_+ = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad \chi_- = \begin{pmatrix} 0 \\ 1 \end{pmatrix}")

    # --- MÓDULO 2: SPIN-ORBIT MIXING METRICS TRACE ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Spin-Orbit Mixing Metrics</p>", unsafe_allow_html=True)
        st.latex(r"Q_R = \frac{\left[ \frac{\alpha_R}{r_0}\left(l + \frac{\Phi}{\Phi_0} + \frac{1}{2}\right) \right]}{\left[ \frac{\hbar^2}{2m^*r_0^2}\left(l + \frac{\Phi}{\Phi_0} + \frac{1}{2}\right) - \frac{1}{2}g\mu_B B_z \right]}")
        st.latex(r"\xi = \arctan(Q_R)")

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1: st.metric(label="Coupling Parameter (Q_R)", value=f"{QR_val:.4f}" if np.isfinite(QR_val) else "∞")
        with m_col2: st.metric(label="Mixing Angle ξ (rad)", value=f"{xi_rad:.4f} rad")
        with m_col3: st.metric(label="Mixing Angle ξ (deg)", value=f"{xi_deg:.2f}°")

    # ==============================================================================
    # STEP 2 & 3 & 4 & 5: PHYSICAL EIGENSTATE CONSTRUCTION
    # ==============================================================================
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Physical Eigenstate Construction</p>", unsafe_allow_html=True)
        st.markdown("Mathematical projections for the four analytical components mapped dynamically to the current mixing parameter metrics:")
        
        # Mathematical trace equations for current trigonometric angles
        st.latex(f"\\xi = {xi_rad:.4f}\\,\\text{{rad}} \\quad \\longrightarrow \\quad \\sin(\\xi/2) = {s_coef:.4f}, \\quad \\cos(\\xi/2) = {c_coef:.4f}")
        
        # Columns layout deployment for the four analytical equations
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        
        with s_col1:
            st.markdown(r"""<div class='state-card'><h6>State 1: $\psi^+_{\text{ccw}}$</h6></div>""", unsafe_allow_html=True)
            st.latex(r"\psi^+_{\text{ccw}} = e^{i l \varphi} \begin{pmatrix} \sin(\xi/2) \\ e^{i\varphi} \cos(\xi/2) \end{pmatrix}")
            st.markdown(f"""<div class='state-numeric-box'>sin(ξ/2) = {s_coef:.4f}<br>cos(ξ/2) = {c_coef:.4f}</div>""", unsafe_allow_html=True)
            
        with s_col2:
            st.markdown(r"""<div class='state-card'><h6>State 2: $\psi^+_{\text{cw}}$</h6></div>""", unsafe_allow_html=True)
            st.latex(r"\psi^+_{\text{cw}} = e^{-i l \varphi} \begin{pmatrix} \cos(\xi/2) \\ -e^{i\varphi} \sin(\xi/2) \begin{pmatrix}")
            st.markdown(f"""<div class='state-numeric-box'>cos(ξ/2) = {c_coef:.4f}<br>sin(ξ/2) = {s_coef:.4f}</div>""", unsafe_allow_html=True)
            
        with s_col3:
            st.markdown(r"""<div class='state-card'><h6>State 3: $\psi^-_{\text{ccw}}$</h6></div>""", unsafe_allow_html=True)
            st.latex(r"\psi^-_{\text{ccw}} = e^{i l \varphi} \begin{pmatrix} \cos(\xi/2) \\ -e^{i\varphi} \sin(\xi/2) \end{pmatrix}")
            st.markdown(f"""<div class='state-numeric-box'>cos(ξ/2) = {c_coef:.4f}<br>sin(ξ/2) = {s_coef:.4f}</div>""", unsafe_allow_html=True)
            
        with s_col4:
            st.markdown(r"""<div class='state-card'><h6>State 4: $\psi^-_{\text{cw}}$</h6></div>""", unsafe_allow_html=True)
            st.latex(r"\psi^-_{\text{cw}} = e^{-i l \varphi} \begin{pmatrix} \sin(\xi/2) \\ e^{i\varphi} \cos(\xi/2) \end{pmatrix}")
            st.markdown(f"""<div class='state-numeric-box'>sin(ξ/2) = {s_coef:.4f}<br>cos(ξ/2) = {c_coef:.4f}</div>""", unsafe_allow_html=True)

    # ==============================================================================
    # FUTURE COMPATIBILITY ANCHOR REGISTRATION
    # ==============================================================================
    # def compute_spin_texture(xi):
    #     pass

    # --- MÓDULO INTERACTIVO ORIGINAL DE BARRAS DE PROBABILIDAD ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Quantum Spin Component Probability Readout</p>", unsafe_allow_html=True)
        fig_spin = go.Figure()
        fig_spin.add_trace(go.Bar(
            x=['Spin Up (c₁)', 'Spin Down (c₂)'], y=[prob_up_plus, prob_down_plus],
            marker_color=['#0056b3', '#dc2626'], width=0.4
        ))
        fig_spin.update_layout(
            title=dict(text=f"Spin Component Probabilities for E₊ State (l = {l_val})", font=dict(size=13, color='#001f3f')),
            yaxis=dict(title="Probability |c_i|²", range=[0, 1.05], gridcolor='#cbd5e1'), xaxis=dict(gridcolor='#cbd5e1'),
            plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=40, r=20, t=40, b=40)
        )
        st.plotly_chart(fig_spin, use_container_width=True, key="spin_prob_plot")

with col_right:
    # --- MÓDULO 3 (COLUMNA DERECHA): INSIGHTS ORIGINALES ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>State Insights</p>", unsafe_allow_html=True)
        
        if abs(xi_rad) < (np.pi / 12.0):
            mixing_regime_title, mixing_regime_desc = "Weak spin mixing", "System resides in an uncoupled or highly asymmetric Zeeman-dominated configuration."
        elif (np.pi / 12.0) <= abs(xi_rad) < (np.pi / 4.0):
            mixing_regime_title, mixing_regime_desc = "Moderate spin mixing", "The Rashba spin-orbit field stands on comparable energy terms with the structural kinetic offsets."
        else:
            mixing_regime_title, mixing_regime_desc = "Strong spin mixing", "Relativistic spin-orbit coupling dominates. Eigenstates prepare a clean spin-momentum locking profile."

        # ==============================================================================
        # STEP 6: COMPACT DATA-DRIVEN INTERPRETATION PANEL
        # ==============================================================================
        p_up_analytical = s_coef ** 2
        p_down_analytical = c_coef ** 2
        
        st.markdown(f"""
        <div class='insight-card' style='border-top: 4px solid #8b5cf6;'>
            <h4>ANALYSIS PROFILE</h4>
            <p style='font-family: monospace; font-size: 11px; margin: 0; line-height: 1.4;'>
                Q_R  = {QR_val:.4f}<br>
                ξ    = {xi_rad:.4f} rad<br>
                ξ    = {xi_deg:.2f}°<br><br>
                <b>Spin Composition:</b><br>
                P↑ = sin²(ξ/2) = {p_up_analytical:.4f}<br>
                P↓ = cos²(ξ/2) = {p_down_analytical:.4f}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='insight-card'>
            <h4>MIXING REGIME</h4>
            <p><b>{mixing_regime_title}.</b> {mixing_regime_desc}</p>
        </div>
        <div class='insight-card'><h4>SPIN TEXTURE</h4><p>The probability of detecting vertical orientation axis (Up) is <b>{prob_up_plus*100:.1f}%</b>.</p></div>
        <div class='insight-card'><h4>ORBITAL SYMMETRY</h4><p>{"Time Reversal Asymmetry driven by the active magnetic flux ratio." if phi_ratio != 0 else "Spatial charge density maintains perfect inversion symmetry."}</p></div>
        """, unsafe_allow_html=True)