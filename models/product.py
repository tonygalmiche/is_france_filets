# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_entrepot     = fields.Selection([('acpl', u'ACPL'),('tampon', u'Tampon')], "Entrepôt de stockage", default='acpl')
    is_agrement_rlc = fields.Boolean('Agrément RLC', default=False, help="Cocher pour afficher l'agrément sur les factures")





