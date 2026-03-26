# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    """Extends the Stock Picking model to include digital signature
    functionality."""
    _inherit = "stock.picking"

    def _default_show_sign(self):
        """Get the default value for the 'Show Digital Signature' field."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'digital_signature.is_show_digital_sign_inventory')

    def _default_enable_options(self):
        """Get the default value for the 'Enable Digital Signature Options'
        field."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'digital_signature.is_enable_options_inventory')

    digital_sign = fields.Binary(string='Signature',
                                 help="Digital signature file")
    sign_by = fields.Char(string='Signed By',
                          help="Name of the person who signed")
    designation = fields.Char(string='Designation',
                              help="Designation of the person who signed")
    sign_on = fields.Datetime(string='Signed On',
                              help="Date and time of signing")
    is_show_sign = fields.Boolean(string="Show Sign",
                                  compute='_compute_show_sign',
                                  default=_default_show_sign,
                                  help="Show or hide the digital signature")
    is_enable_option = fields.Boolean(string="Enable Option",
                                      compute='_compute_enable_option',
                                      default=_default_enable_options,
                                      help="Enable or disable digital "
                                           "signature options")
    sign_applicable = fields.Selection(
        [('picking_operations', 'Picking Operations'),
         ('delivery', 'Delivery Slip'), ('both', 'Both')],
        string="Sign Applicable inside", compute='_compute_sign_applicable',
        help="Define where the digital signature is applicable")

    is_sign_user_authorized = fields.Boolean(
        compute='_compute_is_sign_user_authorized',
    )

    @api.model
    def _get_authorized_sign_user_ids(self):
        param = self.env['ir.config_parameter'].sudo().get_param(
            'digital_signature.authorized_user_ids',
            default='',
        )
        user_ids = set()
        if param:
            for part in param.split(','):
                part = part.strip()
                if part.isdigit():
                    user_ids.add(int(part))
        return user_ids

    def _compute_is_sign_user_authorized(self):
        allowed_user_ids = self._get_authorized_sign_user_ids()
        is_authorized = (not allowed_user_ids) or (self.env.user.id in allowed_user_ids)
        for record in self:
            record.is_sign_user_authorized = is_authorized

    def write(self, vals):
        if 'digital_sign' in vals:
            allowed_user_ids = self._get_authorized_sign_user_ids()
            if allowed_user_ids and self.env.user.id not in allowed_user_ids:
                raise UserError(_("You are not allowed to sign this document."))
        return super().write(vals)

    def button_validate(self):
        """Extends the base method to enforce signature confirmation."""
        res = super(StockPicking, self).button_validate()
        if self.env['ir.config_parameter'].sudo().get_param(
                'digital_signature.is_confirm_sign_inventory') and \
                self.digital_sign is False:
            raise UserError('Signature is missing')
        return res

    def _compute_show_sign(self):
        """Compute whether to show or hide the digital signature field."""
        is_show_signature = self._default_show_sign()
        for record in self:
            record.is_show_sign = is_show_signature

    def _compute_enable_option(self):
        """Compute whether to enable or disable digital signature options."""
        is_enable_others = self._default_enable_options()
        for record in self:
            record.is_enable_option = is_enable_others

    def _compute_sign_applicable(self):
        """Compute where the digital signature is applicable."""
        for rec in self:
            rec.sign_applicable = self.env[
                'ir.config_parameter'].sudo().get_param(
                'digital_signature.sign_applicable')
