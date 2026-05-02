from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmRuangan(models.Model):
    _name = "ipfarm.ruangan"
    _description = "Ruangan Tanam IP FarmBook"
    _order = "name"

    name = fields.Char(string="Nama Ruangan", required=True)
    kode = fields.Char(string="Kode Ruangan")
    active = fields.Boolean(default=True)
    kapasitas = fields.Integer(string="Kapasitas Bibit", default=0)
    lokasi = fields.Char(string="Lokasi")
    catatan = fields.Text(string="Catatan")

    _sql_constraints = [
        ("kode_ruangan_unique", "unique(kode)", "Kode ruangan harus unik."),
    ]

    @api.constrains("kapasitas")
    def _check_kapasitas(self):
        for ruangan in self:
            if ruangan.kapasitas < 0:
                raise ValidationError(_("Kapasitas ruangan tidak boleh negatif."))
