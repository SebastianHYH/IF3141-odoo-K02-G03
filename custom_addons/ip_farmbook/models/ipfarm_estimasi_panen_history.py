from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmEstimasiPanenHistory(models.Model):
    _name = "ipfarm.estimasi_panen_history"
    _description = "Histori Estimasi Panen IP FarmBook"
    _order = "tanggal_pembaruan desc, id desc"

    name = fields.Char(string="Referensi", compute="_compute_name", store=True)
    batch_id = fields.Many2one(
        "ipfarm.batch",
        string="Batch",
        required=True,
        ondelete="restrict",
        index=True,
    )
    tanggal_tanam = fields.Date(string="Tanggal Tanam", related="batch_id.tanggal_tanam", store=True)
    ruangan_id = fields.Many2one("ipfarm.ruangan", string="Ruangan", related="batch_id.ruangan_id", store=True)
    estimasi_panen_lama = fields.Date(string="Estimasi Panen Lama", readonly=True)
    estimasi_panen_baru = fields.Date(string="Estimasi Panen Baru", required=True)
    pegawai_id = fields.Many2one(
        "hr.employee",
        string="Pegawai yang Memperbarui",
        required=True,
        ondelete="restrict",
        default=lambda self: self._default_pegawai_id(),
    )
    tanggal_pembaruan = fields.Date(
        string="Tanggal Pembaruan",
        required=True,
        default=fields.Date.context_today,
    )
    catatan = fields.Text(string="Catatan Estimasi")

    @api.model
    def _default_pegawai_id(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.uid)], limit=1)

    @api.depends("batch_id", "estimasi_panen_baru", "tanggal_pembaruan")
    def _compute_name(self):
        for history in self:
            history.name = "%s - %s" % (
                history.batch_id.display_name or "Estimasi Panen",
                history.tanggal_pembaruan or "",
            )

    @api.onchange("batch_id")
    def _onchange_batch_id(self):
        if self.batch_id:
            self.estimasi_panen_lama = self.batch_id.estimasi_panen

    @api.constrains("batch_id", "estimasi_panen_baru")
    def _check_estimasi(self):
        for history in self:
            if not history.batch_id or not history.batch_id.active:
                raise ValidationError(_("Batch harus valid dan aktif."))
            if not history.estimasi_panen_baru:
                raise ValidationError(_("Estimasi panen baru tidak boleh kosong."))
            if history.tanggal_tanam and history.estimasi_panen_baru < history.tanggal_tanam:
                raise ValidationError(_("Estimasi panen tidak boleh lebih awal dari tanggal tanam."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            batch = self.env["ipfarm.batch"].browse(vals.get("batch_id"))
            vals["estimasi_panen_lama"] = batch.estimasi_panen if batch else False
        records = super().create(vals_list)
        for history in records:
            history.batch_id.write(
                {
                    "estimasi_panen": history.estimasi_panen_baru,
                    "pegawai_estimasi_id": history.pegawai_id.id,
                    "tanggal_update_estimasi": history.tanggal_pembaruan,
                    "catatan_estimasi": history.catatan,
                }
            )
        return records

    def action_show_success(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Estimasi panen diperbarui"),
                "message": _("Batch %s berhasil diperbarui.") % self.batch_id.display_name,
                "type": "success",
                "sticky": False,
            },
        }
