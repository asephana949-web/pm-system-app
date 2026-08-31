import os
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import pymysql
import json
from google import genai

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'kunci_rahasia_sangat_aman')
CORS(app)

# ==========================================
# KONFIGURASI GEMINI AI (SDK BARU: google-genai)
# ==========================================
# Key dibaca dari Environment Variable GEMINI_API_KEY di Vercel.
# Jangan pernah menuliskan key asli langsung di file ini!
client_ai = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
# Alias resmi Google yang otomatis mengikuti model Flash stabil terbaru,
# supaya kode ini tidak perlu diubah lagi setiap Google memensiunkan versi model.
MODEL_AI = "gemini-flash-latest"

# ==========================================
# KONFIGURASI DATABASE (dibaca dari Environment Variable di Vercel)
# ==========================================
DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT', 4000)),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
    'ssl': {
        'ssl_verify_cert': True,
        'ssl_verify_identity': True
    },
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# ==========================================
# ROUTE HALAMAN & LOGIN
# ==========================================
@app.route('/', methods=['GET'])
def index():
    if 'loggedin' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
                user = cursor.fetchone()
                if user:
                    session['loggedin'] = True
                    session['username'] = user['username']
                    session['role'] = user['role']
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('login.html', error="Username atau Password salah!")
        finally:
            conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/machine-profile')
def machine_profile():
    if 'loggedin' not in session: return redirect(url_for('login'))
    return render_template('machine_profile.html')

@app.route('/pm-schedule')
def pm_schedule():
    if 'loggedin' not in session: return redirect(url_for('login'))
    return render_template('pm_schedule.html')

@app.route('/machine-history')
def machine_history():
    if 'loggedin' not in session: return redirect(url_for('login'))
    return render_template('machine_history.html')

@app.route('/ai-analysis')
def ai_analysis():
    if 'loggedin' not in session: return redirect(url_for('login'))
    if session['role'] != 'Admin':
        return "Akses Ditolak!"
    return render_template('ai_analysis.html')

# ==========================================
# API BARU: GENERATE GEMINI AI (ANALISIS)
# ==========================================
@app.route('/api/generate-ai', methods=['POST'])
def generate_ai_diagnosis():
    if 'loggedin' not in session: return jsonify({"error": "Belum login"}), 403
    data = request.json
    vib = data.get('vibrasi')
    gejala = data.get('gejala')
    
    # Prompt khusus yang merubah Gemini menjadi Pakar Vibrasi
    prompt = f"""
    Anda adalah seorang insinyur Pakar Analisis Vibrasi Mesin Industri (berpedoman pada ISO 10816-3 & Mobius Institute).
    Sebuah mesin menunjukkan nilai vibrasi overall sebesar {vib} mm/s (berbasis Rigid Foundation).
    Gejala spektrum (FFT) dominan yang diamati oleh teknisi di lapangan adalah: "{gejala}".

    Tugas Anda:
    1. Tentukan Status ISO 10816-3 (Pilih salah satu persis seperti ini: "Zone A/B (Aman)", "Zone C (Waspada)", atau "Zone D (Berbahaya)").
    2. Berikan "Indikasi" masalah (maksimal 2 kalimat) berdasarkan perpaduan nilai vibrasi dan gejala FFT tersebut.
    3. Berikan "Rekomendasi" teknis (maksimal 2 kalimat) mengenai tindakan maintenance korektif apa yang harus segera dilakukan mekanik.

    PENTING: Output Anda HARUS murni berbentuk JSON format seperti di bawah ini, tanpa teks pengantar, dan tanpa penanda markdown (```json).
    {{
        "status_iso": "Zone C (Waspada)",
        "indikasi": "Terdapat unbalance ...",
        "rekomendasi": "Lakukan pembersihan ..."
    }}
    """
    
    # Retry otomatis khusus untuk error 503 (model Gemini sedang sibuk/high demand).
    # Percobaan ke-1: langsung. Percobaan ke-2: tunggu 2 detik. Percobaan ke-3: tunggu 4 detik.
    MAX_PERCOBAAN = 3
    error_terakhir = None

    for percobaan in range(1, MAX_PERCOBAAN + 1):
        try:
            response = client_ai.models.generate_content(
                model=MODEL_AI,
                contents=prompt
            )
            ai_teks = response.text.strip()

            # Membersihkan format markdown jika AI membandel
            if ai_teks.startswith("```json"): ai_teks = ai_teks[7:-3].strip()
            elif ai_teks.startswith("```"): ai_teks = ai_teks[3:-3].strip()

            hasil_json = json.loads(ai_teks)
            return jsonify({"status": "success", "data": hasil_json})

        except Exception as e:
            error_terakhir = e
            pesan_error = str(e)

            # Cek apakah ini error 503/UNAVAILABLE (server Gemini sedang sibuk) -> layak dicoba ulang.
            # Kalau errornya jenis lain (misal API key salah, JSON tidak valid), langsung berhenti, tidak perlu retry.
            sedang_sibuk = ("503" in pesan_error) or ("UNAVAILABLE" in pesan_error) or ("overloaded" in pesan_error.lower())

            if sedang_sibuk and percobaan < MAX_PERCOBAAN:
                jeda_detik = 2 * percobaan  # 2 detik, lalu 4 detik
                time.sleep(jeda_detik)
                continue  # coba lagi dari awal loop
            else:
                # Bukan error 503, atau sudah percobaan terakhir -> menyerah dan lapor ke frontend.
                break

    pesan_gagal = "Model AI sedang mengalami permintaan tinggi (sibuk). Sudah dicoba ulang beberapa kali, silakan coba lagi dalam beberapa menit."
    if error_terakhir and not (("503" in str(error_terakhir)) or ("UNAVAILABLE" in str(error_terakhir))):
        pesan_gagal = str(error_terakhir)

    return jsonify({"status": "error", "message": pesan_gagal}), 500

# ==========================================
# API: MASTER MESIN
# ==========================================
@app.route('/api/master-mesin', methods=['GET'])
def get_master_mesin():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM master_mesin ORDER BY area, id_mesin")
            return jsonify(cursor.fetchall())
    finally:
        conn.close()

@app.route('/api/master-mesin/<id_mesin>', methods=['PUT'])
def update_master_mesin(id_mesin):
    if session.get('role') != 'Admin': return jsonify({"status": "error", "message": "Akses Ditolak!"}), 403
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """UPDATE master_mesin 
                     SET tipe_mesin=%s, tahun_instalasi=%s, daya_motor=%s, rpm=%s, kode_bearing=%s, link_dokumen=%s 
                     WHERE id_mesin=%s"""
            cursor.execute(sql, (
                data.get('tipe_mesin'), data.get('tahun_instalasi'), data.get('daya_motor'), 
                data.get('rpm'), data.get('kode_bearing'), data.get('link_dokumen'), id_mesin
            ))
            conn.commit()
            return jsonify({"status": "success", "message": "Spesifikasi Teknis berhasil diperbarui!"})
    finally:
        conn.close()

# ==========================================
# API: JADWAL PM 
# ==========================================
@app.route('/api/jadwal', methods=['GET', 'POST'])
def handle_jadwal():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                cursor.execute("SELECT * FROM jadwal_pm ORDER BY id DESC")
                return jsonify(cursor.fetchall())
            elif request.method == 'POST':
                if 'loggedin' not in session: return jsonify({"error": "Belum login"}), 403
                data = request.json
                sql = """INSERT INTO jadwal_pm (no_task, id_mesin, area, jenis_pekerjaan, tgl_rencana, periode, status, dibuat_oleh) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (data.get('no_task'), data.get('id_mesin'), data.get('area'), data.get('jenis_pekerjaan'), data.get('tgl_rencana'), data.get('periode'), 'Scheduled', session['username']))
                conn.commit()
                return jsonify({"status": "success", "message": "Jadwal berhasil ditambahkan!"})
    finally:
        conn.close()

@app.route('/api/jadwal/<int:id>/selesai', methods=['PUT'])
def selesaikan_jadwal(id):
    if 'loggedin' not in session: return jsonify({"error": "Belum login"}), 403
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM jadwal_pm WHERE id=%s", (id,))
            jadwal = cursor.fetchone()
            if not jadwal: return jsonify({"status": "error", "message": "Jadwal tidak ditemukan!"}), 404

            cursor.execute("UPDATE jadwal_pm SET status='Completed' WHERE id=%s", (id,))
            
            is_dt = data.get('is_downtime', 'Tidak')
            dt_jam = data.get('downtime_jam', 0)
            if not dt_jam or str(dt_jam).strip() == '': dt_jam = 0
            
            sql_history = """INSERT INTO riwayat_perbaikan (tgl_eksekusi, nama_alat, tipe_pekerjaan, penyebab_kerusakan, uraian_pekerjaan, sparepart_terpakai, durasi_jam, dibuat_oleh, is_downtime, downtime_jam) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql_history, (data.get('tgl_eksekusi'), jadwal['id_mesin'], 'Preventive', data.get('penyebab'), data.get('uraian'), data.get('sparepart'), data.get('durasi'), session['username'], is_dt, dt_jam))
            conn.commit()
            return jsonify({"status": "success", "message": "Pekerjaan selesai & masuk ke History dengan rincian Downtime!"})
    finally:
        conn.close()

@app.route('/api/jadwal/<int:id>', methods=['PUT', 'DELETE'])
def manage_jadwal(id):
    if session.get('role') != 'Admin': return jsonify({"status": "error", "message": "Akses Ditolak!"}), 403
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'PUT':
                data = request.json
                sql = """UPDATE jadwal_pm SET no_task=%s, id_mesin=%s, area=%s, jenis_pekerjaan=%s, tgl_rencana=%s, periode=%s, status=%s WHERE id=%s"""
                cursor.execute(sql, (data.get('no_task'), data.get('id_mesin'), data.get('area'), data.get('jenis_pekerjaan'), data.get('tgl_rencana'), data.get('periode'), data.get('status'), id))
                pesan = "Data jadwal diubah!"
            elif request.method == 'DELETE':
                cursor.execute("DELETE FROM jadwal_pm WHERE id = %s", (id,))
                pesan = "Jadwal dihapus!"
            conn.commit()
            return jsonify({"status": "success", "message": pesan})
    finally:
        conn.close()

# ==========================================
# API: RIWAYAT PERBAIKAN
# ==========================================
@app.route('/api/riwayat', methods=['GET', 'POST'])
def manage_riwayat_all():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                cursor.execute("SELECT * FROM riwayat_perbaikan ORDER BY id DESC")
                return jsonify(cursor.fetchall())
            elif request.method == 'POST':
                if 'loggedin' not in session: return jsonify({"error": "Belum login"}), 403
                data = request.json
                
                is_dt = data.get('is_downtime', 'Tidak')
                dt_jam = data.get('downtime_jam', 0)
                if not dt_jam or str(dt_jam).strip() == '': dt_jam = 0
                    
                sql = """INSERT INTO riwayat_perbaikan (tgl_eksekusi, nama_alat, tipe_pekerjaan, penyebab_kerusakan, uraian_pekerjaan, sparepart_terpakai, durasi_jam, dibuat_oleh, is_downtime, downtime_jam) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (data.get('tgl'), data.get('alat'), data.get('tipe'), data.get('penyebab'), data.get('uraian'), data.get('sparepart'), data.get('durasi'), session['username'], is_dt, dt_jam))
                conn.commit()
                return jsonify({"status": "success", "message": "Riwayat berhasil disimpan!"})
    finally:
        conn.close()

@app.route('/api/riwayat/<int:id>', methods=['PUT', 'DELETE'])
def manage_riwayat_id(id):
    if session.get('role') != 'Admin': return jsonify({"status": "error", "message": "Akses Ditolak!"}), 403
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'PUT':
                data = request.json
                is_dt = data.get('is_downtime', 'Tidak')
                dt_jam = data.get('downtime_jam', 0)
                if not dt_jam or str(dt_jam).strip() == '': dt_jam = 0
                    
                sql = """UPDATE riwayat_perbaikan SET tgl_eksekusi=%s, nama_alat=%s, tipe_pekerjaan=%s, penyebab_kerusakan=%s, uraian_pekerjaan=%s, sparepart_terpakai=%s, durasi_jam=%s, is_downtime=%s, downtime_jam=%s WHERE id=%s"""
                cursor.execute(sql, (data.get('tgl'), data.get('alat'), data.get('tipe'), data.get('penyebab'), data.get('uraian'), data.get('sparepart'), data.get('durasi'), is_dt, dt_jam, id))
                pesan = "Data riwayat diubah!"
            elif request.method == 'DELETE':
                cursor.execute("DELETE FROM riwayat_perbaikan WHERE id = %s", (id,))
                pesan = "Riwayat dihapus!"
            conn.commit()
            return jsonify({"status": "success", "message": pesan})
    finally:
        conn.close()

# ==========================================
# API: LOG AI ANALYSIS
# ==========================================
@app.route('/api/ai-analysis', methods=['GET', 'POST'])
def handle_ai_analysis():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                id_mesin = request.args.get('id_mesin')
                if id_mesin:
                    cursor.execute("SELECT * FROM log_ai_analysis WHERE id_mesin = %s ORDER BY tgl_analisis ASC", (id_mesin,))
                else:
                    cursor.execute("SELECT * FROM log_ai_analysis ORDER BY tgl_analisis ASC")
                return jsonify(cursor.fetchall())
            
            elif request.method == 'POST':
                if 'loggedin' not in session: return jsonify({"error": "Belum login"}), 403
                data = request.json
                sql = """INSERT INTO log_ai_analysis (id_mesin, tgl_analisis, status_iso, nilai_vibrasi, indikasi, diagnosis_lengkap, rekomendasi, file_pdf, file_gambar) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    data.get('id_mesin'), data.get('tgl_analisis'), data.get('status_iso'), 
                    data.get('nilai_vibrasi'), data.get('indikasi'), data.get('diagnosis_lengkap'), 
                    data.get('rekomendasi'), data.get('file_pdf'), data.get('file_gambar')
                ))
                conn.commit()
                return jsonify({"status": "success", "message": "Log Analisis AI berhasil disimpan secara permanen!"})
    finally:
        conn.close()

@app.route('/api/ai-analysis/<int:id>', methods=['PUT', 'DELETE'])
def manage_ai_analysis_id(id):
    if session.get('role') != 'Admin': return jsonify({"status": "error", "message": "Akses Ditolak!"}), 403
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'PUT':
                data = request.json
                sql = """UPDATE log_ai_analysis 
                         SET indikasi=%s, diagnosis_lengkap=%s, rekomendasi=%s 
                         WHERE id=%s"""
                cursor.execute(sql, (data.get('indikasi'), data.get('diagnosis'), data.get('rekomendasi'), id))
                pesan = "Data Log Diagnosa AI berhasil diperbarui!"
            elif request.method == 'DELETE':
                cursor.execute("DELETE FROM log_ai_analysis WHERE id = %s", (id,))
                pesan = "Data Log AI berhasil dihapus permanen!"
            conn.commit()
            return jsonify({"status": "success", "message": pesan})
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 Server Backend PM System Berjalan di: [http://127.0.0.1:5000](http://127.0.0.1:5000)")
    app.run(debug=True, port=5000)