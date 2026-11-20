from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request
from werkzeug.exceptions import NotFound, HTTPException

from ..settings import DEFAULT_PATH, PARAM, normalize_path


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    traceback_controller_path = fields.Char(
        string='Traceback controller name', default=DEFAULT_PATH,
        config_parameter=PARAM,
        help='Example: my_error opens /my_error. Only Settings administrators can view the traceback.')

    @api.constrains('traceback_controller_path')
    def _check_traceback_controller_path(self):
        for record in self:
            try:
                normalize_path(record.traceback_controller_path)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc

    def set_values(self):
        self.ensure_one()
        path = normalize_path(self.traceback_controller_path)
        old_path = self.env['ir.config_parameter'].sudo().get_param(PARAM, DEFAULT_PATH)
        if path != old_path:
            if not self.env.user.has_group('base.group_system') or not (request and request.session.debug):
                raise AccessError('Enable developer mode as a Settings administrator to change this URL.')
            # Do not take over another module's registered route.
            adapter = self.env['ir.http'].routing_map().bind('localhost')
            try:
                adapter.match(path, method='GET')
            except NotFound:
                pass
            except HTTPException as exc:
                raise ValidationError('This URL is reserved by another route.') from exc
            else:
                raise ValidationError('This URL already belongs to another controller. Choose another name.')
        self.traceback_controller_path = path
        result = super().set_values()
        if request and self.env.user.has_group('base.group_system'):
            from ..emergency import authorize_browser
            authorize_browser(request, path)
        return result

    def action_open_traceback(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system') or not (request and request.session.debug):
            raise AccessError('Enable developer mode as a Settings administrator.')
        from urllib.parse import urlencode
        from ..emergency import authorize_browser
        path = self.env['ir.config_parameter'].sudo().get_param(PARAM, DEFAULT_PATH)
        if normalize_path(self.traceback_controller_path) != path:
            raise ValidationError('Save the controller name first, then click Open traceback.')
        authorize_browser(request, path)
        return {'type': 'ir.actions.act_url', 'url': path + '?' + urlencode({'db': request.db}), 'target': 'new'}
