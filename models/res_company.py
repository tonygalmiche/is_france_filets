# -*- coding: utf-8 -*-

from openerp import models,fields,api
from openerp.tools.translate import _


class res_company(models.Model):
    _inherit = 'res.company'

    is_affacturage          = fields.Text(u'Affacturage')
    is_conditions_generales = fields.Text(u'Conditions générales')


