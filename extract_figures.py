"""
Script to extract key visualizations from the Ising model notebook.
Generates high-quality PNG images for the portfolio README.
"""
import numpy as np
import matplotlib.pyplot as plt
from numba import njit
import os

# Ensure figures directory exists
os.makedirs('figures', exist_ok=True)

# Set high DPI for quality images
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Define the core functions from the notebook
@njit
def h(S):
    """Calculate energy per particle of the lattice in state S"""
    H = 0
    L = len(S)
    for i in range(0, L):
        for j in range(0, L):
            H += S[i, j] * (S[i-1, j] + S[i, j-1])
    return -H / L**2

@njit
def metropolis(S, prob):
    """Apply Metropolis algorithm to state S"""
    L = len(S)
    
    p = np.random.rand()
    i = np.random.randint(L)
    j = np.random.randint(L)
    
    dm = -S[i, j] * 2 / L**2
    delta_e = 2 * S[i, j] * (S[(i+1)%L, j] + S[i-1, j] + S[i, (j+1)%L] + S[i, j-1])
    de = delta_e / L**2
    
    if delta_e <= 0:
        S[i, j] = -S[i, j]
        return (S, dm, de)
    elif delta_e == 4:
        if p > prob[0]:
            return (S, 0, 0)
        else:
            S[i, j] = -S[i, j]
            return (S, dm, de)
    elif delta_e == 8:
        if p > prob[1]:
            return (S, 0, 0)
        else:
            S[i, j] = -S[i, j]
            return (S, dm, de)

print("Generating visualizations...")
print("This may take several minutes...")

# 1. THERMALIZATION PLOT
print("\n1. Generating thermalization plot...")
L = 30
beta = 1
nequilibrio = 1000  # Reduced from 100000 for faster execution

prob = np.array([np.exp(-4*beta), np.exp(-8*beta)])
S = 2 * np.random.randint(2, size=(L, L)) - 1

m = np.zeros(nequilibrio)
e = np.zeros(nequilibrio)
m[0] = np.mean(S)
e[0] = h(S)

for n in range(1, nequilibrio):
    S, dm, de = metropolis(S, prob)
    m[n] = m[n-1] + dm
    e[n] = e[n-1] + de

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
ax1.plot(m, linewidth=0.5)
ax1.set_ylabel('Magnetization', fontsize=12)
ax1.set_title('System Thermalization (T=1.0)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)

ax2.plot(e * (L**2), linewidth=0.5)
ax2.set_ylabel('Energy', fontsize=12)
ax2.set_xlabel('Monte Carlo Steps', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('figures/thermalization.png', dpi=300, bbox_inches='tight')
plt.close()
print("   Saved: figures/thermalization.png")

# 2. SPIN CONFIGURATION AT DIFFERENT TEMPERATURES
print("\n2. Generating spin configuration visualizations...")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
temperatures = [1.0, 2.27, 3.5]
temp_labels = ['Low T (T=1.0)', 'Critical T (T≈2.27)', 'High T (T=3.5)']

for idx, (temp, label) in enumerate(zip(temperatures, temp_labels)):
    L = 50
    beta = 1/temp
    nequilibrio = 1000  # Reduced from 50000 for faster execution
    
    prob = np.array([np.exp(-4*beta), np.exp(-8*beta)])
    S = 2 * np.random.randint(2, size=(L, L)) - 1
    
    # Thermalize
    for n in range(nequilibrio):
        S, dm, de = metropolis(S, prob)
    
    axes[idx].imshow(S, cmap='RdBu_r', interpolation='nearest')
    axes[idx].set_title(label, fontsize=12, fontweight='bold')
    axes[idx].axis('off')

plt.suptitle('Spin Configurations at Different Temperatures', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('figures/spin_configurations.png', dpi=300, bbox_inches='tight')
plt.close()
print("   Saved: figures/spin_configurations.png")

# 3. PHASE TRANSITION PLOTS (using pre-computed data)
print("\n3. Generating phase transition plots...")

# Load pre-computed data files
try:
    data_L16 = np.loadtxt('notebook/datos_t_L_16.txt')
    data_L32 = np.loadtxt('notebook/datos_t_L_32.txt')
    data_L64 = np.loadtxt('notebook/datos_t_L_64.txt')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Magnetization vs Temperature
    ax1.plot(data_L16[:, 0], data_L16[:, 1], 'o-', label='L=16', markersize=4)
    ax1.plot(data_L32[:, 0], data_L32[:, 1], 's-', label='L=32', markersize=4)
    ax1.plot(data_L64[:, 0], data_L64[:, 1], '^-', label='L=64', markersize=4)
    ax1.axvline(x=2.27, color='red', linestyle='--', alpha=0.7, label='Critical T')
    ax1.set_xlabel('Temperature (T)', fontsize=12)
    ax1.set_ylabel('Magnetization |⟨m⟩|', fontsize=12)
    ax1.set_title('Phase Transition: Magnetization vs Temperature', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Energy vs Temperature
    ax2.plot(data_L16[:, 0], data_L16[:, 2], 'o-', label='L=16', markersize=4)
    ax2.plot(data_L32[:, 0], data_L32[:, 2], 's-', label='L=32', markersize=4)
    ax2.plot(data_L64[:, 0], data_L64[:, 2], '^-', label='L=64', markersize=4)
    ax2.axvline(x=2.27, color='red', linestyle='--', alpha=0.7, label='Critical T')
    ax2.set_xlabel('Temperature (T)', fontsize=12)
    ax2.set_ylabel('Energy per Spin ⟨e⟩', fontsize=12)
    ax2.set_title('Energy vs Temperature', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/phase_transition.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   Saved: figures/phase_transition.png")
    
except FileNotFoundError as e:
    print(f"   Warning: Could not load data files for phase transition plot: {e}")
    print("   Skipping phase transition plot...")

# 4. SUSCEPTIBILITY AND SPECIFIC HEAT
print("\n4. Generating susceptibility and specific heat plots...")
try:
    data_chi_cv = np.loadtxt('notebook/datos_t_chi_cv.txt')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Susceptibility
    ax1.plot(data_chi_cv[:, 0], data_chi_cv[:, 1], 'o-', color='blue', markersize=5)
    ax1.axvline(x=2.27, color='red', linestyle='--', alpha=0.7, label='Critical T')
    ax1.set_xlabel('Temperature (T)', fontsize=12)
    ax1.set_ylabel('Susceptibility χ', fontsize=12)
    ax1.set_title('Magnetic Susceptibility vs Temperature', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Specific Heat
    ax2.plot(data_chi_cv[:, 0], data_chi_cv[:, 2], 'o-', color='green', markersize=5)
    ax2.axvline(x=2.27, color='red', linestyle='--', alpha=0.7, label='Critical T')
    ax2.set_xlabel('Temperature (T)', fontsize=12)
    ax2.set_ylabel('Specific Heat Cv', fontsize=12)
    ax2.set_title('Specific Heat vs Temperature', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/susceptibility_specific_heat.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   Saved: figures/susceptibility_specific_heat.png")
    
except FileNotFoundError as e:
    print(f"   Warning: Could not load data files: {e}")
    print("   Skipping susceptibility and specific heat plots...")

# 5. CORRELATION LENGTH
print("\n5. Generating correlation length plot...")
try:
    data_lc_a = np.loadtxt('notebook/datos_t_lc_30_a.txt')
    data_lc_b = np.loadtxt('notebook/datos_t_lc_30_b.txt')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(data_lc_a[:, 0], data_lc_a[:, 1], 'o-', label='Method A', markersize=5)
    ax.plot(data_lc_b[:, 0], data_lc_b[:, 1], 's-', label='Method B', markersize=5)
    ax.axvline(x=2.27, color='red', linestyle='--', alpha=0.7, label='Critical T')
    ax.set_xlabel('Temperature (T)', fontsize=12)
    ax.set_ylabel('Correlation Length ξ', fontsize=12)
    ax.set_title('Correlation Length vs Temperature (L=30)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/correlation_length.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   Saved: figures/correlation_length.png")
    
except FileNotFoundError as e:
    print(f"   Warning: Could not load correlation length data: {e}")
    print("   Skipping correlation length plot...")

print("\n" + "="*60)
print("Visualization extraction complete!")
print("="*60)
print("\nGenerated files in figures/ directory:")
for filename in sorted(os.listdir('figures')):
    if filename.endswith('.png'):
        filepath = os.path.join('figures', filename)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  - {filename} ({size_kb:.1f} KB)")
print("\nAll images are saved at 300 DPI for high quality.")
