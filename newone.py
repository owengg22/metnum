import tkinter as tk
import math

# ==========================================
# 1. KONFIGURASI VARIABEL GLOBAL
# ==========================================

# Parameter Fisik (Sesuai Halaman 10-12 PDF)
m = 1.0       # Massa (kg)
l = 1.0       # Panjang (m)
g = 9.81      # Gravitasi (m/s^2)
b = 0.5       # Koefisien Gesekan (Damping)

# Momen Inersia Batang Tipis di Pusat Massa
# I = 1/12 * m * l^2
I_cm = (1.0/12.0) * m * (l**2)

# Variabel State (Kondisi Berjalan)
t = 0.0
theta = 0.0      # Sudut (Radian)
omega = 0.0      # Kecepatan Sudut (Rad/s)
dt = 0.01        # Time Sampling
running = False
data_history = [] 

# Variabel GUI
root = None
canvas_anim = None
canvas_graph = None
entry_dt = None
entry_theta = None
use_friction = None

# Posisi Pusat Animasi & Skala Gambar
cx, cy = 250, 200
scale = 180

# ==========================================
# 2. RUMUS FISIKA & NUMERIK (MANUAL)
# ==========================================

def hitung_percepatan_manual(theta_in, omega_in):
    """
    Menghitung alpha (percepatan sudut) secara manual.
    Referensi: PDF Halaman 12 - Persamaan Lagrange
    """
    global m, l, g, b, I_cm, use_friction
    
    # 1. Momen Inersia Total (J)
    # Rumus: (1/4 * m * l^2) + I
    J = (0.25 * m * (l**2)) + I_cm
    
    # 2. Torsi Gravitasi
    # Rumus: -m * g * (l/2) * sin(theta)
    torsi_gravitasi = -m * g * (l / 2.0) * math.sin(theta_in)
    
    # 3. Torsi Gesekan (Opsional)
    torsi_gesek = 0.0
    if use_friction.get():
        torsi_gesek = -b * omega_in
        
    # 4. Percepatan Sudut (Alpha) = Torsi Total / Inersia
    total_torsi = torsi_gravitasi + torsi_gesek
    alpha = total_torsi / J
    
    return alpha

def rk4_step_manual():
    """
    Metode Runge-Kutta Orde 4 (RK4).
    Referensi: PDF Halaman 7
    """
    global theta, omega, t, dt
    
    h = dt
    th = theta
    om = omega

    # Langkah k1
    k1_omega = hitung_percepatan_manual(th, om)
    k1_theta = om

    # Langkah k2
    th_k2 = th + (0.5 * h * k1_theta)
    om_k2 = om + (0.5 * h * k1_omega)
    k2_omega = hitung_percepatan_manual(th_k2, om_k2)
    k2_theta = om_k2

    # Langkah k3
    th_k3 = th + (0.5 * h * k2_theta)
    om_k3 = om + (0.5 * h * k2_omega)
    k3_omega = hitung_percepatan_manual(th_k3, om_k3)
    k3_theta = om_k3

    # Langkah k4
    th_k4 = th + (h * k3_theta)
    om_k4 = om + (h * k3_omega)
    k4_omega = hitung_percepatan_manual(th_k4, om_k4)
    k4_theta = om_k4

    # Update Nilai Akhir (Rata-rata Terbobot)
    theta = th + (h / 6.0) * (k1_theta + 2*k2_theta + 2*k3_theta + k4_theta) #sudut
    omega = om + (h / 6.0) * (k1_omega + 2*k2_omega + 2*k3_omega + k4_omega) #kecepatan sudut
    
    # Update Waktu
    t += h


#VISUAL
def draw_pendulum(theta_rad):
    canvas_anim.delete("pendulum")
    
    # Konversi Polar ke Cartesian
    sin_t = math.sin(theta_rad)
    cos_t = math.cos(theta_rad)
    
    x_end = cx + (l * scale * sin_t)
    y_end = cy + (l * scale * cos_t)
    
    # Gambar Tali
    canvas_anim.create_line(cx, cy, x_end, y_end, width=3, fill="black", tags="pendulum")
    # Gambar Pivot (Segitiga)
    canvas_anim.create_polygon(cx-15, cy-10, cx+15, cy-10, cx, cy, fill="black", tags="pendulum")
    # Gambar Bola
    r = 20
    canvas_anim.create_oval(x_end-r, y_end-r, x_end+r, y_end+r, fill="red", outline="red", tags="pendulum")

def draw_grid_labels(event=None):
    """
    Menggambar garis sumbu, grid, dan label teks.
    Dipanggil otomatis saat jendela di-resize (<Configure>).
    """
    canvas_graph.delete("grid_static")
    
    w = canvas_graph.winfo_width()
    h = canvas_graph.winfo_height()
    
    # Mencegah error saat minimize
    if w < 50 or h < 50: return

    # --- PENGATURAN MARGIN ---
    margin_left = 50   
    margin_bottom = 40 
    margin_top = 20
    margin_right = 40  
    
    # Area aktif grafik
    graph_h = h - margin_bottom - margin_top
    cy = margin_top + (graph_h / 2) # Titik tengah vertikal
    
    # 1. Gambar Sumbu Y (Vertikal)
    canvas_graph.create_line(margin_left, margin_top, margin_left, h - margin_bottom, 
                             fill="black", width=2, tags="grid_static")
    
    # 2. Gambar Sumbu X (Horizontal)
    canvas_graph.create_line(margin_left, h - margin_bottom, w - margin_right, h - margin_bottom, 
                             fill="black", width=2, tags="grid_static")
    
    # 3. Gambar Garis Tengah (Putus-putus) - SELALU DI TENGAH
    canvas_graph.create_line(margin_left, cy, w - margin_right, cy, 
                             fill="gray", dash=(2,4), tags="grid_static")

    
    
    # Label Theta [deg] 
    canvas_graph.create_text(margin_left + 10, margin_top, text="Theta [deg]", 
                             anchor="nw", fill="blue", font=("Arial", 9, "bold"), tags="grid_static")
    
    # Label Angka Y (90, 0, -90)
    canvas_graph.create_text(margin_left - 5, margin_top, text="180", anchor="e", font=("Arial", 8), tags="grid_static")
    canvas_graph.create_text(margin_left - 5, cy, text="0", anchor="e", font=("Arial", 8), tags="grid_static")
    canvas_graph.create_text(margin_left - 5, margin_top + graph_h, text="-180", anchor="e", font=("Arial", 8), tags="grid_static")

    # Label Time [s] (Pojok Kanan Bawah)
    canvas_graph.create_text(w - margin_right, h - margin_bottom - 15, text="Time [s]", 
                             anchor="e", fill="blue", font=("Arial", 9, "bold"), tags="grid_static")
    
    # Angka 0 (Pojok Kiri Bawah)
    canvas_graph.create_text(margin_left, h - margin_bottom + 5, text="0", anchor="n", font=("Arial", 8), tags="grid_static")

def update_graph():
    """
    Menggambar garis grafik (plot) data history.
    """
    canvas_graph.delete("plot")
    canvas_graph.delete("dynamic_labels")
    
    w = canvas_graph.winfo_width()
    h = canvas_graph.winfo_height()
    
    margin_left = 50
    margin_bottom = 40
    margin_top = 20
    margin_right = 40
    
    graph_w = w - margin_left - margin_right
    graph_h = h - margin_bottom - margin_top
    cy = margin_top + (graph_h / 2)
    
    if len(data_history) < 2: return

    # Auto Scale Waktu
    t_max = data_history[-1][0]
    t_scale = max(10.0, t_max)
    
    points = []
    for t_val, theta_deg in data_history:
        # Mapping Waktu (X)
        px = margin_left + (t_val / t_scale) * graph_w
        
        # Mapping Sudut (Y)
        py = cy - (theta_deg / 180.0) * (graph_h / 2) * 0.9
        
        points.append(px)
        points.append(py)
    
    # Gambar Garis Biru Grafik
    if len(points) >= 4:
        canvas_graph.create_line(points, fill="blue", width=2, tags="plot")
        
    # Gambar Label Waktu Berjalan (Dinamis)
    label_x_pos = margin_left + (t_max / t_scale) * graph_w
    
    limit_x = w - margin_right - 60
    if label_x_pos > limit_x: label_x_pos = limit_x
        
    canvas_graph.create_text(label_x_pos, h - margin_bottom + 5, 
                             text=f"{t_max:.1f}", anchor="n", fill="blue", font=("Arial", 8), tags="dynamic_labels")

# ==========================================
# 4. KONTROL UTAMA (LOOP)
# ==========================================

def start_sim():
    global theta, omega, t, dt, running, data_history
    try:
        val_dt = float(entry_dt.get())
        val_deg = float(entry_theta.get())
        
        # --- [BARU] NORMALISASI SUDUT ---
        # Mengubah sudut berapapun (misal 300, 720, -400) 
        # Menjadi rentang antara -180 sampai 180.
        # Rumus: (sudut + 180) % 360 - 180
        
        val_deg = (val_deg + 180) % 360 - 180
        
        # Setelah dinormalisasi, baru dicek apakah 180 atau -180
        # (Sesuai permintaan: biarkan 180 tetap 0 / diam)
        
        dt = val_dt
        theta = math.radians(val_deg)
        omega = 0.0
        t = 0.0
        running = True
        data_history = []
        
        run_loop()
    except ValueError:
        print("Input Error: Masukkan angka yang valid!")

def stop_sim():
    global running
    running = False

def run_loop():
    global t, theta, running
    
    if running:
        # 1. Hitung Fisika
        rk4_step_manual()
        
        # 2. Simpan Data
        deg = math.degrees(theta)
        
        # Opsional: Normalisasi data grafik juga biar grafiknya tidak 'terbang' kalau berputar
        # Jika bandul berputar penuh (looping), grafik akan tetap di range -180 s/d 180
        deg_graph = (deg + 180) % 360 - 180
        
        data_history.append((t, deg_graph))
        
        # Hapus data lama jika terlalu banyak
        if len(data_history) > 100000: data_history.pop(0)
        
        # 3. Update Visual
        draw_pendulum(theta)
        
        if len(data_history) % 3 == 0:
            update_graph()
            
        # 4. Schedule Frame Berikutnya
        delay = int(dt * 1000)
        if delay < 1: delay = 1
        root.after(delay, run_loop)

# ==========================================
# 5. SETUP GUI (TAMPILAN)
# ==========================================

root = tk.Tk()
root.title("Simulasi Physical Pendulum (Normalized)")
root.geometry("1100x600")

# --- FRAME KIRI (ANIMASI) ---
frame_anim = tk.Frame(root, width=500, bg="white", relief="sunken", bd=2)
frame_anim.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas_anim = tk.Canvas(frame_anim, bg="white")
canvas_anim.pack(fill=tk.BOTH, expand=True)

# --- FRAME TENGAH (KONTROL) ---
frame_control = tk.Frame(root, width=200, bg="#f0f0f0")
frame_control.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=10)

tk.Label(frame_control, text="Time Sampling, dt").pack(pady=(30, 0))
entry_dt = tk.Entry(frame_control, width=10, justify='center')
entry_dt.insert(0, "0.01")
entry_dt.pack(pady=5)

tk.Label(frame_control, text="Teta awal (deg)").pack(pady=(10, 0))
entry_theta = tk.Entry(frame_control, width=10, justify='center')
entry_theta.insert(0, "90")
entry_theta.pack(pady=5)

btn_start = tk.Button(frame_control, text="Start", bg="#ddffdd", command=start_sim, width=15, height=2)
btn_start.pack(pady=(30, 10))

btn_stop = tk.Button(frame_control, text="Stop", bg="#ffdddd", command=stop_sim, width=15, height=2)
btn_stop.pack(pady=5)

use_friction = tk.BooleanVar(value=True)
tk.Checkbutton(frame_control, text="Gunakan Gesekan", variable=use_friction).pack(pady=20)

# --- FRAME KANAN (GRAFIK) ---
frame_graph = tk.Frame(root, width=500, bg="white", relief="sunken", bd=2)
frame_graph.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

tk.Label(frame_graph, text="Grafik Theta vs Time", bg="white", font=("Arial", 10, "bold")).pack()
canvas_graph = tk.Canvas(frame_graph, bg="white")
canvas_graph.pack(fill=tk.BOTH, expand=True)

# BINDING PENTING: Agar Grid Responsif saat Resize
canvas_graph.bind("<Configure>", draw_grid_labels)

# Gambar awal saat aplikasi dibuka
draw_pendulum(math.radians(90))

# Jalankan Aplikasi
root.mainloop()