from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmBatch(models.Model):
    _name = "ipfarm.batch"
    _description = "Batch Penanaman IP FarmBook"
    _order = "name"

    name = fields.Char(string="Nama Batch", required=True, copy=False, readonly=True, default="New")
    active = fields.Boolean(default=True)
    penanaman_id = fields.Many2one(
        "ipfarm.penanaman",
        string="Kode Penanaman",
        ondelete="restrict",
        required=True,
        index=True,
    )
    bibit_id = fields.Many2one(
        "ipfarm.bibit",
        string="Bibit",
        ondelete="restrict",
        required=True,
    )
    ruangan_id = fields.Many2one(
        "ipfarm.ruangan",
        string="Ruangan Tanam",
        ondelete="restrict",
        required=True,
    )
    tanggal_tanam = fields.Date(
        related="penanaman_id.tanggal_penanaman",
        string="Tanggal Tanam",
        store=True,
    )
    jumlah_bibit = fields.Integer(string="Jumlah Bibit", required=True)
    estimasi_panen = fields.Date(string="Estimasi Panen")
    pegawai_estimasi_id = fields.Many2one(
        "hr.employee",
        string="Pegawai Update Estimasi",
        ondelete="restrict",
    )
    tanggal_update_estimasi = fields.Date(string="Tanggal Update Estimasi")
    catatan_estimasi = fields.Text(string="Catatan Estimasi")
    pegawai_last_edit_id = fields.Many2one(
        "hr.employee",
        string="Terakhir Diubah Oleh",
        ondelete="restrict",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("aktif", "Aktif"),
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

    def _get_current_employee(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.uid)], limit=1)

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

    @api.model_create_multi
    def create(self, vals_list):
        employee = self._get_current_employee()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                penanaman_id = vals.get("penanaman_id")
                penanaman = self.env["ipfarm.penanaman"].browse(penanaman_id)
                existing_count = self.search_count([("penanaman_id", "=", penanaman_id)])
                vals["name"] = f"{penanaman.name}/B{existing_count + 1:02d}"
            if employee:
                vals["pegawai_last_edit_id"] = employee.id
        return super().create(vals_list)

    def write(self, vals):
        employee = self._get_current_employee()
        if employee:
            vals["pegawai_last_edit_id"] = employee.id
        return super().write(vals)
