import numpy as np

C = 343.0     # speed of sound (m/s)
D = 0.18      # spacing between your two ears (m)

def angle_to_delay(theta_deg):
    return D * np.sin(np.deg2rad(theta_deg)) / C

# quick check that everything works
print("delay at 90 deg:", round(angle_to_delay(90) * 1e6), "microseconds")
print("delay at  0 deg:", round(angle_to_delay(0) * 1e6), "microseconds")

FS = 48000     # sample rate: how many audio samples per second

def delay_signal(x, tau):
    # shift a sound slightly in time by tau seconds
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / FS)
    return np.fft.irfft(np.fft.rfft(x) * np.exp(-1j * 2 * np.pi * f * tau), n)

def make_two_ear_signal(theta_deg, snr_db=10, dur=0.05):
    n = int(FS * dur)
    src = np.random.randn(n)              # a broadband "whoosh," like a passing car
    tau = angle_to_delay(theta_deg)
    left = delay_signal(src, +tau / 2)
    right = delay_signal(src, -tau / 2)
    nz = 10 ** (-snr_db / 20)
    return left + nz * np.random.randn(n), right + nz * np.random.randn(n)

# test the new piece
L, R = make_two_ear_signal(35)
print("made a fake recording:", len(L), "samples for each ear")
MAX_TAU = D / C    # the biggest delay physically possible

def gcc_phat(sig, ref, interp=16):
    # find the tiny delay between the two ear signals
    n = len(sig) + len(ref)
    SIG = np.fft.rfft(sig, n)
    REF = np.fft.rfft(ref, n)
    R = SIG * np.conj(REF)
    R /= np.abs(R) + 1e-12          # keep only the timing, ignore loudness
    cc = np.fft.irfft(R, interp * n)
    m = int(interp * FS * MAX_TAU)
    cc = np.concatenate((cc[-m:], cc[:m + 1]))
    return (np.argmax(np.abs(cc)) - m) / float(interp * FS)

def delay_to_angle(tau):
    return np.rad2deg(np.arcsin(np.clip(tau * C / D, -1, 1)))

# test the direction-finder
print("\nDirection-finder test:")
for true_angle in [35, -50, 0, 70]:
    L, R = make_two_ear_signal(true_angle)
    estimate = delay_to_angle(gcc_phat(L, R))
    print(f"  true {true_angle:+d} deg  ->  estimated {estimate:+.1f} deg")
import matplotlib.pyplot as plt

# measure accuracy across many angles and draw a graph
true_angles = np.arange(-80, 81, 5)
TRIALS = 30
means, errors = [], []
for th in true_angles:
    ests = [delay_to_angle(gcc_phat(*make_two_ear_signal(th))) for _ in range(TRIALS)]
    means.append(np.mean(ests))
    errors.append(np.mean(np.abs(np.array(ests) - th)))
mae = float(np.mean(errors))
print(f"\nMean error across all angles: {mae:.2f} degrees")

plt.figure(figsize=(6, 6))
plt.plot([-90, 90], [-90, 90], "--", color="gray", label="perfect")
plt.plot(true_angles, means, "o", label="your estimator")
plt.xlabel("true direction (degrees)")
plt.ylabel("estimated direction (degrees)")
plt.title(f"Direction-finding accuracy (mean error {mae:.2f} deg)")
plt.legend()
plt.grid(True)
plt.savefig("doa_accuracy.png", dpi=130)
plt.show()
print("Saved graph: doa_accuracy.png")
