from datetime import timedelta

from odoo import api, fields, models


class TracebackLog(models.Model):
    _name = 'traceback.log'
    _description = 'HTTP 500 Traceback Log'
    _order = 'id desc'

    name = fields.Char('Reference', readonly=True, index=True)
    error_type = fields.Char(readonly=True)
    error_message = fields.Text(readonly=True)
    traceback = fields.Text(readonly=True)
    path = fields.Char(readonly=True)
    method = fields.Char(readonly=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True)

    @api.autovacuum
    def _gc_old_logs(self):
        """Delete logs older than 30 days."""
        limit = fields.Datetime.now() - timedelta(days=30)
        self.search([('create_date', '<', limit)]).unlink()
