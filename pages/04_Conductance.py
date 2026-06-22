import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# --- High-End Scientific Page Configuration ---
st.set_page_config(
    page_title="NEXUS | Quantum Conductance Simulator", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- BLINDAJE DE ESTADOS ---
if "engine_running" not in st.session_state:
    st.session_state.engine_running = False
if "use_flux" not in st.session_state:
    st.session_state.use_flux = True
if "use_zeeman" not in st.session_state:
    st.session_state.use_zeeman = True
st.session_state["use_rashba"] = True

# Recuperación segura de variables globales
if "r0_val" not in st.session_state: st.session_state["r0_val"] = 40.0
if "meff_val" not in st.session_state: st.session_state["meff_val"] = 0.023
if "l_val" not in st.session_state: st.session_state["l_val"] = 1
if "phi_ratio" not in st.session_state: st.session_state["phi_ratio"] = 1.2
if "bz_val" not in st.session_state: st.session_state["bz_val"] = 2.5
if "alpha_val" not in st.session_state: st.session_state["alpha_val"] = 15.0

# --- CSS NEXUS: Diseño Ultra-Limpio ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #f8fafc; font-family: 'Segoe UI', sans-serif; color: #0f172a; }

    /* NAVBAR SUPERIOR COHESIVA */
    .nexus-navbar {
        background: linear-gradient(90deg, #091e3a 0%, #002244 100%);
        padding: 24px 40px;
        border-bottom: 3px solid #00d4ff;
        margin: -65px -50px 25px -50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-area h1 { color: white !important; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 0.5px; }
    .brand-area p { color: #00d4ff; margin: 2px 0 0 0; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    /* PANELES TIPO DASHBOARD CIENTÍFICO */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02) !important; border-radius: 8px !important;
    }
    .panel-title { color: #091e3a; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 15px; }
    .insight-content { color: #475569; font-size: 12px; line-height: 1.6; padding: 0px 10px 10px 10px; }
    
    .stDetails { background: #f8fafc !important; border: 1px solid #e2e8f0 !important; border-radius: 6px !important; margin-bottom: 8px !important; }
    .stDetails summary p { color: #091e3a !important; font-size: 12px !important; font-weight: 700; text-transform: uppercase; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# --- NAVBAR HEADER ---
st.markdown("<div class='nexus-navbar'><div class='brand-area'><h1>NEXUS</h1><p>Advanced Quantum Simulation Environment</p></div></div>", unsafe_allow_html=True)

# --- BOTONERA SUPERIOR ---
if st.session_state.engine_running:
    st.markdown("<div style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3, b_col4 = st.columns([2.5, 2.5, 2.5, 2.5])
    with b_col1:
        if st.button("1. Hamiltonian", use_container_width=True): st.switch_page("pages/01_Hamiltonian.py")
    with b_col2:
        if st.button("2. Eigenenergies", use_container_width=True): st.switch_page("pages/02_Eigenenergies.py")
    with b_col3:
        if st.button("3. Eigenstates", use_container_width=True): st.switch_page("pages/03_Eigenstates.py")
    with b_col4:
        if st.button("4. Conductance", use_container_width=True, type="primary"): st.switch_page("pages/04_conductance.py") 
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: -5px 0 25px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)

if not st.session_state.engine_running:
    st.warning("Please initialize the Quantum Engine in the Hamiltonian Builder panel before accessing the transport console.")
else:
    # --- PANEL DE PARÁMETROS INTERACTIVOS ---
    with st.container(border=True):
        st.markdown("<p class='panel-title'>Interactive Transport & Wavefront Controls</p>", unsafe_allow_html=True)
        ctrl_col1, ctrl_col2 = st.columns(2)
        with ctrl_col1:
            q_r_calc = st.session_state.alpha_val / 6.25 if st.session_state.alpha_val > 0 else 2.4
            Q_R = st.slider("Rashba Coupling Strength ($Q_R$)", min_value=0.0, max_value=10.0, value=float(q_r_calc), step=0.1)
        with ctrl_col2:
            phi_actual = st.slider("Wavefront Phase Advance ($\phi$)", min_value=0.0, max_value=np.pi, value=0.0, step=0.05)

    # --- CÁLCULOS MATEMÁTICOS DE INTERFERENCIA ---
    xi = np.arctan(Q_R)
    raiz = np.sqrt(1 + Q_R**2)
    angulo_precesion = raiz * phi_actual

    # Coordenadas espaciales de los paquetes de ondas (CCW y CW)
    x_ccw, y_ccw = -np.cos(phi_actual), np.sin(phi_actual)
    x_cw, y_cw = -np.cos(phi_actual), -np.sin(phi_actual)

    # Vectores de espín 3D reales
    Sx_ccw = np.sin(xi) * np.sin(angulo_precesion)
    Sy_ccw = np.cos(angulo_precesion)
    Sz_ccw = np.cos(xi) * np.sin(angulo_precesion)

    Sx_cw = -np.sin(xi) * np.sin(angulo_precesion)
    Sy_cw = np.cos(angulo_precesion)
    Sz_cw = -np.cos(xi) * np.sin(angulo_precesion)

    # Conductancia de interferencia del dispositivo
    Q_vals = np.linspace(0, 10, 500)
    xi_vals = np.arctan(Q_vals)
    Phi_vals = np.pi * Q_vals * np.sin(xi_vals) - np.pi * (1 - np.cos(xi_vals))
    G_vals = 1 + np.cos(Phi_vals)

    Phi_actual_total = np.pi * Q_R * np.sin(xi) - np.pi * (1 - np.cos(xi))
    G_actual_total = 1 + np.cos(Phi_actual_total)

    # --- SECCIÓN GRÁFICA PRINCIPAL ASIMÉTRICA ---
    col_left, col_right = st.columns([1, 1])

    with col_left:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Active Meso-Ring Transport Channel (Interactive 3D View)</p>", unsafe_allow_html=True)
            
            # --- CONSTRUCCIÓN PREMIUM CON PLOTLY 3D ---
            fig_3d = go.Figure()

            # 1. El anillo base cuantizado
            theta_ring = np.linspace(0, 2*np.pi, 200)
            fig_3d.add_trace(go.Scatter3d(
                x=np.cos(theta_ring), y=np.sin(theta_ring), z=np.zeros_like(theta_ring),
                mode='lines', line=dict(color='#cbd5e1', width=5), name='Rashba Channel', showlegend=False
            ))

            # 2. Los accesos/leads balísticos
            fig_3d.add_trace(go.Scatter3d(x=[-1.6, -1.0], y=[0, 0], z=[0, 0], mode='lines', line=dict(color='#475569', width=6), showlegend=False))
            fig_3d.add_trace(go.Scatter3d(x=[1.0, 1.6], y=[0, 0], z=[0, 0], mode='lines', line=dict(color='#475569', width=6), showlegend=False))

            # 3. Portadores de carga (CCW y CW)
            fig_3d.add_trace(go.Scatter3d(x=[x_ccw], y=[y_ccw], z=[0], mode='markers', marker=dict(size=9, color='#00d4ff', symbol='circle'), name='Electron CCW'))
            fig_3d.add_trace(go.Scatter3d(x=[x_cw], y=[y_cw], z=[0], mode='markers', marker=dict(size=9, color='#091e3a', symbol='circle'), name='Electron CW'))

            # 4. Vectores de espín dinámicos (Conos de dirección premium)
            scale = 0.4
            fig_3d.add_trace(go.Cone(x=[x_ccw], y=[y_ccw], z=[0], u=[Sx_ccw*scale], v=[Sy_ccw*scale], w=[Sz_ccw*scale], colorscale=[[0, '#e11d48'], [1, '#e11d48']], showscale=False, sizemode='absolute', sizeref=0.3, name='Spin CCW'))
            fig_3d.add_trace(go.Cone(x=[x_cw], y=[y_cw], z=[0], u=[Sx_cw*scale], v=[Sy_cw*scale], w=[Sz_cw*scale], colorscale=[[0, '#091e3a'], [1, '#091e3a']], showscale=False, sizemode='absolute', sizeref=0.3, name='Spin CW'))

            # Configuración de cámara y entorno premium libre de ruido visual (Corregido 'paper_bgcolor')
            fig_3d.update_layout(
                margin=dict(l=0, r=0, b=0, t=0), height=380, paper_bgcolor='rgba(0,0,0,0)',
                scene=dict(
                    xaxis=dict(title='X (nm)', backgroundcolor='rgba(0,0,0,0)', gridcolor='#f1f5f9', showbackground=False),
                    yaxis=dict(title='Y (nm)', backgroundcolor='rgba(0,0,0,0)', gridcolor='#f1f5f9', showbackground=False),
                    zaxis=dict(title='Spin Sz', range=[-1, 1], backgroundcolor='rgba(0,0,0,0)', gridcolor='#f1f5f9', showbackground=False),
                    camera=dict(eye=dict(x=1.3, y=-1.3, z=1.0))
                ),
                legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.05, font=dict(size=10))
            )
            st.plotly_chart(fig_3d, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Ballistic Quantum Interference Profile</p>", unsafe_allow_html=True)
            
            # --- GRÁFICA DE CONDUCTANCIA OPTIMIZADA CON MATPLOTLIB ---
            fig_2d, ax2 = plt.subplots(figsize=(6, 3.4), dpi=250)
            fig_2d.patch.set_facecolor('white')
            ax2.set_facecolor('#f8fafc')
            
            # Perfil e iluminación de fondo
            ax2.plot(Q_vals, G_vals, color='#002244', alpha=0.85, linewidth=2, label=r'Transmission $G(Q_R)$')
            ax2.fill_between(Q_vals, G_vals, color='#00d4ff', alpha=0.04)
            
            # Estado cuántico actual
            ax2.scatter(Q_R, G_actual_total, color='#e11d48', s=90, zorder=6, edgecolor='white', linewidth=1, label='Operating Point')
            
            # Ajustes finos de tipografía y bordes minimalistas
            ax2.set_xlim(0, 10)
            ax2.set_ylim(-0.1, 2.3)
            ax2.set_xlabel(r"Rashba Coupling Strength $Q_R$", fontsize=7, color='#475569')
            ax2.set_ylabel(r"Conductance $G \ / \ (e^2/h)$", fontsize=7, color='#475569')
            ax2.grid(True, linestyle=':', linewidth=0.5, color='#cbd5e1')
            ax2.legend(loc='upper right', fontsize=6, frameon=True, facecolor='white', edgecolor='#e2e8f0')
            ax2.tick_params(colors='#64748b', labelsize=6)
            for spine in ax2.spines.values():
                spine.set_color('#e2e8f0')
                
            plt.tight_layout()
            st.pyplot(fig_2d)

    # --- PANEL INFERIOR DE ANALÍTICAS METRIC-CARDS Y CONTEXTO ---
    col_inf_left, col_inf_right = st.columns([5.4, 1.6])
    with col_inf_left:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Real-Time Transport Analytics</p>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(label="Wavefront Angle", value=f"{phi_actual:.2f} rad", delta="In Transit" if phi_actual < np.pi else "Collected")
            with m2:
                st.metric(label="Total Differential Conductance", value=f"{G_actual_total:.4f} e²/h", delta=f"{G_actual_total/2*100:.1f}% Trans.")
            with m3:
                st.metric(label="Geometric Phase Shift (Δθ)", value=f"{angulo_precesion:.2f} rad")

    with col_inf_right:
        with st.container(border=True):
            st.markdown("<p class='panel-title'>Aharonov-Casher Insights</p>", unsafe_allow_html=True)
            with st.expander("3D Spin Texture", expanded=True):
                st.markdown("<div class='insight-content'><p>The effective relativistic field forces spins to tilt vertically out of the plane, creating an explicit $S_z$ projection visible via rotation.</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Reset Quantum Engine", type="secondary"):
        st.session_state.engine_running = False
        st.rerun()