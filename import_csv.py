import csv
import pymysql

# Konfigurasi Database
conn = pymysql.connect(host='localhost', user='root', password='', db='db_pm_system')
cursor = conn.cursor()

def generate_area_code(area_name):
    if not area_name: return "UMUM"
    words = area_name.replace('-', ' ').split()
    code = "".join([w[0].upper() for w in words])
    if len(code) == 1: code = area_name[:3].upper()
    return code

print("🚀 Memulai import data mode Ultra Cerdas (Deteksi Baris & Toleransi Judul)...")

try:
    cursor.execute("TRUNCATE TABLE master_mesin")
    
    with open('Daftar Peralatan Teknik Revisi 2.csv', mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        
        header_found = False
        idx_nama, idx_kategori, idx_area, idx_wilayah = -1, -1, -1, -1
        
        # 1. Cari baris yang benar-benar berisi Header/Judul Kolom
        for row in reader:
            clean_row = [str(col).strip().lower() for col in row] # Ubah ke huruf kecil semua
            
            for i, col in enumerate(clean_row):
                if "nama" in col: idx_nama = i
                elif "kategori" in col: idx_kategori = i
                elif "area" in col: idx_area = i
                elif "wilayah" in col: idx_wilayah = i
                
            # Jika minimal kolom Nama ketemu, kita anggap itu adalah baris headernya
            if idx_nama != -1: 
                header_found = True
                print(f"🔍 Header otomatis terdeteksi! (Nama: Kolom {idx_nama+1}, Area: {idx_area+1}, Wilayah: {idx_wilayah+1}, Kategori: {idx_kategori+1})")
                break
                
        if not header_found:
            print("❌ Gagal! Tidak dapat menemukan kolom yang mengandung kata 'Nama'. Pastikan file CSV tidak kosong.")
            exit()
            
        current_area = "UMUM"
        current_wilayah = "UMUM"
        current_kategori = "Desirable"
        counter = 1

        # 2. Mulai baca datanya
        for row in reader:
            if len(row) <= idx_nama: continue

            # Ambil data dengan aman (jika kolomnya ada)
            nama_mesin = row[idx_nama].strip() if idx_nama != -1 else ''
            if not nama_mesin: # Lewati baris jika nama mesin kosong
                continue
                
            # Logika "Forward-Fill" (Pakai data sebelumnya jika cell di-merge/dikosongi)
            if idx_area != -1 and len(row) > idx_area:
                area_csv = row[idx_area].strip()
                if area_csv:
                    if current_area != area_csv:
                        counter = 1 # Reset nomor ID jika pindah area
                    current_area = area_csv

            if idx_wilayah != -1 and len(row) > idx_wilayah:
                wilayah_csv = row[idx_wilayah].strip()
                if wilayah_csv:
                    current_wilayah = wilayah_csv

            if idx_kategori != -1 and len(row) > idx_kategori:
                kategori_csv = row[idx_kategori].strip()
                if kategori_csv:
                    current_kategori = kategori_csv

            # Menentukan Tipe Mesin untuk Prefix ID (contoh: PMP, MTR)
            prefix = "MSC"
            nama_lower = nama_mesin.lower()
            if "motor" in nama_lower: prefix = "MTR"
            elif "pump" in nama_lower or "pompa" in nama_lower: prefix = "PMP"
            elif "roll" in nama_lower: prefix = "RLL"
            elif "chest" in nama_lower or "agt" in nama_lower: prefix = "AGT"
            elif "fan" in nama_lower or "blower" in nama_lower: prefix = "FAN"
            elif "conveyor" in nama_lower: prefix = "CNV"
            elif "tdr" in nama_lower or "deflaker" in nama_lower or "refiner" in nama_lower: prefix = "RFN"

            area_code = generate_area_code(current_area)
            id_mesin = f"{prefix}-{area_code}-{counter:03d}"
            counter += 1

            # Masukkan ke Database
            cursor.execute("""
                INSERT IGNORE INTO master_mesin (id_mesin, nama_mesin, area, kategori, wilayah) 
                VALUES (%s, %s, %s, %s, %s)
            """, (id_mesin, nama_mesin, current_area, current_kategori, current_wilayah))
            
    conn.commit()
    print("✅ Berhasil! Ratusan data mesin telah tersimpan ke database beserta Wilayah dan Kategorinya.")
except Exception as e:
    print(f"❌ Terjadi kesalahan saat membaca database: {e}")
finally:
    conn.close()