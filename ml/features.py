
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.signal import hilbert
from scipy.stats import kurtosis, skew


FS = 12000            
WINDOW = 2048        
OVERLAP = 0.5        
RPM_DEFAULT = 1772   
BEARING_MULTIPLIERS = {
    "bpfo": 3.5848,  
    "bpfi": 5.4152,  
    "bsf":  4.7135,   
    "ftf":  0.3983,   
}

FILES = {
    "healthy":    "data/Time_Normal_1_098.mat",
    "inner_race": "data/IR007_1_110.mat",
    "ball":       "data/B007_1_123.mat",
    "outer_race": "data/OR007_6_1_136.mat",
}



def load_recording(path):
    """Return (drive-end signal, shaft speed in RPM) from a CWRU .mat file."""
    mat = loadmat(path)

    de_keys = [k for k in mat if k.endswith("DE_time")]
    if not de_keys:
        raise KeyError(f"No drive-end channel found in {path}")
    signal = mat[de_keys[0]].ravel().astype(float)


    rpm_keys = [k for k in mat if "RPM" in k.upper()]
    rpm = float(np.asarray(mat[rpm_keys[0]]).ravel()[0]) if rpm_keys else RPM_DEFAULT

    return signal, rpm


def make_windows(signal, size=WINDOW, overlap=OVERLAP):
    """Split a 1-D signal into overlapping windows."""
    step = int(size * (1 - overlap))
    return [signal[i:i + size] for i in range(0, len(signal) - size + 1, step)]


def time_features(x):
    rms = np.sqrt(np.mean(x ** 2))
    peak = np.max(np.abs(x))
    mean_abs = np.mean(np.abs(x))

    return {
        "rms": rms,
        "peak": peak,
        "peak_to_peak": np.ptp(x),
        "std": np.std(x),
        "kurtosis": kurtosis(x),          # impulsiveness — rises with bearing damage
        "skewness": skew(x),
        "crest_factor": peak / rms if rms else 0.0,
        "shape_factor": rms / mean_abs if mean_abs else 0.0,
        "impulse_factor": peak / mean_abs if mean_abs else 0.0,
    }



def freq_features(x, fs=FS, n_peaks=3, n_bands=5):
    spectrum = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), d=1 / fs)

    feats = {}


    top = np.argsort(spectrum)[-n_peaks:][::-1]
    for i, idx in enumerate(top):
        feats[f"peak{i+1}_freq"] = freqs[idx]
        feats[f"peak{i+1}_amp"] = spectrum[idx]


    total = np.sum(spectrum ** 2)
    for i, band in enumerate(np.array_split(spectrum, n_bands)):
        feats[f"band{i+1}_energy"] = np.sum(band ** 2) / total if total else 0.0


    feats["spectral_centroid"] = (np.sum(freqs * spectrum) / np.sum(spectrum)
                                  if np.sum(spectrum) else 0.0)
    return feats



def envelope_features(x, rpm, fs=FS, tol=3.0):
    """
    Bearing defects modulate a high-frequency resonance rather than producing
    energy at the defect frequency directly. Demodulating with the Hilbert
    transform recovers the repetition rate, which is what we measure here.
    """
    env = np.abs(hilbert(x))
    env = env - np.mean(env)                      # remove DC before transforming

    spectrum = np.abs(np.fft.rfft(env * np.hanning(len(env))))
    freqs = np.fft.rfftfreq(len(env), d=1 / fs)
    total = np.sum(spectrum) or 1.0

    fr = rpm / 60.0                               # shaft rotation frequency, Hz
    feats = {"shaft_freq": fr}

    for name, mult in BEARING_MULTIPLIERS.items():
        for harmonic in (1, 2):                   # defect tone and its 2nd harmonic
            target = mult * fr * harmonic
            band = (freqs >= target - tol) & (freqs <= target + tol)
            feats[f"env_{name}_h{harmonic}"] = np.sum(spectrum[band]) / total

    return feats



def build_feature_table(files=FILES):
    rows = []

    for label, path in files.items():
        signal, rpm = load_recording(path)
        windows = make_windows(signal)
        print(f"{label:12s} {len(signal):7d} samples  ->  {len(windows):4d} windows  "
              f"({rpm:.0f} RPM)")

        for i, w in enumerate(windows):
            row = {"label": label, "source_file": path, "window_index": i}
            row.update(time_features(w))
            row.update(freq_features(w))
            row.update(envelope_features(w, rpm))
            rows.append(row)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build_feature_table()
    df.to_csv("ml/features.csv", index=False)

    n_feat = len(df.columns) - 3      # exclude label, source_file, window_index
    print(f"\n{len(df)} windows x {n_feat} features -> ml/features.csv")
    print(df.groupby("label")[["rms", "kurtosis", "env_bpfi_h1", "env_bpfo_h1"]].mean())