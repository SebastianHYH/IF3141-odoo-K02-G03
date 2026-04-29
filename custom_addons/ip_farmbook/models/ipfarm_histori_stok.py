from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmHistoriStok(models.Model):
    _name = "ipfarm.histori_stok"
    _description = "Histori Perubahan Stok IP FarmBook"
    _order = "tanggal desc, id desc"

    name = fields.Char(string="Referensi", compute="_compute_name", store=True)
    produk_id = fields.Many2one(
        "ipfarm.produk",
        string="Produk",
        required=True,
        ondelete="restrict",
        index=True,
    )
    jenis_kegiatan = fields.Selection(
        [
            ("panen", "Panen"),
            ("pemrosesan", "Pemrosesan"),
            ("penyesuaian", "Penyesuaian"),
        ],
        string="Jenis Kegiatan",
        required=True,
        index=True,
    )
    arah = fields.Selection(
        [
            ("masuk", "Masuk"),
            ("keluar", "Keluar"),
        ],
        string="Arah Stok",
        required=True,
    )
    jumlah = fields.Float(string="Jumlah Perubahan", required=True)
    jumlah_masuk = fields.Float(
        string="Jumlah Masuk",
        compute="_compute_jumlah_masuk_keluar",
        store=True,
    )
    jumlah_keluar = fields.Float(
        string="Jumlah Keluar",
        compute="_compute_jumlah_masuk_keluar",
        store=True,
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Satuan",
        required=True,
        ondelete="restrict",
    )
    tanggal = fields.Date(
        string="Tanggal Perubahan",
        required=True,
        default=fields.Date.context_today,
        index=True,
    )
    panen_id = fields.Many2one(
        "ipfarm.panen",
        string="Referensi Hasil Panen",
        ondelete="restrict",
    )
    pemrosesan_id = fields.Many2one(
        "ipfarm.pemrosesan",
        string="Referensi Pemrosesan",
        ondelete="restrict",
    )
    pegawai_id = fields.Many2one(
        "hr.employee",
        string="Pegawai Pencatat",
        required=True,
        ondelete="restrict",
    )
    catatan = fields.Text(string="Catatan")

    @api.depends("produk_id", "jenis_kegiatan", "tanggal", "jumlah", "uom_id")
    def _compute_name(self):
        for history in self:
            if history.produk_id and history.tanggal:
                history.name = "%s - %s - %s" % (
                    dict(history._fields["jenis_kegiatan"].selection).get(
                        history.jenis_kegiatan,
                        history.jenis_kegiatan,
                    ),
                    history.produk_id.display_name,
                    history.tanggal,
                )
            else:
                history.name = "Perubahan Stok"

    @api.depends("arah", "jumlah")
    def _compute_jumlah_masuk_keluar(self):
        for history in self:
            history.jumlah_masuk = history.jumlah if history.arah == "masuk" else 0.0
            history.jumlah_keluar = history.jumlah if history.arah == "keluar" else 0.0

    @api.constrains("jumlah")
    def _check_jumlah_positive(self):
        for history in self:
            if history.jumlah <= 0:
                raise ValidationError(_("Jumlah perubahan stok harus lebih dari 0."))

    @api.constrains("jenis_kegiatan", "arah")
    def _check_arah_kegiatan(self):
        for history in self:
            if history.jenis_kegiatan == "panen" and history.arah != "masuk":
                raise ValidationError(_("Kegiatan panen harus menambah stok."))
            if history.jenis_kegiatan == "pemrosesan" and history.arah != "keluar":
                raise ValidationError(_("Kegiatan pemrosesan harus mengurangi stok."))
