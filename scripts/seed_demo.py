from datetime import date, timedelta

today = date.today()

print("=" * 60)
print("Seed Data")
print("=" * 60)

# Clean Data Lama
print("\n[0] Membersihkan data lama...")

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

# Hapus user demo lama 
demo_logins = ['andi.manager', 'budi.pembibitan', 'sari.produksi', 'raka.processing', 'diana.finance']
env['res.users'].search([('login', 'in', demo_logins)]).unlink()
env['hr.employee'].search([
    ('name', 'in', ['Andi Manajer', 'Budi Santoso', 'Sari Dewi', 'Raka Pratama', 'Diana Keuangan'])
]).unlink()

env.cr.commit()
print("    Data lama dibersihkan.")

# Buat User Demo per role
print("\n[1] Membuat user demo per role...")

def buat_user(nama, login, password, group_xml_id):
    group = env.ref(group_xml_id)
    base_group = env.ref('base.group_user')
    user = env['res.users'].create({
        'name': nama,
        'login': login,
        'password': password,
        'groups_id': [(6, 0, [base_group.id, group.id])],
        'lang': 'en_US',
    })
    print(f"    User dibuat: {login} -> {group.name}")
    return user

user_andi  = buat_user('Andi Manajer',   'andi.manager',     'ipfarm123', 'ip_farmbook.group_ipfarm_management')
user_budi  = buat_user('Budi Santoso',   'budi.pembibitan',  'ipfarm123', 'ip_farmbook.group_ipfarm_seedling')
user_sari  = buat_user('Sari Dewi',      'sari.produksi',    'ipfarm123', 'ip_farmbook.group_ipfarm_production')
user_raka  = buat_user('Raka Pratama',   'raka.processing',  'ipfarm123', 'ip_farmbook.group_ipfarm_processing')
user_diana = buat_user('Diana Keuangan', 'diana.finance',    'ipfarm123', 'ip_farmbook.group_ipfarm_finance')

env.cr.commit()

# Buat Employee
print("\n[2] Membuat data pegawai...")

emp_andi  = env['hr.employee'].create({'name': 'Andi Manajer',   'user_id': user_andi.id,  'job_title': 'Manajer Operasional'})
emp_budi  = env['hr.employee'].create({'name': 'Budi Santoso',   'user_id': user_budi.id,  'job_title': 'Staff Pembibitan'})
emp_sari  = env['hr.employee'].create({'name': 'Sari Dewi',      'user_id': user_sari.id,  'job_title': 'Staff Produksi/Growing'})
emp_raka  = env['hr.employee'].create({'name': 'Raka Pratama',   'user_id': user_raka.id,  'job_title': 'Staff Processing'})
emp_diana = env['hr.employee'].create({'name': 'Diana Keuangan', 'user_id': user_diana.id, 'job_title': 'Staff Finance'})

for emp in [emp_andi, emp_budi, emp_sari, emp_raka, emp_diana]:
    print(f"    Pegawai: {emp.name} ({emp.job_title})")

env.cr.commit()

# Master Data Bibit
print("\n[3] Membuat master data bibit...")

bibit_data = [
    {'name': 'Jamur Tiram',    'kode': 'BIB-001', 'kategori': 'lainnya', 'estimasi_hari_panen': 45,
     'catatan': 'Jamur tiram putih (Pleurotus ostreatus), cocok untuk budidaya indoor suhu 22-28°C'},
    {'name': 'Jamur Shiitake', 'kode': 'BIB-002', 'kategori': 'lainnya', 'estimasi_hari_panen': 60,
     'catatan': 'Jamur shiitake premium (Lentinus edodes), butuh suhu 15-20°C'},
    {'name': 'Jamur Kuping',   'kode': 'BIB-003', 'kategori': 'lainnya', 'estimasi_hari_panen': 40,
     'catatan': 'Jamur kuping (Auricularia auricula-judae), tahan suhu 20-30°C'},
    {'name': 'Rosemary',       'kode': 'BIB-004', 'kategori': 'herbal',  'estimasi_hari_panen': 90,
     'catatan': 'Herbal aromatik, digunakan dalam masakan Mediterania'},
    {'name': 'Mint',           'kode': 'BIB-005', 'kategori': 'herbal',  'estimasi_hari_panen': 30,
     'catatan': 'Mint segar, panen cepat, cocok untuk minuman dan aromaterapi'},
    {'name': 'Asparagus',      'kode': 'BIB-006', 'kategori': 'sayur',   'estimasi_hari_panen': 60,
     'catatan': 'Sayuran premium bergizi tinggi'},
    {'name': 'Thyme',          'kode': 'BIB-007', 'kategori': 'herbal',  'estimasi_hari_panen': 60,
     'catatan': 'Herbal untuk bumbu masakan'},
    {'name': 'Sage',           'kode': 'BIB-008', 'kategori': 'herbal',  'estimasi_hari_panen': 75,
     'catatan': 'Herbal sage untuk kuliner dan obat herbal'},
]

bibits = {}
for d in bibit_data:
    rec = env['ipfarm.bibit'].create(d)
    bibits[d['name']] = rec
    print(f"    {d['kode']}: {d['name']}")

# Master Data Ruangan
print("\n[4] Membuat master data ruangan...")

ruangan_data = [
    {'name': 'Ruangan A - Budidaya Jamur',  'kode': 'RNG-A', 'kapasitas': 500,
     'lokasi': 'Gedung Utama Lt. 1',
     'catatan': 'Ruangan khusus budidaya jamur, dilengkapi sistem humidifier dan sirkulasi udara'},
    {'name': 'Ruangan B - Herbal Indoor',   'kode': 'RNG-B', 'kapasitas': 200,
     'lokasi': 'Gedung Utama Lt. 2',
     'catatan': 'Ruangan herbal dengan pencahayaan LED spectrum penuh'},
    {'name': 'Ruangan C - Sayur & Buah',    'kode': 'RNG-C', 'kapasitas': 300,
     'lokasi': 'Gedung Samping',
     'catatan': 'Ruangan hidroponik untuk sayur dan buah premium'},
]

ruangans = {}
for d in ruangan_data:
    rec = env['ipfarm.ruangan'].create(d)
    ruangans[d['kode']] = rec
    print(f"    {d['kode']}: {d['name']} (kapasitas {d['kapasitas']})")

# Master Data Produk
print("\n[5] Membuat master data produk...")

uom_kg = env.ref('uom.product_uom_kgm')
uom_g  = env.ref('uom.product_uom_gram')
uom_l  = env.ref('uom.product_uom_litre')

produk_data = [
    # Jamur -> kg
    {'name': 'Jamur Tiram Segar',    'kode': 'PRD-001', 'kategori': 'lainnya', 'minimum_stok': 10.0, 'uom_id': uom_kg.id},
    {'name': 'Jamur Shiitake Segar', 'kode': 'PRD-002', 'kategori': 'lainnya', 'minimum_stok': 5.0,  'uom_id': uom_kg.id},
    {'name': 'Jamur Kuping Segar',   'kode': 'PRD-003', 'kategori': 'lainnya', 'minimum_stok': 5.0,  'uom_id': uom_kg.id},
    # Herbal -> gram
    {'name': 'Rosemary Segar',       'kode': 'PRD-004', 'kategori': 'herbal',  'minimum_stok': 300.0,'uom_id': uom_g.id},
    {'name': 'Thyme Segar',          'kode': 'PRD-005', 'kategori': 'herbal',  'minimum_stok': 200.0,'uom_id': uom_g.id},
    {'name': 'Sage Segar',           'kode': 'PRD-006', 'kategori': 'herbal',  'minimum_stok': 150.0,'uom_id': uom_g.id},
    # Mint -> liter
    {'name': 'Mint Segar',           'kode': 'PRD-007', 'kategori': 'herbal',  'minimum_stok': 3.0,  'uom_id': uom_l.id},
    # Sayur -> kg
    {'name': 'Asparagus Segar',      'kode': 'PRD-008', 'kategori': 'sayur',   'minimum_stok': 5.0,  'uom_id': uom_kg.id},
]

produks = {}
for d in produk_data:
    rec = env['ipfarm.produk'].create(d)
    produks[d['name']] = rec
    uom_name = env['uom.uom'].browse(d['uom_id']).name
    print(f"    {d['kode']}: {d['name']} (satuan: {uom_name}, min stok: {d['minimum_stok']})")

env.cr.commit()

# Historis Penanaman
print("\n[6] Membuat data historis penanaman (sudah selesai)...")

pen1 = env['ipfarm.penanaman'].create({
    'tanggal_penanaman': today - timedelta(days=65),
    'pegawai_id': emp_budi.id,
    'catatan': 'Sesi tanam perdana Jamur Tiram - musim tanam Q1',
})
print(f"  {pen1.name}: Jamur Tiram ({today - timedelta(days=65)})")

b_tiram_1 = env['ipfarm.batch'].create({
    'penanaman_id': pen1.id, 'bibit_id': bibits['Jamur Tiram'].id,
    'ruangan_id': ruangans['RNG-A'].id, 'jumlah_bibit': 120,
    'estimasi_panen': today - timedelta(days=20), 'state': 'selesai',
})
b_tiram_2 = env['ipfarm.batch'].create({
    'penanaman_id': pen1.id, 'bibit_id': bibits['Jamur Tiram'].id,
    'ruangan_id': ruangans['RNG-A'].id, 'jumlah_bibit': 120,
    'estimasi_panen': today - timedelta(days=18), 'state': 'selesai',
})
b_tiram_3 = env['ipfarm.batch'].create({
    'penanaman_id': pen1.id, 'bibit_id': bibits['Jamur Tiram'].id,
    'ruangan_id': ruangans['RNG-A'].id, 'jumlah_bibit': 120,
    'estimasi_panen': today - timedelta(days=15), 'state': 'selesai',
})
print(f"    → {b_tiram_1.name}, {b_tiram_2.name}, {b_tiram_3.name} (state: selesai)")

pen2 = env['ipfarm.penanaman'].create({
    'tanggal_penanaman': today - timedelta(days=55),
    'pegawai_id': emp_budi.id,
    'catatan': 'Sesi tanam Jamur Shiitake - produk premium',
})
print(f"  {pen2.name}: Jamur Shiitake ({today - timedelta(days=55)})")

b_shiitake_1 = env['ipfarm.batch'].create({
    'penanaman_id': pen2.id, 'bibit_id': bibits['Jamur Shiitake'].id,
    'ruangan_id': ruangans['RNG-A'].id, 'jumlah_bibit': 100,
    'estimasi_panen': today - timedelta(days=10), 'state': 'selesai',
})
b_shiitake_2 = env['ipfarm.batch'].create({
    'penanaman_id': pen2.id, 'bibit_id': bibits['Jamur Shiitake'].id,
    'ruangan_id': ruangans['RNG-A'].id, 'jumlah_bibit': 100,
    'estimasi_panen': today - timedelta(days=8), 'state': 'selesai',
})
print(f"    → {b_shiitake_1.name}, {b_shiitake_2.name} (state: selesai)")

env.cr.commit()

# Historis Panen
print("\n[7] Mencatat data historis panen...")

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
    print(f"    {panen.name}: {jumlah} {produk.uom_id.name} {produk.name}")
    return panen

# Panen
catat_panen(b_tiram_1, produks['Jamur Tiram Segar'], 18.5, today - timedelta(days=19), emp_sari,
            'Panen flush pertama jamur tiram - kualitas A')
catat_panen(b_tiram_2, produks['Jamur Tiram Segar'], 16.0, today - timedelta(days=17), emp_sari,
            'Panen flush pertama batch 2 - kualitas A/B')
catat_panen(b_tiram_3, produks['Jamur Tiram Segar'], 15.0, today - timedelta(days=14), emp_sari,
            'Panen flush pertama batch 3')

catat_panen(b_shiitake_1, produks['Jamur Shiitake Segar'], 14.5, today - timedelta(days=9), emp_sari,
            'Panen shiitake batch 1 - kualitas premium')
catat_panen(b_shiitake_2, produks['Jamur Shiitake Segar'], 12.0, today - timedelta(days=7), emp_sari,
            'Panen shiitake batch 2')

env.cr.commit()
print("    Panen historis tersimpan, stok diperbarui otomatis.")

# Historis Pemrosesan
print("\n[8] Mencatat data historis pemrosesan...")

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
    print(f"    {prs.name}: {jenis} {jumlah} {produk.uom_id.name} {produk.name}")
    return prs

catat_pemrosesan(produks['Jamur Tiram Segar'], 'sortir', 5.0, today - timedelta(days=12), emp_raka,
                 'Sortir grade A/B/C - pisahkan jamur cacat')
catat_pemrosesan(produks['Jamur Tiram Segar'], 'pengemasan', 8.0, today - timedelta(days=8), emp_raka,
                 'Kemas 200g/pack untuk pengiriman ke resto')
catat_pemrosesan(produks['Jamur Shiitake Segar'], 'sortir', 2.5, today - timedelta(days=6), emp_raka,
                 'Sortir shiitake premium grade A')
catat_pemrosesan(produks['Jamur Shiitake Segar'], 'pengemasan', 2.0, today - timedelta(days=4), emp_raka,
                 'Kemas shiitake premium 100g/box')

env.cr.commit()
print("    Pemrosesan historis tersimpan, stok dikurangi otomatis.")

# Data Penanaman Aktif
print("\n[9] Membuat data penanaman AKTIF...")

pen3 = env['ipfarm.penanaman'].create({
    'tanggal_penanaman': today - timedelta(days=35),
    'pegawai_id': emp_budi.id,
    'catatan': 'Sesi tanam herbal - mint dan rosemary untuk musim ini',
})
print(f"  {pen3.name}: Herbal (Mint + Rosemary) - AKTIF")

b_mint_1 = env['ipfarm.batch'].create({
    'penanaman_id': pen3.id, 'bibit_id': bibits['Mint'].id,
    'ruangan_id': ruangans['RNG-B'].id, 'jumlah_bibit': 80,
    'estimasi_panen': today + timedelta(days=5),  
    'state': 'aktif',
    'catatan': 'Batch mint pertama - pertumbuhan sangat baik',
})
b_rosemary_1 = env['ipfarm.batch'].create({
    'penanaman_id': pen3.id, 'bibit_id': bibits['Rosemary'].id,
    'ruangan_id': ruangans['RNG-B'].id, 'jumlah_bibit': 60,
    'estimasi_panen': today + timedelta(days=55), 
    'state': 'aktif',
})
print(f"    → {b_mint_1.name}: Mint (est. panen {today + timedelta(days=5)}) ← untuk demo update estimasi")
print(f"    → {b_rosemary_1.name}: Rosemary (est. panen {today + timedelta(days=55)})")

pen4 = env['ipfarm.penanaman'].create({
    'tanggal_penanaman': today - timedelta(days=20),
    'pegawai_id': emp_budi.id,
    'catatan': 'Sesi tanam Asparagus - produk premium sayur',
})
print(f"  {pen4.name}: Asparagus - AKTIF")

b_asp_1 = env['ipfarm.batch'].create({
    'penanaman_id': pen4.id, 'bibit_id': bibits['Asparagus'].id,
    'ruangan_id': ruangans['RNG-C'].id, 'jumlah_bibit': 80,
    'estimasi_panen': today + timedelta(days=40), 'state': 'aktif',
})
b_asp_2 = env['ipfarm.batch'].create({
    'penanaman_id': pen4.id, 'bibit_id': bibits['Asparagus'].id,
    'ruangan_id': ruangans['RNG-C'].id, 'jumlah_bibit': 80,
    'estimasi_panen': today + timedelta(days=40), 'state': 'aktif',
})
print(f"    → {b_asp_1.name}, {b_asp_2.name}: Asparagus (est. panen {today + timedelta(days=40)})")

env.cr.commit()

print("\n" + "=" * 60)
print("SEED SELESAI!")
print("=" * 60)

print("\MASTER DATA:")
print(f"  Bibit   : {env['ipfarm.bibit'].search_count([])} jenis")
print(f"  Ruangan : {env['ipfarm.ruangan'].search_count([])} ruangan")
print(f"  Produk  : {env['ipfarm.produk'].search_count([])} jenis produk")

print("\nPENANAMAN & BATCH:")
print(f"  Penanaman total : {env['ipfarm.penanaman'].search_count([])} record")
print(f"  Batch total     : {env['ipfarm.batch'].search_count([])} batch")
print(f"  Batch aktif     : {env['ipfarm.batch'].search_count([('state','=','aktif')])} batch")
print(f"  Batch selesai   : {env['ipfarm.batch'].search_count([('state','=','selesai')])} batch")

print("\nTRANSAKSI:")
print(f"  Panen      : {env['ipfarm.panen'].search_count([])} record")
print(f"  Pemrosesan : {env['ipfarm.pemrosesan'].search_count([])} record")
print(f"  Histori Stok: {env['ipfarm.histori_stok'].search_count([])} record")

print("\nSTOK PRODUK SAAT INI:")
for p in env['ipfarm.produk'].search([]):
    status = {'aman': '✓ AMAN', 'rendah': '⚠ RENDAH', 'habis': '✗ HABIS'}.get(p.status_stok, p.status_stok)
    print(f"  {p.kode} {p.name}: {p.stok_tersedia:.1f} {p.uom_id.name} [{status}]")

print("\nAKUN DEMO:")
print("  Username            | Password    | Role")
print("  ------------------- | ----------- | -------------------")
print("  andi.manager        | ipfarm123  | Management (full access)")
print("  budi.pembibitan     | ipfarm123  | Divisi Pembibitan")
print("  sari.produksi       | ipfarm123  | Divisi Produksi")
print("  raka.processing     | ipfarm123  | Divisi Processing")
print("  diana.finance       | ipfarm123  | Divisi Finance")