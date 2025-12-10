import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

# --- KONFIGURASI ---
DT = 0.05          # Kecepatan waktu
DURASI = 1000      # Lama simulasi

class PendulumSederhana:
    def __init__(self):
        #default parameter fisika (real life)
        self.m = 1.0
        self.l = 1.0
        self.g = 9.8
        self.J = (1/3) * self.m * (self.l**2)
        
        # Posisi Awal for pendulum
        self.sudut = math.radians(-270) 
        self.kecepatan = 0.0
        self.waktu = 0.0
        
        # Declaration for PID
        self.error_sebelumnya = 0.0
        self.tabungan_error = 0.0

    def get_pid(self):
        # What we want
        target = 0.0 
        
        # Tuning (u can change these values)
        Kp = 3.0   # Tenaga Per (Spring)
        Kd = 0.5   # Tenaga Rem (Damping)
        
        error = target - self.sudut
        
        # Rumus PID Sederhana
        P = Kp * error
        D = Kd * (error - self.error_sebelumnya) / DT
        self.error_sebelumnya = error
        
        return P + D

    def update_fisika(self, kekuatan_dorong):
        torsi_gravitasi = self.m * self.g * (self.l / 2) * math.sin(self.sudut)
        
        # perhitungan percepatan sudut
        percepatan = (kekuatan_dorong - torsi_gravitasi) / self.J
        
        self.kecepatan = self.kecepatan + (percepatan * DT)
        self.sudut = self.sudut + (self.kecepatan * DT)
        self.waktu = self.waktu + DT
        
        # Gesekan Udara (Damping Alami)
        # Kalau mau "Without Friction" murni, kasih # di baris bawah ini:
        self.kecepatan = self.kecepatan * 0.995 

# for setup
simulasi = PendulumSederhana()
fig, (ax_kiri, ax_kanan) = plt.subplots(1, 2, figsize=(10, 5))

# animasi
ax_kiri.set_xlim(-1.5, 1.5); ax_kiri.set_ylim(-1.5, 1.5)
ax_kiri.set_aspect('equal'); ax_kiri.grid(True)
ax_kiri.set_title("Animasi Pendulum")
garis, = ax_kiri.plot([], [], 'o-', lw=3, color='black')
bola, = ax_kiri.plot([], [], 'o', markersize=20, color='red')

# graph
ax_kanan.set_xlim(0, 10); ax_kanan.set_ylim(-150, 150)
ax_kanan.set_title("Grafik Respon")
ax_kanan.grid(True)
ax_kanan.axhline(0, color='black', linestyle='--')
grafik, = ax_kanan.plot([], [], color='blue')

data_waktu, data_sudut = [], []

def update_gambar(frame):
    
    #1
    kekuatan = simulasi.get_pid()
    
    #2
    #kekuatan = 0.0
    
    #declarate paramater fisika tadi wak
    simulasi.update_fisika(kekuatan)
    
    # realtime update gambar
    x = simulasi.l * math.sin(simulasi.sudut)
    y = -simulasi.l * math.cos(simulasi.sudut)
    garis.set_data([0, x], [0, y])
    bola.set_data([x], [y])
    
    data_waktu.append(simulasi.waktu)
    data_sudut.append(math.degrees(simulasi.sudut))
    grafik.set_data(data_waktu, data_sudut)
    
    if simulasi.waktu > 10:
        ax_kanan.set_xlim(simulasi.waktu - 10, simulasi.waktu)
        
    return garis, bola, grafik

animasi = animation.FuncAnimation(fig, update_gambar, interval=30, blit=False)
plt.show()