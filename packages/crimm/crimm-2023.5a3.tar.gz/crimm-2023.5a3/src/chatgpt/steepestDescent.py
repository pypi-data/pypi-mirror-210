import numpy as np
from scipy.optimize import minimize

def energy(coord, atoms, params):
    """
    Computes the total energy of the protein structure using the given coordinates, 
    atoms, and force field parameters.
    """
    # Compute pairwise distances between atoms
    n_atoms = len(atoms)
    dist = np.zeros((n_atoms, n_atoms))
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            diff = coord[i] - coord[j]
            dist[i, j] = np.sqrt(np.sum(diff ** 2))
            dist[j, i] = dist[i, j]

    # Compute energy contributions from bonds, angles, and dihedrals
    bond_energy = 0.0
    angle_energy = 0.0
    dihedral_energy = 0.0
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            r = dist[i, j]
            sigma = (params[atoms[i]][0] + params[atoms[j]][0]) / 2.0
            epsilon = np.sqrt(params[atoms[i]][1] * params[atoms[j]][1])
            bond_energy += params[atoms[i]][2] * (r - sigma) ** 2
            angle_energy += params[atoms[i]][3] * (1.0 - np.cos(params[atoms[i]][4] * (r - sigma)))
            for k in range(j + 1, n_atoms):
                s = dist[j, k]
                phi = np.arccos(np.dot(coord[i] - coord[j], coord[k] - coord[j]) / (r * s))
                dihedral_energy += params[atoms[i]][5] * (1.0 + np.cos(params[atoms[i]][6] * phi))

    # Compute energy contribution from non-bonded interactions
    nb_energy = 0.0
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            r = dist[i, j]
            sigma = (params[atoms[i]][0] + params[atoms[j]][0]) / 2.0
            epsilon = np.sqrt(params[atoms[i]][1] * params[atoms[j]][1])
            nb_energy += 4.0 * epsilon * ((sigma / r) ** 12 - (sigma / r) ** 6)

    # Compute total energy
    total_energy = bond_energy + angle_energy + dihedral_energy + nb_energy
    return total_energy

def compute_energy_gradient(coords, bonds, angles, atom_types, ff_params):
    """
    Compute the energy gradient of a protein structure.

    Parameters:
    coords (np.ndarray): Atomic coordinates of the structure in angstroms.
    bonds (np.ndarray)
    angles (np.ndarray)
    atom_types (np.ndarray): Array of atomic types, where each element is an integer representing the atomic number.
    ff_params (dict): Dictionary of force field parameters, containing the force constants and Lennard-Jones parameters.

    Returns:
    np.ndarray: The energy gradient vector.
    """

    # Define constants
    N = coords.shape[0]  # number of atoms
    k_bond = ff_params['k_bond']  # bond force constant
    r_bond = ff_params['r_bond']  # bond dist constant
    k_angle = ff_params['k_angle']  # angle force constant
    theta_0 = ff_params['theta_0']  # reference angle 
    eps_lj = ff_params['eps_lj']  # Lennard-Jones epsilon parameter
    sig_lj = ff_params['sig_lj']  # Lennard-Jones sigma parameter

    # Initialize the energy gradient vector to zero
    energy_grad = np.zeros_like(coords)

    # Compute the bond contribution to the energy gradient
    for bond in bonds:
        i, j = bond
        r_ij = coords[j] - coords[i]
        dist = np.linalg.norm(r_ij)
        r_ij_hat = r_ij / dist
        force = -2 * k_bond[bond] * (dist - r_bond[bond]) * r_ij_hat
        energy_grad[i] += force
        energy_grad[j] -= force

    # Compute the angle contribution to the energy gradient
    for angle in angles:
        i, j, k = angle
        r_ij = coords[j] - coords[i]
        r_jk = coords[k] - coords[j]
        dist_ij = np.linalg.norm(r_ij)
        dist_jk = np.linalg.norm(r_jk)
        r_ij_hat = r_ij / dist_ij
        r_jk_hat = r_jk / dist_jk
        cos_theta = np.dot(r_ij_hat, r_jk_hat)
        sin_theta = np.sqrt(1 - cos_theta**2)
        force_ij = -2 * k_angle[angle] * (cos_theta - np.cos(theta_0[angle]))\
              / dist_ij / sin_theta * (r_jk_hat - cos_theta * r_ij_hat)
        force_jk = -2 * k_angle[angle] * (cos_theta - np.cos(theta_0[angle]))\
              / dist_jk / sin_theta * (r_ij_hat - cos_theta * r_jk_hat)
        energy_grad[i] += force_ij
        energy_grad[j] -= force_ij + force_jk
        energy_grad[k] += force_jk

    # Compute the Lennard-Jones contribution to the energy gradient
    for i in range(N):
        for j in range(i + 1, N):
            r_ij = coords[j] - coords[i]
            dist = np.linalg.norm(r_ij)
            r_ij_hat = r_ij / dist
            eps_ij = np.sqrt(eps_lj[atom_types[i]] * eps_lj[atom_types[j]])
            sig_ij = 0.5 * (sig_lj[atom_types[i]] + sig_lj[atom_types[j]])
            factor = 24 * eps_ij * (2 * (sig_ij / dist)**12 - (sig_ij / dist)**6) / dist**2
            energy_grad[i] += factor * r_ij_hat
            energy_grad[j] -= factor * r_ij_hat

    return energy_grad