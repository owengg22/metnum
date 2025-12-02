import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv("FetalECG.txt", sep="\t", header=None)

t = data.iloc[:, 0].values      
y = data.iloc[:, 1].values      

start = 1
end = 1200
t = t[start:end]
y = y[start:end]

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


plt.figure(figsize=(13,8))

plt.subplot(3,1,1)
plt.plot(t, y, label="Original Fetal ECG")
plt.title("Original Fetal ECG")
plt.legend()
plt.grid(True)

plt.subplot(3,1,2)
plt.plot(t, y, label="Original")
plt.plot(t, baseline, linewidth=2, label=f"Baseline Polyfit (Order {order})")
plt.title(f"Baseline Fitting (order={order}) - R²={r2:.4f}")
plt.legend()
plt.grid(True)


plt.subplot(3,1,3)
plt.plot(t, y_detrended, label="Detrended Fetal ECG")
plt.title("Detrended ECG")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
