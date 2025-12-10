import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ======================================================
# 1. PARAMETER FISIS
# ======================================================
m = 1.0        # massa (kg)
l = 1.0        # panjang (m)
g = 9.81       # gravitasi (m/s^2)
c = 0.2        # gesekan udara (Koefisien Damping)

# Perhitungan Momen Inersia (Sesuai PDF Hal 12)
# I_cm = Inersia di pusat massa (tengah batang)
I_cm = (1/12) * m * l**2
# A = Total Inersia di poros (Pivot) -> Pakai Teorema Sumbu Sejajar
A = (1/4) * m * l**2 + I_cm
# B = Konstanta Gravitasi (mg * l/2)
B = (m * g * l) / 2

# ======================================================
# 2. PID CONTROLLER
# ======================================================
# Tuning PID (Silakan diubah-ubah kalau kurang stabil)
Kp = 20.0  # Saya naikkan dikit biar lebih kuat ngangkatnya
Ki = 0.0   # Integral biasanya 0 dulu untuk pendulum
Kd = 5.0   # Derivative buat ngerem

setpoint = 0.0          # Target: 0 derajat (Bawah)
integral = 0.0
prev_error = 0.0

def PID_control(theta, theta_dot, dt):
    global integral, prev_error

    error = setpoint - theta
    integral += error * dt
    derivative = (error - prev_error) / dt
    prev_error = error

    # Rumus PID: τ = Kp*e + Ki*∫e + Kd*de/dt
    tau = Kp * error + Ki * integral + Kd * derivative
    return tau

# ======================================================
# 3. LOOP SIMULASI (Kalkulasi Dulu, Animasi Belakangan)
# ======================================================
dt = 0.02              # Time step
t_max = 10             # Durasi simulasi (detik)
t = np.arange(0, t_max, dt)

# Array kosong untuk menampung data
theta = np.zeros(len(t))
theta_dot = np.zeros(len(t))

# Kondisi Awal
theta[0] = math.radians(90) # Mulai dari 90 derajat
theta_dot[0] = 0.0

print("Sedang menghitung fisika...")
for i in range(len(t) - 1):
    # Hitung Torsi dari PID
    tau = 0.0

    # Rumus Gerak (F=ma versi putar): 
    # Percepatan Sudut = (TorsiPID - TorsiGravitasi - Gesekan) / Inersia
    theta_ddot = (tau - B * math.sin(theta[i]) - c * theta_dot[i]) / A

    # Update Kecepatan & Posisi (Euler Method)
    theta_dot[i+1] = theta_dot[i] + theta_ddot * dt
    theta[i+1] = theta[i] + theta_dot[i+1] * dt

# Konversi ke Koordinat X, Y untuk gambar
# (Menggunakan ujung batang sebagai posisi bola)
x = l * np.sin(theta)
y = -l * np.cos(theta)

print("Selesai menghitung. Membuka animasi...")

# ======================================================
# 4. SETUP ANIMASI & GRAFIK (GUI)
# ======================================================
fig = plt.figure(figsize=(10, 8))

# --- Plot Animasi (Atas) ---
ax_anim = fig.add_subplot(2, 1, 1)
# Kasih batas lebih lebar (1.5x panjang tali) biar gak mentok pinggir
ax_anim.set_xlim(-l*1.5, l*1.5)
ax_anim.set_ylim(-l*1.5, l*1.5)
ax_anim.set_aspect('equal')
ax_anim.grid(True)
ax_anim.set_title("Simulasi Pendulum (Pre-Calculated)")

# Garis batang dan Bola
line, = ax_anim.plot([], [], 'o-', lw=3, color='black')
mass_point, = ax_anim.plot([], [], 'o', markersize=20, color='red')
time_template = 'Waktu = %.1fs'
time_text = ax_anim.text(0.05, 0.9, '', transform=ax_anim.transAxes)

# --- Plot Grafik (Bawah) ---
ax_graph = fig.add_subplot(2, 1, 2)
ax_graph.set_title("Grafik Respon PID")
ax_graph.set_xlabel("Waktu (detik)")
ax_graph.set_ylabel("Sudut (radian)")
ax_graph.grid(True)
ax_graph.plot(t, theta, color='blue') # Plot semua data sekaligus
ax_graph.axhline(0, color='black', linestyle='--') # Garis target

# Penanda posisi waktu di grafik (Garis merah berjalan)
time_line, = ax_graph.plot([], [], 'r|', markersize=15, markeredgewidth=2)

# ======================================================
# 5. FUNGSI UPDATE ANIMASI
# ======================================================
def update(frame):
    # Update posisi Garis: Dari (0,0) ke (x,y)
    line.set_data([0, x[frame]], [0, y[frame]])
    
    # Update posisi Bola: [x], [y] -> HARUS PAKAI KURUNG SIKU []
    mass_point.set_data([x[frame]], [y[frame]])
    
    # Update teks waktu
    time_text.set_text(time_template % (frame * dt))
    
    # Update garis penanda di grafik bawah
    time_line.set_data([t[frame]], [theta[frame]])

    return line, mass_point, time_text, time_line

# Jalankan Animasi
ani = FuncAnimation(fig, update, frames=len(t), interval=dt*1000, blit=True)
plt.show()