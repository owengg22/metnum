import math
import matplotlib.pyplot as plt

# ===================== BACA FILE TXT =====================
filename = "FetalECG.txt"

t = []
y = []

with open(filename, "r") as file:
    for i, line in enumerate(file):
        parts = line.strip().split()
        if len(parts) == 1:        # hanya amplitudo
            t.append(i)
            y.append(float(parts[0]))
        else:                      # waktu + amplitudo
            t.append(float(parts[0]))
            y.append(float(parts[1]))

# ===================== SEGMENT ANALISIS =====================
start = 0
end = 10000

t = t[start:end]
y = y[start:end]

n_data = len(t)

# ===================== ORDE POLINOMIAL =====================
order = 15    # coba 5 vs 15

# ===================== BENTUK PERSAMAAN NORMAL =====================
N = order + 1

A = [[0.0 for _ in range(N)] for _ in range(N)]
B = [0.0 for _ in range(N)]

for i in range(N):
    for j in range(N):
        A[i][j] = sum((t[k] ** (i + j)) for k in range(n_data))
    B[i] = sum((t[k] ** i) * y[k] for k in range(n_data))

# ===================== ELIMINASI GAUSS =====================
for i in range(N):
    pivot = A[i][i]
    for j in range(i, N):
        A[i][j] /= pivot
    B[i] /= pivot

    for k in range(i + 1, N):
        factor = A[k][i]
        for j in range(i, N):
            A[k][j] -= factor * A[i][j]
        B[k] -= factor * B[i]

# ===================== SUBSTITUSI MUNDUR =====================
coeffs = [0.0 for _ in range(N)]

for i in range(N - 1, -1, -1):
    coeffs[i] = B[i] - sum(A[i][j] * coeffs[j] for j in range(i + 1, N))

print("Koefisien polinomial:")
for i, c in enumerate(coeffs):
    print(f"a{i} = {c}")

# ===================== HITUNG BASELINE (POLYVAL MANUAL) =====================
baseline = []
for k in range(n_data):
    val = 0.0
    for i in range(N):
        val += coeffs[i] * (t[k] ** i)
    baseline.append(val)

# ===================== DETREND =====================
y_detrended = [y[i] - baseline[i] for i in range(n_data)]

# ===================== HITUNG Sr, St, R² =====================
mean_y = sum(y) / n_data

Sr = sum((y[i] - baseline[i]) ** 2 for i in range(n_data))
St = sum((y[i] - mean_y) ** 2 for i in range(n_data))

r2 = 1 - (Sr / St)

print(f"\nOrder = {order}")
print(f"R² = {r2}")

# ===================== PLOT =====================
plt.figure(figsize=(13, 8))

plt.subplot(3, 1, 1)
plt.plot(t, y)
plt.title("Original Fetal ECG")
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(t, y, label="Original", alpha=0.6)
plt.plot(t, baseline, label="Baseline (Manual)", linewidth=2)
plt.title(f"Baseline Fitting Manual (Order {order}) | R² = {r2:.4f}")
plt.legend()
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(t, y_detrended)
plt.title("Detrended ECG")
plt.grid(True)

plt.tight_layout()
plt.show()
