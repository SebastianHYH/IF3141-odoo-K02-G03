from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmBatch(models.Model):
    _name = "ipfarm.batch"
    _description = "Batch Penanaman IP FarmBook"
    _order = "tanggal_tanam desc, name"

    name = fields.Char(string="Nama Batch", required=True)
    active = fields.Boolean(default=True)
    penanaman_id = fields.Many2one(
        "ipfarm.penanaman",
        string="Kode Penanaman",
        ondelete="restrict",
        index=True,
    )
    bibit_id = fields.Many2one(
        "ipfarm.bibit",
        string="Bibit",
        ondelete="restrict",
    )
    ruangan_id = fields.Many2one(
        "ipfarm.ruangan",
        string="Ruangan Tanam",
        ondelete="restrict",
    )
    tanggal_tanam = fields.Date(string="Tanggal Tanam")
    jumlah_bibit = fields.Integer(string="Jumlah Bibit")
    estimasi_panen = fields.Date(string="Estimasi Panen")
    pegawai_estimasi_id = fields.Many2one(
        "hr.employee",
        string="Pegawai Update Estimasi",
        ondelete="restrict",
    )
    tanggal_update_estimasi = fields.Date(string="Tanggal Update Estimasi")
    catatan_estimasi = fields.Text(string="Catatan Estimasi")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("aktif", "Aktif"),
            ("panen", "Panen"),
            ("selesai", "Selesai"),
        ],
        string="Status",
        default="aktif",
        required=True,
    )
    catatan = fields.Text(string="Catatan")
    estimasi_history_ids = fields.One2many(
        "ipfarm.estimasi_panen_history",
        "batch_id",
        string="Histori Estimasi Panen",
    )
    panen_ids = fields.One2many("ipfarm.panen", "batch_id", string="Hasil Panen")

    @api.constrains("jumlah_bibit")
    def _check_jumlah_bibit(self):
        for batch in self:
            if batch.jumlah_bibit < 0:
                raise ValidationError(_("Jumlah bibit pada batch tidak boleh negatif."))

    @api.constrains("estimasi_panen", "tanggal_tanam")
    def _check_estimasi_panen(self):
        for batch in self:
            if batch.estimasi_panen and batch.tanggal_tanam and batch.estimasi_panen < batch.tanggal_tanam:
                raise ValidationError(_("Estimasi panen tidak boleh lebih awal dari tanggal tanam."))
