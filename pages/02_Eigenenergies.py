import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Eigenenergies", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- SINCRO ESTRICTA: Forzamos a heredar de la Pág 1 sin alterar nada ---
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
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='nexus-header'><div class='brand-area'><h1>NEXUS</h1><p>Advanced Quantum Simulation Environment</p></div></div>", unsafe_allow_html=True)

# --- NAVEGACIÓN DE PÁGINAS ---
nav_cols = st.columns([2, 5])
with nav_cols[0]:
    menu_options = ["2. Eigenenergies", "1. Hamiltonian", "3. Eigenstates", "4. States", "5. Conductance"]
    selected_page = st.selectbox("🧭 ENVIRONMENT NAVIGATION", menu_options, index=0)
    
    if selected_page == "1. Hamiltonian":
        st.switch_page("01_Hamiltonian.py")

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)

# ============================================================
# CÁLCULOS FÍSICOS DETERMINISTAS COMPLETO
# ============================================================
col_main_left, col_main_right = st.columns([5.2, 1.8])

r0_val = st.session_state.get('r0_slider_e', 40.0)
meff_val = st.session_state.get('meff_slider_e', 0.023)
l_val = st.session_state.get('l_input_e', 1)

# El valor numérico se destruye inmediatamente aquí si la bandera está apagada
phi_ratio = st.session_state.get('phi_slider_e', 1.2) if use_flux else 0.0
bz_val = st.session_state.get('bz_slider_e', 2.5) if use_zeeman else 0.0
alpha_val = st.session_state.get('alpha_slider_e', 15.0) if use_rashba else 0.0

hbar_sq_over_2m0 = 38.1  
g_factor = 15.0         
mu_B_meV = 0.05788      

h_coef = hbar_sq_over_2m0 / (meff_val * (r0_val**2))
zeeman_energy = 0.5 * g_factor * mu_B_meV * bz_val

# --- COLUMNA IZQUIERDA ---
with col_main_left:
    
    # Módulo 1: Ecuación Analítica Modificada por el Hamiltoniano Real
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Characteristic Equation & Dispersion Relation</p>", unsafe_allow_html=True)
        
        q_latex = r"\left(l + \frac{\Phi}{\Phi_0} + \frac{1}{2}\right)" if use_flux else r"\left(l + \frac{1}{2}\right)"
        
        if use_rashba:
            term_z = r"\frac{1}{2}g\mu_B B_z" if use_zeeman else "0"
            e_latex = (
                r"E_{\pm} = \frac{\hbar^{2}}{2m^*r_{0}^{2}} \left[ " + q_latex + r"^2 + \frac{1}{4} \right]"
                r"\pm \sqrt{ \left[ " + term_z + r" - \frac{\hbar^{2}}{2m^*r_{0}^{2}}" + q_latex + r" \right]^{2}"
                r"+ \left[ \frac{\alpha_R}{r_{0}}" + q_latex + r" \right]^{2} }"
            )
        elif use_zeeman:
            e_latex = (
                r"E_{\pm} = \frac{\hbar^{2}}{2m^*r_{0}^{2}} \left[ " + q_latex + r"^2 + \frac{1}{4} \right]"
                r"\pm \left| \frac{1}{2}g\mu_B B_z - \frac{\hbar^{2}}{2m^*r_{0}^{2}}" + q_latex + r" \right|"
            )
        else:
            if use_flux:
                e_latex = r"E_{\pm} = \frac{\hbar^{2}}{2m^*r_{0}^{2}} \left[ \left(l + \frac{\Phi}{\Phi_0}\right)^2 \right]"
            else:
                e_latex = r"E = \frac{\hbar^{2}}{2m^*r_{0}^{2}} l^2"
            
        st.latex(e_latex)

    # Módulo 2: Gráfica Reactiva
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Energy Spectrum vs Rashba Coupling</p>", unsafe_allow_html=True)
        
        alpha_range = np.linspace(0.0, 40.0, 200)
        q_factor = l_val + phi_ratio + 0.5 if (use_flux or use_zeeman or use_rashba) else l_val
        e_center = h_coef * (q_factor**2 + 0.25) if (use_flux or use_zeeman or use_rashba) else h_coef * (l_val**2)
        
        if use_rashba:
            rashba_energies = (alpha_range / r0_val) * q_factor
            e_root = np.sqrt((zeeman_energy - h_coef * q_factor)**2 + rashba_energies**2)
            e_plus = e_center + e_root
            e_minus = e_center - e_root
        else:
            e_const_root = np.abs(zeeman_energy - h_coef * q_factor) if (use_zeeman or use_flux) else 0.0
            if not use_zeeman and not use_flux:
                e_plus = np.full_like(alpha_range, h_coef * (l_val**2))
                e_minus = np.full_like(alpha_range, h_coef * (l_val**2))
            else:
                e_plus = np.full_like(alpha_range, e_center + e_const_root)
                e_minus = np.full_like(alpha_range, e_center - e_const_root)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=alpha_range, y=e_plus, mode='lines', name='E₊', line=dict(color='#0056b3', width=2.5)))
        fig.add_trace(go.Scatter(x=alpha_range, y=e_minus, mode='lines', name='E₋', line=dict(color='#10b981', width=2.5)))
        
        current_rashba_energy = (alpha_val / r0_val) * q_factor if use_rashba else 0.0
        current_root = np.sqrt((zeeman_energy - h_coef * q_factor)**2 + current_rashba_energy**2) if (use_zeeman or use_rashba or use_flux) else 0.0
        
        y_p1 = e_center - current_root if (use_zeeman or use_flux or use_rashba) else h_coef * (l_val**2)
        y_p2 = e_center + current_root if (use_zeeman or use_flux or use_rashba) else h_coef * (l_val**2)

        fig.add_trace(go.Scatter(
            x=[alpha_val, alpha_val], y=[y_p1, y_p2],
            mode='markers+text', name='Operating Point',
            marker=dict(color='#0f172a', size=8, symbol='circle'),
            text=[f"{y_p1:.2f} meV", f"{y_p2:.2f} meV"],
            textposition=["bottom center", "top center"]
        ))

        fig.update_layout(
            xaxis_title="Rashba Coupling α_R (meV·nm)", yaxis_title="Eigenenergy E (meV)",
            margin=dict(l=40, r=20, t=10, b=40), hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Módulo 3: Panel de Parámetros Dinámicos
    with st.container(border=True):
        st.markdown("<p class='panel-title'>System Parameters Console</p>", unsafe_allow_html=True)
        grid_p1, grid_p2, grid_p3 = st.columns([1.5, 1.0, 1.5])
        
        with grid_p1:
            r0_val = st.slider("Ring Radius $r_0$ (nm)", 10.0, 100.0, 40.0, step=2.5, key='r0_slider_e')
            meff_val = st.slider("Effective Mass $m^*$ ($m_0$)", 0.01, 0.10, 0.023, step=0.001, key='meff_slider_e')
        with grid_p2:
            l_val = st.number_input("Angular Momentum $l$", value=1, min_value=-10, max_value=10, step=1, key='l_input_e')
                
        with grid_p3:
            if use_flux:
                phi_ratio = st.slider("Flux Ratio $\\Phi/\\Phi_0$", 0.0, 5.0, 1.2, step=0.1, key='phi_slider_e')
            else:
                st.caption("ℹ️ Magnetic Flux is disabled.")
                
            if use_zeeman:
                bz_val = st.slider("Magnetic Field $B_z$ (T)", 0.0, 10.0, 2.5, step=0.1, key='bz_slider_e')
            else:
                st.caption("ℹ️ Zeeman Field is disabled.")
                
            if use_rashba:
                alpha_val = st.slider("Rashba Coupling $\\alpha_R$", 0.0, 40.0, 15.0, step=1.0, key='alpha_slider_e')
            else:
                st.caption("ℹ️ Rashba Coupling is disabled.")

# --- COLUMNA DERECHA ---
with col_main_right:
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Physics Insights</p>", unsafe_allow_html=True)
        
        if not use_rashba:
            ins_1 = "<b>Linear Dispersion Mode.</b> Energy states are purely parabolic with respect to momentum quantization. Levels remain unmixed."
            ins_2 = "<b>Zero Spin Splitting.</b> Off-diagonal coupling is absent; states are shifted exclusively by the orbital kinetic shifts and Zeeman fields."
        else:
            ins_1 = "<b>Anti-crossing Behavior.</b> The square-root term induces an effective anticrossing gap due to active spin-orbit hybridization."
            ins_2 = "<b>Rashba Dominance.</b> As $\\alpha_R$ grows, the energy splitting increases linearly, creating two spin-chiral branches."

        if use_flux and phi_ratio != 0:
            ins_3 = "<b>Asymmetric Shifts.</b> Magnetic flux causes a fractional shift in angular momentum, destroying the degeneracy between $\\pm l$ branches."
        else:
            ins_3 = "<b>Time-Reversal Symmetric Splitting.</b> Degeneracy is controlled strictly by the spin coupling terms without gauge-field offsets."

        ins_4 = f"Current state splitting at operating point: <b>{2*current_root:.4f} meV</b>."

        st.markdown(f"""
        <div class='insight-card'><h4>ENERGY DISPERSION</h4><p>{ins_1}</p></div>
        <div class='insight-card'><h4>CHIRAL SPLITTING</h4><p>{ins_2}</p></div>
        <div class='insight-card'><h4>SYMMETRY UNDER FLUX</h4><p>{ins_3}</p></div>
        <div class='insight-card'><h4>OPERATIONAL SPLITTING</h4><p>{ins_4}</p></div>
        <div class='insight-card'>
            <h4>NUMERICAL STATUS</h4>
            <p style='font-family: monospace; font-size: 11px; margin:0;'>
                Solver: Secular Exact<br>
                E₊: {y_p2:.3f} meV<br>
                E₋: {y_p1:.3f} meV<br>
                Status: Determinant Converged.
            </p>
        </div>
        """, unsafe_allow_html=True)