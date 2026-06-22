import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.colors
import sympy as sp

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Eigenstates", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- STATE PROTECTION & LINKING WITH BUILDER ---
if "engine_running" not in st.session_state or not st.session_state.engine_running:
    st.warning("⚠️ No active Hamiltonian configuration detected. Please initialize the Core Engine in step 1 first.")
    if st.button("Go to 1. Hamiltonian"):
        st.switch_page("pages/01_Hamiltonian.py")
    st.stop()

# Fallback session settings matching the Hamiltonian builder exactly
r0_val = st.session_state.get('r0_val', 40.0)
meff_val = st.session_state.get('meff_val', 0.023)
l_val = st.session_state.get('l_val', 1)

use_flux = st.session_state.get("use_flux", True)
use_zeeman = st.session_state.get("use_zeeman", True)
use_rashba = st.session_state.get("use_rashba", True)

phi_ratio = st.session_state.get('phi_ratio', 1.2) if use_flux else 0.0
bz_val = st.session_state.get('bz_val', 2.5) if use_zeeman else 0.0
alpha_val = st.session_state.get('alpha_val', 15.0) if use_rashba else 0.0

case_type = "general" if (use_zeeman or use_flux) else "base"
case_title = "General Regime (Rashba + Flux + Zeeman)" if case_type == "general" else "Base Regime (Rashba Only - Recovered)"

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

    /* Premium Orthonormality Matrix Table Styling */
    .ortho-table { width: 100%; border-collapse: collapse; font-size: 10px; font-family: 'Segoe UI', monospace; margin-top: 5px; }
    .ortho-table th { background-color: #f8fafc; color: #001f3f; text-align: center; padding: 6px; border: 1px solid #cbd5e1; font-weight: 700; }
    .ortho-table td { padding: 6px; border: 1px solid #e2e8f0; text-align: center; color: #334155; }
    .ortho-badge { padding: 3px 6px; border-radius: 4px; font-weight: 600; font-size: 10px; display: inline-block; white-space: nowrap; }
    .badge-norm { background-color: #dcfce7; color: #166534; }
    .badge-ortho { background-color: #e0f2fe; color: #0369a1; }
    .badge-phase { background-color: #fef3c7; color: #92400e; font-family: monospace; }
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

# Botonera superior de navegación dinámica
st.markdown("<div style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
b_col1, b_col2, b_col3, b_col4 = st.columns([2.5, 2.5, 2.5, 2.5])
with b_col1:
    if st.button("1. Hamiltonian", use_container_width=True): st.switch_page("pages/01_Hamiltonian.py")
with b_col2:
    if st.button("2. Eigenenergies", use_container_width=True): st.switch_page("pages/02_Eigenenergies.py")
with b_col3:
    if st.button("3. Eigenstates", use_container_width=True, type="primary"): st.switch_page("pages/03_Eigenstates.py")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<hr style='margin: -5px 0 25px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)

# --- REAL-TIME NUMERICAL COUPLING ENGINE ---
hbar_sq_over_2m0 = 38.1  
g_factor = 15.0       
mu_B_meV = 0.05788      

h_coef = hbar_sq_over_2m0 / (meff_val * (r0_val**2))
zeeman = 0.5 * g_factor * mu_B_meV * bz_val
rashba = (alpha_val / r0_val) * (l_val + 0.5 + phi_ratio) if use_rashba else 0.0

h11 = h_coef * ((l_val + phi_ratio)**2) + zeeman if use_zeeman else h_coef * ((l_val + phi_ratio)**2)
h22 = h_coef * ((1 + l_val + phi_ratio)**2) - zeeman if use_zeeman else h_coef * ((1 + l_val + phi_ratio)**2)

denominator_QR = (h11 - h22) / 2.0
xi_rad = np.arctan2(rashba, denominator_QR) if use_rashba else 0.0

# --- EXACT COMPUTATION OF ENERGY AND DYNAMIC GAMMA ---
E_plus = (h11 + h22)/2.0 + np.sqrt(((h11 - h22)/2.0)**2 + rashba**2)

if case_type == "base":
    num_gamma = h_coef * (l_val**2) - E_plus
    den_gamma = (alpha_val / r0_val) * (l_val + 0.5)
    gamma_num = (num_gamma / den_gamma) if den_gamma != 0.0 else 0.0
else: # case_type == "general"
    num_gamma = E_plus - h_coef * ((l_val + phi_ratio)**2) + zeeman
    den_gamma = (alpha_val / r0_val) * (l_val + 0.5 + phi_ratio)
    gamma_num = (num_gamma / den_gamma) if den_gamma != 0.0 else 0.0

# --- MAIN TWO-COLUMN LABORATORY LAYOUT ---
col_main_left, col_main_right = st.columns([5.2, 1.8])

with col_main_left:
    # PANEL 1: Analytical Eigensystem Trace
    with st.container(border=True):
        st.markdown(f"<p class='panel-title'>Analytical Eigensystem Trace</p>", unsafe_allow_html=True)
        
        if use_flux:
            h11_latex = r"\frac{\hbar^2}{2mr_0^2}\left(l + \frac{\Phi}{\Phi_0}\right)^2"
            if use_zeeman:
                h11_latex += r" + \frac{1}{2}g\mu_BB_z"
            h22_latex = r"\frac{\hbar^2}{2mr_0^2}\left(l + \frac{\Phi}{\Phi_0} + 1\right)^2"
            if use_zeeman:
                h22_latex += r" - \frac{1}{2}g\mu_BB_z"
            h12_latex = r"\frac{\alpha_R}{r_0}\left(l + \frac{1}{2} + \frac{\Phi}{\Phi_0}\right)"
        else:
            h11_latex = r"\frac{\hbar^2}{2mr_0^2}l^2"
            if use_zeeman:
                h11_latex += r" + \frac{1}{2}g\mu_BB_z"
            h22_latex = r"\frac{\hbar^2}{2mr_0^2}(l+1)^2"
            if use_zeeman:
                h22_latex += r" - \frac{1}{2}g\mu_BB_z"
            h12_latex = r"\frac{\alpha_R}{r_0}\left(l + \frac{1}{2}\right)"
            
        if not use_rashba:
            h12_latex = "0"

        # Ecuación 1
        st.markdown("Effective Matrix Hamiltonian ($H_{2\\times 2}$)")
        st.latex(r"""
        \begin{pmatrix} %s & %s \\ %s & %s \end{pmatrix} 
        \begin{pmatrix} \chi_1 \\ \chi_2 \end{pmatrix} = E \begin{pmatrix} \chi_1 \\ \chi_2 \end{pmatrix}
        """ % (h11_latex, h12_latex, h12_latex, h22_latex))
        
        # Ecuación 2
        st.markdown("Normalized Spinor")
        st.latex(r"\begin{pmatrix} \chi_1 \\ \chi_2 \end{pmatrix} = \frac{1}{\sqrt{1+\Gamma^2}}\begin{pmatrix} 1 \\ \Gamma \end{pmatrix}")
        
        # Ecuación 3
        st.markdown("Mixing Coefficient ($\\Gamma$)")
        if case_type == "base":
            st.latex(r"\Gamma = \frac{\frac{\hbar^2}{2mr_0^2}l^2 - E}{\frac{\alpha_R}{r_0}\left(l + \frac{1}{2}\right)}")
        else:
            st.latex(r"\Gamma = \frac{E - \frac{\hbar^2}{2mr_0^2}\left(l + \frac{\Phi}{\Phi_0}\right)^2 + \frac{1}{2}g\mu_BB_z}{\frac{\alpha_R}{r_0}\left(l + \frac{1}{2} + \frac{\Phi}{\Phi_0}\right)}")

    # PANEL 2: Interactive System Selection & Radial Components
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Physical Eigenstate Components</p>", unsafe_allow_html=True)
        
        selected_state_label = st.radio(
            "Select target quantum eigenstate to inspect in the visualizer map below:",
            ["Ψ⁺ ccw (State 1)", "Ψ⁺ cw (State 2)", "Ψ⁻ ccw (State 3)", "Ψ⁻ cw (State 4)"],
            horizontal=True,
            key="eigen_state_main_radio_panel"
        )

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

    # PANEL 3: 3D Interactive Spin Texture Mapping
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
            x=r_ring * np.cos(phi_fine), y=r_ring * np.sin(phi_fine), z=np.zeros_like(phi_fine),
            mode='lines', line=dict(color='#0f172a', width=10),
            name="Quantum Ring Channel", hoverinfo='none'
        ))

        fig_texture.add_trace(go.Cone(
            x=[0], y=[0], z=[9999], u=[0], v=[0], w=[0],
            colorscale='RdBu', cmin=-1.0, cmax=1.0, showscale=True,
            colorbar=dict(
                title=dict(text="<b>Spin ⟨S<sub>z</sub>⟩ Projection</b>", side="top"),
                thickness=14, len=0.7, yanchor="middle", y=0.5
            ),
            name="Scale", hoverinfo='skip'
        ))

        for i in range(len(phi_points)):
            xi, yi, zi = x_ring[i], y_ring[i], z_ring[i]
            ui, vi, wi = u_components[i], v_components[i], w_components[i]
            
            normalized_w = (wi + 1.0) / 2.0
            normalized_w = max(0.0, min(1.0, normalized_w))
            point_color = plotly.colors.sample_colorscale('RdBu', normalized_w)[0]
            
            fig_texture.add_trace(go.Cone(
                x=[xi], y=[yi], z=[zi], u=[ui], v=[vi], w=[wi],
                colorscale=[[0, point_color], [1, point_color]], 
                sizemode='absolute', sizeref=7.0, showscale=False, 
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
                aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.4),
                camera=dict(eye=dict(x=1.3, y=1.3, z=0.75), up=dict(x=0, y=0, z=1))
            ),
            paper_bgcolor='white', plot_bgcolor='white', showlegend=False, height=540
        )
        st.plotly_chart(fig_texture, use_container_width=True, key="spin_texture_3d_render_final")

        # Coherence Status Message
        status_msg = f"LIVE EIGENVAL SOLVER ACTIVE | r0={st.session_state.r0_val}nm | m*={st.session_state.meff_val}m0"
        st.markdown(f"<div class='matrix-status'>FORTRAN ENGINE COHERENCE STATUS: {status_msg}</div>", unsafe_allow_html=True)

with col_main_right:
    # PANEL 4: States Insights
    with st.container(border=True):
        st.markdown("<p class='panel-title'>States Insights</p>", unsafe_allow_html=True)
        
        # CAMBIO AQUÍ: Se cambió expanded=True a expanded=False para que inicie colapsado
        with st.expander("Orthonormality Matrix", expanded=False):
            # --- INTEGRACIÓN DEL MOTOR DE SIMPLIFICACIÓN SYM PY ---
            I_sp = sp.I
            l_sp = sp.Symbol("l", integer=True)
            phi_sp = sp.Symbol("phi", real=True)
            xi_sp = sp.Symbol("xi", real=True)

            # Construcción analítica exacta de los espinores base según tu libro (8.108 - 8.111)
            spinor_p_ccw = sp.Matrix([sp.sin(xi_sp/2), sp.exp(I_sp * phi_sp) * sp.cos(xi_sp/2)])
            spinor_p_cw  = sp.Matrix([sp.cos(xi_sp/2), -sp.exp(I_sp * phi_sp) * sp.sin(xi_sp/2)])
            spinor_m_ccw = sp.Matrix([sp.cos(xi_sp/2), -sp.exp(I_sp * phi_sp) * sp.sin(xi_sp/2)])
            spinor_m_cw  = sp.Matrix([sp.sin(xi_sp/2), sp.exp(I_sp * phi_sp) * sp.cos(xi_sp/2)])

            # Inyección de las fases orbitales de propagación cruzadas e^(+- i l phi)
            psi_p_ccw = sp.exp(I_sp * l_sp * phi_sp)  * spinor_p_ccw
            psi_m_ccw = sp.exp(I_sp * l_sp * phi_sp)  * spinor_m_ccw
            psi_p_cw  = sp.exp(-I_sp * l_sp * phi_sp) * spinor_p_cw
            psi_m_cw  = sp.exp(-I_sp * l_sp * phi_sp) * spinor_m_cw

            # Mapeo de nombres con formato HTML seguro para las cabeceras
            estados_sym = [
                ("ψ₊<sup>ccw</sup>", psi_p_ccw),
                ("ψ₋<sup>ccw</sup>", psi_m_ccw),
                ("ψ₊<sup>cw</sup>",  psi_p_cw),
                ("ψ₋<sup>cw</sup>",  psi_m_cw)
            ]

            def calcular_bra_ket(psi_a, psi_b):
                prod = (psi_a.conjugate().T * psi_b)[0]
                return sp.trigsimp(sp.simplify(prod))

            # Estructuración limpia de la tabla HTML usando entidades nativas
            html_table = """
            <div class='insight-content' style='padding: 0;'>
                <p style='margin-bottom: 8px;'>Rigorous analytical mapping of all 16 Hilbert cross-products (&lang;&psi;<sub>i</sub>|&psi;<sub>j</sub>&rang;):</p>
                <table class='ortho-table'>
                    <thead>
                        <tr>
                            <th>Bra / Ket</th>
                            <th>|ψ₊<sup>ccw</sup>&rang;</th>
                            <th>|ψ₋<sup>ccw</sup>&rang;</th>
                            <th>|ψ₊<sup>cw</sup>&rang;</th>
                            <th>|ψ₋<sup>cw</sup>&rang;</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for name_bra, psi_bra in estados_sym:
                html_table += f"<tr><th>&lang;{name_bra}|</th>"
                for name_ket, psi_ket in estados_sym:
                    res_raw = calcular_bra_ket(psi_bra, psi_ket)
                    
                    if res_raw == 1:
                        badge_class = "badge-norm"
                        text_display = "1.0"
                    elif res_raw == 0:
                        badge_class = "badge-ortho"
                        text_display = "0.0"
                    else:
                        badge_class = "badge-phase"
                        # Mapeo manual a Unicode elegante para los badges
                        res_str = str(res_raw)
                        if "exp(2*I*l*phi)" in res_str:
                            fase = "e<sup>2il&phi;</sup>"
                        elif "exp(-2*I*l*phi)" in res_str or "exp(-2*I*l*phi" in res_str:
                            fase = "e<sup>-2il&phi;</sup>"
                        else:
                            fase = ""

                        if "sin(xi)" in res_str:
                            trig = "sin(&xi;)"
                        elif "cos(xi)" in res_str:
                            trig = "cos(&xi;)"
                        else:
                            trig = ""
                        
                        signo = "-" if res_str.startswith("-") else ""
                        text_display = f"{signo}{fase} {trig}".strip()
                    
                    html_table += f"<td><span class='ortho-badge {badge_class}'>{text_display}</span></td>"
                html_table += "</tr>"

            html_table += """
                    </tbody>
                </table>
                <div style='margin-top: 10px; font-size: 10.5px; color: #475569;'>
                    <ul style='padding-left: 12px; margin: 0;'>
                        <li><b>Normalized (1.0):</b> Probability density conservation.</li>
                        <li><b>Orthogonal (0.0):</b> Independent subbands within the same direction channel.</li>
                        <li><b>Phase Factor:</b> Coherent quantum interference potential preserved across cross-propagation paths (e<sup>&plusmn;2il&phi;</sup>).</li>
                    </ul>
                </div>
            </div>
            """
            st.markdown(html_table, unsafe_allow_html=True)

        with st.expander("Mixing Regime Status", expanded=False):
            if abs(xi_rad) < (np.pi / 12.0):
                mixing_regime_desc = "<b>Weak spin mixing:</b> System resides in an uncoupled or highly asymmetric Zeeman-dominated configuration. Spins point almost vertically."
            elif (np.pi / 12.0) <= abs(xi_rad) < (np.pi / 3.0):
                mixing_regime_desc = "<b>Moderate spin mixing:</b> The Rashba spin-orbit field stands on comparable energy terms with the structural kinetic offsets."
            else:
                mixing_regime_desc = "<b>Strong spin mixing:</b> Relativistic spin-orbit coupling dominates. Eigenstates prepare a clean spin-momentum locking profile."
            st.markdown(f"<div class='insight-content'><p>{mixing_regime_desc}</p></div>", unsafe_allow_html=True)
            
        with st.expander("Spin-Momentum Locking", expanded=False):
            st.markdown("""
            <div class='insight-content'>
                <p>Notice how rotating around the ring (changing spatial parameter φ) causes the spin vector to rotate continuously in the XY plane. This is the direct experimental hallmark of relativistic Rashba physics.</p>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("Quantum Symmetry Structure", expanded=False):
            if case_type == "general":
                sym_status = "<b>Broken Time-Reversal Symmetry:</b> The concurrent application of non-zero magnetic flux and Zeeman splitting eliminates Kramers degeneracy, featuring highly polarized pathways."
            else:
                sym_status = "<b>Preserved Spatial Parity Symmetry:</b> Without gauge fields breaking the quantum phase coherence, the eigenstates preserve tight chiral symmetries across both analytic branches."
            st.markdown(f"<div class='insight-content'><p>{sym_status}</p></div>", unsafe_allow_html=True)

# --- GLOBAL INTERACTIVE BOTTOM FOOTER ---
st.markdown("---")
col_btn_reset, col_btn_spacer = st.columns([1.5, 8.5])
with col_btn_reset:
    if st.button("Reset", use_container_width=True, type="secondary", key="nexus_global_reset"):
        st.session_state.engine_running = False
        try:
            st.switch_page("pages/01_Hamiltonian.py")
        except Exception:
            try:
                st.switch_page("app.py")
            except Exception:
                st.rerun()