# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IsTypePrestation(models.Model):
    _name='is.type.prestation'
    _order='name'

    name = fields.Char(u'Type de prestation')


class IsNacelle(models.Model):
    _name='is.nacelle'
    _order='name'

    name = fields.Char(u'Nacelle')


class IsEquipe(models.Model):
    _name='is.equipe'
    _order='name'

    name = fields.Char(u'Equipe')


class IsSaleOrderPlanning(models.Model):
    _name='is.sale.order.planning'
    _order='order_id,date_debut'

    order_id       = fields.Many2one('sale.order', 'Commande', required=True, ondelete='cascade', readonly=True)
    date_debut     = fields.Date('Date début')
    date_fin       = fields.Date('Date fin')
    commentaire    = fields.Char('Commentaire planning')
    equipe_ids     = fields.Many2many('is.equipe','is_sale_order_planning_equipe_rel','order_id','equipe_id', string="Equipes")
    pose_depose    = fields.Selection([
        ('pose'  , 'Pose'),
        ('depose', 'Dépose'),
    ], 'Pose / Dépose')
    realise = fields.Selection([
        ('oui', 'Oui'),
        ('non', 'Non'),
    ], 'Réalisé')
    realisation    = fields.Char('Réalisation', help=u'Réalisation du chantier')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_nom_chantier        = fields.Char('Nom du chantier')
    is_date_previsionnelle = fields.Date('Date prévisionnelle du chantier')
    is_contact_id          = fields.Many2one('res.partner', u'Contact du client')
    is_distance_chantier   = fields.Integer('Distance du chantier (en km)')
    is_num_ancien_devis    = fields.Char('N°ancien devis')
    is_entete_devis        = fields.Text('Entête devis')
    is_pied_devis          = fields.Text('Pied devis')
    is_superficie          = fields.Char('Superficie')
    is_hauteur             = fields.Char('Hauteur')
    is_nb_interventions    = fields.Char("Nombre d'interventions")
    is_type_chantier       = fields.Selection([
        ('neuf'           , 'Neuf'),
        ('renovation'     , 'Rénovation'),
        ('neuf_renovation', 'Neuf et Rénovation'),
    ], 'Type de chantier')
    is_type_prestation_id  = fields.Many2one('is.type.prestation', u'Type de prestation')
    is_nacelle_id          = fields.Many2one('is.nacelle', u'Nacelle')
    is_planning_ids        = fields.One2many('is.sale.order.planning', 'order_id', u"Planning")








    @api.multi
    def get_nacelles(self):
        nacelles = self.env['is.nacelle'].search([])
        return nacelles





