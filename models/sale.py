# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IsTypePrestation(models.Model):
    _name='is.type.prestation'
    _order='name'

    name = fields.Char(u'Type de prestation')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_nom_chantier        = fields.Char('Nom du chantier')
    is_date_previsionnelle = fields.Date('Date prévisionnelle du chantier')
    is_contact_id          = fields.Many2one('res.partner', u'Contact du client')
    is_distance_chantier   = fields.Integer('Distance du chantier (en km)')
    is_entete_devis        = fields.Text('Entête devis')
    is_superficie          = fields.Char('Superficie')
    is_hauteur             = fields.Char('Hauteur')
    is_nb_interventions    = fields.Char("Nombre d'interventions")
    is_type_chantier       = fields.Selection([
        ('Neuf', 'Neuf'),
        ('Rénovation', 'Rénovation'),
    ], 'Type de chantier')
    is_type_prestation_id  = fields.Many2one('is.type.prestation', u'Type de prestation')



