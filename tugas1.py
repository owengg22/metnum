import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv("abdomen1.txt", header=None)
y = data.iloc[:, 0].values

start = 1
end = 1000 #max 20000
y = y[start:end]


t = np.arange(len(y))       

order = 5
coeffs = np.polyfit(t, y, order)
baseline = np.polyval(coeffs, t)
y_detrended = y - baseline

Sr = np.sum((y - baseline) ** 2)
St = np.sum((y - np.mean(y)) ** 2)
r2 = 1 - Sr / St

print("Order polynomial =", order)
print("Koefisien regresi =", coeffs)
print("Nilai r^2 =", r2)

plt.figure(figsize=(13, 4))
plt.plot(t, y, label='Sinyal ECG asli')
plt.plot(t, baseline, label='Baseline (Polynomial)', linewidth=2)
plt.title(f"Sinyal ECG & Baseline (Order {order}) - r² = {r2:.4f}")
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(13, 4))
plt.plot(t, y_detrended, label='Sinyal setelah koreksi baseline')
plt.title("Sinyal ECG Detrended")
plt.legend()
plt.grid()
plt.show()
