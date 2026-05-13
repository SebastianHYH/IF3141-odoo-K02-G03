from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmPenanaman(models.Model):
    _name = "ipfarm.penanaman"
    _description = "Penanaman Bibit IP FarmBook"
    _order = "tanggal_penanaman desc, id desc"

    name = fields.Char(
        string="Kode Penanaman",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    tanggal_penanaman = fields.Date(
        string="Tanggal Penanaman",
        required=True,
        default=fields.Date.context_today,
    )
    bibit_id = fields.Many2one(
        "ipfarm.bibit",
        string="Bibit",
        required=True,
        ondelete="restrict",
    )
    jumlah_batch = fields.Integer(string="Jumlah Batch", required=True, default=1)
    jumlah_bibit = fields.Integer(string="Jumlah Bibit Tertanam", required=True)
    ruangan_id = fields.Many2one(
        "ipfarm.ruangan",
        string="Ruangan Tanam",
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
    batch_ids = fields.One2many("ipfarm.batch", "penanaman_id", string="Batch")
    batch_count = fields.Integer(string="Jumlah Batch Dibuat", compute="_compute_batch_count")

    @api.model
    def _default_pegawai_id(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.uid)], limit=1)

    @api.depends("batch_ids")
    def _compute_batch_count(self):
        for penanaman in self:
            penanaman.batch_count = len(penanaman.batch_ids)

    @api.constrains("tanggal_penanaman")
    def _check_tanggal_penanaman(self):
        for penanaman in self:
            if not penanaman.tanggal_penanaman:
                raise ValidationError(_("Tanggal penanaman tidak boleh kosong."))

    @api.constrains("bibit_id")
    def _check_bibit_valid(self):
        for penanaman in self:
            if not penanaman.bibit_id or not penanaman.bibit_id.active:
                raise ValidationError(_("Bibit harus tersedia dan aktif."))

    @api.constrains("jumlah_batch", "jumlah_bibit")
    def _check_jumlah(self):
        for penanaman in self:
            if penanaman.jumlah_batch <= 0:
                raise ValidationError(_("Jumlah batch harus lebih dari 0."))
            if penanaman.jumlah_bibit <= 0:
                raise ValidationError(_("Jumlah bibit tertanam harus lebih dari 0."))

    @api.constrains("ruangan_id")
    def _check_ruangan_valid(self):
        for penanaman in self:
            if not penanaman.ruangan_id or not penanaman.ruangan_id.active:
                raise ValidationError(_("Ruangan tanam harus valid dan aktif."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("ipfarm.penanaman") or "New"
        records = super().create(vals_list)
        for penanaman in records:
            penanaman._create_batch_records()
        return records

    def _create_batch_records(self):
        for penanaman in self:
            if penanaman.batch_ids:
                continue
            estimasi = False
            if penanaman.bibit_id.estimasi_hari_panen and penanaman.tanggal_penanaman:
                estimasi = penanaman.tanggal_penanaman + timedelta(days=penanaman.bibit_id.estimasi_hari_panen)
            base_qty = penanaman.jumlah_bibit // penanaman.jumlah_batch
            remainder = penanaman.jumlah_bibit % penanaman.jumlah_batch
            batches = []
            for index in range(penanaman.jumlah_batch):
                qty = base_qty + (1 if index < remainder else 0)
                batches.append(
                    {
                        "name": "%s-B%02d" % (penanaman.name, index + 1),
                        "penanaman_id": penanaman.id,
                        "bibit_id": penanaman.bibit_id.id,
                        "ruangan_id": penanaman.ruangan_id.id,
                        "tanggal_tanam": penanaman.tanggal_penanaman,
                        "jumlah_bibit": qty,
                        "estimasi_panen": estimasi,
                        "state": "aktif",
                        "catatan": penanaman.catatan,
                    }
                )
            self.env["ipfarm.batch"].create(batches)

    def action_show_success(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Penanaman tersimpan"),
                "message": _("%s batch berhasil dibuat dan terhubung ke penanaman.") % len(self.batch_ids),
                "type": "success",
                "sticky": False,
            },
        }
