# -*- coding: utf-8 -*-
"""
MODUL WORK ORDER (WO) TERPUSAT
==============================
Dipasang ke app.py lewat dua baris saja:

    from wo_module import init_wo
    init_wo(app, get_db_connection)

Halaman  : /wo/dashboard  /wo  /wo/baru
API      : /api/wo  /api/wo/<id>  /api/wo/stats  /api/wo/pilihan

Jenis akun (kolom `role` di tabel users; huruf besar/kecil tidak berpengaruh):
  - WO_User     : akun departemen lain. HANYA boleh halaman & API WO.
                  Hanya melihat/membatalkan WO miliknya sendiri.
  - WO_Manager  : pengelola WO. Boleh ubah status/prioritas/penugasan WO dan
                  boleh membuka halaman lain di aplikasi, kecuali AI Analysis
                  (halaman itu sudah khusus Admin di app.py).
  - Admin       : sama seperti pengelola WO.
  - role lain (preventive, perencanaan, dst): boleh MELIHAT dashboard & daftar WO,
                  tidak bisa mengubah. Tambahkan username ke WO_USERNAMES_PENGELOLA
                  bila ada yang perlu bisa mengubah status (mis. kasek bengkel).
"""
import datetime
import pymysql
from flask import render_template, request, jsonify, redirect, url_for, session

# ----------------------------------------------------------------------
# KONFIGURASI (aman diubah)
# ----------------------------------------------------------------------
WO_ROLE_PEMOHON = 'wo_user'
WO_ROLES_PENGELOLA = ['admin', 'wo_manager']
WO_USERNAMES_PENGELOLA = []          # contoh: ['kasek_bengkel']

SEKSI_TUJUAN = ['MPC', 'Bengkel', 'Lainnya']
STATUS_LIST = ['Baru', 'Diterima', 'Antri', 'Dikerjakan', 'Menunggu', 'Selesai', 'Dibatalkan']
STATUS_AKTIF = ['Baru', 'Diterima', 'Antri', 'Dikerjakan', 'Menunggu']
STATUS_ANTRIAN = ['Baru', 'Diterima', 'Antri']
PRIORITAS_LIST = ['Darurat', 'Tinggi', 'Normal', 'Rendah']
PRIORITAS_RANK = {p: i for i, p in enumerate(PRIORITAS_LIST)}

# Saran isian "Lokasi" (diambil dari checklist sarana & prasarana bangunan)
AREA_BANGUNAN = [
    'Kantor Direktur Utama', 'Ruang Rapat Direksi', 'Ruang Sekretaris', 'Kantor Direktur Keuangan',
    'Kantor VP Operasional', 'Selasar Kantor Direksi', 'Pantri Kantor Direksi', 'Lobi', 'Toilet Lobi',
    'Selasar', 'Ruang Seti', 'Mushola', 'Kantor Pemasaran', 'Kantor Akpro', 'Kantor SDM',
    'Kantor Keuangan', 'Kantor Fasum', 'Kantor Pengadaan', 'Kantor LPP', 'Kantor Rismindal',
    'Kantor SPI', 'Toilet SPI', 'Klinik', 'Satpam/Security',
    'Bahan Jadi I', 'Mesin Kertas I', 'Departemen Produksi', 'Finishing Unit I', 'Ekspedisi I',
    'Stock Preparation', 'Mesin Kertas III', 'Finishing Unit II', 'Ekspedisi II', 'Loss Cabana',
    'Gudang Chemical', 'Posko Satpam', 'Substation', 'Panel Board', 'Boiler', 'Gudang Besar',
    'Ruang Pemeliharaan Unit I', 'Departemen Teknik',
]


def init_wo(app, get_db_connection):
    # ------------------------------------------------------------------
    # UTIL
    # ------------------------------------------------------------------
    def now_wib():
        # Server Vercel memakai UTC; WO dicatat dalam WIB (UTC+7)
        utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        return utc + datetime.timedelta(hours=7)

    def today_wib():
        return now_wib().date()

    def role():
        return (session.get('role') or '').lower()

    def username():
        return session.get('username') or ''

    def is_pemohon():
        return role() == WO_ROLE_PEMOHON

    def can_manage():
        return role() in WO_ROLES_PENGELOLA or username().lower() in [u.lower() for u in WO_USERNAMES_PENGELOLA]

    def ser(row):
        out = {}
        for k, v in row.items():
            if isinstance(v, datetime.datetime):
                out[k] = v.strftime('%Y-%m-%d %H:%M')
            elif isinstance(v, datetime.date):
                out[k] = v.isoformat()
            else:
                out[k] = v
        return out

    def parse_date(val):
        if isinstance(val, str):
            val = val.strip()
        if not val:
            return None
        return datetime.date.fromisoformat(val)

    def fmt_tgl(d):
        return d.strftime('%d/%m/%Y') if d else '-'

    def in_clause(values):
        return ','.join(['%s'] * len(values))

    def is_terlambat(row, today):
        batas = row.get('target_selesai') or row.get('tgl_dibutuhkan')
        return bool(row['status'] in STATUS_AKTIF and batas and batas < today)

    def api_gagal(pesan, kode=400):
        return jsonify({"status": "error", "message": pesan}), kode

    # ------------------------------------------------------------------
    # PEMBATAS AKUN PEMOHON (di sisi server, berlaku untuk SEMUA halaman & API)
    # Akun WO_User hanya boleh /wo*, /api/wo*, login, logout, dan file static.
    # ------------------------------------------------------------------
    @app.before_request
    def wo_batasi_akun_pemohon():
        if not is_pemohon():
            return None
        p = request.path
        if (p in ('/login', '/logout') or p.startswith('/static/')
                or p == '/wo' or p.startswith('/wo/') or p.startswith('/api/wo')):
            return None
        if p.startswith('/api/'):
            return api_gagal("Akses Ditolak!", 403)
        return redirect(url_for('wo_dashboard'))

    # ------------------------------------------------------------------
    # HALAMAN
    # ------------------------------------------------------------------
    def render(tpl, active):
        return render_template(
            tpl, active=active, username=username(), role=session.get('role', ''),
            can_manage=can_manage(), is_pemohon=is_pemohon(),
            seksi_list=SEKSI_TUJUAN, status_list=STATUS_LIST,
            prioritas_list=PRIORITAS_LIST, status_aktif=STATUS_AKTIF)

    @app.route('/wo/dashboard')
    def wo_dashboard():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render('wo_dashboard.html', 'dashboard')

    @app.route('/wo')
    def wo_daftar():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render('wo_list.html', 'daftar')

    @app.route('/wo/baru')
    def wo_baru():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render('wo_baru.html', 'baru')

    # ------------------------------------------------------------------
    # PENGAYAAN DATA (posisi antrian, terlambat, umur)
    # ------------------------------------------------------------------
    def peta_antrian(cursor):
        cursor.execute(
            "SELECT id, seksi_tujuan, prioritas FROM wo WHERE status IN (%s)" % in_clause(STATUS_ANTRIAN),
            STATUS_ANTRIAN)
        per_seksi = {}
        for r in cursor.fetchall():
            per_seksi.setdefault(r['seksi_tujuan'], []).append(r)
        peta = {}
        for items in per_seksi.values():
            items.sort(key=lambda r: (PRIORITAS_RANK.get(r['prioritas'], 2), r['id']))
            for i, r in enumerate(items, 1):
                peta[r['id']] = (i, len(items))
        return peta

    def perkaya(row, today, peta):
        r = ser(row)
        r['terlambat'] = is_terlambat(row, today)
        masuk = row.get('tgl_masuk')
        if masuk and row['status'] != 'Dibatalkan':
            akhir = row['tgl_selesai'] if (row['status'] == 'Selesai' and row.get('tgl_selesai')) else today
            r['umur_hari'] = max((akhir - masuk).days, 0)
        else:
            r['umur_hari'] = None
        if row['id'] in peta:
            r['antrian_ke'], r['antrian_total'] = peta[row['id']]
        return r

    def nomor_berikutnya(cursor, tahun):
        prefix = "WO-%s-" % tahun
        cursor.execute(
            "SELECT MAX(CAST(SUBSTRING_INDEX(no_wo,'-',-1) AS UNSIGNED)) AS m FROM wo WHERE no_wo LIKE %s",
            (prefix + '%',))
        m = (cursor.fetchone() or {}).get('m') or 0
        return "%s%04d" % (prefix, int(m) + 1)

    # ------------------------------------------------------------------
    # API: DAFTAR & BUAT WO
    # ------------------------------------------------------------------
    @app.route('/api/wo', methods=['GET', 'POST'])
    def wo_api_daftar():
        if 'loggedin' not in session:
            return api_gagal("Belum login", 403)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if request.method == 'GET':
                    sql, params = "SELECT * FROM wo", ()
                    if is_pemohon():
                        sql, params = sql + " WHERE dibuat_oleh=%s", (username(),)
                    cursor.execute(sql + " ORDER BY id DESC LIMIT 2000", params)
                    rows = cursor.fetchall()
                    today, peta = today_wib(), peta_antrian(cursor)
                    return jsonify({"items": [perkaya(r, today, peta) for r in rows]})

                # ---- POST: buat WO baru ----
                data = request.json or {}
                judul = (data.get('judul') or '').strip()[:200]
                lokasi = (data.get('lokasi') or '').strip()[:150]
                dept = (data.get('departemen_pemohon') or '').strip()[:100]
                nama = (data.get('nama_pemohon') or '').strip()[:100]
                deskripsi = (data.get('deskripsi') or '').strip()[:4000]
                seksi = data.get('seksi_tujuan')
                prioritas = data.get('prioritas') or 'Normal'
                if not (judul and lokasi and dept and nama and deskripsi):
                    return api_gagal("Judul, lokasi, uraian, nama pemohon, dan departemen wajib diisi.")
                if seksi not in SEKSI_TUJUAN:
                    return api_gagal("Seksi tujuan tidak dikenali.")
                if prioritas not in PRIORITAS_LIST:
                    return api_gagal("Prioritas tidak dikenali.")
                try:
                    tgl_butuh = parse_date(data.get('tgl_dibutuhkan'))
                except ValueError:
                    return api_gagal("Format tanggal 'Dibutuhkan sebelum' tidak valid.")

                now = now_wib()
                no_wo = None
                for percobaan in range(3):
                    no_wo = nomor_berikutnya(cursor, now.year)
                    try:
                        cursor.execute(
                            """INSERT INTO wo (no_wo, no_ref, tgl_masuk, departemen_pemohon, nama_pemohon,
                                   seksi_tujuan, lokasi, id_mesin, judul, deskripsi, prioritas, status,
                                   tgl_dibutuhkan, dibuat_oleh, created_at, updated_at)
                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Baru',%s,%s,%s,%s)""",
                            (no_wo, (data.get('no_ref') or '').strip()[:50] or None, now.date(), dept, nama,
                             seksi, lokasi, (data.get('id_mesin') or '').strip()[:50] or None, judul,
                             deskripsi, prioritas, tgl_butuh, username(), now, now))
                        break
                    except pymysql.err.IntegrityError:
                        if percobaan == 2:
                            raise
                id_baru = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO wo_log (id_wo, waktu, oleh, status_baru, perubahan) VALUES (%s,%s,%s,'Baru',%s)",
                    (id_baru, now, username(), "WO diajukan oleh %s (%s)" % (nama, dept)))
                conn.commit()
                return jsonify({"status": "success", "message": "WO berhasil diajukan.",
                                "id": id_baru, "no_wo": no_wo})
        except Exception as e:
            return api_gagal("Gagal memproses WO. Pastikan tabel 'wo' & 'wo_log' sudah dibuat (wo_schema.sql). Detail: %s" % e, 500)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # API: DETAIL & UBAH WO
    # ------------------------------------------------------------------
    @app.route('/api/wo/<int:id>', methods=['GET', 'PUT'])
    def wo_api_detail(id):
        if 'loggedin' not in session:
            return api_gagal("Belum login", 403)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM wo WHERE id=%s", (id,))
                row = cursor.fetchone()
                if not row:
                    return api_gagal("WO tidak ditemukan.", 404)
                if is_pemohon() and row['dibuat_oleh'] != username():
                    return api_gagal("Akses Ditolak!", 403)

                if request.method == 'GET':
                    cursor.execute("SELECT * FROM wo_log WHERE id_wo=%s ORDER BY id DESC", (id,))
                    log = [ser(r) for r in cursor.fetchall()]
                    return jsonify({"wo": perkaya(row, today_wib(), peta_antrian(cursor)), "log": log})

                # ---------------- PUT ----------------
                data = request.json or {}
                catatan = (data.get('catatan') or '').strip()[:1000]
                now, today = now_wib(), today_wib()

                if is_pemohon():
                    # Pemohon hanya boleh membatalkan WO miliknya yang masih berstatus Baru
                    if data.get('status') != 'Dibatalkan':
                        return api_gagal("Akun ini hanya dapat membatalkan WO miliknya.", 403)
                    if row['status'] != 'Baru':
                        return api_gagal("WO sudah diproses dan tidak bisa dibatalkan di sini. Hubungi pengelola WO.")
                    cursor.execute(
                        "UPDATE wo SET status='Dibatalkan', keterangan=%s, updated_at=%s WHERE id=%s",
                        (catatan or None, now, id))
                    cursor.execute(
                        "INSERT INTO wo_log (id_wo, waktu, oleh, status_baru, perubahan, catatan) VALUES (%s,%s,%s,%s,%s,%s)",
                        (id, now, username(), 'Dibatalkan', 'Status: Baru → Dibatalkan (oleh pemohon)', catatan or None))
                    conn.commit()
                    return jsonify({"status": "success", "message": "WO dibatalkan."})

                if not can_manage():
                    return api_gagal("Akun ini hanya dapat melihat WO.", 403)

                def pilih(kunci):
                    return data[kunci] if kunci in data else row[kunci]

                status_baru = pilih('status')
                prioritas_baru = pilih('prioritas')
                seksi_baru = pilih('seksi_tujuan')
                assign_baru = (pilih('assign_ke') or '').strip()[:100] or None
                if status_baru not in STATUS_LIST:
                    return api_gagal("Status tidak dikenali.")
                if prioritas_baru not in PRIORITAS_LIST:
                    return api_gagal("Prioritas tidak dikenali.")
                if seksi_baru not in SEKSI_TUJUAN:
                    return api_gagal("Seksi tujuan tidak dikenali.")
                try:
                    target_baru = parse_date(data['target_selesai']) if 'target_selesai' in data else row['target_selesai']
                except ValueError:
                    return api_gagal("Format tanggal estimasi selesai tidak valid.")

                status_berubah = status_baru != row['status']
                if status_berubah and status_baru in ('Menunggu', 'Dibatalkan') and not catatan:
                    return api_gagal("Isi catatan: alasan WO ditandai '%s' wajib ditulis agar pemohon tahu." % status_baru)

                perubahan = []
                if status_berubah:
                    perubahan.append("Status: %s → %s" % (row['status'], status_baru))
                if prioritas_baru != row['prioritas']:
                    perubahan.append("Prioritas: %s → %s" % (row['prioritas'], prioritas_baru))
                if seksi_baru != row['seksi_tujuan']:
                    perubahan.append("Seksi tujuan: %s → %s" % (row['seksi_tujuan'], seksi_baru))
                if assign_baru != row['assign_ke']:
                    perubahan.append("Ditugaskan ke: %s" % (assign_baru or '-'))
                if target_baru != row['target_selesai']:
                    perubahan.append("Estimasi selesai: %s → %s" % (fmt_tgl(row['target_selesai']), fmt_tgl(target_baru)))

                if not perubahan and not catatan:
                    return jsonify({"status": "success", "message": "Tidak ada perubahan."})

                tgl_mulai, tgl_selesai = row['tgl_mulai'], row['tgl_selesai']
                if status_berubah:
                    if status_baru == 'Dikerjakan' and not tgl_mulai:
                        tgl_mulai = today
                    tgl_selesai = today if status_baru == 'Selesai' else None
                    keterangan = catatan or None
                else:
                    keterangan = catatan or row['keterangan']

                cursor.execute(
                    """UPDATE wo SET status=%s, prioritas=%s, seksi_tujuan=%s, assign_ke=%s, target_selesai=%s,
                           keterangan=%s, tgl_mulai=%s, tgl_selesai=%s, updated_at=%s WHERE id=%s""",
                    (status_baru, prioritas_baru, seksi_baru, assign_baru, target_baru,
                     keterangan, tgl_mulai, tgl_selesai, now, id))
                cursor.execute(
                    "INSERT INTO wo_log (id_wo, waktu, oleh, status_baru, perubahan, catatan) VALUES (%s,%s,%s,%s,%s,%s)",
                    (id, now, username(), status_baru, '; '.join(perubahan) or None, catatan or None))
                conn.commit()
                return jsonify({"status": "success", "message": "WO diperbarui."})
        except Exception as e:
            return api_gagal("Gagal memproses WO. Detail: %s" % e, 500)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # API: STATISTIK DASHBOARD
    # ------------------------------------------------------------------
    @app.route('/api/wo/stats')
    def wo_api_stats():
        if 'loggedin' not in session:
            return api_gagal("Belum login", 403)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT id, no_wo, judul, seksi_tujuan, prioritas, status, assign_ke, departemen_pemohon,
                              dibuat_oleh, tgl_masuk, tgl_mulai, tgl_selesai, target_selesai, tgl_dibutuhkan
                       FROM wo""")
                semua = cursor.fetchall()
        except Exception as e:
            return api_gagal("Gagal membaca data WO. Pastikan tabel 'wo' sudah dibuat (wo_schema.sql). Detail: %s" % e, 500)
        finally:
            conn.close()

        today = today_wib()
        milik = [r for r in semua if (not is_pemohon() or r['dibuat_oleh'] == username())]

        def hitung(rows, daftar_status):
            return sum(1 for r in rows if r['status'] in daftar_status)

        # Beban kerja per seksi: angka global (tanpa rincian WO) agar semua pemohon melihat antrian
        beban = []
        for s in SEKSI_TUJUAN:
            rs = [r for r in semua if r['seksi_tujuan'] == s]
            beban.append({
                "seksi": s,
                "dikerjakan": hitung(rs, ['Dikerjakan']),
                "antri": hitung(rs, STATUS_ANTRIAN),
                "menunggu": hitung(rs, ['Menunggu']),
                "selesai_30h": sum(1 for r in rs if r['status'] == 'Selesai' and r['tgl_selesai']
                                   and (today - r['tgl_selesai']).days <= 30),
            })

        selesai_90 = [(r['tgl_selesai'] - r['tgl_masuk']).days for r in milik
                      if r['status'] == 'Selesai' and r['tgl_selesai'] and r['tgl_masuk']
                      and (today - r['tgl_selesai']).days <= 90]
        ringkasan = {
            "aktif": hitung(milik, STATUS_AKTIF),
            "baru": hitung(milik, ['Baru']),
            "terlambat": sum(1 for r in milik if is_terlambat(r, today)),
            "selesai_bulan_ini": sum(1 for r in milik if r['status'] == 'Selesai' and r['tgl_selesai']
                                     and (r['tgl_selesai'].year, r['tgl_selesai'].month) == (today.year, today.month)),
            "rata2_hari": round(sum(selesai_90) / len(selesai_90), 1) if selesai_90 else None,
        }
        per_status = {s: hitung(milik, [s]) for s in STATUS_LIST}

        # Tren 6 bulan terakhir
        tren, y, m = [], today.year, today.month
        bulan = []
        for _ in range(6):
            bulan.append((y, m))
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        for (y, m) in reversed(bulan):
            tren.append({
                "bulan": "%04d-%02d" % (y, m),
                "masuk": sum(1 for r in milik if r['tgl_masuk'] and (r['tgl_masuk'].year, r['tgl_masuk'].month) == (y, m)),
                "selesai": sum(1 for r in milik if r['status'] == 'Selesai' and r['tgl_selesai']
                               and (r['tgl_selesai'].year, r['tgl_selesai'].month) == (y, m)),
            })

        hasil = {"beban_seksi": beban, "ringkasan": ringkasan, "per_status": per_status, "tren": tren}

        if not is_pemohon():
            def baris(r):
                return {"id": r['id'], "no_wo": r['no_wo'], "judul": r['judul'], "seksi": r['seksi_tujuan'],
                        "prioritas": r['prioritas'], "assign_ke": r['assign_ke']}
            dikerjakan = sorted([r for r in semua if r['status'] == 'Dikerjakan'],
                                key=lambda r: (r['tgl_mulai'] or today, r['id']))[:10]
            hasil["sedang_dikerjakan"] = [dict(baris(r), hari=(today - r['tgl_mulai']).days if r['tgl_mulai'] else None)
                                          for r in dikerjakan]
            telat = [r for r in semua if is_terlambat(r, today)]
            telat.sort(key=lambda r: (r.get('target_selesai') or r.get('tgl_dibutuhkan')))
            hasil["terlambat_list"] = [dict(baris(r), status=r['status'],
                                            hari_telat=(today - (r.get('target_selesai') or r.get('tgl_dibutuhkan'))).days)
                                       for r in telat[:10]]
            dept = {}
            for r in semua:
                if r['status'] in STATUS_AKTIF:
                    dept[r['departemen_pemohon']] = dept.get(r['departemen_pemohon'], 0) + 1
            hasil["per_departemen"] = [{"departemen": k, "aktif": v}
                                       for k, v in sorted(dept.items(), key=lambda kv: -kv[1])[:8]]
        return jsonify(hasil)

    # ------------------------------------------------------------------
    # API: PILIHAN UNTUK FORM (daftar mesin, area, departemen yang pernah mengajukan)
    # ------------------------------------------------------------------
    @app.route('/api/wo/pilihan')
    def wo_api_pilihan():
        if 'loggedin' not in session:
            return api_gagal("Belum login", 403)
        conn = get_db_connection()
        mesin, dept = [], []
        try:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("SELECT * FROM master_mesin ORDER BY area, id_mesin")
                    for r in cursor.fetchall():
                        nama = (r.get('nama_mesin') or r.get('nama_alat') or r.get('nama')
                                or r.get('tipe_mesin') or '')
                        mesin.append({"id": r.get('id_mesin'), "nama": nama, "area": r.get('area')})
                except Exception:
                    pass
                try:
                    cursor.execute("SELECT DISTINCT departemen_pemohon FROM wo ORDER BY departemen_pemohon")
                    dept = [r['departemen_pemohon'] for r in cursor.fetchall()]
                except Exception:
                    pass
        finally:
            conn.close()
        return jsonify({"mesin": mesin, "area": AREA_BANGUNAN, "departemen": dept})
