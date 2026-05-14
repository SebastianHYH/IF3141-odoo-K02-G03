# IP FarmBook - Custom Odoo Addon

IP FarmBook adalah aplikasi ERP berbasis Odoo 17 untuk mendukung pencatatan operasional budidaya pertanian urban/indoor farm. Aplikasi ini dikembangkan sebagai custom addon pada proyek IF3141 Sistem Informasi K02 G03, dengan fokus pada alur penanaman, pengelolaan batch, pencatatan panen, pemrosesan hasil, monitoring stok, dashboard operasional, dan rekap laporan.

Repository ini sudah menyediakan konfigurasi Docker untuk menjalankan Odoo dan PostgreSQL secara lokal, serta beberapa script seed untuk menyiapkan data master, akun pengguna, dan data transaksi contoh.

## Ringkasan Aplikasi

Addon utama berada pada folder `custom_addons/ip_farmbook` dengan nama modul **IP FarmBook**.

Informasi modul:

| Item | Nilai |
| --- | --- |
| Nama modul | `IP FarmBook` |
| Technical name | `ip_farmbook` |
| Versi Odoo | `17.0` |
| Kategori | `Agriculture` |
| Dependensi | `base`, `hr`, `uom` |
| Lisensi | `LGPL-3` |

## Fitur Utama

### 1. Master Data

IP FarmBook menyediakan master data untuk fondasi operasional:

- **Bibit**: nama bibit, kode bibit, kategori, estimasi hari panen, dan catatan.
- **Ruangan Tanam**: nama ruangan, kode ruangan, kapasitas bibit, lokasi, dan catatan.
- **Produk**: nama produk, kode produk, kategori, satuan stok, batas stok rendah, stok tersedia, status stok, dan riwayat stok.

Kode bibit, kode ruangan, dan kode produk dibuat unik agar data referensi tidak ganda.

### 2. Penanaman dan Batch

Alur penanaman digunakan untuk mencatat sesi tanam. Setiap sesi penanaman dapat memiliki beberapa batch.

Fitur yang tersedia:

- Nomor penanaman otomatis dengan format sequence `TAN/<tahun>/<nomor>`.
- Batch per penanaman dengan format turunan seperti `TAN/2026/00001/B01`.
- Pencatatan bibit, ruangan, tanggal tanam, jumlah bibit, estimasi panen, dan status batch.
- Status batch: `Aktif` dan `Selesai`.
- Validasi jumlah bibit tidak boleh negatif.
- Validasi estimasi panen tidak boleh lebih awal dari tanggal tanam.
- Histori perubahan estimasi panen.

### 3. Panen

Menu panen digunakan untuk mencatat hasil panen dari batch tertentu.

Fitur yang tersedia:

- Nomor panen otomatis dengan format sequence `PAN/<tahun>/<nomor>`.
- Pencatatan batch, produk hasil panen, jumlah, satuan, tanggal panen, pegawai pencatat, dan catatan.
- Validasi produk dan batch harus aktif.
- Validasi jumlah panen harus lebih dari 0.
- Konversi satuan mengikuti kategori satuan produk Odoo.
- Setelah panen disimpan, stok produk otomatis bertambah dan histori stok otomatis dibuat.
- Data panen yang sudah tersimpan tidak dapat diubah atau dihapus karena sudah memengaruhi stok.

### 4. Pemrosesan Produk

Menu pemrosesan digunakan untuk mencatat penggunaan atau pengurangan stok produk karena kegiatan operasional setelah panen.

Jenis pemrosesan:

- Sortir
- Pengemasan
- Pengolahan
- Pemindahan
- Lainnya

Fitur yang tersedia:

- Nomor pemrosesan otomatis dengan format sequence `PRS/<tahun>/<nomor>`.
- Pencatatan produk, jenis pemrosesan, jumlah, satuan, tanggal pemrosesan, pegawai pencatat, dan catatan.
- Validasi jumlah harus lebih dari 0.
- Validasi stok tidak boleh menjadi negatif.
- Setelah pemrosesan disimpan, stok produk otomatis berkurang dan histori stok otomatis dibuat.
- Data pemrosesan yang sudah tersimpan tidak dapat diubah atau dihapus karena sudah memengaruhi stok.

### 5. Histori Stok

Setiap perubahan stok dicatat pada model histori stok.

Histori stok mencatat:

- Produk
- Jenis kegiatan: panen, pemrosesan, atau penyesuaian
- Arah stok: masuk atau keluar
- Jumlah perubahan
- Satuan
- Tanggal perubahan
- Referensi panen atau pemrosesan
- Pegawai pencatat
- Catatan

Histori ini menjadi dasar untuk audit stok, grafik dashboard, dan laporan operasional.

### 6. Dashboard Operasional

Dashboard analitik menyediakan ringkasan operasional dengan filter tanggal, produk, ruangan, dan batch.

KPI yang tersedia:

- Jumlah batch aktif
- Jumlah penanaman berjalan
- Estimasi panen terdekat
- Total hasil panen
- Total pemrosesan
- Total stok masuk
- Total stok keluar
- Stok produk terkini
- Jumlah produk stok rendah atau habis
- Prediksi sederhana durasi panen dan proyeksi stok 7 hari

Dashboard juga menyediakan akses ke analisis grafik dan pivot untuk hasil panen serta histori stok.

### 7. Laporan PDF

IP FarmBook menyediakan wizard rekap operasional dengan output PDF.

Jenis rekap:

- Hasil panen
- Stok produk
- Histori stok
- Pemrosesan produk

Filter laporan:

- Tanggal mulai
- Tanggal selesai
- Produk
- Ruangan

## Hak Akses

Addon mendefinisikan beberapa grup pengguna:

| Grup | Peran |
| --- | --- |
| `Management` | Pengawasan menyeluruh dan akses manajerial |
| `Divisi Pembibitan` | Pengelolaan data bibit dan aktivitas pembibitan |
| `Divisi Produksi/Growing` | Aktivitas penanaman, batch, dan panen |
| `Divisi Processing` | Aktivitas pemrosesan produk |
| `Divisi Finance` | Akses data rekap dan monitoring terkait laporan |
| `User` | Grup dasar untuk pengguna IP FarmBook |

Script `scripts/seed_users.py` dapat digunakan untuk membuat akun uji sesuai grup tersebut.

## Struktur Repository

```text
.
|-- config/
|   `-- odoo.conf
|-- custom_addons/
|   `-- ip_farmbook/
|       |-- data/
|       |   `-- ipfarm_sequence.xml
|       |-- models/
|       |-- report/
|       |-- security/
|       |-- views/
|       |-- __init__.py
|       `-- __manifest__.py
|-- dump/
|-- scripts/
|   |-- export_db.cmd
|   |-- export_db.sh
|   |-- import_db.cmd
|   |-- import_db.sh
|   |-- seed_data.py
|   |-- seed_master.py
|   `-- seed_users.py
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

Keterangan penting:

- `custom_addons/ip_farmbook/models`: definisi model bisnis IP FarmBook.
- `custom_addons/ip_farmbook/views`: tampilan form, tree, graph, pivot, dashboard, dan menu.
- `custom_addons/ip_farmbook/security`: grup pengguna dan access control.
- `custom_addons/ip_farmbook/report`: template dan action laporan PDF.
- `scripts`: script database dump/restore dan seed data.
- `docker-compose.yml`: konfigurasi service Odoo 17, PostgreSQL 16, dan helper Alpine.

## Prasyarat

Pastikan dependency berikut sudah tersedia:

1. Docker Desktop atau Docker Engine dengan Docker Compose.
2. Python 3.11, jika ingin menggunakan virtual environment lokal untuk development.
3. Git.

## Menjalankan Aplikasi

Jalankan service Odoo dan PostgreSQL:

```bash
docker compose up -d
```

Cek status container:

```bash
docker compose ps
```

Buka aplikasi di browser:

```text
http://localhost:8069
```

Kredensial awal Odoo:

| Login | Password |
| --- | --- |
| `admin` | `admin` |

Jika database belum dibuat, buat database Odoo melalui halaman awal di browser. Konfigurasi compose menggunakan database PostgreSQL dengan user `odoo` dan password `password`.

## Instalasi Modul IP FarmBook

Setelah Odoo berjalan:

1. Login sebagai `admin`.
2. Aktifkan Developer Mode melalui menu **Settings**.
3. Buka menu **Apps**.
4. Klik **Update Apps List**.
5. Cari **IP FarmBook**.
6. Klik **Activate** atau **Install**.

Jika modul sudah terpasang dan terdapat perubahan kode, update modul dengan command:

```bash
docker compose exec web odoo -d postgres -u ip_farmbook --stop-after-init --no-http
```

Setelah command selesai, jalankan ulang service:

```bash
docker compose restart web
```

## Menjalankan Script Seed

Semua script seed dijalankan melalui `odoo shell`, sehingga environment Odoo, model, ORM, dan database aktif dapat digunakan langsung.

Pastikan service sedang berjalan:

```bash
docker compose up -d
```

### 1. Seed Master Data

Script ini membuat data master bibit, ruangan, dan produk.

```bash
docker compose exec -T web odoo shell -d postgres --no-http < scripts/seed_master.py
```

Catatan: script ini membersihkan master data lama sebelum membuat data baru.

### 2. Seed User Uji

Script ini membuat akun uji dan menghubungkannya dengan grup akses IP FarmBook.

```bash
docker compose exec -T web odoo shell -d postgres --no-http < scripts/seed_users.py
```

Akun yang dibuat:

| Login | Password | Role |
| --- | --- | --- |
| `admin` | `admin` | Administrator |
| `management` | `ipfarm123` | Management |
| `pembibitan` | `ipfarm123` | Divisi Pembibitan |
| `produksi` | `ipfarm123` | Divisi Produksi/Growing |
| `processing` | `ipfarm123` | Divisi Processing |
| `finance` | `ipfarm123` | Divisi Finance |

### 3. Seed Data Lengkap

Script ini membuat data demo yang lebih lengkap, termasuk employee, bibit, ruangan, produk, penanaman, batch, update estimasi panen, panen, pemrosesan, dan histori stok.

```bash
docker compose exec -T web odoo shell -d postgres --no-http < scripts/seed_data.py
```

Peringatan: script ini menghapus data IP FarmBook lama sebelum membuat data demo baru. Gunakan hanya pada environment development atau demo.

## Menjalankan File dan Command Pendukung

### Melihat Log Odoo

```bash
docker compose logs -f web
```

### Masuk ke Odoo Shell

```bash
docker compose exec web odoo shell -d postgres --no-http
```

Contoh cek jumlah produk dari Odoo shell:

```python
env["ipfarm.produk"].search_count([])
```

### Restart Service

```bash
docker compose restart
```

### Stop Service

```bash
docker compose down
```

### Reset Container dan Volume

Gunakan command ini hanya jika ingin menghapus state database lokal dan memulai dari awal.

```bash
docker compose down -v
docker compose up -d
```

## Export dan Import Database

Repository menyediakan script dump dan restore database di folder `scripts`.

Sebelum export atau import database, matikan service:

```bash
docker compose down
```

Export database:

```bash
./scripts/export_db.sh
```

Import database:

```bash
./scripts/import_db.sh
```

Untuk Windows:

```bat
scripts\export_db.cmd
scripts\import_db.cmd
```

File dump disimpan pada folder `dump`.

## Development Lokal

Virtual environment Python dapat dibuat untuk kebutuhan linting, editor integration, atau development script pendukung.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Setelah mengubah file Python, XML view, security, report, atau manifest, update modul:

```bash
docker compose exec web odoo -d postgres -u ip_farmbook --stop-after-init --no-http
docker compose restart web
```

Jika hanya mengubah tampilan XML dan perubahan belum muncul, lakukan:

1. Update modul `ip_farmbook`.
2. Refresh browser.
3. Jika perlu, aktifkan Developer Mode dan clear asset/cache dari Odoo.

## Alur Operasional yang Direkomendasikan

Urutan penggunaan aplikasi:

1. Isi master data **Bibit**, **Ruangan**, dan **Produk**.
2. Buat sesi **Penanaman**.
3. Tambahkan satu atau beberapa **Batch** pada penanaman.
4. Update **Estimasi Panen** jika ada perubahan kondisi budidaya.
5. Catat **Panen** ketika batch menghasilkan produk.
6. Catat **Pemrosesan Produk** untuk aktivitas sortir, pengemasan, pengolahan, pemindahan, atau aktivitas lain.
7. Monitor stok melalui **Produk** dan **Histori Stok**.
8. Gunakan **Dashboard** untuk memantau KPI.
9. Gunakan **Rekap Laporan** untuk mencetak laporan PDF.

## Troubleshooting

### Modul IP FarmBook tidak muncul di Apps

Pastikan volume addon sudah terpasang di `docker-compose.yml`:

```yaml
./custom_addons:/mnt/extras-addons
```

Lalu lakukan **Update Apps List** dari menu Apps.

### Perubahan kode belum muncul

Update modul dan restart service:

```bash
docker compose exec web odoo -d postgres -u ip_farmbook --stop-after-init --no-http
docker compose restart web
```

### Error akses menu atau model

Periksa apakah user sudah masuk ke salah satu grup IP FarmBook. Untuk data uji, jalankan:

```bash
docker compose exec -T web odoo shell -d postgres --no-http < scripts/seed_users.py
```

### Error stok tidak mencukupi

Pemrosesan produk akan ditolak jika jumlah pemrosesan melebihi stok tersedia. Tambahkan stok melalui transaksi panen atau sesuaikan data demo.

### Seed gagal karena modul belum terpasang

Pastikan modul IP FarmBook sudah di-install terlebih dahulu. Model seperti `ipfarm.produk`, `ipfarm.panen`, dan `ipfarm.batch` hanya tersedia setelah modul aktif.

## Catatan Teknis

- Aplikasi menggunakan ORM Odoo untuk menjaga integritas data.
- Transaksi panen dan pemrosesan bersifat audit-friendly: setelah tersimpan, field utama tidak dapat diubah karena sudah memengaruhi stok.
- Histori stok menjadi sumber pencatatan masuk dan keluar.
- Validasi stok menggunakan `float_compare` Odoo agar sesuai dengan presisi satuan.
- Satuan produk menggunakan modul `uom`, sehingga transaksi dapat memanfaatkan konversi satuan Odoo selama berada dalam kategori satuan yang sama.

## Kontributor

Proyek ini dikembangkan oleh IF3141 K02 G03 untuk kebutuhan tugas besar Sistem Informasi.
