import streamlit as st
import numpy as np
from src.engine import RashbaRing

# --- Page Config ---
st.set_page_config(page_title="Hamiltonian - NEXUS", layout="wide")

# --- Helper Function for Beautiful LaTeX Matrices ---
def format_matrix_to_latex(matrix: np.ndarray) -> str:
    """Convierte una matriz NumPy a un string LaTeX limpio y profesional."""
    latex_str = r"\begin{pmatrix}"
    for row in matrix:
        row_str = []
        for val in row:
            real_part = np.real(val)
            imag_part = np.imag(val)
            
            # Formato científico a 2 decimales
            if abs(imag_part) < 1e-40: 
                row_str.append(f"{real_part:.2e}")
            elif abs(real_part) < 1e-40: 
                row_str.append(f"{imag_part:.2e}i")
            else:
                sign = "+" if imag_part >= 0 else "-"
                row_str.append(f"{real_part:.2e} {sign} {abs(imag_part):.2e}i")
                
        latex_str += " & ".join(row_str) + r" \\ "
    latex_str += r"\end{pmatrix}"
    return latex_str

# --- UI Layout ---
st.title("Hamiltonian Formulation")
st.markdown("---")

# Sidebar for Local Parameters
st.sidebar.header("Quantum State Parameters")
l_val = st.sidebar.slider("Angular Momentum (l)", -5, 5, 1)
Phi_val = st.sidebar.slider("Magnetic Flux (Φ/Φ₀)", -2.0, 2.0, 0.0, step=0.1)
Bz_val = st.sidebar.number_input("Zeeman Splitting (Bz) [J]", value=0.0, format="%.2e")

# Retrieve Global Parameters (with fallbacks if starting directly on this page)
R = st.session_state.get('R', 25.0) * 1e-9          # Convert nm to m
m_star = st.session_state.get('m_star', 0.067) * 9.109e-31 # Effective mass in kg
alpha_R = st.session_state.get('alpha_R', 10.0) * 1e-12    # Rashba param in J*m

# Analytical Equation Section
st.subheader("Analytical Model")
st.latex(r"""
\hat{H}= \frac{\hbar^2}{2m^*R^{2}}\left(-i\frac{\partial }{\partial \phi }+\frac{\Phi }{\Phi_{0}}\right)^2+\frac{1}{2}g\mu_{B}B_{z}\hat{\sigma}_{z}+\frac{\alpha_{R}}{R}\hat{\sigma}_r\left(-i\frac{\partial }{\partial \phi }+\frac{\Phi }{\Phi_{0}}\right)-i\frac{\alpha _R}{2R}\hat{\sigma }_{\phi }
""")

# Numerical Computation Section
st.subheader("Numerical Matrix Representation")

try:
    # Initialize engine and compute
    ring = RashbaRing(R=R, m_star=m_star, alpha_R=alpha_R)
    H_matrix = ring.get_hamiltonian(l=l_val, B_z=Bz_val, Phi=Phi_val)
    
    # Display beautifully
    latex_matrix = format_matrix_to_latex(H_matrix)
    st.latex(r"\hat{H}_{num} = " + latex_matrix)
    
except Exception as e:
    st.error(f"Error computing Hamiltonian: {e}")