from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmBibit(models.Model):
    _name = "ipfarm.bibit"
    _description = "Bibit IP FarmBook"
    _order = "name"

    name = fields.Char(string="Nama Bibit", required=True)
    kode = fields.Char(string="Kode Bibit")
    active = fields.Boolean(default=True)
    kategori = fields.Selection(
        [
            ("sayur", "Sayur"),
            ("buah", "Buah"),
            ("herbal", "Herbal"),
            ("lainnya", "Lainnya"),
        ],
        string="Kategori",
        default="sayur",
        required=True,
    )
    estimasi_hari_panen = fields.Integer(string="Estimasi Hari Panen", default=30)
    catatan = fields.Text(string="Catatan")

    _sql_constraints = [
        ("kode_bibit_unique", "unique(kode)", "Kode bibit harus unik."),
    ]

    @api.constrains("estimasi_hari_panen")
    def _check_estimasi_hari_panen(self):
        for bibit in self:
            if bibit.estimasi_hari_panen <= 0:
                raise ValidationError(_("Estimasi hari panen harus lebih dari 0."))
