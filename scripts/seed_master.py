print("=== SEED Master Data IP FarmBook ===")

print("\n[0] Membersihkan master data lama...")
env['ipfarm.produk'].search([]).unlink()
env['ipfarm.bibit'].search([]).unlink()
env['ipfarm.ruangan'].search([]).unlink()
env.cr.commit()

print("\n[1] Membuat bibit...")
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
for d in bibit_data:
    env['ipfarm.bibit'].create(d)
    print(f"    {d['kode']} - {d['name']}")

print("\n[2] Membuat ruangan...")
ruangan_data = [
    {'name': 'Ruangan A - Budidaya Jamur', 'kode': 'RNG-A', 'kapasitas': 500, 'lokasi': 'Gedung Utama Lt.1'},
    {'name': 'Ruangan B - Herbal Indoor',  'kode': 'RNG-B', 'kapasitas': 200, 'lokasi': 'Gedung Utama Lt.2'},
    {'name': 'Ruangan C - Sayur & Buah',   'kode': 'RNG-C', 'kapasitas': 300, 'lokasi': 'Gedung Samping'},
]
for d in ruangan_data:
    env['ipfarm.ruangan'].create(d)
    print(f"    {d['kode']} - {d['name']}")

print("\n[3] Membuat produk...")
uom_kg = env.ref('uom.product_uom_kgm')
uom_g  = env.ref('uom.product_uom_gram')
uom_l  = env.ref('uom.product_uom_litre')
produk_data = [
    {'name': 'Jamur Tiram Segar',    'kode': 'PRD-001', 'kategori': 'lainnya', 'minimum_stok': 5.0,   'uom_id': uom_kg.id},
    {'name': 'Jamur Shiitake Segar', 'kode': 'PRD-002', 'kategori': 'lainnya', 'minimum_stok': 3.0,   'uom_id': uom_kg.id},
    {'name': 'Jamur Kuping Segar',   'kode': 'PRD-003', 'kategori': 'lainnya', 'minimum_stok': 3.0,   'uom_id': uom_kg.id},
    {'name': 'Jamur Maitake Segar',  'kode': 'PRD-004', 'kategori': 'lainnya', 'minimum_stok': 2.0,   'uom_id': uom_kg.id},
    {'name': 'Asparagus Segar',      'kode': 'PRD-006', 'kategori': 'sayur',   'minimum_stok': 4.0,   'uom_id': uom_kg.id},
    {'name': 'Golden Berry',         'kode': 'PRD-007', 'kategori': 'buah',    'minimum_stok': 2.0,   'uom_id': uom_kg.id},
    {'name': 'Rosemary Segar',       'kode': 'PRD-005', 'kategori': 'herbal',  'minimum_stok': 200.0, 'uom_id': uom_g.id},
    {'name': 'Thyme Segar',          'kode': 'PRD-008', 'kategori': 'herbal',  'minimum_stok': 150.0, 'uom_id': uom_g.id},
    {'name': 'Sage Segar',           'kode': 'PRD-010', 'kategori': 'herbal',  'minimum_stok': 100.0, 'uom_id': uom_g.id},
    {'name': 'Oregano Segar',        'kode': 'PRD-011', 'kategori': 'herbal',  'minimum_stok': 100.0, 'uom_id': uom_g.id},
    {'name': 'Mint Segar',           'kode': 'PRD-009', 'kategori': 'herbal',  'minimum_stok': 2.0,   'uom_id': uom_l.id},
]
for d in produk_data:
    env['ipfarm.produk'].create(d)
    print(f"    {d['kode']} - {d['name']}")

env.cr.commit()

print("\n" + "=" * 45)
print(f"  Bibit   : {env['ipfarm.bibit'].search_count([])} record")
print(f"  Ruangan : {env['ipfarm.ruangan'].search_count([])} record")
print(f"  Produk  : {env['ipfarm.produk'].search_count([])} record")
print("=" * 45)
