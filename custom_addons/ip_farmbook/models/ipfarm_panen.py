from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmPanen(models.Model):
    _name = "ipfarm.panen"
    _description = "Hasil Panen IP FarmBook"
    _order = "tanggal_panen desc, id desc"

    name = fields.Char(
        string="Nomor Panen",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    batch_id = fields.Many2one(
        "ipfarm.batch",
        string="Batch/Penanaman Terkait",
        required=True,
        ondelete="restrict",
    )
    penanaman_id = fields.Many2one(
        "ipfarm.penanaman",
        string="Penanaman Terkait",
        related="batch_id.penanaman_id",
        store=True,
        readonly=True,
    )
    tanggal_panen = fields.Date(
        string="Tanggal Panen",
        required=True,
        default=fields.Date.context_today,
    )
    produk_id = fields.Many2one(
        "ipfarm.produk",
        string="Produk Hasil Panen",
        required=True,
        ondelete="restrict",
    )
    jumlah = fields.Float(string="Jumlah/Berat Hasil Panen", required=True)
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
    catatan = fields.Text(string="Catatan Opsional")
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
        for panen in self:
            if panen.jumlah <= 0:
                raise ValidationError(_("Jumlah hasil panen harus lebih dari 0."))

    @api.constrains("batch_id")
    def _check_batch_valid(self):
        for panen in self:
            if not panen.batch_id or not panen.batch_id.active:
                raise ValidationError(_("Batch/penanaman harus valid dan aktif."))

    @api.constrains("produk_id")
    def _check_produk_valid(self):
        for panen in self:
            if not panen.produk_id or not panen.produk_id.active:
                raise ValidationError(_("Produk hasil panen harus terdaftar dan aktif."))

    @api.constrains("produk_id", "uom_id")
    def _check_uom_compatible(self):
        for panen in self:
            if (
                panen.produk_id
                and panen.uom_id
                and panen.produk_id.uom_id.category_id != panen.uom_id.category_id
            ):
                raise ValidationError(
                    _("Satuan panen harus berada pada kategori yang sama dengan satuan stok produk.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("ipfarm.panen") or "New"
        records = super().create(vals_list)
        for panen in records:
            jumlah_stok = panen.uom_id._compute_quantity(panen.jumlah, panen.produk_id.uom_id)
            history = panen.produk_id._catat_pergerakan_stok(
                jenis_kegiatan="panen",
                arah="masuk",
                jumlah=jumlah_stok,
                tanggal=panen.tanggal_panen,
                pegawai_id=panen.pegawai_id.id,
                panen_id=panen.id,
                catatan=panen.catatan,
            )
            panen.histori_stok_id = history.id
        return records

    def write(self, vals):
        protected_fields = {"batch_id", "tanggal_panen", "produk_id", "jumlah", "uom_id", "pegawai_id"}
        if protected_fields.intersection(vals):
            raise ValidationError(
                _(
                    "Data panen yang sudah tersimpan tidak dapat diubah karena stok dan histori "
                    "sudah diposting. Buat transaksi koreksi melalui histori/penyesuaian stok bila diperlukan."
                )
            )
        return super().write(vals)

    def unlink(self):
        if self.env.context.get("module_uninstall"):
            return super().unlink()
        raise ValidationError(
            _(
                "Data panen tidak dapat dihapus karena sudah memengaruhi stok produk. "
                "Gunakan transaksi penyesuaian untuk koreksi stok."
            )
        )

    def action_lihat_stok_produk(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Ketersediaan Stok Produk"),
            "res_model": "ipfarm.produk",
            "res_id": self.produk_id.id,
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "current",
        }
