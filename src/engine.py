"""Backend engine for a one-dimensional Rashba ring simulator.

This module implements an effective two-band Hamiltonian for a 1D semiconductor
ring with Rashba spin-orbit coupling. It supports an angular momentum basis label
`l`, external magnetic flux `Phi` (in units of the flux quantum), and Zeeman
splitting energy `B_z`.
"""

from __future__ import annotations

import numpy as np


class RashbaRing:
    """Effective Rashba ring Hamiltonian engine.

    Parameters
    ----------
    R : float
        Ring radius in meters.
    m_star : float
        Effective mass in kilograms.
    alpha_R : float
        Rashba coupling coefficient in joule-meters.

    Notes
    -----
    The model uses a minimal two-component spinor basis for a 1D ring. The
    magnetic flux is supplied as a dimensionless quantity normalized to the
    flux quantum, i.e. Phi = Phi_external / Phi_0. The Zeeman parameter `B_z`
    is treated as an energy splitting between spin states.
    """

    hbar: float = 1.054571817e-34

    def __init__(self, R: float, m_star: float, alpha_R: float) -> None:
        if R <= 0.0:
            raise ValueError("Radius R must be positive.")
        if m_star <= 0.0:
            raise ValueError("Effective mass m_star must be positive.")

        self.R = float(R)
        self.m_star = float(m_star)
        self.alpha_R = float(alpha_R)

    def get_hamiltonian(self, l: float, B_z: float = 0.0, Phi: float = 0.0) -> np.ndarray:
        """Return the 2x2 Rashba ring Hamiltonian for a given angular momentum.

        Parameters
        ----------
        l : float
            Angular momentum quantum number for the ring basis state.
        B_z : float, optional
            Zeeman splitting energy in joules. Default is 0.0.
        Phi : float, optional
            External magnetic flux normalized to the flux quantum. Default is 0.0.

        Returns
        -------
        np.ndarray
            Hermitian 2x2 Hamiltonian matrix for the specified parameters.
        """
        l_shifted = float(l) + float(Phi)

        kinetic_energy = (
            self.hbar**2
            / (2.0 * self.m_star * self.R**2)
            * l_shifted**2
        )
        rashba_coupling = self.alpha_R / self.R * l_shifted
        zeeman_energy = 0.5 * float(B_z)

        hamiltonian = np.array(
            [
                [kinetic_energy + zeeman_energy, rashba_coupling],
                [rashba_coupling, kinetic_energy - zeeman_energy],
            ],
            dtype=np.complex128,
        )
        return hamiltonian

    def solve_system(self, l: float, B_z: float = 0.0, Phi: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
        """Diagonalize the Rashba ring Hamiltonian and return eigenpairs.

        Parameters
        ----------
        l : float
            Angular momentum quantum number for the ring basis state.
        B_z : float, optional
            Zeeman splitting energy in joules. Default is 0.0.
        Phi : float, optional
            External magnetic flux normalized to the flux quantum. Default is 0.0.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Sorted eigenenergies and corresponding normalized spinors.
            The first array has shape (2,), and the second array has shape (2, 2)
            where each column is a normalized eigenvector.
        """
        hamiltonian = self.get_hamiltonian(l, B_z=B_z, Phi=Phi)
        energies, spinors = np.linalg.eigh(hamiltonian)
        return energies, spinors
