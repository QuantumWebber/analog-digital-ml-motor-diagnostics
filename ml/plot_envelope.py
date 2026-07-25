"""Compare envelope spectra of a healthy and a faulty bearing."""
import numpy as np
import matplotlib.pyplot as plt
from features import load_recording, make_windows, BEARING_MULTIPLIERS, FS

CASES = [("Healthy", "data/Time_Normal_1_098.mat"),
         ("Outer race fault (0.007\")", "data/OR007_6_1_136.mat")]

from scipy.signal import hilbert

fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

for ax, (title, path) in zip(axes, CASES):
    signal, rpm = load_recording(path)
    window = make_windows(signal)[0]

    env = np.abs(hilbert(window))
    env = env - np.mean(env)
    spectrum = np.abs(np.fft.rfft(env * np.hanning(len(env))))
    freqs = np.fft.rfftfreq(len(env), d=1 / FS)

    mask = freqs <= 500
    ax.plot(freqs[mask], spectrum[mask], linewidth=0.9, color="#1f77b4")

    fr = rpm / 60.0
    for name, mult in BEARING_MULTIPLIERS.items():
        if name == "ftf":
            continue
        f_defect = mult * fr
        if f_defect <= 500:
            ax.axvline(f_defect, color="crimson", linestyle="--", alpha=0.6, linewidth=1)
            ax.text(f_defect, ax.get_ylim()[1] * 0.85, f" {name.upper()}\n {f_defect:.0f} Hz",
                    color="crimson", fontsize=8, va="top")

    ax.set_title(f"{title} — envelope spectrum ({rpm:.0f} RPM)", fontsize=10)
    ax.set_ylabel("Amplitude")

axes[-1].set_xlabel("Frequency (Hz)")
plt.tight_layout()
plt.savefig("ml/plots/envelope_spectrum.png", dpi=150)
plt.show()