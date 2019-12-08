# -*- coding: utf-8 -*-

from openerp import models,fields,api
from openerp.tools.translate import _


class res_company(models.Model):
    _inherit = 'res.company'

    is_affacturage          = fields.Text(u'Affacturage')
    is_conditions_generales = fields.Text(u'Conditions générales')

    is_sms_account  = fields.Char(u'SMS account')
    is_sms_login    = fields.Char(u'SMS login')
    is_sms_password = fields.Char(u'SMS password')
    is_sms_from     = fields.Char(u'SMS from')
    is_sms_message  = fields.Text(u'SMS message')


