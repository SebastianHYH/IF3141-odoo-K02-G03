"""
Seed data untuk IP FarmBook - IF3141 K02 G03
Jalankan via: docker exec -i <web-container> odoo shell -d postgres --no-http < scripts/seed_data.py
"""
from datetime import date, timedelta

today = date.today()

print("=== SEED IP FarmBook ===")

# ─────────────────────────────────────────────
# 0. CLEANUP DATA LAMA
# ─────────────────────────────────────────────
print("\n[0] Membersihkan data lama...")

# Urutan penting: hapus yang punya FK dulu
env['ipfarm.histori_stok'].search([]).unlink()
env['ipfarm.panen'].with_context(module_uninstall=True).search([]).unlink()
env['ipfarm.pemrosesan'].with_context(module_uninstall=True).search([]).unlink()
env['ipfarm.estimasi_panen_history'].search([]).unlink()
env['ipfarm.batch'].search([]).unlink()
env['ipfarm.penanaman'].search([]).unlink()
env['ipfarm.produk'].search([]).write({'stok_tersedia': 0})
env['ipfarm.produk'].search([]).unlink()
env['ipfarm.bibit'].search([]).unlink()
env['ipfarm.ruangan'].search([]).unlink()
env['hr.employee'].search([('name', 'in', ['Budi Santoso', 'Sari Dewi', 'Raka Pratama'])]).unlink()
env.cr.commit()
print("    Data lama dibersihkan.")

# ─────────────────────────────────────────────
# 1. EMPLOYEE
# ─────────────────────────────────────────────
print("\n[1] Membuat employee...")

def get_or_create_employee(name, user_id=None):
    emp = env['hr.employee'].search([('name', '=', name)], limit=1)
    if not emp:
        vals = {'name': name}
        if user_id:
            vals['user_id'] = user_id
        emp = env['hr.employee'].create(vals)
        print(f"    Dibuat: {name}")
    else:
        print(f"    Sudah ada: {name}")
    return emp

admin_emp = get_or_create_employee('Administrator', user_id=1)
emp_budi  = get_or_create_employee('Budi Santoso')
emp_sari  = get_or_create_employee('Sari Dewi')
emp_raka  = get_or_create_employee('Raka Pratama')

# ─────────────────────────────────────────────
# 2. BIBIT
# ─────────────────────────────────────────────
print("\n[2] Membuat bibit...")

bibit_data = [
    {'name': 'Jamur Tiram',    'kode': 'BIB-001', 'kategori': 'lainnya', 'estimasi_hari_panen': 45},
    {'name': 'Jamur Shiitake', 'kode': 'BIB-002', 'kategori': 'lainnya', 'estimasi_hari_panen': 60},
    {'name': 'Jamur Kuping',   'kode': 'BIB-003', 'kategori': 'lainnya', 'estimasi_hari_panen': 40},
    {'name': 'Jamur Maitake',  'kode': 'BIB-004', 'kategori': 'lainnya', 'estimasi_hari_panen': 90},
    {'name': 'Rosemary',       'kode': 'BIB-005', 'kategori': 'herbal',  'estimasi_hari_panen': 90},
    {'name': 'Asparagus',      'kode': 'BIB-006', 'kategori': 'sayur',   'estimasi_hari_panen': 60},
    {'name': 'Golden Berry',   'kode': 'BIB-007', 'kategori': 'buah',    'estimasi_hari_panen': 75},
    {'name': 'Thyme',          'kode': 'BIB-008', 'kategori': 'herbal',  'estimasi_hari_panen': 60},
    {'name': 'Mint',           'kode': 'BIB-009', 'kategori': 'herbal',  'estimasi_hari_panen': 30},
    {'name': 'Sage',           'kode': 'BIB-010', 'kategori': 'herbal',  'estimasi_hari_panen': 75},
    {'name': 'Oregano',        'kode': 'BIB-011', 'kategori': 'herbal',  'estimasi_hari_panen': 60},
]

bibits = {}
for d in bibit_data:
    rec = env['ipfarm.bibit'].create(d)
    bibits[d['name']] = rec
    print(f"    Dibuat: {d['name']}")

# ─────────────────────────────────────────────
# 3. RUANGAN
# ─────────────────────────────────────────────
print("\n[3] Membuat ruangan...")

ruangan_data = [
    {'name': 'Ruangan A - Budidaya Jamur',  'kode': 'RNG-A', 'kapasitas': 500, 'lokasi': 'Gedung Utama Lt.1'},
    {'name': 'Ruangan B - Herbal Indoor',   'kode': 'RNG-B', 'kapasitas': 200, 'lokasi': 'Gedung Utama Lt.2'},
    {'name': 'Ruangan C - Sayur & Buah',    'kode': 'RNG-C', 'kapasitas': 300, 'lokasi': 'Gedung Samping'},
]

ruangans = {}
for d in ruangan_data:
    rec = env['ipfarm.ruangan'].create(d)
    ruangans[d['kode']] = rec
    print(f"    Dibuat: {d['name']}")

# ─────────────────────────────────────────────
# 4. PRODUK
# ─────────────────────────────────────────────
print("\n[4] Membuat produk...")

uom_kg = env.ref('uom.product_uom_kgm')
uom_g  = env.ref('uom.product_uom_gram')
uom_l  = env.ref('uom.product_uom_litre')

produk_data = [
    # Jamur → satuan massa kg
    {'name': 'Jamur Tiram Segar',    'kode': 'PRD-001', 'kategori': 'lainnya', 'minimum_stok': 5.0,  'uom_id': uom_kg.id},
    {'name': 'Jamur Shiitake Segar', 'kode': 'PRD-002', 'kategori': 'lainnya', 'minimum_stok': 3.0,  'uom_id': uom_kg.id},
    {'name': 'Jamur Kuping Segar',   'kode': 'PRD-003', 'kategori': 'lainnya', 'minimum_stok': 3.0,  'uom_id': uom_kg.id},
    {'name': 'Jamur Maitake Segar',  'kode': 'PRD-004', 'kategori': 'lainnya', 'minimum_stok': 2.0,  'uom_id': uom_kg.id},
    # Sayur & buah → satuan massa kg
    {'name': 'Asparagus Segar',      'kode': 'PRD-006', 'kategori': 'sayur',   'minimum_stok': 4.0,  'uom_id': uom_kg.id},
    {'name': 'Golden Berry',         'kode': 'PRD-007', 'kategori': 'buah',    'minimum_stok': 2.0,  'uom_id': uom_kg.id},
    # Herbal kecil → satuan massa gram
    {'name': 'Rosemary Segar',       'kode': 'PRD-005', 'kategori': 'herbal',  'minimum_stok': 200.0,'uom_id': uom_g.id},
    {'name': 'Thyme Segar',          'kode': 'PRD-008', 'kategori': 'herbal',  'minimum_stok': 150.0,'uom_id': uom_g.id},
    {'name': 'Sage Segar',           'kode': 'PRD-010', 'kategori': 'herbal',  'minimum_stok': 100.0,'uom_id': uom_g.id},
    {'name': 'Oregano Segar',        'kode': 'PRD-011', 'kategori': 'herbal',  'minimum_stok': 100.0,'uom_id': uom_g.id},
    # Mint → satuan volume liter (infusi/sari mint segar)
    {'name': 'Mint Segar',           'kode': 'PRD-009', 'kategori': 'herbal',  'minimum_stok': 2.0,  'uom_id': uom_l.id},
]

produks = {}
for d in produk_data:
    rec = env['ipfarm.produk'].create(d)
    produks[d['name']] = rec
    uom_name = env['uom.uom'].browse(d['uom_id']).name
    print(f"    Dibuat: {d['name']} ({uom_name})")

# ─────────────────────────────────────────────
# 5. PENANAMAN + BATCH (dibuat manual per batch)
# ─────────────────────────────────────────────
print("\n[5] Membuat penanaman dan batch...")

def buat_penanaman(tanggal, pegawai, catatan=''):
    rec = env['ipfarm.penanaman'].create({
        'tanggal_penanaman': tanggal,
        'pegawai_id': pegawai.id,
        'catatan': catatan,
    })
    print(f"    Dibuat: {rec.name}")
    return rec

def buat_batch(penanaman, bibit, jumlah, ruangan, estimasi_panen, state='aktif'):
    batch = env['ipfarm.batch'].create({
        'penanaman_id': penanaman.id,
        'bibit_id': bibit.id,
        'ruangan_id': ruangan.id,
        'jumlah_bibit': jumlah,
        'estimasi_panen': estimasi_panen,
        'state': state,
    })
    print(f"      Batch: {batch.name} - {bibit.name} ({jumlah} bibit, est. panen {estimasi_panen})")
    return batch

# Sesi tanam 1: Jamur Tiram (3 batch, sudah selesai panen)
pen_tiram = buat_penanaman(today - timedelta(days=50), emp_budi, 'Sesi tanam jamur tiram musim pertama')
batch_tiram_1 = buat_batch(pen_tiram, bibits['Jamur Tiram'], 100, ruangans['RNG-A'], today - timedelta(days=5), state='selesai')
batch_tiram_2 = buat_batch(pen_tiram, bibits['Jamur Tiram'], 100, ruangans['RNG-A'], today - timedelta(days=3), state='selesai')
batch_tiram_3 = buat_batch(pen_tiram, bibits['Jamur Tiram'], 100, ruangans['RNG-A'], today - timedelta(days=2), state='selesai')

# Sesi tanam 2: Jamur Shiitake (2 batch, aktif)
pen_shiitake = buat_penanaman(today - timedelta(days=30), emp_budi, 'Sesi tanam shiitake premium')
batch_shiitake_1 = buat_batch(pen_shiitake, bibits['Jamur Shiitake'], 100, ruangans['RNG-A'], today + timedelta(days=30))
batch_shiitake_2 = buat_batch(pen_shiitake, bibits['Jamur Shiitake'], 100, ruangans['RNG-A'], today + timedelta(days=30))

# Sesi tanam 3: Mint + Rosemary (dalam 1 sesi tanam herbal)
pen_herbal = buat_penanaman(today - timedelta(days=35), emp_sari, 'Sesi tanam herbal - mint dan rosemary')
batch_mint_1 = buat_batch(pen_herbal, bibits['Mint'], 60, ruangans['RNG-B'], today - timedelta(days=5), state='selesai')
batch_mint_2 = buat_batch(pen_herbal, bibits['Mint'], 60, ruangans['RNG-B'], today - timedelta(days=4), state='selesai')
batch_rosemary_1 = buat_batch(pen_herbal, bibits['Rosemary'], 80, ruangans['RNG-B'], today + timedelta(days=55))

# Sesi tanam 4: Asparagus + Golden Berry
pen_sayur = buat_penanaman(today - timedelta(days=20), emp_raka, 'Sesi tanam sayur dan buah')
batch_asparagus_1 = buat_batch(pen_sayur, bibits['Asparagus'], 80, ruangans['RNG-C'], today + timedelta(days=40))
batch_asparagus_2 = buat_batch(pen_sayur, bibits['Asparagus'], 80, ruangans['RNG-C'], today + timedelta(days=40))
batch_goldenberry_1 = buat_batch(pen_sayur, bibits['Golden Berry'], 60, ruangans['RNG-C'], today + timedelta(days=65))

penanaman_records = [pen_tiram, pen_shiitake, pen_herbal, pen_sayur]

env.cr.commit()
print("    Penanaman & batch berhasil disimpan.")

# ─────────────────────────────────────────────
# 6. UPDATE ESTIMASI PANEN (UC 02)
# ─────────────────────────────────────────────
print("\n[6] Update estimasi panen...")

# Update estimasi untuk Shiitake (maju 10 hari karena pertumbuhan bagus)
env['ipfarm.estimasi_panen_history'].create({
    'batch_id': batch_shiitake_1.id,
    'estimasi_panen_baru': today + timedelta(days=20),
    'pegawai_id': emp_budi.id,
    'tanggal_pembaruan': today - timedelta(days=5),
    'catatan': 'Pertumbuhan miselium lebih cepat dari estimasi, dimajukan 10 hari',
})

# Update estimasi untuk Rosemary (mundur karena suhu kurang optimal)
env['ipfarm.estimasi_panen_history'].create({
    'batch_id': batch_rosemary_1.id,
    'estimasi_panen_baru': today + timedelta(days=60),
    'pegawai_id': emp_sari.id,
    'tanggal_pembaruan': today - timedelta(days=2),
    'catatan': 'Suhu ruangan kurang optimal minggu ini, estimasi mundur 10 hari',
})

env.cr.commit()
print("    Update estimasi tersimpan.")

# ─────────────────────────────────────────────
# 7. PANEN (UC 03) — otomatis update stok
# ─────────────────────────────────────────────
print("\n[7] Mencatat hasil panen...")

def catat_panen(batch, produk, jumlah, tgl, pegawai, catatan=''):
    panen = env['ipfarm.panen'].create({
        'batch_id': batch.id,
        'tanggal_panen': tgl,
        'produk_id': produk.id,
        'jumlah': jumlah,
        'uom_id': produk.uom_id.id,
        'pegawai_id': pegawai.id,
        'catatan': catatan,
    })
    print(f"    {panen.name}: {jumlah} kg {produk.name} dari {batch.name}")
    return panen

# Panen Jamur Tiram (3 batch) → satuan kg
catat_panen(batch_tiram_1, produks['Jamur Tiram Segar'], 18.5, today - timedelta(days=4), emp_budi, 'Panen flush pertama jamur tiram')
catat_panen(batch_tiram_2, produks['Jamur Tiram Segar'], 16.0, today - timedelta(days=3), emp_budi, 'Panen flush pertama batch 2')
catat_panen(batch_tiram_3, produks['Jamur Tiram Segar'], 14.5, today - timedelta(days=2), emp_budi, 'Panen flush pertama batch 3')

# Panen Mint (2 batch) → satuan liter (sari mint segar)
catat_panen(batch_mint_1, produks['Mint Segar'], 5.0, today - timedelta(days=5), emp_sari, 'Panen mint batch 1 - 5L sari mint')
catat_panen(batch_mint_2, produks['Mint Segar'], 4.5, today - timedelta(days=4), emp_sari, 'Panen mint batch 2 - 4.5L sari mint')

env.cr.commit()
print("    Panen tersimpan, stok diperbarui otomatis.")

# ─────────────────────────────────────────────
# 8. PEMROSESAN (UC 05) — otomatis kurangi stok
# ─────────────────────────────────────────────
print("\n[8] Mencatat pemrosesan produk...")

def catat_pemrosesan(produk, jenis, jumlah, tgl, pegawai, catatan=''):
    prs = env['ipfarm.pemrosesan'].create({
        'tanggal_pemrosesan': tgl,
        'produk_id': produk.id,
        'jenis_pemrosesan': jenis,
        'jumlah': jumlah,
        'uom_id': produk.uom_id.id,
        'pegawai_id': pegawai.id,
        'catatan': catatan,
    })
    print(f"    {prs.name}: {jumlah} kg {produk.name} ({jenis})")
    return prs

# Pemrosesan Jamur Tiram → satuan kg
catat_pemrosesan(produks['Jamur Tiram Segar'], 'sortir',     10.0, today - timedelta(days=2), emp_sari, 'Sortir grade A/B/C jamur tiram')
catat_pemrosesan(produks['Jamur Tiram Segar'], 'pengemasan', 15.0, today - timedelta(days=1), emp_raka, 'Kemas 250gr/pack untuk distribusi')
# Pemrosesan Mint → satuan liter
catat_pemrosesan(produks['Mint Segar'],        'pengolahan',  3.0, today - timedelta(days=3), emp_sari, 'Proses filtrasi sari mint')
catat_pemrosesan(produks['Mint Segar'],        'pengemasan',  2.0, today - timedelta(days=2), emp_raka, 'Kemas sari mint 250mL/botol')

env.cr.commit()
print("    Pemrosesan tersimpan, stok dikurangi otomatis.")

# ─────────────────────────────────────────────
# RINGKASAN
# ─────────────────────────────────────────────
print("\n" + "="*50)
print("SEED SELESAI - Ringkasan:")
print(f"  Bibit      : {env['ipfarm.bibit'].search_count([])} record")
print(f"  Ruangan    : {env['ipfarm.ruangan'].search_count([])} record")
print(f"  Produk     : {env['ipfarm.produk'].search_count([])} record")
print(f"  Penanaman  : {env['ipfarm.penanaman'].search_count([])} record")
print(f"  Batch      : {env['ipfarm.batch'].search_count([])} record")
print(f"  Panen      : {env['ipfarm.panen'].search_count([])} record")
print(f"  Pemrosesan : {env['ipfarm.pemrosesan'].search_count([])} record")
print(f"  Histori Stok: {env['ipfarm.histori_stok'].search_count([])} record")
print("\nStok Produk saat ini:")
for p in env['ipfarm.produk'].search([('stok_tersedia', '>', 0)]):
    print(f"  {p.name}: {p.stok_tersedia:.1f} kg [{p.status_stok}]")
print("="*50)
