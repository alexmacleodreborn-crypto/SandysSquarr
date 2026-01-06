import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import lightkurve as lk

# ============================================================
# USER SETTINGS
# ============================================================

TARGET = "TIC 220414682"   # example known TESS SN host
SECTOR = None             # None = auto
CADENCE = "short"         # short or long

Z_THRESHOLD = 0.7
SIGMA_THRESHOLD = 0.2

SMOOTH_WINDOW = 31        # must be odd
SMOOTH_ORDER = 3

# ============================================================
# LOAD TESS LIGHT CURVE
# ============================================================

search = lk.search_lightcurve(TARGET, mission="TESS", cadence=CADENCE)
lc = search.download().remove_nans()

time = lc.time.value
flux = lc.flux.value
flux_err = lc.flux_err.value

# Normalize
flux = flux / np.nanmedian(flux)

# ============================================================
# SMOOTH (remove high-frequency noise)
# ============================================================

flux_smooth = savgol_filter(flux, SMOOTH_WINDOW, SMOOTH_ORDER)

# ============================================================
# TOY 3 VARIABLES
# ============================================================

# Σ(t): normalized escape
Sigma = (flux_smooth - flux_smooth.min()) / (flux_smooth.max() - flux_smooth.min())

# dΣ/dt
dt = np.gradient(time)
dSigma_dt = np.gradient(Sigma) / dt

# Z(t): trap proxy (suppressed slope = high Z)
A = np.nanmax(np.abs(dSigma_dt))
Z = 1.0 - np.abs(dSigma_dt) / A
Z = np.clip(Z, 0, 1)

# ============================================================
# CORNER DETECTION
# ============================================================

corner_mask = (Z > Z_THRESHOLD) & (Sigma < SIGMA_THRESHOLD)

corner_time = np.sum(corner_mask) * np.nanmedian(dt)
corner_fraction = np.sum(corner_mask) / len(Z)

# Quench detection (max curvature)
d2Sigma_dt2 = np.gradient(dSigma_dt) / dt
quench_index = np.argmax(np.abs(d2Sigma_dt2))
quench_time = time[quench_index]

# ============================================================
# OUTPUT METRICS
# ============================================================

print("\n=== TOY 3 DIAGNOSTICS (TESS DATA) ===")
print(f"Corner dwell time     : {corner_time:.4f} days")
print(f"Corner dwell fraction : {corner_fraction*100:.2f}%")
print(f"Quench time (relative): {quench_time:.4f} BTJD")

# ============================================================
# PLOTS
# ============================================================

fig, axs = plt.subplots(1, 3, figsize=(16, 5))

# Phase space
axs[0].plot(Z, Sigma, lw=1.5)
axs[0].set_xlabel("Z (Trap)")
axs[0].set_ylabel("Σ (Escape)")
axs[0].set_title("Toy 3 Phase Space")
axs[0].set_xlim(0, 1)
axs[0].set_ylim(0, 1)
axs[0].grid(alpha=0.4)

# Time series
axs[1].plot(time, Sigma, label="Σ", lw=1.5)
axs[1].plot(time, Z, label="Z", lw=1.2)
axs[1].axvline(quench_time, color="r", ls="--", label="Quench")
axs[1].set_xlabel("Time (BTJD)")
axs[1].set_title("Toy 3 Time Series")
axs[1].legend()
axs[1].grid(alpha=0.4)

# Corner mask
axs[2].plot(time, corner_mask.astype(int), lw=1.5)
axs[2].set_xlabel("Time (BTJD)")
axs[2].set_ylabel("Corner State")
axs[2].set_title("Corner Dwell Indicator")
axs[2].grid(alpha=0.4)

plt.tight_layout()
plt.show()