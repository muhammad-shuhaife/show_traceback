from odoo import http
from odoo.http import request, Response
from werkzeug.exceptions import Forbidden, NotFound

from .. import store
from ..emergency import authorize_browser
from ..page import render_page, HEADERS
from ..settings import DEFAULT_PATH, INTERNAL_PATH, PARAM


class CurrentError(http.Controller):
    @http.route(INTERNAL_PATH, type='http', auth='user', methods=['GET'], sitemap=False)
    def current_error(self, **kwargs):
        path = request.env['ir.config_parameter'].sudo().get_param(PARAM, DEFAULT_PATH)
        if request.httprequest.path.rstrip('/') != path:
            raise NotFound()
        if not request.env.user.has_group('base.group_system'):
            raise Forbidden()
        authorize_browser(request, path)
        return Response(render_page(store.current(request.db)),
                        content_type='text/html; charset=utf-8', headers=HEADERS)
