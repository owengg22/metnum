import math
import matplotlib.pyplot as plt

def load_data(filename):
    t = []
    x = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                t.append(float(parts[0]))
                x.append(float(parts[1]))
    return t, x

# POLYNOMIAL REGRESSION (MANUAL - NORMAL EQUATION)

def poly_regression(xv, yv, degree):
    n = degree + 1
    A = [[0.0]*n for _ in range(n)]
    B = [0.0]*n

    # Sum of powers of x
    xpow = [0.0]*(2*degree+1)
    for k in range(2*degree+1):
        for xi in xv:
            xpow[k] += xi**k

    for i in range(n):
        for j in range(n):
            A[i][j] = xpow[i+j]

    for i in range(n):
        for xi, yi in zip(xv, yv):
            B[i] += (xi**i) * yi

    # Gaussian Elimination
    for i in range(n):
        pivot = A[i][i]
        if pivot == 0:
            continue
        for j in range(i, n):
            A[i][j] /= pivot
        B[i] /= pivot

        for k in range(i+1, n):
            factor = A[k][i]
            for j in range(i, n):
                A[k][j] -= factor * A[i][j]
            B[k] -= factor * B[i]

    # Back Substitution
    coeff = [0.0]*n
    for i in range(n-1, -1, -1):
        s = B[i]
        for j in range(i+1, n):
            s -= A[i][j] * coeff[j]
        coeff[i] = s

    return coeff



# POLYNOMIAL EVALUATION

def poly_eval(coeff, x):
    y = 0.0
    for p, c in enumerate(coeff):
        y += c * (x**p)
    return y



# LOCAL BASELINE REMOVAL (LOW ORDER)

def remove_baseline(t, x, window, degree):
    baseline = []
    corrected = []

    N = len(x)
    half = window // 2

    for i in range(N):
        L = max(0, i-half)
        R = min(N, i+half)

        tx = t[L:R]
        xx = x[L:R]

        if len(tx) < degree + 1:
            baseline.append(0.0)
            corrected.append(x[i])
            continue

        coeff = poly_regression(tx, xx, degree)
        base_val = poly_eval(coeff, t[i])

        baseline.append(base_val)
        corrected.append(x[i] - base_val)

    return corrected, baseline, half



# MAIN PROGRAM

filename = "FetalECG.txt"
t, x = load_data(filename)

window = 200        
degree = 3          

corrected, baseline, half = remove_baseline(t, x, window, degree)


# PLOTTING

plt.figure(figsize=(14, 10))

#subplot1
plt.subplot(3, 1, 1)
plt.plot(t, x, color="blue")
plt.title("Sinyal Fetal ECG Asli")
plt.xlabel("Waktu (s)")
plt.ylabel("Amplitudo")
plt.grid(True)

#subplot2
plt.subplot(3, 1, 2)

plt.plot(
    t[half:-half],
    x[half:-half],
    color="blue",
    linewidth=1.2,
    label="Original ECG"
)

plt.plot(
    t[half:-half],
    baseline[half:-half],
    color="orange",
    linewidth=2.5,
    label=f"Baseline (orde {degree})"
)

plt.title("Baseline Estimation (Low Order, Local)")
plt.xlabel("Waktu (s)")
plt.ylabel("Amplitudo")
plt.legend()
plt.grid(True)

# subplot3
plt.subplot(3, 1, 3)
plt.plot(
    t[half:-half],
    corrected[half:-half],
    color="green"
)
plt.title("Sinyal Setelah Baseline Wander Dihilangkan")
plt.xlabel("Waktu (s)")
plt.ylabel("Amplitudo")
plt.grid(True)

plt.tight_layout()
plt.show()
