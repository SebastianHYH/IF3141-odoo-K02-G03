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
# 5. PENANAMAN (batch otomatis dibuat via create())
# ─────────────────────────────────────────────
print("\n[5] Membuat penanaman...")

penanaman_data = [
    # Jamur Tiram - sudah bisa panen (50 hari lalu, estimasi 45 hari)
    {
        'tanggal_penanaman': today - timedelta(days=50),
        'bibit_id': bibits['Jamur Tiram'].id,
        'jumlah_batch': 3,
        'jumlah_bibit': 300,
        'ruangan_id': ruangans['RNG-A'].id,
        'pegawai_id': emp_budi.id,
        'catatan': 'Batch jamur tiram musim pertama',
    },
    # Jamur Shiitake - aktif (30 hari lalu, estimasi 60 hari)
    {
        'tanggal_penanaman': today - timedelta(days=30),
        'bibit_id': bibits['Jamur Shiitake'].id,
        'jumlah_batch': 2,
        'jumlah_bibit': 200,
        'ruangan_id': ruangans['RNG-A'].id,
        'pegawai_id': emp_budi.id,
        'catatan': 'Batch shiitake premium',
    },
    # Mint - sudah bisa panen (35 hari lalu, estimasi 30 hari)
    {
        'tanggal_penanaman': today - timedelta(days=35),
        'bibit_id': bibits['Mint'].id,
        'jumlah_batch': 2,
        'jumlah_bibit': 120,
        'ruangan_id': ruangans['RNG-B'].id,
        'pegawai_id': emp_sari.id,
        'catatan': 'Mint untuk kebutuhan resto lokal',
    },
    # Rosemary - aktif (40 hari lalu, estimasi 90 hari)
    {
        'tanggal_penanaman': today - timedelta(days=40),
        'bibit_id': bibits['Rosemary'].id,
        'jumlah_batch': 1,
        'jumlah_bibit': 80,
        'ruangan_id': ruangans['RNG-B'].id,
        'pegawai_id': emp_sari.id,
        'catatan': 'Rosemary organik',
    },
    # Asparagus - aktif (20 hari lalu)
    {
        'tanggal_penanaman': today - timedelta(days=20),
        'bibit_id': bibits['Asparagus'].id,
        'jumlah_batch': 2,
        'jumlah_bibit': 160,
        'ruangan_id': ruangans['RNG-C'].id,
        'pegawai_id': emp_raka.id,
        'catatan': 'Asparagus green premium',
    },
    # Golden Berry - aktif (10 hari lalu)
    {
        'tanggal_penanaman': today - timedelta(days=10),
        'bibit_id': bibits['Golden Berry'].id,
        'jumlah_batch': 1,
        'jumlah_bibit': 60,
        'ruangan_id': ruangans['RNG-C'].id,
        'pegawai_id': emp_raka.id,
        'catatan': 'Golden berry eksperimen pertama',
    },
]

penanaman_records = []
for d in penanaman_data:
    rec = env['ipfarm.penanaman'].create(d)
    penanaman_records.append(rec)
    print(f"    Dibuat: {rec.name} - {bibits[next(b['name'] for b in bibit_data if bibits[b['name']].id == d['bibit_id'])].name}")

env.cr.commit()
print("    Penanaman & batch berhasil disimpan.")

# ─────────────────────────────────────────────
# 6. UPDATE ESTIMASI PANEN (UC 02)
# ─────────────────────────────────────────────
print("\n[6] Update estimasi panen...")

# Update estimasi untuk Shiitake (maju 10 hari karena pertumbuhan bagus)
batch_shiitake = penanaman_records[1].batch_ids[0]
env['ipfarm.estimasi_panen_history'].create({
    'batch_id': batch_shiitake.id,
    'estimasi_panen_baru': today + timedelta(days=20),
    'pegawai_id': emp_budi.id,
    'tanggal_pembaruan': today - timedelta(days=5),
    'catatan': 'Pertumbuhan miselium lebih cepat dari estimasi, dimajukan 10 hari',
})

# Update estimasi untuk Rosemary (mundur karena suhu kurang optimal)
batch_rosemary = penanaman_records[3].batch_ids[0]
env['ipfarm.estimasi_panen_history'].create({
    'batch_id': batch_rosemary.id,
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
batches_tiram = penanaman_records[0].batch_ids
catat_panen(batches_tiram[0], produks['Jamur Tiram Segar'], 18.5, today - timedelta(days=4), emp_budi, 'Panen flush pertama jamur tiram')
catat_panen(batches_tiram[1], produks['Jamur Tiram Segar'], 16.0, today - timedelta(days=3), emp_budi, 'Panen flush pertama batch 2')
catat_panen(batches_tiram[2], produks['Jamur Tiram Segar'], 14.5, today - timedelta(days=2), emp_budi, 'Panen flush pertama batch 3')

# Panen Mint (2 batch) → satuan liter (sari mint segar)
batches_mint = penanaman_records[2].batch_ids
catat_panen(batches_mint[0], produks['Mint Segar'], 5.0, today - timedelta(days=5), emp_sari, 'Panen mint batch 1 - 5L sari mint')
catat_panen(batches_mint[1], produks['Mint Segar'], 4.5, today - timedelta(days=4), emp_sari, 'Panen mint batch 2 - 4.5L sari mint')

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
