import numpy as np

C = 343.0
D = 0.18
FS = 48000
MAX_TAU = D / C
RNG = np.random.default_rng(0)

def gcc_phat(sig, ref, interp=16):
    n = len(sig) + len(ref)
    SIG = np.fft.rfft(sig, n)
    REF = np.fft.rfft(ref, n)
    R = SIG * np.conj(REF)
    R /= np.abs(R) + 1e-12
    cc = np.fft.irfft(R, interp * n)
    m = int(interp * FS * MAX_TAU)
    cc = np.concatenate((cc[-m:], cc[:m + 1]))
    return (np.argmax(np.abs(cc)) - m) / float(interp * FS)

def delay_to_angle(tau):
    return np.rad2deg(np.arcsin(np.clip(tau * C / D, -1, 1)))

def fftconv(a, b):
    n = len(a) + len(b) - 1
    N = 1 << int(np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(a, N) * np.fft.rfft(b, N), N)[:n]

def rir(src, mic, room, beta, order, length):
    Lx, Ly, Lz = room
    h = np.zeros(length)
    for mx in range(-order, order + 1):
        for my in range(-order, order + 1):
            for mz in range(-order, order + 1):
                for px in (0, 1):
                    for py in (0, 1):
                        for pz in (0, 1):
                            ix = (1 - 2 * px) * src[0] + 2 * mx * Lx
                            iy = (1 - 2 * py) * src[1] + 2 * my * Ly
                            iz = (1 - 2 * pz) * src[2] + 2 * mz * Lz
                            d = np.sqrt((ix - mic[0]) ** 2 + (iy - mic[1]) ** 2 + (iz - mic[2]) ** 2)
                            refl = abs(mx - px) + abs(mx) + abs(my - py) + abs(my) + abs(mz - pz) + abs(mz)
                            samp = int(round(FS * d / C))
                            if samp < length:
                                h[samp] += (beta ** refl) / (d + 1e-9)
    return h

def simulate(theta_deg, absorption=0.35, order=6, r=2.0, dur=0.4):
    beta = np.sqrt(1 - absorption)
    room = [6.0, 6.0, 3.0]
    cx, cy, cz = 3.0, 3.0, 1.6
    left, right = [cx - D / 2, cy, cz], [cx + D / 2, cy, cz]
    a = np.deg2rad(theta_deg)
    src = [cx + r * np.sin(a), cy + r * np.cos(a), cz]
    length = int(FS * 0.3)
    hL, hR = rir(src, left, room, beta, order, length), rir(src, right, room, beta, order, length)
    dry = RNG.standard_normal(int(FS * dur))
    return fftconv(dry, hL), fftconv(dry, hR)

def estimate_avg(L, R, frame=2400, hop=1200):
    ests = []
    for s in range(0, len(L) - frame, hop):
        l, r = L[s:s + frame], R[s:s + frame]
        if np.sqrt(np.mean(l ** 2)) < 1e-5:
            continue
        ests.append(delay_to_angle(gcc_phat(l, r)))
    return float(np.median(ests)) if ests else 0.0

print("Reverberant-room test (image-source method + short-window averaging)")
print("-" * 60)
angles = list(range(-60, 61, 15))
errors = []
for th in angles:
    L, R = simulate(th)
    est = estimate_avg(L, R)
    err = abs(est - th)
    errors.append(err)
    print(f"  true {th:+4d} deg   ->   estimated {est:+6.1f} deg   (error {err:4.1f} deg)")
print("-" * 60)
print(f"Mean absolute error in reverberation: {np.mean(errors):.1f} deg")
print("(For comparison, the anechoic simulation was about 0.05 deg.)")
