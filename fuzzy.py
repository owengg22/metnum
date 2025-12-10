import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec

# ==========================================
# 1. TEMPAT SETTING (VARIABEL)
# ==========================================

# --- Settingan Otak Robot (Fuzzy) ---
# SEKARANG PAKAI DERAJAT BIAR LEBIH GAMPANG DIPAHAMI
BATAS_MIRING_DERAJAT = 30.0 # Kalau miring 30 Derajat, dianggap "Miring Banget" (Bahaya)
BATAS_JATUH = 2.0           # Kecepatan jatuh (tetap rad/s biar fisika aman)
KEKUATAN_MESIN = 20.0       # Kekuatan maksimal dorongan mesin (Newton)

# --- Settingan Benda (Fisika) ---
BERAT_KERETA = 1.0         # kg
BERAT_BOLA = 0.1           # kg
PANJANG_TALI = 1.0         # meter
GRAVITASI = 9.8            # m/s^2
BATAS_TEMBOK = 3         # meter (batas layar kiri/kanan)

# --- Kondisi Robot Sekarang ---
# Data: [Posisi X, Kecepatan X, Sudut Miring (Rad), Kecepatan Jatuh]
# Kita mulai dengan miring 10 DERAJAT
sudut_awal_rad = np.radians(10) 
data_robot = np.array([0.0, 0.0, sudut_awal_rad, 0.0])


# ==========================================
# 2. FUNGSI OTAK (FUZZY LOGIC)
# ==========================================

def logika_segitiga(nilai, kiri, tengah, kanan):
    """
    Fungsi ini mengubah angka biasa menjadi angka "Fuzzy" (0 sampai 1).
    Bentuk grafiknya segitiga.
    """
    if nilai <= kiri or nilai >= kanan:
        return 0.0
    elif kiri < nilai <= tengah:
        return (nilai - kiri) / (tengah - kiri)
    elif tengah < nilai < kanan:
        return (kanan - nilai) / (kanan - tengah)
    return 0.0

def mikir_pakai_fuzzy(sudut_derajat, kecepatan_jatuh):
    """
    Ini adalah OTAK ROBOTNYA.
    Input 'sudut_derajat' sekarang menerima angka DERAJAT (misal: 15.5)
    """
    
    # --- Langkah 1: Normalisasi ---
    # Kita bandingkan sudut sekarang dengan BATAS DERAJAT
    n_sudut = np.clip(sudut_derajat / BATAS_MIRING_DERAJAT, -1, 1)
    n_kecepatan = np.clip(kecepatan_jatuh / BATAS_JATUH, -1, 1)

    # --- Langkah 2: Fuzzifikasi (Baca Sensor) ---
    sudut_NB = logika_segitiga(n_sudut, -1.5, -1.0, -0.5) # Kiri Banget
    sudut_NS = logika_segitiga(n_sudut, -1.0, -0.5, 0.0)  # Kiri Dikit
    sudut_Z  = logika_segitiga(n_sudut, -0.5, 0.0, 0.5)   # Aman/Tegak
    sudut_PS = logika_segitiga(n_sudut, 0.0, 0.5, 1.0)    # Kanan Dikit
    sudut_PB = logika_segitiga(n_sudut, 0.5, 1.0, 1.5)    # Kanan Banget

    kecepatan_Z = logika_segitiga(n_kecepatan, -0.5, 0.0, 0.5) # Kecepatan Santai
    kecepatan_PB = logika_segitiga(n_kecepatan, 0.5, 1.0, 1.5) # Jatuh ke Kanan Cepat
    kecepatan_NB = logika_segitiga(n_kecepatan, -1.5, -1.0, -0.5) # Jatuh ke Kiri Cepat
    kecepatan_PS = logika_segitiga(n_kecepatan, 0.0, 0.5, 1.0)
    kecepatan_NS = logika_segitiga(n_kecepatan, -1.0, -0.5, 0.0)

    # --- Langkah 3: Aturan Main (Rule Base) ---
    # Aturannya sederhana:
    # Kalau miring kanan -> Dorong kanan (biar bawahnya ngejar atasnya)
    
    keputusan_PB = max(min(sudut_PB, kecepatan_Z), min(sudut_PS, kecepatan_PB)) # Dorong Kanan Kuat
    keputusan_PS = max(min(sudut_PS, kecepatan_Z), min(sudut_Z, kecepatan_PS))  # Dorong Kanan Pelan
    keputusan_Z  = min(sudut_Z, kecepatan_Z)                                    # Diam
    keputusan_NS = max(min(sudut_NS, kecepatan_Z), min(sudut_Z, kecepatan_NS))  # Dorong Kiri Pelan
    keputusan_NB = max(min(sudut_NB, kecepatan_Z), min(sudut_NS, kecepatan_NB)) # Dorong Kiri Kuat

    # --- Langkah 4: Defuzzifikasi (Hitung Rata-rata) ---
    total_bobot = keputusan_NB + keputusan_NS + keputusan_Z + keputusan_PS + keputusan_PB
    
    if total_bobot == 0:
        return 0.0
        
    hasil_atas = (keputusan_NB * -KEKUATAN_MESIN) + \
                 (keputusan_NS * -KEKUATAN_MESIN * 0.5) + \
                 (keputusan_Z  * 0) + \
                 (keputusan_PS * KEKUATAN_MESIN * 0.5) + \
                 (keputusan_PB * KEKUATAN_MESIN)
                 
    return hasil_atas / total_bobot


# ==========================================
# 3. FUNGSI FISIKA (RUMUS GERAK)
# ==========================================

def hitung_gerakan_fisika(data_sekarang, gaya_dorong, selisih_waktu):
    """
    Ini bagian hitung-hitungan fisika. 
    Fisika tetap menggunakan RADIAN karena rumus sin/cos butuh radian.
    """
    x, v, theta, omega = data_sekarang
    
    sin_t = np.sin(theta)
    cos_t = np.cos(theta)
    
    # --- Rumus Fisika Mulai ---
    penyebut = PANJANG_TALI * (BERAT_KERETA + BERAT_BOLA * (1 - cos_t**2))
    
    percepatan_sudut = (GRAVITASI * (BERAT_KERETA + BERAT_BOLA) * sin_t - 
                        cos_t * (gaya_dorong + BERAT_BOLA * PANJANG_TALI * omega**2 * sin_t)) / penyebut
                        
    percepatan_kereta = (gaya_dorong + BERAT_BOLA * PANJANG_TALI * (omega**2 * sin_t - percepatan_sudut * cos_t)) / (BERAT_KERETA + BERAT_BOLA)
    # --- Rumus Fisika Selesai ---
    
    # Update data (Metode Euler)
    x_baru = x + v * selisih_waktu
    v_baru = v + percepatan_kereta * selisih_waktu
    theta_baru = theta + omega * selisih_waktu
    omega_baru = omega + percepatan_sudut * selisih_waktu
    
    # Cek Tembok (Biar gak kabur dari layar)
    if x_baru < -BATAS_TEMBOK:
        x_baru = -BATAS_TEMBOK
        if v_baru < 0: v_baru = 0
    elif x_baru > BATAS_TEMBOK:
        x_baru = BATAS_TEMBOK
        if v_baru > 0: v_baru = 0
        
    return np.array([x_baru, v_baru, theta_baru, omega_baru])




fig = plt.figure(figsize=(10, 6))
layout = GridSpec(3, 3, figure=fig)

#animasi
ax_kartun = fig.add_subplot(layout[:, 0]) 
ax_kartun.set_title("Visualisasi Robot\n(Klik Kotak/Bola untuk Geser)")
ax_kartun.set_xlim(-2.5, 2.5)
ax_kartun.set_ylim(-1, 2)
# --- FIX: BIAR GAMBAR TIDAK BENGKOK/GEPENG ---
ax_kartun.set_aspect('equal') 
ax_kartun.grid(True, linestyle='--')

# Bikin gambar elemen robot
kotak_biru = plt.Rectangle((0,0), 0.5, 0.3, fc='cyan', ec='black') 
garis_tali, = ax_kartun.plot([], [], 'black', linewidth=3)       
bola_merah, = ax_kartun.plot([], [], 'ro', markersize=12)        
ax_kartun.add_patch(kotak_biru)

# --- Kotak Kanan (Grafik Data) ---
ax_grafik1 = fig.add_subplot(layout[0, 1:]) # Kanan Atas
ax_grafik2 = fig.add_subplot(layout[1, 1:]) # Kanan Tengah
ax_grafik3 = fig.add_subplot(layout[2, 1:]) # Kanan Bawah

garis_sudut, = ax_grafik1.plot([], [], 'b-')
garis_gaya, = ax_grafik3.plot([], [], 'r-')

ax_grafik1.set_title("Kemiringan (DERAJAT)") # Judul diganti
ax_grafik1.set_ylim(-45, 45)                 # Batas grafik jadi -45 sampai 45 derajat
ax_grafik1.grid(True)

ax_grafik3.set_title("Kekuatan Mesin (Newton)")
ax_grafik3.set_ylim(-25, 25)

# Variabel pembantu untuk grafik
list_sudut = []
list_gaya = []

# Status apakah mouse lagi narik sesuatu?
sedang_tarik_kereta = False
sedang_tarik_bandul = False

# --- FUNGSI UPDATE GAMBAR ---
def update_animasi(frame):
    global data_robot, sedang_tarik_kereta, sedang_tarik_bandul
    
    # Ambil data (theta masih dalam radian di sini)
    x, v, theta_rad, omega = data_robot
    
    # Ubah ke DERAJAT untuk dikirim ke Otak Fuzzy & Grafik
    theta_deg = np.degrees(theta_rad)
    
    # 1. Mikir & Fisika
    if not sedang_tarik_kereta and not sedang_tarik_bandul:
        # Kirim data DERAJAT ke otak fuzzy
        gaya = mikir_pakai_fuzzy(theta_deg, omega)
        data_robot = hitung_gerakan_fisika(data_robot, gaya, 0.02)
    else:
        gaya = 0
        data_robot[1] = 0 # Kecepatan Kereta 0
        data_robot[3] = 0 # Kecepatan Sudut 0

    # 2. Gambar ulang posisi robot (Visualisasi butuh radian buat sin/cos)
    ujung_atas_x = data_robot[0] + PANJANG_TALI * np.sin(data_robot[2])
    ujung_atas_y = PANJANG_TALI * np.cos(data_robot[2])
    
    kotak_biru.set_x(data_robot[0] - 0.25)
    kotak_biru.set_y(-0.15)
    garis_tali.set_data([data_robot[0], ujung_atas_x], [0, ujung_atas_y])
    bola_merah.set_data([ujung_atas_x], [ujung_atas_y])
    
    # 3. Update Grafik (Simpan data DERAJAT)
    list_sudut.append(np.degrees(data_robot[2]))
    list_gaya.append(gaya)
    
    if len(list_sudut) > 100:
        list_sudut.pop(0)
        list_gaya.pop(0)
        
    garis_sudut.set_data(range(len(list_sudut)), list_sudut)
    ax_grafik1.set_xlim(0, 100)
    
    garis_gaya.set_data(range(len(list_gaya)), list_gaya)
    ax_grafik3.set_xlim(0, 100)
    
    return kotak_biru, garis_tali, bola_merah, garis_sudut, garis_gaya

#interaksi
def saat_klik(event):
    global sedang_tarik_kereta, sedang_tarik_bandul
    if event.inaxes != ax_kartun: return

    ujung_x = data_robot[0] + PANJANG_TALI * np.sin(data_robot[2])
    ujung_y = PANJANG_TALI * np.cos(data_robot[2])

    jarak_ke_bola = np.sqrt((event.xdata - ujung_x)**2 + (event.ydata - ujung_y)**2)
    jarak_ke_kereta = np.abs(event.xdata - data_robot[0])
    tinggi_klik = np.abs(event.ydata)

    if jarak_ke_bola < 0.4:  
        sedang_tarik_bandul = True
    elif jarak_ke_kereta < 0.6 and tinggi_klik < 0.4: 
        sedang_tarik_kereta = True

def saat_lepas(event):
    global sedang_tarik_kereta, sedang_tarik_bandul
    sedang_tarik_kereta = False
    sedang_tarik_bandul = False

def saat_geser(event):
    global data_robot
    if event.inaxes != ax_kartun: return

    # Mode 1: Geser Kereta
    if sedang_tarik_kereta:
        data_robot[0] = np.clip(event.xdata, -BATAS_TEMBOK, BATAS_TEMBOK)
    
    # Mode 2: Putar Sudut Bandul 
    if sedang_tarik_bandul:
        # Kita hanya baca geseran X (Kiri-Kanan) relatif terhadap kereta
        selisih_x = event.xdata - data_robot[0]
        
        # Matematika: Cari sudut dari pergeseran mendatar
        # Pakai np.clip biar aman gak error matematikanya
        ratio = np.clip(selisih_x / PANJANG_TALI, -0.99, 0.99)
        
        sudut_baru = np.arcsin(ratio) #new sudut wak
        data_robot[2] = sudut_baru

# Sambungkan mouse ke kanvas
fig.canvas.mpl_connect('button_press_event', saat_klik)
fig.canvas.mpl_connect('button_release_event', saat_lepas)
fig.canvas.mpl_connect('motion_notify_event', saat_geser)

# Jalankan Animasi
ani = animation.FuncAnimation(fig, update_animasi, interval=20, blit=False)
plt.tight_layout()
plt.show()