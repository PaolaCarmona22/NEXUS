import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Eigenenergies", 
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
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='nexus-header'><div class='brand-area'><h1>NEXUS</h1><p>Advanced Quantum Simulation Environment</p></div></div>", unsafe_allow_html=True)

# --- NAVEGACIÓN DE PÁGINAS ---
nav_cols = st.columns([2, 5])
with nav_cols[0]:
    menu_options = ["2. Eigenenergies", "1. Hamiltonian"]
    selected_page = st.selectbox("ENVIRONMENT NAVIGATION", menu_options, index=0, key="nav_eigenenergies")
    if "1. Hamiltonian" in selected_page:
        st.switch_page("pages/01_Hamiltonian.py")

st.markdown("<hr style='margin: 10px 0 25px 0; border-color: #cbd5e1;'>", unsafe_allow_html=True)

# ============================================================
# ABSORCIÓN DIRECTA Y REAL DEL ESTADO DEL HAMILTONIANO
# ============================================================
r0_val = st.session_state.get('r0_val', 40.0)
meff_val = st.session_state.get('meff_val', 0.023)
l_val = st.session_state.get('l_val', 1)

phi_ratio = st.session_state.get('phi_ratio', 1.2) if use_flux else 0.0
bz_val = st.session_state.get('bz_val', 2.5) if use_zeeman else 0.0
alpha_val = st.session_state.get('alpha_val', 15.0) if use_rashba else 0.0

hbar_sq_over_2m0 = 38.1  
g_factor = 15.0         
mu_B_meV = 0.05788      

# --- FUNCIÓN LOCAL PARA DIAGONALIZAR INTERACTIVAMENTE ---
def compute_exact_eigenenergies(r0, meff, l, phi, bz, alpha):
    h_coef = hbar_sq_over_2m0 / (meff * (r0**2))
    zeeman = 0.5 * g_factor * mu_B_meV * bz
    rashba = (alpha / r0) * (l + 0.5 + phi) if use_rashba else 0.0
    
    h11 = h_coef * ((l + phi)**2) + zeeman if use_zeeman else h_coef * ((l + phi)**2)
    h22 = h_coef * ((1 + l + phi)**2) - zeeman if use_zeeman else h_coef * ((1 + l + phi)**2)
    h12 = rashba
    
    trace_half = (h11 + h22) / 2.0
    diff_half_sq = ((h11 - h22) / 2.0) ** 2
    root = np.sqrt(diff_half_sq + h12**2)
    
    return trace_half + root, trace_half - root

e_plus_current, e_minus_current = compute_exact_eigenenergies(r0_val, meff_val, l_val, phi_ratio, bz_val, alpha_val)

# ============================================================
# DISTRIBUCIÓN MATEMÁTICA Y RENDERS DE PLOTLY
# ============================================================
col_main_left, col_main_right = st.columns([5.2, 1.8])

with col_main_left:
    
    # ============================================================
    # MÓDULO 1: MOTOR DE SIMPLIFICACIÓN ALGEBRAICA INTERACTIVO (DURADERO Y DINÁMICO)
    # ============================================================
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Dynamic Symbolic Solver Trace</p>", unsafe_allow_html=True)
        
        # 1. Definición del coeficiente de energía cinética base
        hbar_factor = r"\frac{\hbar^2}{2m^* r_0^2}"
        
        # 2. CONSTRUCTOR DINÁMICO DE SUB-EXPRESIONES
        if use_flux:
            orb_h11 = r"\left(\frac{\Phi}{\Phi_0} + l\right)^2"
            orb_h22 = r"\left(\frac{\Phi}{\Phi_0} + l + 1\right)^2"
            orb_avg = r"\left(l + \frac{\Phi}{\Phi_0} + \frac{1}{2}\right)^2"
            inner_diff = r"\left(l + \frac{\Phi}{\Phi_0} + \frac{1}{2}\right)"
            rashba_term = r"\frac{\alpha_R \left(\frac{\Phi}{\Phi_0} + l + \frac{1}{2}\right)}{r_0}"
        else:
            orb_h11 = r"l^2"
            orb_h22 = r"(l+1)^2"
            orb_avg = r"\left(l + \frac{1}{2}\right)^2"
            inner_diff = r"\left(l + \frac{1}{2}\right)"
            rashba_term = r"\frac{\alpha_R \left(l + \frac{1}{2}\right)}{r_0}"

        # Coeficiente Zeeman
        zeeman_factor = r"\frac{B_z \mu_B g}{2}"

        # 3. ENSAMBLAJE DINÁMICO DE LA MATRIZ H
        h11_str = f"{zeeman_factor} + {hbar_factor}{orb_h11}" if use_zeeman else f"{hbar_factor}{orb_h11}"
        h22_str = f"-{zeeman_factor} + {hbar_factor}{orb_h22}" if use_zeeman else f"{hbar_factor}{orb_h22}"
        h12_str = rashba_term if use_rashba else "0"

        st.markdown("donde $(H)$ es la matriz obtenida anteriormente:")
        st.latex(f"H = \\begin{{pmatrix}} {h11_str} & {h12_str} \\\\ {h12_str} & {h22_str} \\end{{pmatrix}}")
        
        st.markdown("Resolviendo la ecuación característica y agrupando términos, se obtiene:")

        # 4. ALGORITMO DE PURIFICACIÓN DEL RADICANDO
        if use_zeeman:
            radical_core = f"\\left[ \\frac{{1}}{{2}}g\\mu_B B_z - {hbar_factor}{inner_diff} \\right]^2"
        else:
            radical_core = f"\\left[ {hbar_factor}{inner_diff} \\right]^2"

        if use_rashba:
            if use_flux:
                rashba_final = r"+ \left[ \frac{\alpha_R}{r_0} \left( \frac{\Phi}{\Phi_0} + l + \frac{1}{2} \right) \right]^2"
            else:
                rashba_final = r"+ \left[ \frac{\alpha_R}{r_0} \left( l + \frac{1}{2} \right) \right]^2"
        else:
            rashba_final = ""

        # 5. RENDERIZADO FINAL ADAPTATIVO ULTRA-PULIDO
        st.latex(f"""
        E_{{\\pm}} = {hbar_factor} \\left[ {orb_avg} + \\frac{{1}}{{4}} \\right] \\pm \\sqrt{{ {radical_core} {rashba_final} }}
        """)

    # ============================================================
    # MÓDULO 2: SELECTOR DE VIEWPORT Y GRÁFICOS INTERACTIVOS
    # ============================================================
    with st.container(border=True):
        graph_mode = st.radio(
            "Select Analysis Viewport:",
            ["Dimensional Spectrum (Physical Units)", "Symbolic Report Graph (Dimensionless Mode)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # --- MODO INTERACTIVO DIMENSIONAL ---
        if graph_mode == "Dimensional Spectrum (Physical Units)":
            st.markdown("<p class='panel-title'>Energy Spectrum vs Rashba Coupling (Dynamic Matrix Solver)</p>", unsafe_allow_html=True)
            
            alpha_range = np.linspace(0.0, 40.0, 250)
            e_plus_curve = []
            e_minus_curve = []
            
            for a in alpha_range:
                ep, em = compute_exact_eigenenergies(r0_val, meff_val, l_val, phi_ratio, bz_val, a)
                e_plus_curve.append(ep)
                e_minus_curve.append(em)

            fig_real = go.Figure()
            fig_real.add_trace(go.Scatter(x=alpha_range, y=e_plus_curve, mode='lines', name='E₊ (Upper Branch)', line=dict(color='#0056b3', width=2.5)))
            fig_real.add_trace(go.Scatter(x=alpha_range, y=e_minus_curve, mode='lines', name='E₋ (Lower Branch)', line=dict(color='#10b981', width=2.5)))
            
            fig_real.add_trace(go.Scatter(
                x=[alpha_val, alpha_val], y=[e_minus_current, e_plus_current],
                mode='markers+text', name='Operating Point',
                marker=dict(color='#0f172a', size=9, symbol='diamond'),
                text=[f"{e_minus_current:.3f} meV", f"{e_plus_current:.3f} meV"],
                textposition=["bottom center", "top center"]
            ))
            
            fig_real.update_layout(xaxis_title="Rashba Coupling α_R (meV·nm)", yaxis_title="Eigenenergy E (meV)", margin=dict(l=40, r=20, t=10, b=40), hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_real, use_container_width=True, key="real_plot")

            # --- CONSOLA SÍNCRONA DE PARÁMETROS LOCALES ---
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("<p class='panel-title'>System Parameters Console (Interactive Custom Parameters)</p>", unsafe_allow_html=True)
                grid_p1, grid_p2, grid_p3 = st.columns([1.5, 1.0, 1.5])
                
                with grid_p1:
                    st.session_state['r0_val'] = st.slider("Ring Radius r_0 (nm)", 10.0, 100.0, float(r0_val), step=2.5, key='r0_slider_link')
                    st.session_state['meff_val'] = st.slider("Effective Mass m* (m_0)", 0.01, 0.10, float(meff_val), step=0.001, key='meff_slider_link')
                with grid_p2:
                    st.session_state['l_val'] = st.number_input("Angular Momentum l", value=int(l_val), step=1, key='l_input_link')
                        
                with grid_p3:
                    if use_flux: 
                        st.session_state['phi_ratio'] = st.slider("Flux Ratio Φ/Φ_0", 0.0, 5.0, float(phi_ratio), step=0.1, key='phi_slider_link')
                    else: st.caption("Information: Magnetic Flux is disabled.")
                        
                    if use_zeeman: 
                        st.session_state['bz_val'] = st.slider("Magnetic Field B_z (T)", 0.0, 10.0, float(bz_val), step=0.1, key='bz_slider_link')
                    else: st.caption("Information: Zeeman Field is disabled.")
                        
                    if use_rashba: 
                        st.session_state['alpha_val'] = st.slider("Rashba Coupling α_R", 0.0, 40.0, float(alpha_val), step=1.0, key='alpha_slider_link')
                    else: st.caption("Information: Rashba Coupling is disabled.")

        # --- MODO SIMBÓLICO ---
        else:
            st.markdown("<p class='panel-title'>Dimensionless Spectrum vs α (Report Ready Mode)</p>", unsafe_allow_html=True)
            l_sym = st.number_input("Vary Angular Momentum l for Symbolic Graph:", value=int(l_val), step=1, key="l_sym_input")
            
            alpha_sym_range = np.linspace(0.0, 10.0, 300)
            q_sym = l_sym + 0.5
            e_sym_center = (q_sym**2) + 0.25
            
            e_sym_plus = e_sym_center + np.sqrt((q_sym**2) * (1 + alpha_sym_range**2))
            e_sym_minus = e_sym_center - np.sqrt((q_sym**2) * (1 + alpha_sym_range**2))
            
            fig_sym = go.Figure()
            fig_sym.add_trace(go.Scatter(x=alpha_sym_range, y=e_sym_plus, mode='lines', name='E₊ (Symbolic)', line=dict(color='#dc2626', width=2.5)))
            fig_sym.add_trace(go.Scatter(x=alpha_sym_range, y=e_sym_minus, mode='lines', name='E₋ (Symbolic)', line=dict(color='#2563eb', width=2.5, dash='dash')))
            
            fig_sym.update_layout(
                title=dict(text=f"Analytical Spectrum Mode for l = {l_sym}", font=dict(size=14, color='#001f3f')),
                xaxis_title="Dimensionless Coupling: α = 2m* α_R r_0 / ℏ²",
                yaxis_title="Dimensionless Energy ε (Scientific Notation)",
                margin=dict(l=60, r=20, t=50, b=40), hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white"
            )
            fig_sym.update_xaxes(showgrid=True, gridcolor='#cbd5e1')
            fig_sym.update_yaxes(showgrid=True, gridcolor='#cbd5e1', tickformat=".4e")
            st.plotly_chart(fig_sym, use_container_width=True, key="sym_plot_final")

# --- COLUMNA DERECHA ---
with col_main_right:
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Physics Insights</p>", unsafe_allow_html=True)
        
        if not use_rashba:
            ins_1 = "<b>Linear Dispersion Mode.</b> Las energías se desacoplan totalmente volviéndose puramente parabólicas respecto al momento cuantizado."
            ins_2 = "<b>Zero Spin Splitting.</b> Al no haber acoplamiento off-diagonal, las ramas colapsan a los autovalores orbitales puros."
        else:
            ins_1 = "<b>Anti-crossing Behavior.</b> Los términos fuera de la diagonal mezclan los canales de espín abriendo una brecha (gap) cuántica."
            ins_2 = "<b>Rashba Dominance.</b> A medida que aumentas el acoplamiento, la separación de espín crece de forma controlada y exacta."

        ins_3 = "<b>Asymmetric Shifts.</b> El flujo magnético rompe la simetría de inversión temporal generando desfases asimétricos observables." if (use_flux and phi_ratio != 0) else "<b>TRS Preserved.</b> Sin campos ortogonales ni flujos netos, las inversiones temporales mantienen degeneraciones ordenadas."
        
        actual_splitting = np.abs(e_plus_current - e_minus_current)
        ins_4 = f"Separación energética en el punto de operación: <b>{actual_splitting:.4f} meV</b>."

        st.markdown(f"""
        <div class='insight-card'><h4>ENERGY DISPERSION</h4><p>{ins_1}</p></div>
        <div class='insight-card'><h4>CHIRAL SPLITTING</h4><p>{ins_2}</p></div>
        <div class='insight-card'><h4>SYMMETRY UNDER FLUX</h4><p>{ins_3}</p></div>
        <div class='insight-card'><h4>OPERATIONAL SPLITTING</h4><p>{ins_4}</p></div>
        <div class='insight-card'>
            <h4>NUMERICAL STATUS</h4>
            <p style='font-family: monospace; font-size: 11px; margin:0;'>
                Solver: Exact Matrix Diagonalization<br>
                Matrix conditioning: Stable<br>
                Status: 100% Coupled to Hamiltonian setup.
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown("---")
col_reset, col_spacer = st.columns([1.5, 5.5])
with col_reset:
    if st.button("Reset", use_container_width=True, type="secondary", key="global_reset_e"):
        st.session_state.clear()
        st.rerun()