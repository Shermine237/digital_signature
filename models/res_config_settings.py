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
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Inherit re.config.settings to add more fields"""
    _inherit = 'res.config.settings'

    sign_user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Authorized Sign Users',
        relation='digital_signature_res_config_settings_sign_user_rel',
        column1='settings_id',
        column2='user_id',
        domain=[('share', '=', False)],
    )

    is_show_digital_sign_po = fields.Boolean(
        config_parameter='digital_signature.is_show_digital_sign_po',
        help="Show digital signature for purchase orders.")
    is_enable_options_po = fields.Boolean(
        config_parameter='digital_signature.is_enable_options_po',
        help="Enable options for digital signatures on purchase orders.")
    is_confirm_sign_po = fields.Boolean(
        config_parameter='digital_signature.is_confirm_sign_po',
        help="Require confirmation for digital signatures on purchase orders.")
    is_show_digital_sign_inventory = fields.Boolean(
        config_parameter='digital_signature.is_show_digital_sign_inventory',
        help="Show digital signature for inventory operations.")
    is_enable_options_inventory = fields.Boolean(
        config_parameter='digital_signature.is_enable_options_inventory',
        help="Enable options for digital signatures on inventory operations.")
    sign_applicable = fields.Selection(
        [('picking_operations', 'Picking Operations'),
         ('delivery', 'Delivery Slip'), ('both', 'Both')],
        string="Sign Applicable inside", default="picking_operations",
        config_parameter='digital_signature.sign_applicable',
        help="Define where the digital signature is applicable.")
    is_confirm_sign_inventory = fields.Boolean(
        config_parameter='digital_signature.is_confirm_sign_inventory',
        help="Require confirmation for digital signatures on inventory "
             "operations.")
    is_show_digital_sign_invoice = fields.Boolean(
        config_parameter='digital_signature.is_show_digital_sign_invoice',
        help="Show digital signature for invoices.")
    is_enable_options_invoice = fields.Boolean(
        config_parameter='digital_signature.is_enable_options_invoice',
        help="Enable options for digital signatures on invoices.")
    is_confirm_sign_invoice = fields.Boolean(
        config_parameter='digital_signature.is_confirm_sign_invoice',
        help="Require confirmation for digital signatures on invoices.")
    is_show_digital_sign_bill = fields.Boolean(
        config_parameter='digital_signature.is_show_digital_sign_bill',
        help="Show digital signature for bills.")

    @api.model
    def get_values(self):
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo().get_param(
            'digital_signature.authorized_user_ids',
            default='',
        )
        user_ids = []
        if param:
            for part in param.split(','):
                part = part.strip()
                if part.isdigit():
                    user_ids.append(int(part))
        res.update(sign_user_ids=[(6, 0, user_ids)])
        return res

    def set_values(self):
        res = super().set_values()
        value = ','.join(str(uid) for uid in self.sign_user_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'digital_signature.authorized_user_ids',
            value,
        )
        return res
