from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class IPFarmProduk(models.Model):
    _name = "ipfarm.produk"
    _description = "Produk IP FarmBook"
    _order = "name"

    name = fields.Char(string="Nama Produk", required=True)
    kode = fields.Char(string="Kode Produk")
    active = fields.Boolean(default=True)
    kategori = fields.Selection(
        [
            ("sayur", "Sayur"),
            ("buah", "Buah"),
            ("herbal", "Herbal"),
            ("hasil_olahan", "Hasil Olahan"),
            ("lainnya", "Lainnya"),
        ],
        string="Kategori/Jenis",
        default="sayur",
        required=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Satuan Stok",
        required=True,
        default=lambda self: self.env.ref("uom.product_uom_kgm", raise_if_not_found=False),
        ondelete="restrict",
    )
    minimum_stok = fields.Float(string="Batas Stok Rendah", default=0.0)
    stok_tersedia = fields.Float(
        string="Stok Tersedia Saat Ini",
        default=0.0,
        readonly=True,
        copy=False,
    )
    total_stok_masuk_panen = fields.Float(
        string="Total Stok Masuk dari Panen",
        compute="_compute_ringkasan_stok",
        store=True,
    )
    total_stok_keluar_pemrosesan = fields.Float(
        string="Total Stok Keluar akibat Pemrosesan",
        compute="_compute_ringkasan_stok",
        store=True,
    )
    last_stock_update = fields.Date(
        string="Tanggal Pembaruan Terakhir",
        compute="_compute_ringkasan_stok",
        store=True,
    )
    status_stok = fields.Selection(
        [
            ("habis", "Habis"),
            ("rendah", "Rendah"),
            ("aman", "Aman"),
        ],
        string="Status Stok",
        compute="_compute_status_stok",
        store=True,
    )
    histori_ids = fields.One2many(
        "ipfarm.histori_stok",
        "produk_id",
        string="Riwayat Perubahan Stok",
    )
    panen_ids = fields.One2many("ipfarm.panen", "produk_id", string="Hasil Panen")
    pemrosesan_ids = fields.One2many(
        "ipfarm.pemrosesan",
        "produk_id",
        string="Pemrosesan",
    )

    _sql_constraints = [
        ("kode_unique", "unique(kode)", "Kode produk harus unik."),
    ]

    @api.constrains("minimum_stok", "stok_tersedia")
    def _check_non_negative_stock_fields(self):
        for product in self:
            if product.minimum_stok < 0:
                raise ValidationError(_("Batas stok rendah tidak boleh negatif."))
            if product.stok_tersedia < 0:
                raise ValidationError(_("Stok tersedia tidak boleh negatif."))

    @api.depends(
        "histori_ids.jenis_kegiatan",
        "histori_ids.jumlah_masuk",
        "histori_ids.jumlah_keluar",
        "histori_ids.tanggal",
    )
    def _compute_ringkasan_stok(self):
        for product in self:
            histories = product.histori_ids
            product.total_stok_masuk_panen = sum(
                histories.filtered(lambda h: h.jenis_kegiatan == "panen").mapped("jumlah_masuk")
            )
            product.total_stok_keluar_pemrosesan = sum(
                histories.filtered(lambda h: h.jenis_kegiatan == "pemrosesan").mapped("jumlah_keluar")
            )
            product.last_stock_update = max(histories.mapped("tanggal")) if histories else False

    @api.depends("stok_tersedia", "minimum_stok")
    def _compute_status_stok(self):
        for product in self:
            if product.stok_tersedia <= 0:
                product.status_stok = "habis"
            elif product.minimum_stok and product.stok_tersedia <= product.minimum_stok:
                product.status_stok = "rendah"
            else:
                product.status_stok = "aman"

    def _catat_pergerakan_stok(
        self,
        *,
        jenis_kegiatan,
        arah,
        jumlah,
        tanggal,
        pegawai_id,
        panen_id=False,
        pemrosesan_id=False,
        catatan=False,
    ):
        self.ensure_one()
        rounding = self.uom_id.rounding or 0.01
        if float_compare(jumlah, 0.0, precision_rounding=rounding) <= 0:
            raise ValidationError(_("Jumlah perubahan stok harus lebih dari 0."))
        if not tanggal:
            raise ValidationError(_("Tanggal perubahan stok tidak boleh kosong."))
        if not pegawai_id:
            raise ValidationError(_("Pegawai pencatat harus diisi."))

        delta = jumlah if arah == "masuk" else -jumlah
        stok_baru = self.stok_tersedia + delta
        if float_compare(stok_baru, 0.0, precision_rounding=rounding) < 0:
            raise UserError(
                _(
                    "Stok produk %(produk)s tidak mencukupi. "
                    "Stok tersedia %(stok).2f %(satuan)s, kebutuhan %(jumlah).2f %(satuan)s."
                )
                % {
                    "produk": self.display_name,
                    "stok": self.stok_tersedia,
                    "jumlah": jumlah,
                    "satuan": self.uom_id.display_name,
                }
            )

        self.write({"stok_tersedia": stok_baru})
        return self.env["ipfarm.histori_stok"].create(
            {
                "produk_id": self.id,
                "jenis_kegiatan": jenis_kegiatan,
                "arah": arah,
                "jumlah": jumlah,
                "uom_id": self.uom_id.id,
                "tanggal": tanggal,
                "panen_id": panen_id,
                "pemrosesan_id": pemrosesan_id,
                "pegawai_id": pegawai_id,
                "catatan": catatan,
            }
        )
