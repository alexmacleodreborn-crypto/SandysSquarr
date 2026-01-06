import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import lightkurve as lk

# ============================================================
# SETTINGS
# ============================================================

TARGET = "TIC 141914082"      # guaranteed TESS target (for validation)
MISSION = "TESS"

Z_THRESHOLD = 0.7
SIGMA_THRESHOLD = 0.25

SMOOTH_ORDER = 3
MAX_SMOOTH_WINDOW = 31        # will auto-adjust if too large

# ============================================================
# LOAD LIGHT CURVE (API-CORRECT)
# ============================================================

search = lk.search_lightcurve(TARGET, mission=MISSION)
if len(search) == 0:
    raise RuntimeError("No light curve found for target.")

lc = search.download()
lc = lc.remove_nans()

# Extract numerical arrays (CRITICAL)
time = lc.time.value
flux = lc.flux.value
flux_err = lc.flux_err.value if lc.flux_err is not None else None

print(f"Loaded {len(time)} data points")

# ============================================================
# NORMALIZE
# ============================================================

flux = flux / np.nanmedian(flux)

# ============================================================
# SAFE SMOOTHING
# ============================================================

N = len(flux)
window = min(MAX_SMOOTH_WINDOW, (N // 2) * 2 - 1)
if window < 5:
    raise RuntimeError("Not enough data points to smooth safely.")

flux_smooth = savgol_filter(flux, window, SMOOTH_ORDER)

# ============================================================
# TOY 3 VARIABLES
# ============================================================

# Σ(t): escape proxy
Sigma = (flux_smooth - flux_smooth.min()) / (
    flux_smooth.max() - flux_smooth.min()
)

# Time derivatives
dt = np.gradient(time)
dSigma_dt = np.gradient(Sigma) / dt
d2Sigma_dt2 = np.gradient(dSigma_dt) / dt

# Z(t): trap proxy (low slope = high trap)
A = np.nanmax(np.abs(dSigma_dt))
Z = 1.0 - np.abs(dSigma_dt) / A
Z = np.clip(Z, 0, 1)

# ============================================================
# CORNER & QUENCH DIAGNOSTICS
# ============================================================

corner_mask = (Z > Z_THRESHOLD) & (Sigma < SIGMA_THRESHOLD)

corner_time = np.sum(corner_mask) * np.nanmedian(dt)
corner_fraction = np.sum(corner_mask) / len(Z)

quench_index = np.argmax(np.abs(d2Sigma_dt2))
quench_time = time[quench_index]

# ============================================================
# PRINT RESULTS
# ============================================================

print("\n=== TOY 3 DIAGNOSTICS ===")
print(f"Corner dwell time     : {corner_time:.4f} days")
print(f"Corner dwell fraction : {corner_fraction*100:.2f}%")
print(f"Quench time           : {quench_time:.4f}")

# ============================================================
# PLOTS
# ============================================================

fig, axs = plt.subplots(1, 3, figsize=(18, 5))

# --- Phase Space ---
axs[0].plot(Z, Sigma, lw=1.4)
axs[0].set_xlabel("Z (Trap Proxy)")
axs[0].set_ylabel("Σ (Escape Proxy)")
axs[0].set_title("Toy 3 Phase Space")
axs[0].set_xlim(0, 1)
axs[0].set_ylim(0, 1)
axs[0].grid(alpha=0.4)

# --- Time Series ---
axs[1].plot(time, Sigma, label="Σ (escape)", lw=1.4)
axs[1].plot(time, Z, label="Z (trap)", lw=1.2)
axs[1].axvline(quench_time, color="r", ls="--", label="Quench")
axs[1].set_xlabel("Time (BTJD)")
axs[1].set_title("Toy 3 Time Evolution")
axs[1].legend()
axs[1].grid(alpha=0.4)

# --- Corner Mask ---
axs[2].plot(time, corner_mask.astype(int), lw=1.5)
axs[2].set_xlabel("Time (BTJD)")
axs[2].set_ylabel("Corner State")
axs[2].set_title("Corner Dwell Indicator")
axs[2].grid(alpha=0.4)

plt.tight_layout()
plt.show()