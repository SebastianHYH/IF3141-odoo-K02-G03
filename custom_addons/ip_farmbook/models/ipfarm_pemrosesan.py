from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmPemrosesan(models.Model):
    _name = "ipfarm.pemrosesan"
    _description = "Pemrosesan Produk IP FarmBook"
    _order = "tanggal_pemrosesan desc, id desc"

    name = fields.Char(
        string="Nomor Pemrosesan",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    tanggal_pemrosesan = fields.Date(
        string="Tanggal Pemrosesan",
        required=True,
        default=fields.Date.context_today,
    )
    produk_id = fields.Many2one(
        "ipfarm.produk",
        string="Produk Diproses",
        required=True,
        ondelete="restrict",
    )
    jenis_pemrosesan = fields.Selection(
        [
            ("sortir", "Sortir"),
            ("pengemasan", "Pengemasan"),
            ("pengolahan", "Pengolahan"),
            ("pemindahan", "Pemindahan"),
            ("lainnya", "Lainnya"),
        ],
        string="Jenis Pemrosesan",
        required=True,
        default="sortir",
    )
    jumlah = fields.Float(string="Volume Diproses", required=True)
    uom_id = fields.Many2one(
        "uom.uom",
        string="Satuan",
        required=True,
        ondelete="restrict",
    )
    pegawai_id = fields.Many2one(
        "hr.employee",
        string="Pegawai Pencatat",
        required=True,
        ondelete="restrict",
        default=lambda self: self._default_pegawai_id(),
    )
    catatan = fields.Text(string="Catatan")
    histori_stok_id = fields.Many2one(
        "ipfarm.histori_stok",
        string="Histori Stok",
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        [
            ("done", "Tersimpan"),
        ],
        string="Status",
        default="done",
        required=True,
        readonly=True,
    )

    @api.model
    def _default_pegawai_id(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.uid)], limit=1)

    @api.onchange("produk_id")
    def _onchange_produk_id(self):
        if self.produk_id:
            self.uom_id = self.produk_id.uom_id

    @api.constrains("jumlah")
    def _check_jumlah_positive(self):
        for pemrosesan in self:
            if pemrosesan.jumlah <= 0:
                raise ValidationError(_("Jumlah pemrosesan harus lebih dari 0."))

    @api.constrains("produk_id")
    def _check_produk_valid(self):
        for pemrosesan in self:
            if not pemrosesan.produk_id or not pemrosesan.produk_id.active:
                raise ValidationError(_("Produk yang diproses harus terdaftar dan aktif."))

    @api.constrains("produk_id", "uom_id")
    def _check_uom_compatible(self):
        for pemrosesan in self:
            if (
                pemrosesan.produk_id
                and pemrosesan.uom_id
                and pemrosesan.produk_id.uom_id.category_id != pemrosesan.uom_id.category_id
            ):
                raise ValidationError(
                    _("Satuan pemrosesan harus berada pada kategori yang sama dengan satuan stok produk.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("ipfarm.pemrosesan") or "New"
        records = super().create(vals_list)
        for pemrosesan in records:
            jumlah_stok = pemrosesan.uom_id._compute_quantity(
                pemrosesan.jumlah,
                pemrosesan.produk_id.uom_id,
            )
            history = pemrosesan.produk_id._catat_pergerakan_stok(
                jenis_kegiatan="pemrosesan",
                arah="keluar",
                jumlah=jumlah_stok,
                tanggal=pemrosesan.tanggal_pemrosesan,
                pegawai_id=pemrosesan.pegawai_id.id,
                pemrosesan_id=pemrosesan.id,
                catatan=pemrosesan.catatan,
            )
            pemrosesan.histori_stok_id = history.id
        return records

    def write(self, vals):
        protected_fields = {"tanggal_pemrosesan", "produk_id", "jenis_pemrosesan", "jumlah", "uom_id", "pegawai_id"}
        if protected_fields.intersection(vals):
            raise ValidationError(
                _(
                    "Data pemrosesan yang sudah tersimpan tidak dapat diubah karena stok dan histori "
                    "sudah diposting. Buat transaksi koreksi melalui histori/penyesuaian stok bila diperlukan."
                )
            )
        return super().write(vals)

    def unlink(self):
        if self.env.context.get("module_uninstall"):
            return super().unlink()
        raise ValidationError(
            _(
                "Data pemrosesan tidak dapat dihapus karena sudah memengaruhi stok produk. "
                "Gunakan transaksi penyesuaian untuk koreksi stok."
            )
        )
