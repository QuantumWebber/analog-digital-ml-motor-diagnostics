# Analog Signal Conditioning Front End

Vibration sensor se ADC tak ka signal chain, LTspice me simulate kiya gaya.

## Chain
Accelerometer (5 mV, 1 kHz) → Instrumentation Amplifier (G = 210) → Sallen-Key LPF (fc = 5.1 kHz) → Level Shift (1.65 V) → ADC

## Design

### Instrumentation Amplifier
Stage 1 (dual buffer with gain): G1 = 1 + 2·R1/Rg = 1 + 2(10k/1k) = 21
Stage 2 (difference amp):        G2 = R4/R3 = 10k/1k = 10
Total gain = 210

5 mV sensor signal → 1.05 V, jo ADC ke input range ke liye theek hai.

### Anti-Aliasing Low-Pass Filter
2nd-order Butterworth, unity-gain Sallen-Key topology.

fc = 1/(2π·R·√(C1·C2)) = 1/(2π·22k·√(2n·1n)) = 5.12 kHz
Q  = 0.5·√(C1/C2) = 0.707  (Butterworth)

CWRU dataset 12 kHz pe sampled hai → Nyquist 6 kHz. 5.1 kHz cutoff aliasing rok deta hai.

### Level Shift
AC coupling (1 µF) ke baad 3.3 V rail se resistive divider (10k/10k) → 1.65 V bias.
Output range: 0.6 V – 2.7 V, yaani 0–3.3 V ADC window ke andar.

## Results

### AC Response (plots/bode.png)
- Passband gain ≈ 46 dB (= 210) ✓
- −3 dB point ≈ 5 kHz ✓
- −40 dB/decade rolloff (2nd order) ✓

### Transient Response (plots/transient.png)
- INA output V(o3): 1 kHz signal + 50 kHz interference
- Filter output V(adc): saaf 1 kHz sine, 1.65 V pe centered, interference removed

## Files
- `signal_conditioning.cir` — SPICE netlist (LTspice me "All Files" filter se kholo)
- `plots/bode.png`, `plots/transient.png`

## Note
Op-amps ideal VCVS (gain 1e6) se model kiye hain — design values verify karne ke liye. Real implementation me rail-to-rail op-amp (e.g. LT1013) aur ±5 V supply chahiye.