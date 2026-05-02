from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IPFarmReportWizard(models.TransientModel):
    _name = "ipfarm.report_wizard"
    _description = "Wizard Rekap Data Operasional IP FarmBook"

    date_start = fields.Date(string="Tanggal Mulai", required=True)
    date_end = fields.Date(string="Tanggal Selesai", required=True, default=fields.Date.context_today)
    jenis_data = fields.Selection(
        [
            ("panen", "Hasil Panen"),
            ("stok", "Stok Produk"),
            ("histori_stok", "Histori Stok"),
            ("pemrosesan", "Pemrosesan Produk"),
        ],
        string="Jenis Data Rekap",
        required=True,
    )
    produk_id = fields.Many2one("ipfarm.produk", string="Produk")
    ruangan_id = fields.Many2one("ipfarm.ruangan", string="Ruangan")
    format_output = fields.Selection([("pdf", "PDF")], string="Format Output", required=True, default="pdf")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for wizard in self:
            if wizard.date_start and wizard.date_end and wizard.date_start > wizard.date_end:
                raise ValidationError(_("Tanggal mulai tidak boleh lebih besar dari tanggal selesai."))

    def action_export_pdf(self):
        self.ensure_one()
        if not self.jenis_data:
            raise ValidationError(_("Jenis data rekap harus dipilih."))
        return self.env.ref("ip_farmbook.action_report_ipfarm_operasional").report_action(self)

    def _get_report_title(self):
        self.ensure_one()
        return dict(self._fields["jenis_data"].selection).get(self.jenis_data, _("Rekap Operasional"))

    def _base_product_domain(self):
        return [("id", "=", self.produk_id.id)] if self.produk_id else []

    def _get_report_lines(self):
        self.ensure_one()
        if self.jenis_data == "panen":
            domain = [("tanggal_panen", ">=", self.date_start), ("tanggal_panen", "<=", self.date_end)]
            if self.produk_id:
                domain.append(("produk_id", "=", self.produk_id.id))
            if self.ruangan_id:
                domain.append(("batch_id.ruangan_id", "=", self.ruangan_id.id))
            return [
                {
                    "tanggal": rec.tanggal_panen,
                    "produk": rec.produk_id.display_name,
                    "referensi": rec.name,
                    "keterangan": rec.batch_id.display_name,
                    "masuk": rec.jumlah,
                    "keluar": 0.0,
                    "satuan": rec.uom_id.display_name,
                    "pegawai": rec.pegawai_id.display_name,
                }
                for rec in self.env["ipfarm.panen"].search(domain, order="tanggal_panen asc")
            ]
        if self.jenis_data == "pemrosesan":
            domain = [("tanggal_pemrosesan", ">=", self.date_start), ("tanggal_pemrosesan", "<=", self.date_end)]
            if self.produk_id:
                domain.append(("produk_id", "=", self.produk_id.id))
            return [
                {
                    "tanggal": rec.tanggal_pemrosesan,
                    "produk": rec.produk_id.display_name,
                    "referensi": rec.name,
                    "keterangan": dict(rec._fields["jenis_pemrosesan"].selection).get(rec.jenis_pemrosesan),
                    "masuk": 0.0,
                    "keluar": rec.jumlah,
                    "satuan": rec.uom_id.display_name,
                    "pegawai": rec.pegawai_id.display_name,
                }
                for rec in self.env["ipfarm.pemrosesan"].search(domain, order="tanggal_pemrosesan asc")
            ]
        if self.jenis_data == "histori_stok":
            domain = [("tanggal", ">=", self.date_start), ("tanggal", "<=", self.date_end)]
            if self.produk_id:
                domain.append(("produk_id", "=", self.produk_id.id))
            return [
                {
                    "tanggal": rec.tanggal,
                    "produk": rec.produk_id.display_name,
                    "referensi": rec.name,
                    "keterangan": dict(rec._fields["jenis_kegiatan"].selection).get(rec.jenis_kegiatan),
                    "masuk": rec.jumlah_masuk,
                    "keluar": rec.jumlah_keluar,
                    "satuan": rec.uom_id.display_name,
                    "pegawai": rec.pegawai_id.display_name,
                }
                for rec in self.env["ipfarm.histori_stok"].search(domain, order="tanggal asc")
            ]
        products = self.env["ipfarm.produk"].search(self._base_product_domain(), order="name")
        return [
            {
                "tanggal": product.last_stock_update,
                "produk": product.display_name,
                "referensi": product.kode or "-",
                "keterangan": dict(product._fields["status_stok"].selection).get(product.status_stok),
                "masuk": product.total_stok_masuk_panen,
                "keluar": product.total_stok_keluar_pemrosesan,
                "satuan": product.uom_id.display_name,
                "pegawai": "-",
                "stok_akhir": product.stok_tersedia,
            }
            for product in products
        ]

    def _get_report_summary(self, lines):
        total_masuk = sum(line.get("masuk", 0.0) for line in lines)
        total_keluar = sum(line.get("keluar", 0.0) for line in lines)
        if self.jenis_data == "stok":
            stok_akhir = sum(line.get("stok_akhir", 0.0) for line in lines)
        elif self.produk_id:
            stok_akhir = self.produk_id.stok_tersedia
        else:
            stok_akhir = sum(self.env["ipfarm.produk"].search([]).mapped("stok_tersedia"))
        return {
            "total_masuk": total_masuk,
            "total_keluar": total_keluar,
            "stok_akhir": stok_akhir,
        }


class IPFarmReportOperasional(models.AbstractModel):
    _name = "report.ip_farmbook.report_ipfarm_operasional"
    _description = "Report Rekap Data Operasional IP FarmBook"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["ipfarm.report_wizard"].browse(docids)
        wizard = docs[:1]
        lines = wizard._get_report_lines() if wizard else []
        return {
            "doc_ids": docids,
            "doc_model": "ipfarm.report_wizard",
            "docs": docs,
            "wizard": wizard,
            "lines": lines,
            "summary": wizard._get_report_summary(lines) if wizard else {},
            "title": wizard._get_report_title() if wizard else _("Rekap Operasional"),
            "generated_at": fields.Datetime.context_timestamp(self, fields.Datetime.now()).strftime("%Y-%m-%d %H:%M"),
        }
