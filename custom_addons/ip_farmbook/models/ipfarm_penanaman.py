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
    pegawai_id = fields.Many2one(
        "hr.employee",
        string="Pegawai Pencatat",
        required=True,
        ondelete="restrict",
        default=lambda self: self._default_pegawai_id(),
    )
    catatan = fields.Text(string="Catatan")
    batch_ids = fields.One2many("ipfarm.batch", "penanaman_id", string="Batch")
    batch_count = fields.Integer(string="Jumlah Batch", compute="_compute_batch_count")

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("ipfarm.penanaman") or "New"
        return super().create(vals_list)
