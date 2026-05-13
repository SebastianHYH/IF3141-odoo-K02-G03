from datetime import timedelta

from odoo import api, fields, models, _


class IPFarmDashboardWizard(models.TransientModel):
    _name = "ipfarm.dashboard_wizard"
    _description = "Dashboard Analitik Operasional IP FarmBook"

    date_start = fields.Date(string="Tanggal Mulai")
    date_end = fields.Date(string="Tanggal Selesai", default=fields.Date.context_today)
    produk_id = fields.Many2one("ipfarm.produk", string="Produk")
    ruangan_id = fields.Many2one("ipfarm.ruangan", string="Ruangan")
    batch_id = fields.Many2one("ipfarm.batch", string="Batch")

    batch_aktif_count = fields.Integer(string="Batch Aktif", compute="_compute_kpi")
    penanaman_berjalan_count = fields.Integer(string="Penanaman Berjalan", compute="_compute_kpi")
    estimasi_panen_terdekat = fields.Date(string="Estimasi Panen Terdekat", compute="_compute_kpi")
    total_hasil_panen = fields.Float(string="Total Hasil Panen", compute="_compute_kpi")
    stok_produk_terkini = fields.Float(string="Stok Produk Terkini", compute="_compute_kpi")
    produk_stok_rendah_count = fields.Integer(string="Produk Stok Rendah", compute="_compute_kpi")
    total_stok_masuk = fields.Float(string="Total Stok Masuk", compute="_compute_kpi")
    total_stok_keluar = fields.Float(string="Total Stok Keluar", compute="_compute_kpi")
    total_pemrosesan = fields.Float(string="Total Pemrosesan", compute="_compute_kpi")
    prediksi_html = fields.Html(string="Prediksi Sederhana", compute="_compute_kpi", sanitize=False)

    def _date_domain(self, field_name):
        domain = []
        if self.date_start:
            domain.append((field_name, ">=", self.date_start))
        if self.date_end:
            domain.append((field_name, "<=", self.date_end))
        return domain

    def _batch_filter_domain(self):
        domain = []
        if self.batch_id:
            domain.append(("id", "=", self.batch_id.id))
        if self.ruangan_id:
            domain.append(("ruangan_id", "=", self.ruangan_id.id))
        return domain

    @api.depends("date_start", "date_end", "produk_id", "ruangan_id", "batch_id")
    def _compute_kpi(self):
        for wizard in self:
            batch_domain = [("state", "=", "aktif")] + wizard._batch_filter_domain()
            penanaman_domain = []
            if wizard.ruangan_id:
                penanaman_domain.append(("ruangan_id", "=", wizard.ruangan_id.id))
            if wizard.date_start:
                penanaman_domain.append(("tanggal_penanaman", ">=", wizard.date_start))
            if wizard.date_end:
                penanaman_domain.append(("tanggal_penanaman", "<=", wizard.date_end))

            panen_domain = wizard._date_domain("tanggal_panen")
            pemrosesan_domain = wizard._date_domain("tanggal_pemrosesan")
            histori_domain = wizard._date_domain("tanggal")
            if wizard.produk_id:
                panen_domain.append(("produk_id", "=", wizard.produk_id.id))
                pemrosesan_domain.append(("produk_id", "=", wizard.produk_id.id))
                histori_domain.append(("produk_id", "=", wizard.produk_id.id))
            if wizard.batch_id:
                panen_domain.append(("batch_id", "=", wizard.batch_id.id))
            if wizard.ruangan_id:
                panen_domain.append(("batch_id.ruangan_id", "=", wizard.ruangan_id.id))

            produk_domain = []
            if wizard.produk_id:
                produk_domain.append(("id", "=", wizard.produk_id.id))

            batches = self.env["ipfarm.batch"].search(batch_domain)
            nearest = self.env["ipfarm.batch"].search(
                batch_domain + [("estimasi_panen", "!=", False)],
                order="estimasi_panen asc",
                limit=1,
            )
            panen_group = self.env["ipfarm.panen"].read_group(panen_domain, ["jumlah:sum"], [])
            pemrosesan_group = self.env["ipfarm.pemrosesan"].read_group(pemrosesan_domain, ["jumlah:sum"], [])
            histori_group = self.env["ipfarm.histori_stok"].read_group(
                histori_domain,
                ["jumlah_masuk:sum", "jumlah_keluar:sum"],
                [],
            )
            products = self.env["ipfarm.produk"].search(produk_domain)
            low_stock = self.env["ipfarm.produk"].search_count([("status_stok", "in", ["rendah", "habis"])])

            wizard.batch_aktif_count = len(batches)
            wizard.penanaman_berjalan_count = self.env["ipfarm.penanaman"].search_count(penanaman_domain)
            wizard.estimasi_panen_terdekat = nearest.estimasi_panen if nearest else False
            wizard.total_hasil_panen = panen_group[0]["jumlah"] if panen_group else 0.0
            wizard.stok_produk_terkini = sum(products.mapped("stok_tersedia"))
            wizard.produk_stok_rendah_count = low_stock
            wizard.total_pemrosesan = pemrosesan_group[0]["jumlah"] if pemrosesan_group else 0.0
            wizard.total_stok_masuk = histori_group[0]["jumlah_masuk"] if histori_group else 0.0
            wizard.total_stok_keluar = histori_group[0]["jumlah_keluar"] if histori_group else 0.0
            wizard.prediksi_html = wizard._build_prediction_html()

    def _build_prediction_html(self):
        self.ensure_one()
        harvests = self.env["ipfarm.panen"].search([("batch_id.tanggal_tanam", "!=", False)])
        durations = [
            (harvest.tanggal_panen - harvest.batch_id.tanggal_tanam).days
            for harvest in harvests
            if harvest.tanggal_panen and harvest.batch_id.tanggal_tanam
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        date_to = self.date_end or fields.Date.context_today(self)
        date_from = self.date_start or (date_to - timedelta(days=30))
        days = max((date_to - date_from).days + 1, 1)
        histories = self.env["ipfarm.histori_stok"].search([("tanggal", ">=", date_from), ("tanggal", "<=", date_to)])
        if self.produk_id:
            histories = histories.filtered(lambda h: h.produk_id == self.produk_id)
        avg_in = sum(histories.mapped("jumlah_masuk")) / days
        avg_out = sum(histories.mapped("jumlah_keluar")) / days
        current_stock = self.produk_id.stok_tersedia if self.produk_id else sum(self.env["ipfarm.produk"].search([]).mapped("stok_tersedia"))
        projected_7_days = current_stock + ((avg_in - avg_out) * 7)

        if avg_duration:
            panen_text = _("Rata-rata durasi tanam ke panen: %.1f hari.") % avg_duration
        else:
            panen_text = _("Belum ada data panen historis untuk menghitung rata-rata durasi panen.")
        stok_text = _("Prediksi stok 7 hari: %.2f berdasarkan rata-rata stok masuk %.2f/hari dan keluar %.2f/hari.") % (
            projected_7_days,
            avg_in,
            avg_out,
        )
        return "<p>%s</p><p>%s</p>" % (panen_text, stok_text)

    def action_refresh(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Dashboard Analitik Operasional"),
            "res_model": "ipfarm.dashboard_wizard",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "current",
        }

    def action_open_panen(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Analisis Hasil Panen"),
            "res_model": "ipfarm.panen",
            "view_mode": "graph,pivot,tree,form",
            "views": [(False, "graph"), (False, "pivot"), (False, "tree"), (False, "form")],
            "domain": self._date_domain("tanggal_panen"),
        }

    def action_open_histori_stok(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Tren Stok Masuk dan Keluar"),
            "res_model": "ipfarm.histori_stok",
            "view_mode": "graph,pivot,tree,form",
            "views": [(False, "graph"), (False, "pivot"), (False, "tree"), (False, "form")],
            "domain": self._date_domain("tanggal"),
        }
