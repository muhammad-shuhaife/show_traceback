from odoo import http, models
from ..settings import DEFAULT_PATH, INTERNAL_PATH, PARAM


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _match(cls, path_info):
        path = http.request.env['ir.config_parameter'].sudo().get_param(PARAM, DEFAULT_PATH)
        if path_info.rstrip('/') == path:
            # Reuse Odoo's normal route authentication and dispatch mechanisms.
            return super()._match(INTERNAL_PATH)
        return super()._match(path_info)

    @classmethod
    def _handle_error(cls, exception):
        from ..emergency import capture
        capture(exception)
        return super()._handle_error(exception)
