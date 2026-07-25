
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt

FILES = {
    "healthy":     "data/Time_Normal_1_098.mat",
    "inner_race":  "data/IR007_1_110.mat",
    "ball":        "data/B007_1_123.mat",
    "outer_race":  "data/OR007_6_1_136.mat",
}

fig, axes = plt.subplots(4, 1, figsize=(11, 8), sharex=True)

for ax, (label, path) in zip(axes, FILES.items()):
    mat = loadmat(path)
    key = [k for k in mat if k.endswith("DE_time")][0]
    signal = mat[key].ravel()

    print(f"{label:12s} key={key:15s} n={len(signal):7d} "
          f"rms={np.sqrt(np.mean(signal**2)):.4f} peak={np.max(np.abs(signal)):.4f}")

    ax.plot(signal[:4096], linewidth=0.6)
    ax.set_ylabel(label, fontsize=9)

axes[-1].set_xlabel("Sample index")
plt.tight_layout()
plt.show()