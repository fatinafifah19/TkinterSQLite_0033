import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "prediksi_diabetes.db"


# Membuat database dan tabel
def buat_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pasien TEXT NOT NULL,
            usia INTEGER NOT NULL,
            gula_darah REAL NOT NULL,
            bmi REAL NOT NULL,
            riwayat_ortu TEXT NOT NULL,
            hasil_prediksi TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Fungsi prediksi risiko diabetes
def prediksi_diabetes(gula, bmi, riwayat):
    if gula >= 200:
        if bmi >= 30 or riwayat == "Ya":
            return "Sangat Tinggi"
        return "Tinggi"

    elif 140 <= gula < 200:
        if bmi >= 30 and riwayat == "Ya":
            return "Tinggi"
        return "Sedang"

    elif gula < 140:
        if bmi >= 30:
            if riwayat == "Ya":
                return "Sedang"
            return "Waspada"

        elif riwayat == "Ya":
            return "Waspada"

        else:
            return "Rendah"


# Menyimpan data dan menampilkan hasil prediksi
def simpan_prediksi():
    nama = entry_nama.get().strip()
    usia = entry_usia.get().strip()
    gula = entry_gula.get().strip().replace(",", ".")
    bmi = entry_bmi.get().strip().replace(",", ".")
    riwayat = combo_riwayat.get()

    # Validasi input
    if not nama or not usia or not gula or not bmi:
        messagebox.showwarning(
            "Peringatan",
            "Semua data harus diisi!"
        )
        return

    try:
        usia = int(usia)
        gula = float(gula)
        bmi = float(bmi)
    except ValueError:
        messagebox.showwarning(
            "Peringatan",
            "Usia harus bilangan bulat, sedangkan gula darah dan BMI harus berupa angka!"
        )
        return

    if usia < 1 or usia > 120:
        messagebox.showwarning(
            "Peringatan",
            "Usia harus antara 1 sampai 120 tahun!"
        )
        return

    if gula <= 0 or gula > 1000:
        messagebox.showwarning(
            "Peringatan",
            "Gula darah harus lebih dari 0 dan maksimal 1000 mg/dL!"
        )
        return

    if bmi <= 0 or bmi > 100:
        messagebox.showwarning(
            "Peringatan",
            "BMI harus lebih dari 0 dan maksimal 100!"
        )
        return

    if riwayat not in ("Ya", "Tidak"):
        messagebox.showwarning(
            "Peringatan",
            "Pilih riwayat diabetes orang tua!"
        )
        return

    hasil = prediksi_diabetes(gula, bmi, riwayat)

    # Menyimpan data ke SQLite
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pasien
            (nama_pasien, usia, gula_darah, bmi,
             riwayat_ortu, hasil_prediksi)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nama, usia, gula, bmi, riwayat, hasil))

        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Kesalahan Database",
            str(error)
        )
        return

    # Warna hasil prediksi
    warna = {
        "Rendah": "green",
        "Waspada": "yellow green",
        "Sedang": "orange",
        "Tinggi": "red",
        "Sangat Tinggi": "purple"
    }

    label_hasil.config(
        text="Hasil Prediksi: " + hasil,
        fg=warna[hasil]
    )

    tampilkan_data()

    messagebox.showinfo(
        "Berhasil",
        "Data pasien berhasil disimpan!"
    )


# Menampilkan seluruh riwayat pasien
def tampilkan_data():
    for item in tabel.get_children():
        tabel.delete(item)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, nama_pasien, usia, gula_darah,
           bmi, riwayat_ortu, hasil_prediksi
    FROM pasien
    ORDER BY id ASC
""")

    data = cursor.fetchall()
    conn.close()

    for baris in data:
        tabel.insert("", tk.END, values=baris)


# Membersihkan form
def bersihkan_form():
    entry_nama.delete(0, tk.END)
    entry_usia.delete(0, tk.END)
    entry_gula.delete(0, tk.END)
    entry_bmi.delete(0, tk.END)
    combo_riwayat.set("Tidak")

    label_hasil.config(
        text="Hasil Prediksi: -",
        fg="black"
    )


# Membuat database
buat_database()

# Membuat jendela aplikasi
root = tk.Tk()
root.title("Aplikasi Prediksi Risiko Diabetes")
root.geometry("950x650")
root.configure(bg="#f0f4f8")

# Judul aplikasi
judul = tk.Label(
    root,
    text="APLIKASI PREDIKSI RISIKO DIABETES",
    font=("Arial", 18, "bold"),
    bg="#f0f4f8",
    fg="#17365d"
)
judul.pack(pady=15)

# Form input
frame_form = ttk.LabelFrame(
    root,
    text="Form Data Pasien",
    padding=15
)
frame_form.pack(fill="x", padx=20, pady=5)

# Nama pasien
ttk.Label(
    frame_form,
    text="Nama Pasien"
).grid(row=0, column=0, padx=10, pady=8, sticky="w")

entry_nama = ttk.Entry(frame_form, width=30)
entry_nama.grid(row=0, column=1, padx=10, pady=8)

# Usia
ttk.Label(
    frame_form,
    text="Usia (tahun)"
).grid(row=0, column=2, padx=10, pady=8, sticky="w")

entry_usia = ttk.Entry(frame_form, width=20)
entry_usia.grid(row=0, column=3, padx=10, pady=8)

# Gula darah
ttk.Label(
    frame_form,
    text="Gula Darah (mg/dL)"
).grid(row=1, column=0, padx=10, pady=8, sticky="w")

entry_gula = ttk.Entry(frame_form, width=30)
entry_gula.grid(row=1, column=1, padx=10, pady=8)

# BMI
ttk.Label(
    frame_form,
    text="BMI"
).grid(row=1, column=2, padx=10, pady=8, sticky="w")

entry_bmi = ttk.Entry(frame_form, width=20)
entry_bmi.grid(row=1, column=3, padx=10, pady=8)

# Riwayat diabetes orang tua
ttk.Label(
    frame_form,
    text="Riwayat Diabetes Orang Tua"
).grid(row=2, column=0, padx=10, pady=8, sticky="w")

combo_riwayat = ttk.Combobox(
    frame_form,
    values=["Ya", "Tidak"],
    state="readonly",
    width=27
)
combo_riwayat.grid(row=2, column=1, padx=10, pady=8)
combo_riwayat.set("Tidak")

# Tombol
frame_tombol = tk.Frame(root, bg="#f0f4f8")
frame_tombol.pack(pady=10)

ttk.Button(
    frame_tombol,
    text="Simpan & Prediksi",
    command=simpan_prediksi
).grid(row=0, column=0, padx=5)

ttk.Button(
    frame_tombol,
    text="Lihat Data",
    command=tampilkan_data
).grid(row=0, column=1, padx=5)

ttk.Button(
    frame_tombol,
    text="Bersihkan",
    command=bersihkan_form
).grid(row=0, column=2, padx=5)

# Label hasil prediksi
label_hasil = tk.Label(
    root,
    text="Hasil Prediksi: -",
    font=("Arial", 14, "bold"),
    bg="#f0f4f8",
    fg="black"
)
label_hasil.pack(pady=10)

# Tabel riwayat pasien
frame_tabel = ttk.LabelFrame(
    root,
    text="Riwayat Data Pasien",
    padding=10
)
frame_tabel.pack(fill="both", expand=True, padx=20, pady=10)

kolom = (
    "no",
    "nama_pasien",
    "usia",
    "gula_darah",
    "bmi",
    "riwayat_ortu",
    "hasil_prediksi"
)

tabel = ttk.Treeview(
    frame_tabel,
    columns=kolom,
    show="headings"
)

judul_kolom = [
    "No",
    "Nama Pasien",
    "Usia",
    "Gula Darah",
    "BMI",
    "Riwayat Ortu",
    "Hasil Prediksi"
]

for nama_kolom, teks in zip(kolom, judul_kolom):
    tabel.heading(nama_kolom, text=teks)
    tabel.column(nama_kolom, width=115, anchor="center")

tabel.pack(fill="both", expand=True)

# Menampilkan data yang sudah tersimpan
tampilkan_data()

# Menjalankan aplikasi
root.mainloop()