import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.colors

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Eigenstates", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- BLINDAJE DE SEGURIDAD: CONTROL DE FLUJO ---
if "engine_running" not in st.session_state or not st.session_state.engine_running:
    st.warning("⚠️ No active Hamiltonian configuration detected. Please initialize the Core Engine in step 1 first.")
    if st.button("Go to 1. Hamiltonian"):
        st.switch_page("pages/01_Hamiltonian.py")
    st.stop()

# --- SIDEBAR: SYSTEM NAVIGATION & RESET ACTION ---
with st.sidebar:
    st.markdown("### SYSTEM NAVIGATION")
    if st.button("🔙 Back to 1. Hamiltonian", use_container_width=True):
        st.switch_page("pages/01_Hamiltonian.py")
        
    st.markdown("---")
    st.markdown("### CONTROL PANEL ACTIONS")
    if st.button("🔄 Reset Visualizer", type="primary", use_container_width=True):
        st.session_state['r0_val'] = 40.0
        st.session_state['meff_val'] = 0.023
        st.session_state['l_val'] = 1
        st.session_state['phi_ratio'] = 1.2
        st.session_state['bz_val'] = 2.5
        st.session_state['alpha_val'] = 15.0
        st.rerun()

# --- SINCRO ESTRICTA: Heredamos la estructura activa de la Pág 1 ---
use_flux = st.session_state.get("use_flux", True)
use_zeeman = st.session_state.get("use_zeeman", True)
use_rashba = st.session_state.get("use_rashba", True)

case_type = "general" if (use_zeeman or use_flux) else "base"

# --- CSS NEXUS ---
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='nexus-header'><div class='brand-area'><h1>NEXUS</h1><p>Advanced Quantum Simulation Environment</p></div></div>", unsafe_allow_html=True)

# --- NAVEGACIÓN EN REDISEÑO DE 5 ETAPAS SINCRO ---
if st.session_state.engine_running:
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([2, 2, 2, 2, 2])
    with b_col1:
        if st.button("1. Hamiltonian", use_container_width=True): st.switch_page("pages/01_Hamiltonian.py")
    with b_col2:
        if st.button("2. Eigenenergies", use_container_width=True): st.switch_page("pages/02_Eigenenergies.py")
    with b_col3:
        if st.button("3. Eigenstates", use_container_width=True, type="primary"): st.switch_page("pages/03_Eigenstates.py")
    with b_col4:
        if st.button("4. States", use_container_width=True): st.switch_page("pages/04_States.py")
    with b_col5:
        if st.button("5. Conductance", use_container_width=True): st.switch_page("pages/05_Conductance.py")
    st.markdown("<hr style='margin: 10px 0 25px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)

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
    a_kin = f"{hbar_factor_sym}\\left(\\frac{{\\Phi}} Leibnitz{{\\Phi_0}} + l\\right)^2"
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

# --- COMPUTACIÓN DE LA VARIABLE DE CONTROL ξ ---
if use_rashba:
    numerator_QR = rashba
    denominator_QR = ((h11 - h22) / 2.0)
    QR_val = numerator_QR / denominator_QR if abs(denominator_QR) > 1e-12 else (np.inf if numerator_QR >= 0 else -np.inf)
    xi_rad = np.arctan2(numerator_QR, denominator_QR)
    xi_deg = np.degrees(xi_rad)
else:
    QR_val = 0.0
    xi_rad = 0.0
    xi_deg = 0.0

s_coef = np.sin(xi_rad / 2.0)
c_coef = np.cos(xi_rad / 2.0)

# --- TWO-COLUMN MAIN NEXUS LAYOUT ---
col_left, col_right = st.columns([5.2, 1.8])

with col_left:
    # --- MÓDULO 1: TRAZA ANALÍTICA ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Analytical Eigensystem Trace</p>", unsafe_allow_html=True)
        st.latex(f"""
        \\begin{{pmatrix}} {h11_str} & {h12_str} \\\\ {h12_str} & {h22_str} \\end{{pmatrix}} 
        \\begin{{pmatrix}} c_1 \\\\ c_2 \\end{{pmatrix}} = E \\begin{{pmatrix}} c_1 \\\\ c_2 \\end{{pmatrix}}
        """)

    # --- MÓDULO 2: SPIN-ORBIT MIXING METRICS ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Spin-Orbit Mixing Metrics</p>", unsafe_allow_html=True)
        st.markdown("The mixing angle $\\xi$ absorbs the direct competition between the geometric Rashba confinement and the symmetry-breaking perpendicular Zeeman field $B_z$:")
        st.latex(r"\tan(\xi) = Q_R")
        
        if case_type == "base":
            st.markdown("**Base Case (Uncoupled / Zero Field):**")
            st.latex(r"Q_R = \frac{2m^*\alpha_Rr_0}{\hbar^2}")
        else:
            st.markdown("**General Case (Coupled with $B_z$ and Flux $\\Phi$):**")
            st.latex(r"Q_R = \frac{\frac{\alpha_R}{r_0}\left(l+\frac{\Phi}{\Phi_0}+\frac{1}{2}\right)}{\frac{\hbar^2}{2m^*r_0^2}\left(l+\frac{\Phi}{\Phi_0}+\frac{1}{2}\right)-\frac{1}{2}g\mu_BB_z}")

    # --- MÓDULO 3: PHYSICAL EIGENSTATE SELECTION (CORREGIDO DE RAÍZ) ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Physical Eigenstate Components</p>", unsafe_allow_html=True)
        
        selected_state_label = st.radio(
            "Select target quantum eigenstate to inspect in the visualizer:",
            ["Ψ⁺ ccw (State 1)", "Ψ⁺ cw (State 2)", "Ψ⁻ ccw (State 3)", "Ψ⁻ cw (State 4)"],
            horizontal=True,
            key="eigen_state_radio_fixed_final"
        )

        # Usamos st.markdown puro sin HTML inline para los títulos con LaTeX
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        with s_col1:
            st.markdown(r"**State 1:** $\Psi^+_{\text{ccw}}$")
            st.latex(r"\begin{pmatrix} \sin(\xi/2) \\ e^{i\phi}\cos(\xi/2) \end{pmatrix}")
        with s_col2:
            st.markdown(r"**State 2:** $\Psi^+_{\text{cw}}$")
            st.latex(r"\begin{pmatrix} \cos(\xi/2) \\ -e^{i\phi}\sin(\xi/2) \end{pmatrix}")
        with s_col3:
            st.markdown(r"**State 3:** $\Psi^-_{\text{ccw}}$")
            st.latex(r"\begin{pmatrix} \cos(\xi/2) \\ -e^{i\phi}\sin(\xi/2) \end{pmatrix}")
        with s_col4:
            st.markdown(r"**State 4:** $\Psi^-_{\text{cw}}$")
            st.latex(r"\begin{pmatrix} \sin(\xi/2) \\ e^{i\phi}\cos(\xi/2) \end{pmatrix}")

    # --- MÓDULO 4: TEXTURA DE ESPÍN ---
    with st.container(border=True):
        st.markdown(f"<p class='panel-title'>Real-Time Interactive Spin Texture Mapping — {selected_state_label}</p>", unsafe_allow_html=True)
        
        phi_points = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        r_ring = r0_val

        x_ring = r_ring * np.cos(phi_points)
        y_ring = r_ring * np.sin(phi_points)
        z_ring = np.zeros_like(phi_points)

        if "Ψ⁺ ccw" in selected_state_label:
            u_components = -np.sin(xi_rad) * np.sin(phi_points)
            v_components = np.sin(xi_rad) * np.cos(phi_points)
            w_components = np.cos(xi_rad) * np.ones_like(phi_points)
        elif "Ψ⁺ cw" in selected_state_label:
            u_components = np.sin(xi_rad) * np.sin(phi_points)
            v_components = -np.sin(xi_rad) * np.cos(phi_points)
            w_components = np.cos(xi_rad) * np.ones_like(phi_points)
        elif "Ψ⁻ ccw" in selected_state_label:
            u_components = np.sin(xi_rad) * np.sin(phi_points)
            v_components = -np.sin(xi_rad) * np.cos(phi_points)
            w_components = -np.cos(xi_rad) * np.ones_like(phi_points)
        else: 
            u_components = -np.sin(xi_rad) * np.sin(phi_points)
            v_components = np.sin(xi_rad) * np.cos(phi_points)
            w_components = -np.cos(xi_rad) * np.ones_like(phi_points)

        fig_texture = go.Figure()

        phi_fine = np.linspace(0, 2 * np.pi, 150)
        fig_texture.add_trace(go.Scatter3d(
            x=r_ring * np.cos(phi_fine),
            y=r_ring * np.sin(phi_fine),
            z=np.zeros_like(phi_fine),
            mode='lines',
            line=dict(color='#0f172a', width=10),
            name="Quantum Ring Channel",
            hoverinfo='none'
        ))

        fig_texture.add_trace(go.Cone(
            x=[0], y=[0], z=[9999],  
            u=[0], v=[0], w=[0],
            colorscale='RdBu',
            cmin=-1.0,
            cmax=1.0,
            showscale=True,
            colorbar=dict(
                title=dict(text="<b>Spin ⟨S<sub>z</sub>⟩ Projection</b>", side="top"),
                thickness=14,
                len=0.7,
                yanchor="middle",
                y=0.5
            ),
            name="Scale",
            hoverinfo='skip'
        ))

        for i in range(len(phi_points)):
            xi, yi, zi = x_ring[i], y_ring[i], z_ring[i]
            ui, vi, wi = u_components[i], v_components[i], w_components[i]
            
            normalized_w = (wi + 1.0) / 2.0
            normalized_w = max(0.0, min(1.0, normalized_w))
            point_color = plotly.colors.sample_colorscale('RdBu', normalized_w)[0]
            
            fig_texture.add_trace(go.Cone(
                x=[xi], y=[yi], z=[zi],
                u=[ui], v=[vi], w=[wi],
                colorscale=[[0, point_color], [1, point_color]], 
                sizemode='absolute',
                sizeref=7.0, 
                showscale=False, 
                name=f"Spin Vector {i}",
                hovertext=[f"⟨Sx⟩: {ui:.2f}<br>⟨Sy⟩: {vi:.2f}<br>⟨Sz⟩: {wi:.2f}"],
                hoverinfo="text"
            ))

        fig_texture.update_layout(
            margin=dict(l=0, r=0, b=0, t=30),
            scene=dict(
                xaxis=dict(title='X (nm)', backgroundcolor="#fafafa", gridcolor="#e2e8f0", range=[-r_ring*1.4, r_ring*1.4]),
                yaxis=dict(title='Y (nm)', backgroundcolor="#fafafa", gridcolor="#e2e8f0", range=[-r_ring*1.4, r_ring*1.4]),
                zaxis=dict(title='Sz Component', backgroundcolor="#f1f5f9", gridcolor="#cbd5e1", range=[-r_ring*0.5, r_ring*0.5]),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.4),
                camera=dict(
                    eye=dict(x=1.3, y=1.3, z=0.75),
                    up=dict(x=0, y=0, z=1)
                )
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False,
            height=580
        )
        st.plotly_chart(fig_texture, use_container_width=True, key="spin_texture_3d_cone_final_render")

with col_right:
    # --- MÓDULO COLUMNA DERECHA: INSIGHTS DINÁMICOS ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>State Insights</p>", unsafe_allow_html=True)
        
        if abs(xi_rad) < (np.pi / 12.0):
            mixing_regime_title, mixing_regime_desc = "Weak spin mixing", "System resides in an uncoupled or highly asymmetric Zeeman-dominated configuration. Spins point almost vertically."
        elif (np.pi / 12.0) <= abs(xi_rad) < (np.pi / 3.0):
            mixing_regime_title, mixing_regime_desc = "Moderate spin mixing", "The Rashba spin-orbit field stands on comparable energy terms with the structural kinetic offsets."
        else:
            mixing_regime_title, mixing_regime_desc = "Strong spin mixing", "Relativistic spin-orbit coupling dominates. Eigenstates prepare a clean spin-momentum locking profile (Spins lie flat on the ring plane)."

        p_up_analytical = s_coef ** 2
        p_down_analytical = c_coef ** 2
        
        st.markdown(f"""
        <div class='insight-card' style='border-top: 4px solid #8b5cf6;'>
            <h4>ANALYSIS PROFILE</h4>
            <p style='font-family: monospace; font-size: 11px; margin: 0; line-height: 1.4;'>
                Q_R  = {QR_val:.4f}<br>
                ξ    = {xi_rad:.4f} rad<br>
                ξ    = {xi_deg:.2f}°<br><br>
                <b>Spin Base Weights:</b><br>
                P↑ = sin²(ξ/2) = {p_up_analytical:.4f}<br>
                P↓ = cos²(ξ/2) = {p_down_analytical:.4f}
            </p>
        </div>
        <div class='insight-card'>
            <h4>MIXING REGIME</h4>
            <p><b>{mixing_regime_title}.</b> {mixing_regime_desc}</p>
        </div>
        <div class='insight-card'>
            <h4>SPIN-MOMENTUM LOCKING</h4>
            <p>Notice how rotating around the ring (changing φ) causes the spin vector to rotate in the XY plane. This is the direct hallmark of Rashba physics.</p>
        </div>
        """, unsafe_allow_html=True)