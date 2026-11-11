-- =====================================================================
-- MODUL WORK ORDER (WO) - jalankan SEKALI di TiDB Cloud (SQL Editor)
-- =====================================================================

-- 1) Tabel utama WO
CREATE TABLE IF NOT EXISTS wo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  no_wo VARCHAR(20) NOT NULL,
  no_ref VARCHAR(50) NULL,
  tgl_masuk DATE NOT NULL,
  departemen_pemohon VARCHAR(100) NOT NULL,
  nama_pemohon VARCHAR(100) NOT NULL,
  seksi_tujuan VARCHAR(30) NOT NULL,
  lokasi VARCHAR(150) NOT NULL,
  id_mesin VARCHAR(50) NULL,
  judul VARCHAR(200) NOT NULL,
  deskripsi TEXT NULL,
  prioritas VARCHAR(15) NOT NULL DEFAULT 'Normal',
  status VARCHAR(20) NOT NULL DEFAULT 'Baru',
  tgl_dibutuhkan DATE NULL,
  target_selesai DATE NULL,
  assign_ke VARCHAR(100) NULL,
  keterangan TEXT NULL,
  tgl_mulai DATE NULL,
  tgl_selesai DATE NULL,
  dibuat_oleh VARCHAR(100) NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  UNIQUE KEY uq_wo_no (no_wo),
  KEY idx_wo_status (status),
  KEY idx_wo_dibuat (dibuat_oleh)
);

-- 2) Riwayat perubahan status / catatan progres per WO
CREATE TABLE IF NOT EXISTS wo_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  id_wo INT NOT NULL,
  waktu DATETIME NOT NULL,
  oleh VARCHAR(100) NOT NULL,
  status_baru VARCHAR(20) NULL,
  perubahan TEXT NULL,
  catatan TEXT NULL,
  KEY idx_wolog_wo (id_wo)
);

-- 3) Akun baru. Cek dulu struktur tabel users:  DESCRIBE users;
--    Ganti username/password sesuai kebutuhan, lalu hapus tanda "--" di depan baris INSERT.
--    Role 'WO_Manager' = pengelola WO (bisa buka halaman lain, KECUALI AI Analysis)
--    Role 'WO_User'    = akun departemen lain (HANYA bisa halaman WO)
--
-- INSERT INTO users (username, password, role) VALUES ('pengelola_wo', 'GANTI_PASSWORD_1', 'WO_Manager');
-- INSERT INTO users (username, password, role) VALUES ('wo_produksi',  'GANTI_PASSWORD_2', 'WO_User');
-- INSERT INTO users (username, password, role) VALUES ('wo_keuangan',  'GANTI_PASSWORD_3', 'WO_User');
